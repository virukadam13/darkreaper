from ddgs import DDGS
from googlesearch import search as google_search
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import time

class GoogleSearch:
    """Google search engine"""
    
    def __init__(self):
        self.name = "google"
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        results = []
        try:
            for url in google_search(query, num=num_results, stop=num_results, pause=1):
                results.append({
                    "url": url,
                    "title": self._extract_title_from_url(url),
                    "source": "google",
                    "query": query
                })
        except Exception as e:
            print(f"Google search error: {e}")
        return results
    
    def _extract_title_from_url(self, url: str) -> str:
        try:
            domain = url.split('//')[-1].split('/')[0]
            return f"Google: {domain}"
        except:
            return "Google Result"

class DuckDuckGoSearch:
    """DuckDuckGo search engine"""
    
    def __init__(self):
        self.name = "duckduckgo"
        self.ddgs = DDGS()
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        results = []
        try:
            for result in self.ddgs.text(query, max_results=num_results):
                results.append({
                    "url": result.get('href', ''),
                    "title": result.get('title', ''),
                    "snippet": result.get('body', ''),
                    "source": "duckduckgo",
                    "query": query
                })
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
        return results

class BingSearch:
    """Bing search engine (via HTML scraping)"""
    
    def __init__(self):
        self.name = "bing"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        results = []
        try:
            url = f"https://www.bing.com/search?q={query}&count={num_results}"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Bing result selectors
            for result in soup.find_all('li', class_='b_algo')[:num_results]:
                link = result.find('a')
                if link and link.get('href'):
                    title = link.get_text(strip=True)
                    results.append({
                        "url": link.get('href'),
                        "title": f"Bing: {title}" if title else "Bing Result",
                        "source": "bing",
                        "query": query
                    })
        except Exception as e:
            print(f"Bing search error: {e}")
        return results

class YahooSearch:
    """Yahoo search engine (via HTML scraping)"""
    
    def __init__(self):
        self.name = "yahoo"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        results = []
        try:
            url = f"https://search.yahoo.com/search?p={query}&n={num_results}"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Yahoo result selectors
            for result in soup.find_all('div', class_='dd'):
                link = result.find('a')
                if link and link.get('href'):
                    title = link.get_text(strip=True)
                    results.append({
                        "url": link.get('href'),
                        "title": f"Yahoo: {title}" if title else "Yahoo Result",
                        "source": "yahoo",
                        "query": query
                    })
                    if len(results) >= num_results:
                        break
        except Exception as e:
            print(f"Yahoo search error: {e}")
        return results

class AskSearch:
    """Ask.com search engine"""
    
    def __init__(self):
        self.name = "ask"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        results = []
        try:
            url = f"https://www.ask.com/web?q={query}"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ask.com result selectors
            for result in soup.find_all('div', class_='PartialSearchResults-item'):
                link = result.find('a')
                if link and link.get('href'):
                    title = link.get_text(strip=True)
                    results.append({
                        "url": link.get('href'),
                        "title": f"Ask: {title}" if title else "Ask Result",
                        "source": "ask",
                        "query": query
                    })
                    if len(results) >= num_results:
                        break
        except Exception as e:
            print(f"Ask.com search error: {e}")
        return results

class AolSearch:
    """AOL search engine"""
    
    def __init__(self):
        self.name = "aol"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        results = []
        try:
            url = f"https://search.aol.com/aol/search?q={query}"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # AOL result selectors
            for result in soup.find_all('div', class_='algo'):
                link = result.find('a')
                if link and link.get('href'):
                    title = link.get_text(strip=True)
                    results.append({
                        "url": link.get('href'),
                        "title": f"AOL: {title}" if title else "AOL Result",
                        "source": "aol",
                        "query": query
                    })
                    if len(results) >= num_results:
                        break
        except Exception as e:
            print(f"AOL search error: {e}")
        return results

class MultiSearchEngine:
    """Main class to use all search engines"""
    
    def __init__(self):
        self.engines = {
            "google": GoogleSearch(),
            "duckduckgo": DuckDuckGoSearch(),
            "bing": BingSearch(),
            "yahoo": YahooSearch(),
            "ask": AskSearch(),
            "aol": AolSearch()
        }
    
    def search_all(self, query: str, engines: List[str] = None, num_results: int = 3) -> Dict:
        """Search all engines or specific ones"""
        if engines is None:
            engines = list(self.engines.keys())
        
        all_results = {}
        
        for engine_name in engines:
            if engine_name in self.engines:
                print(f"Searching {engine_name}...")
                try:
                    results = self.engines[engine_name].search(query, num_results)
                    all_results[engine_name] = {
                        "results_count": len(results),
                        "results": results
                    }
                    time.sleep(1)  # Be nice to servers
                except Exception as e:
                    all_results[engine_name] = {"error": str(e)}
        
        return all_results
    
    def get_available_engines(self) -> List[str]:
        """Get list of available search engines"""
        return list(self.engines.keys())

# Simple usage functions
def search_phone_all_engines(phone_number: str) -> Dict:
    """Search phone number across all engines"""
    searcher = MultiSearchEngine()
    query = f'"{phone_number}"'
    return searcher.search_all(query)

def search_phone_specific_engines(phone_number: str, engines: List[str]) -> Dict:
    """Search phone number using specific engines"""
    searcher = MultiSearchEngine()
    query = f'"{phone_number}"'
    return searcher.search_all(query, engines)

def quick_google_ddg_search(phone_number: str) -> List[Dict]:
    """Quick search using just Google and DuckDuckGo"""
    searcher = MultiSearchEngine()
    query = f'"{phone_number}"'
    results = searcher.search_all(query, ["google", "duckduckgo"])
    
    # Combine all results
    all_links = []
    for engine, data in results.items():
        if "results" in data:
            all_links.extend(data["results"])
    return all_links

# Test it
if __name__ == "__main__":
    phone = "+1234567890"
    
    print("=== All Search Engines ===")
    all_results = search_phone_all_engines(phone)
    
    for engine, data in all_results.items():
        print(f"\n{engine.upper()}: {data.get('results_count', 0)} results")
        if "results" in data:
            for result in data["results"][:2]:  # Show first 2
                print(f"  - {result['title']}")
                print(f"    URL: {result['url']}")
    
    print("\n=== Quick Google + DDG ===")
    quick_results = quick_google_ddg_search(phone)
    print(f"Found {len(quick_results)} total results")
    for result in quick_results[:3]:
        print(f"  {result['source']}: {result['url']}")