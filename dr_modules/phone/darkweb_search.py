import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
import argparse
import json
import os
import time
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.error
import re
import subprocess
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional


api_key = "api_key"
class OnionSearch:
    """Search engine for .onion sites via OnionSearchEngine API"""
    
    API_URL = "https://onionsearchengine.com/api.php"
    USER_AGENT = "aigt-client/working.py (https://github.com/)"
    RETRY_DELAY = 3

    def __init__(self, api_key: str, timeout: int = 15):
        self.api_key = api_key
        self.timeout = timeout

    def _call_api(self, query: str, page: int = 1) -> Optional[Dict[str, Any]]:
        """Make API call to OnionSearchEngine"""
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "application/json",
            "X-API-Key": self.api_key
        }
        params = {"q": query, "page": page}

        try:
            resp = requests.get(self.API_URL, headers=headers, params=params, timeout=self.timeout)
        except requests.RequestException:
            return None

        if resp.status_code == 429:
            time.sleep(self.RETRY_DELAY)
            try:
                resp = requests.get(self.API_URL, headers=headers, params=params, timeout=self.timeout)
            except requests.RequestException:
                return None

        if resp.status_code != 200:
            return None

        try:
            return resp.json()
        except ValueError:
            return None

    def _extract_results(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return a list of results dictionaries from the API JSON response."""
        if not isinstance(json_data, dict):
            return []
        for key in ("results", "data", "items"):
            val = json_data.get(key)
            if isinstance(val, list):
                return val
        return []

    def search(self, query: str, pages: int = 1) -> List[Dict[str, Any]]:
        """
        Perform a search query and return combined results as a list of dicts.

        Each dict typically contains: 'title', 'url', 'context', 'rank', etc.
        """
        all_results: List[Dict[str, Any]] = []

        for page in range(1, pages + 1):
            json_data = self._call_api(query, page=page)
            if not json_data:
                continue
            results = self._extract_results(json_data)
            all_results.extend(results)
            time.sleep(0.2)  # small delay to be polite

        return all_results


ONION_RE = re.compile(r"[a-z2-7]{16,56}\.onion", re.IGNORECASE)
PGP_LINK_RE = re.compile(r"\.asc$|\.sig$|pgp", re.IGNORECASE)
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

class DarkFailChecker:
    def __init__(self, base_url: str = "https://dark.fail/", outdir: str = "darkfail_artifacts", timeout: int = 15):
        """
        Create a checker instance.
        - base_url: clearnet URL to scrape (default https://dark.fail/)
        - outdir: where to store downloaded artefacts (pgp, sigs, onion_homepages)
        - timeout: requests timeout seconds
        """
        self.base_url = base_url
        self.outdir = outdir
        self.timeout = timeout
        os.makedirs(self.outdir, exist_ok=True)

    def fetch(self, url: Optional[str] = None) -> str:
        """Fetch page HTML (returns empty string on error)."""
        url = url or self.base_url
        try:
            r = requests.get(url, headers=HEADERS, timeout=self.timeout, allow_redirects=True)
            r.raise_for_status()
            return r.text
        except requests.RequestException as e:
            print(f"[!] fetch error for {url}: {e}")
            return ""

    def extract_onions_with_context(self, html: str, context_lines: int = 6) -> List[Dict[str, str]]:
        """Extract unique .onion addresses and a small surrounding text snippet (context_lines)."""
        lines = html.splitlines()
        results = []
        seen = set()
        for idx, line in enumerate(lines):
            for m in ONION_RE.finditer(line):
                onion = m.group(0).lower()
                if onion in seen:
                    continue
                seen.add(onion)
                start = max(0, idx - context_lines)
                end = min(len(lines), idx + 2)
                snippet = " ".join(lines[start:end])
                snippet = re.sub(r"\s+", " ", snippet)
                snippet = re.sub(r"<[^>]+>", "", snippet)
                results.append({"onion": onion, "context": snippet})
        results.sort(key=lambda x: x["onion"])
        return results

    def find_pgp_links(self, html: str) -> List[str]:
        """Return deduplicated list of absolute URLs that look like PGP keys/signatures."""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            # resolve relative links
            full = urljoin(self.base_url, href)
            if PGP_LINK_RE.search(href) or "pgp" in href.lower() or "signature" in href.lower():
                links.append(full)
        # catch explicit plain-text URLs in page body too
        text_urls = re.findall(r"https?://[^\s'\"<>]+", html)
        for u in text_urls:
            if PGP_LINK_RE.search(u) or "pgp" in u.lower() or "signature" in u.lower():
                links.append(u)
        # dedupe while preserving order
        seen = []
        for l in links:
            if l not in seen:
                seen.append(l)
        return seen

    def download_file(self, url: str) -> Optional[str]:
        """Download resource at url into outdir; return saved path or None on error."""
        try:
            r = requests.get(url, headers=HEADERS, timeout=self.timeout, stream=True)
            r.raise_for_status()
            filename = os.path.basename(urlparse(url).path) or "downloaded_file"
            outpath = os.path.join(self.outdir, filename)
            with open(outpath, "wb") as fh:
                for chunk in r.iter_content(8192):
                    fh.write(chunk)
            return outpath
        except requests.RequestException as e:
            print(f"[!] Download error {url}: {e}")
            return None

    def verify_gpg(self, sig_path: str, data_path: str) -> Dict[str, str]:
        """
        Run `gpg --verify sig_path data_path` and return dict with 'ok' (bool), 'stdout' and 'stderr'.
        Requires `gpg` in PATH. This does not auto-trust keys — you'll still need to check fingerprints manually.
        """
        result = {"ok": False, "stdout": "", "stderr": ""}
        try:
            proc = subprocess.run(["gpg", "--verify", sig_path, data_path], capture_output=True, text=True, timeout=30)
            result["stdout"] = proc.stdout.strip()
            result["stderr"] = proc.stderr.strip()
            result["ok"] = proc.returncode == 0
            return result
        except FileNotFoundError:
            result["stderr"] = "gpg not found in PATH"
            return result
        except subprocess.SubprocessError as e:
            result["stderr"] = f"gpg error: {e}"
            return result

    def fetch_onion_via_tor(self, onion: str, save_filename: Optional[str] = None) -> Optional[str]:
        """
        Attempt to fetch an .onion homepage with torsocks+curl.
        - Requires `torsocks` (and tor) installed and running.
        - Returns saved path or None on error.
        """
        save_filename = save_filename or f"{onion.replace('.onion','')}_home.html"
        outpath = os.path.join(self.outdir, save_filename)
        cmd = ["torsocks", "curl", "-sS", f"http://{onion}/", "-o", outpath]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if proc.returncode == 0:
                return outpath
            else:
                print(f"[!] torsocks curl failed for {onion}: rc={proc.returncode}")
                print("stderr:", proc.stderr.strip())
                return None
        except FileNotFoundError:
            print("[!] torsocks not found in PATH")
            return None
        except subprocess.SubprocessError as e:
            print(f"[!] torsocks subprocess error: {e}")
            return None

    def run(self, query: Optional[str] = None, save_json: Optional[str] = None,
            auto_verify_gpg: bool = False, fetch_onion_via_tor: bool = False) -> Dict:
        """
        High-level runner:
          - fetch clearnet page
          - extract onion entries
          - find & download pgp/sig files
          - optionally run gpg verify if pairs are obvious (heuristic)
          - optionally fetch first discovered onion via torsocks
        Returns a result dict with keys: source, onions, pgp_links, downloaded, gpg_verifications, tor_fetches
        """
        html = self.fetch(self.base_url)
        if not html:
            return {"error": "failed to fetch base page", "source": self.base_url}
        onions = self.extract_onions_with_context(html)
        if query:
            q = query.lower()
            onions = [it for it in onions if q in it["onion"] or q in it["context"].lower()]

        pgp_links = self.find_pgp_links(html)
        downloaded = []
        gpg_verifications = []
        tor_fetches = []

        # download any pgp/signature-related links
        for link in pgp_links:
            path = self.download_file(link)
            if path:
                downloaded.append({"url": link, "path": path})

        # optional: run gpg verifies heuristically if both .sig/.asc and a candidate data file exist
        if auto_verify_gpg:
            # naive pairing: if we downloaded both a .asc/.sig and a file without extension nearby, try to verify
            # (this is heuristic — many sites use detached sigs; manual steps are safer)
            downloaded_paths = [d["path"] for d in downloaded]
            for p in downloaded_paths:
                # if p looks like a signature file (.sig or .asc) try to find a data file with similar basename
                if p.lower().endswith((".sig", ".asc")):
                    base = os.path.splitext(os.path.basename(p))[0]
                    # find candidate data files in downloaded list
                    candidates = [c for c in downloaded_paths if base in os.path.basename(c) and c != p]
                    for cand in candidates:
                        res = self.verify_gpg(p, cand)
                        gpg_verifications.append({"sig": p, "data": cand, "result": res})

        # optional: fetch first onion via torsocks
        if fetch_onion_via_tor and onions:
            first_onion = onions[0]["onion"]
            fetched = self.fetch_onion_via_tor(first_onion)
            tor_fetches.append({"onion": first_onion, "path": fetched})

        # save JSON if requested
        payload = {
            "source": self.base_url,
            "count_onions": len(onions),
            "onions": onions,
            "pgp_links": pgp_links,
            "downloaded": downloaded,
            "gpg_verifications": gpg_verifications,
            "tor_fetches": tor_fetches,
        }
        if save_json:
            try:
                with open(save_json, "w", encoding="utf-8") as fh:
                    json.dump(payload, fh, indent=2, ensure_ascii=False)
                print(f"[*] saved results to {save_json}")
            except Exception as e:
                print(f"[!] error saving json: {e}")

        # print a short summary
        print(f"[*] found {len(onions)} onion(s), {len(pgp_links)} PGP-related link(s), {len(downloaded)} downloaded file(s).")
        if gpg_verifications:
            print(f"[*] performed {len(gpg_verifications)} gpg verification attempts (see payload).")
        if tor_fetches:
            print(f"[*] attempted {len(tor_fetches)} torsocks fetch(es).")

        return payload

class Ahmia:
    """Ahmia search engine interface for .onion site discovery"""
    
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def search(self, query: str) -> Optional[List[Dict[str, str]]]:
        """
        Safe Ahmia clearnet search for OSINT.
        Tries JSON first; if not available, parses HTML.
        Never connects to the dark web.
        """
        safe_query = quote(query)
        url = f"https://ahmia.fi/search/?q={safe_query}&format=json"

        try:
            response = requests.get(url, timeout=self.timeout, 
                                  headers={"User-Agent": "AIGT-OSINT"})
            response.raise_for_status()

            # Try parsing JSON first
            try:
                data = response.json()
                if "results" in data:
                    return data["results"]
            except ValueError:
                pass  # Fall back to HTML below

            # HTML fallback parsing
            return self._parse_html_search(safe_query)
            
        except requests.RequestException as e:
            print(f"[!] Error querying Ahmia: {e}")
            return None

    def _parse_html_search(self, safe_query: str) -> List[Dict[str, str]]:
        """Parse HTML results from Ahmia search"""
        html_url = f"https://ahmia.fi/search/?q={safe_query}"
        try:
            html_resp = requests.get(html_url, timeout=self.timeout, 
                                   headers={"User-Agent": "AIGT-OSINT"})
            html_resp.raise_for_status()
            soup = BeautifulSoup(html_resp.text, "html.parser")

            results = []
            for result in soup.select("li.result"):
                title_elem = result.find("a")
                snippet_elem = result.find("p")
                
                title = title_elem.get_text(strip=True) if title_elem else "No title"
                link = title_elem.get("href") if title_elem else None
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No snippet"

                if link and ".onion" in link:
                    results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet
                    })

            return results
            
        except requests.RequestException as e:
            print(f"[!] Error fetching HTML from Ahmia: {e}")
            return []


# Example usage function
def main():
    """Example usage of the darkweb search modules"""
    
    # Example with OnionSearch (requires API key)
    searcher = OnionSearch(api_key)
    results = searcher.search("example query", pages=1)
    print(results)
    
    # Example with DarkFail
    checker = DarkFailChecker()
    result = checker.run(save_json="darkfail_results.json", auto_verify_gpg=False, fetch_onion_via_tor=False)
    # pretty print short list
    for o in result.get("onions", []):
        print(" -", o["onion"])
    
    # Example with Ahmia
    ahmia = Ahmia()
    ahmia_results = ahmia.search("example")
    print(f"Ahmia found {len(ahmia_results) if ahmia_results else 0} results")


if __name__ == "__main__":
    main()