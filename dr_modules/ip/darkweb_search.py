import requests
from urllib.parse import quote
from bs4 import BeautifulSoup

def ahmia_search(query):
    """
    Safe Ahmia clearnet search for OSINT.
    Tries JSON first; if not available, parses HTML.
    Never connects to the dark web.
    """
    safe_query = quote(query)
    url = f"https://ahmia.fi/search/?q={safe_query}&format=json"

    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "AIGT-OSINT"})
        response.raise_for_status()

        # --- Try parsing JSON first ---
        try:
            data = response.json()
            if "results" in data:
                return data["results"]
        except ValueError:
            pass  # Fall back to HTML below

        # --- HTML fallback parsing ---
        html_url = f"https://ahmia.fi/search/?q={safe_query}"
        html_resp = requests.get(html_url, timeout=15, headers={"User-Agent": "AIGT-OSINT"})
        html_resp.raise_for_status()
        soup = BeautifulSoup(html_resp.text, "html.parser")

        results = []
        for result in soup.select("li.result"):
            title = result.find("a").get_text(strip=True) if result.find("a") else None
            link = result.find("a")["href"] if result.find("a") else None
            snippet = result.find("p").get_text(strip=True) if result.find("p") else None

            if link and ".onion" in link:
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })

        return results

    except requests.RequestException as e:
        print(f"[!] Error querying Ahmia: {e}")
        return None


# Example usage
if __name__ == "__main__":
    query = "bitcoin market"
    results = ahmia_search(query)

    if results:
        print(f"\n[+] Found {len(results)} dark web results on Ahmia:\n")
        for entry in results[:10]:  # limit output
            print(f"Title: {entry.get('title')}")
            print(f"Link: {entry.get('link')}")
            print(f"Snippet: {entry.get('snippet')}\n")
    else:
        print("[!] No results found or connection error.")
