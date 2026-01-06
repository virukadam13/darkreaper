
import requests
from bs4 import BeautifulSoup

class LeakCheckAPI:
    def __init__(self, api_key, phone):
        self.api_key = api_key
        self.phone = phone

    def check(self):
        url = f"https://leakcheck.io/api/public?key={self.api_key}&check={self.phone}"
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            if data.get("found"):
                return {"source": "LeakCheck", "status": "leaked"}
            else:
                return {"source": "LeakCheck", "status": "not_leaked"}
        except Exception as e:
            return {"source": "LeakCheck", "status": f"error: {e}"}


class BreachDirectoryScraper:
    def __init__(self, phone):
        self.phone = phone

    def check(self):
        # fallback using web search method
        url = f"https://breachdirectory.org/search?query={self.phone}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if "No results found" in r.text:
                return {"source": "BreachDirectory", "status": "not_leaked"}
            elif "results found" in r.text or "results" in r.text.lower():
                return {"source": "BreachDirectory", "status": "leaked"}
            elif len(r.text.strip()) == 0:
                return {"source": "BreachDirectory", "status": "error: empty response"}
            else:
                # heuristic check
                soup = BeautifulSoup(r.text, "html.parser")
                if soup.find(string=lambda x: x and "results" in x.lower()):
                    return {"source": "BreachDirectory", "status": "leaked"}
                else:
                    return {"source": "BreachDirectory", "status": "not_leaked"}
        except Exception as e:
            return {"source": "BreachDirectory", "status": f"error: {e}"}



def main():
    phone = input("+919850112195").strip()
    leakcheck_key = "api_key"  # register at leakcheck.io

    apis = [
        LeakCheckAPI(leakcheck_key, phone),
        BreachDirectoryScraper(phone),
    ]

    print(f"\n🔍 Checking {phone} against free breach sources:\n")
    for api in apis:
        result = api.check()
        status = result["status"]
        if status == "found":
            print(f"✅ {result['source']}: Found in breaches!")
        elif status == "not_found":
            print(f"❌ {result['source']}: Not found.")
        else:
            print(f"⚠️ {result['source']}: {status}")


if __name__ == "__main__":
    main()
