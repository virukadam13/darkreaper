import requests
from bs4 import BeautifulSoup
from googlesearch import search
from ddgs import DDGS
import time

class GoogleDorking:
    def __init__(self):
        pass
    
    def search_email(self, email, num_results=5):
        """Search for email using Google dorks"""
        try:
            query = f'"{email}"'
            results = []
            
            # Fixed: removed 'pause' parameter which is not supported in newer versions
            for url in search(query, num_results=num_results):
                results.append({'url': url})
            
            return {'results': results}
        except Exception as e:
            return {'error': str(e)}
    
    def dork_search(self, dork_query, num_results=5):
        """Execute custom Google dork query"""
        try:
            results = []
            # Fixed: removed 'pause' parameter
            for url in search(dork_query, num_results=num_results):
                results.append({'url': url})
            return {'results': results}
        except Exception as e:
            return {'error': str(e)}

class DuckDuckGo:
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query, max_results=5):
        """Search using DuckDuckGo API"""
        try:
            results = []
            for result in self.ddgs.text(query, max_results=max_results):
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'description': result.get('body', '')
                })
            return {'results': results}
        except Exception as e:
            return {'error': str(e)}

class PastebinSearch:
    def __init__(self):
        self.base_url = "https://psbdmp.ws/api/v3"
    
    def search_email(self, email):
        """Search Pastebin dumps for email"""
        try:
            response = requests.get(f"{self.base_url}/search/{email}")
            return response.json() if response.status_code == 200 else {'error': f"API error: {response.status_code}"}
        except Exception as e:
            return {'error': str(e)}

class CustomScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_url(self, url):
        """Scrape content from a URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Improved title extraction
            title = ''
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            
            # Extract meta description
            description = ''
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                description = meta_desc['content'].strip()
            
            # Extract all text content (first 500 chars)
            text_content = soup.get_text()[:500].strip()
            
            return {
                'url': url,
                'title': title,
                'description': description,
                'content_preview': text_content,
                'content_length': len(response.text),
                'status_code': response.status_code
            }
        except Exception as e:
            return {'error': str(e)}

if __name__ == "__main__":
    print("Testing Search Engines & OSINT Dorking Module...")
    test_email = "johndoe@gmail.com"
    test_url = "https://httpbin.org/html"
    
    # Test GoogleDorking
    print("\n1. Testing GoogleDorking...")
    google = GoogleDorking()
    result = google.search_email(test_email, num_results=3)
    print(f"   Result: {result}")
    
    # Test DuckDuckGo
    print("\n2. Testing DuckDuckGo...")
    ddg = DuckDuckGo()
    result = ddg.search(test_email, max_results=3)
    print(f"   Result: {result}")
    
    # Test PastebinSearch
    print("\n3. Testing PastebinSearch...")
    pastebin = PastebinSearch()
    result = pastebin.search_email(test_email)
    print(f"   Result count: {len(result) if isinstance(result, list) else 'Error'}")
    
    # Test CustomScraper
    print("\n4. Testing CustomScraper...")
    scraper = CustomScraper()
    result = scraper.scrape_url(test_url)
    print(f"   Result: {result}")
    
    print("\nSearch Engines module test completed!")