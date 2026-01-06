import requests
import json
from bs4 import BeautifulSoup
import subprocess
import os
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime, timezone


class HaveIBeenPwned:
    def __init__(self, api_key=None):
        self.base_url = "https://haveibeenpwned.com/api/v3"
        self.headers = {
            'User-Agent': 'OSINT-Tool-v1.0',
            'hibp-api-key': api_key if api_key else ''
        }
    
    def check_email(self, email):
        """Check if email appears in breaches using HIBP API"""
        try:
            url = f"{self.base_url}/breachedaccount/{email}"
            response = requests.get(url, headers=self.headers, params={'truncateResponse': 'false'})
            
            if response.status_code == 200:
                breaches = response.json()
                return {
                    'breached': True,
                    'breach_count': len(breaches),
                    'breaches': [{'name': b['Name'], 'date': b['BreachDate']} for b in breaches]
                }
            elif response.status_code == 404:
                return {'breached': False, 'breach_count': 0}
            else:
                return {'error': f"API error: {response.status_code}"}
        except Exception as e:
            return {'error': str(e)}

class BreachDirectory:
    def __init__(self, api_key=None):
        self.api_key = api_key
    
    def check_email(self, email):
        """Check email in BreachDirectory"""
        try:
            if not self.api_key:
                return {'error': 'API key required for BreachDirectory'}
                
            url = "https://breachdirectory.p.rapidapi.com/"
            headers = {
                'X-RapidAPI-Key': self.api_key,
                'X-RapidAPI-Host': 'breachdirectory.p.rapidapi.com'
            }
            params = {'func': 'auto', 'term': email}
            
            response = requests.get(url, headers=headers, params=params)
            return response.json() if response.status_code == 200 else {'error': f"API error: {response.status_code}"}
        except Exception as e:
            return {'error': str(e)}
        

# api_key = "221959
class LeakCheck:
    def __init__(self, api_key: str | None = None, cache_dir="results/cache", max_retries=2):
        self.api_key = api_key or os.getenv("LEAKCHECK_API_KEY", "").strip()
        self.base_auth = "https://leakcheck.io/api"
        self.base_public = "https://leakcheck.io/api/public"
        self.cache_dir = cache_dir
        self.max_retries = max_retries
        os.makedirs(self.cache_dir, exist_ok=True)

    def _cache_path(self, email: str):
        safe = re.sub(r'[^a-zA-Z0-9_.-]', '_', email)
        return os.path.join(self.cache_dir, f"leakcheck_{safe}.json")

    def _load_cache(self, email: str):
        path = self._cache_path(email)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def _save_cache(self, email: str, data: dict):
        path = self._cache_path(email)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def check_email(self, email: str):
        # try cache first (quick dev convenience)
        cached = self._load_cache(email)
        if cached:
            cached['cached'] = True
            return cached

        # If user provided API key — call authenticated API (same contract as before)
        if self.api_key:
            params = {'key': self.api_key, 'check': email, 'type': 'email'}
            try:
                resp = requests.get(self.base_auth + "/", params=params, timeout=20)
            except Exception as e:
                return {'error': f"request exception: {e}"}

            if resp.status_code == 200:
                try:
                    js = resp.json()
                    out = {
                        "source": "leakcheck",
                        "method": "auth",
                        "found": bool(js.get("found", False)),
                        "fields": js.get("fields", []),
                        "sources": js.get("sources", []),
                        "raw": js
                    }
                    self._save_cache(email, out)
                    out['cached'] = False
                    return out
                except Exception:
                    return {'error': 'failed to parse LeakCheck (auth) JSON'}
            elif resp.status_code in (401, 403):
                return {'error': f'forbidden ({resp.status_code}): LeakCheck key invalid or quota exceeded'}
            else:
                return {'error': f"LeakCheck (auth) API returned status {resp.status_code}"}

        # No API key -> use public endpoint fallback
        query_url = f"{self.base_public}?check={email}"
        headers = {"User-Agent": "AIGT/LeakCheckPublic"}
        last_exc = None
        for attempt in range(self.max_retries):
            try:
                r = requests.get(query_url, headers=headers, timeout=20)
                # public endpoint commonly returns 200
                if r.status_code == 200:
                    try:
                        js = r.json()
                    except Exception:
                        return {'error': 'failed to parse LeakCheck public JSON', 'status_code': r.status_code}
                    # Normalise public response (observed fields: success, found, fields, sources)
                    out = {
                        "source": "leakcheck",
                        "method": "public",
                        "found": bool(js.get("found") or js.get("success") and js.get("found")),
                        "fields": js.get("fields", []),
                        "sources": js.get("sources", []),
                        "raw": js
                    }
                    self._save_cache(email, out)
                    out['cached'] = False
                    return out
                elif r.status_code in (429, 503):
                    # rate-limited or temporary issue: small backoff and retry
                    last_exc = f"status {r.status_code}"
                    time.sleep(1 + attempt)
                    continue
                else:
                    return {'error': f'LeakCheck public endpoint returned status {r.status_code}'}
            except Exception as e:
                last_exc = str(e)
                time.sleep(0.6)

        return {'error': f'LeakCheck public endpoint failure: {last_exc}'}




class Dehashed:
    def __init__(self, email=None, api_key=None):
        self.email = email
        self.api_key = api_key
    
    def search(self, query):
        """Search Dehashed (limited free tier)"""
        try:
            if not self.api_key:
                return {'error': 'API key required for Dehashed'}
                
            url = "https://api.dehashed.com/search"
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Basic {self.api_key}'
            }
            params = {'query': query}
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            return response.json() if response.status_code == 200 else {'error': f"API error: {response.status_code}"}
        except Exception as e:
            return {'error': str(e)}
        
class H8mailLookup:
    """
    Integrates the open-source h8mail tool for email breach checks.
    Requires h8mail installed and accessible in PATH.
    """

    def __init__(self, output_dir="results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def lookup(self, email: str) -> dict:
        """Run h8mail and parse JSON/text output for a single email."""
        cmd = f"h8mail -t {email}"
        try:
            process = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=300
            )
        except subprocess.TimeoutExpired:
            return {"source": "h8mail", "email": email, "found": False, "error": "timeout"}

        raw_out = process.stdout.strip()
        if not raw_out:
            return {"source": "h8mail", "email": email, "found": False}

        # try:
        #     data = json.loads(raw_out)
        #     found = bool(data)
        # except json.JSONDecodeError:
        # Sometimes h8mail outputs non-JSON; fallback parser
        lines = [l.strip() for l in raw_out.splitlines() if l.strip()]
        data = [{"breach": l} for l in lines]
        found = len(data) > 0

        result = {
            "source": "h8mail",
            "email": email,
            "found": found,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.save_to_json(email, result)
        return result

    def save_to_json(self, email: str, data: dict):
        """Save result to a JSON file."""
        safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", email)
        path = os.path.join(self.output_dir, f"h8mail_{safe_name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return path
    

class PasteSiteLookup:
    """
    Searches multiple paste sites for leaks using free HTML queries.
    Focuses on reliability and clean link extraction.
    """

    def __init__(self, output_dir="results", max_retries=2):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.max_retries = max_retries
        self.sources = {
            "pastebin": "https://pastebin.com/search?q={query}",
            "pastetool": "https://paste.tools/search?query={query}",
            "psbdmp": "https://psbdmp.ws/api/search/{query}",
            "dumpz": "https://dumpz.org/en/search/?q={query}",
        }

    def lookup(self, email: str) -> dict:
        headers = {"User-Agent": "Mozilla/5.0 (AIGT Paste OSINT)"}
        all_hits = []

        for name, url in self.sources.items():
            search_url = url.format(query=email)
            for attempt in range(self.max_retries):
                try:
                    r = requests.get(search_url, headers=headers, timeout=12)
                    if r.status_code == 200:
                        new_hits = self._extract_hits(name, r.text, email)
                        all_hits.extend(new_hits)
                    break  # success or 404 → break retry loop
                except Exception as e:
                    if attempt + 1 == self.max_retries:
                        all_hits.append({"source": name, "error": str(e)})
                    time.sleep(1.5)  # backoff

        # Deduplicate by URL
        unique_hits = []
        seen = set()
        for hit in all_hits:
            if "url" in hit and hit["url"] not in seen:
                seen.add(hit["url"])
                unique_hits.append(hit)

        found = len(unique_hits) > 0
        result = {
            "source": "paste_sites",
            "email": email,
            "found": found,
            "data": unique_hits,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
#       self._save_to_json(email, result)
        return result

    def _extract_hits(self, source_name: str, html: str, email: str):
        """Extract possible paste URLs or matches from HTML."""
        hits = []

        # Try JSON (some APIs like psbdmp.ws)
        try:
            js = json.loads(html)
            if isinstance(js, list):
                for j in js:
                    if "id" in j:
                        hits.append(
                            {"source": source_name, "url": f"https://psbdmp.ws/{j['id']}"}
                        )
                return hits
        except json.JSONDecodeError:
            pass

        # Otherwise parse HTML
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if re.search(r"(paste|view|dump|id)[/=_-]", href, re.I):
                if not href.startswith("http"):
                    href = f"https://{source_name}.com{href}"
                hits.append({"source": source_name, "url": href})
        # Optional: simple text search fallback
        if email.lower() in html.lower():
            hits.append({"source": source_name, "context": "email_mentioned"})

        return hits

    def _save_to_json(self, email: str, data: dict):
        safe = re.sub(r"[^a-zA-Z0-9_.-]", "_", email)
        path = os.path.join(self.output_dir, f"pastes_{safe}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return path


if __name__ == "__main__":
    print("Testing Breaches & Leaks Module...")
    test_email = "johndoe@gmail.com"
    email = "johndoe@gmail.com"
    
    # Test HaveIBeenPwned
    print("\n1. Testing HaveIBeenPwned...")
    hibp = HaveIBeenPwned()
    result = hibp.check_email(test_email)
    print(f"   Result: {result}")
    
    # Test BreachDirectory
    print("\n2. Testing BreachDirectory...")
    breach_dir = BreachDirectory()
    result = breach_dir.check_email(test_email)
    print(f"   Result: {result}")
    
    # Test LeakCheck
    lc = LeakCheck()
    res = lc.check_email("johndoe@gmail.com")
    print(json.dumps(res, indent=2))
    
    # Test Dehashed
    print("\n4. Testing Dehashed...")
    dehashed = Dehashed()
    result = dehashed.search(test_email)
    print(f"   Result: {result}")
    
    # Test h8mail
    print("[*] Running H8mailLookup...")
    h8 = H8mailLookup()
    print(json.dumps(h8.lookup(email), indent=2))

    # Test pastesite
    print("\n[*] Running PasteSiteLookup...")
    paste = PasteSiteLookup()
    print(json.dumps(paste.lookup(email), indent=2))

    print("\nBreaches & Leaks module test completed!")