import asyncio
import aiohttp
import re
from typing import Dict, List, Optional

class BreachSearch:
    """1. Public breach/leak searches"""
    
    async def search_hibp(self, phone: str) -> List[str]:
        """Have I Been Pwned basic checks"""
        # HIBP doesn't directly support phone search
        # This would check if phone appears in breach databases
        return []
    
    async def search_local_dumps(self, phone: str, dump_path: str = None) -> List[str]:
        """Search local breach dumps"""
        emails = []
        if dump_path:
            # Use grep/parse on local dumps
            try:
                with open(dump_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if phone in line and '@' in line:
                            emails.extend(re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', line))
            except:
                pass
        return emails

class PasteSiteSearch:
    """2. Public paste sites search"""
    
    async def search_pastebin(self, phone: str) -> List[str]:
        """Search Pastebin via dorks"""
        emails = []
        try:
            async with aiohttp.ClientSession() as session:
                # Search via Google dork
                url = f"https://www.google.com/search?q=site:pastebin.com+{phone}"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        emails.extend(re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text))
        except:
            pass
        return emails
    
    async def search_ghostbin(self, phone: str) -> List[str]:
        """Search Ghostbin"""
        emails = []
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://ghostbin.com/search?q={phone}"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        emails.extend(re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text))
        except:
            pass
        return emails

class SearchEngineDorking:
    """3. Search engine dorking"""
    
    async def google_dork(self, phone: str) -> List[str]:
        """Google dorking for phone+email patterns"""
        emails = []
        dorks = [
            f'"{phone}" "@gmail.com"',
            f'"{phone}" "@yahoo.com"',
            f'"{phone}" "email"',
            f'"{phone}" "contact"',
        ]
        
        async with aiohttp.ClientSession() as session:
            for dork in dorks:
                try:
                    url = f"https://www.google.com/search?q={dork}"
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            text = await response.text()
                            emails.extend(re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text))
                except:
                    continue
        return list(set(emails))
    
    async def github_search(self, phone: str) -> List[str]:
        """Search GitHub for phone in code"""
        emails = []
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.github.com/search/code?q={phone}"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        for item in data.get('items', []):
                            # Extract from file content if possible
                            file_url = item['html_url'].replace(
                                'https://github.com/', 
                                'https://raw.githubusercontent.com/'
                            ).replace('/blob/', '/')
                            try:
                                async with session.get(file_url, timeout=5) as file_resp:
                                    if file_resp.status == 200:
                                        content = await file_resp.text()
                                        emails.extend(re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', content))
                            except:
                                continue
        except:
            pass
        return emails

class OSINTIndexSearch:
    """4. OSINT search engines"""
    
    async def intelligencex_search(self, phone: str) -> List[str]:
        """IntelligenceX free search"""
        emails = []
        # Note: IntelX requires API for full access
        # This is basic web search simulation
        return emails

class DirectorySearch:
    """5. Directory reverse lookup"""
    
    async def numlookup_search(self, phone: str) -> List[str]:
        """Numlookup search"""
        emails = []
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://numlookup.com/phone/{phone}"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        text = await response.text()
                        emails.extend(re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text))
        except:
            pass
        return emails

class SocialPivot:
    """6. Social media pivoting"""
    
    async def search_github_profiles(self, phone: str) -> List[str]:
        """Search GitHub profiles for phone"""
        emails = []
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.github.com/search/users?q={phone}"
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        for user in data.get('items', []):
                            # Get user profile for email
                            profile_url = user['url']
                            async with session.get(profile_url, timeout=5) as profile_resp:
                                if profile_resp.status == 200:
                                    profile_data = await profile_resp.json()
                                    if profile_data.get('email'):
                                        emails.append(profile_data['email'])
        except:
            pass
        return emails

class GitRepositorySearch:
    """7. Git repository search"""
    
    async def search_git_commits(self, phone: str) -> List[str]:
        """Search Git commits for phone"""
        emails = []
        # Similar to GitHub search but focused on commits
        return emails

class TestData:
    """8. Synthetic testing"""
    
    def create_test_data(self, phone: str) -> List[str]:
        """Create test data for development"""
        test_emails = [
            f"test{phone[-4:]}@gmail.com",
            f"user{phone[-6:]}@yahoo.com",
            f"contact{phone[-4:]}@test.com"
        ]
        return test_emails


import asyncio
import aiohttp
import re
from typing import Dict, List
from googlesearch import search as google_search
from ddgs import DDGS

class DDGSearch:
    """DuckDuckGo search engine class"""
    
    def __init__(self):
        self.ddg = DDGS()
    
    async def search_phone_emails(self, phone: str) -> List[str]:
        """Search DuckDuckGo for phone + email patterns"""
        emails = []
        
        search_queries = [
            f'"{phone}" "@gmail.com"',
            f'"{phone}" "@yahoo.com"',
            f'"{phone}" "@hotmail.com"',
            f'"{phone}" "email"',
            f'"{phone}" "contact"',
            f'"{phone}" "@"',
        ]
        
        for query in search_queries:
            try:
                results = self.ddg.text(query, max_results=10)
                for result in results:
                    # Extract emails from search result snippets
                    text = f"{result.get('title', '')} {result.get('body', '')}"
                    found_emails = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text)
                    emails.extend(found_emails)
            except Exception as e:
                print(f"DDG search error for {query}: {e}")
                continue
        
        return list(set(emails))
    
    async def search_site_specific(self, phone: str, site: str) -> List[str]:
        """Search specific sites for phone number"""
        emails = []
        
        query = f'site:{site} "{phone}"'
        try:
            results = self.ddg.text(query, max_results=20)
            for result in results:
                text = f"{result.get('title', '')} {result.get('body', '')}"
                found_emails = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text)
                emails.extend(found_emails)
        except Exception as e:
            print(f"DDG site search error: {e}")
        
        return list(set(emails))
    
    async def search_paste_sites(self, phone: str) -> List[str]:
        """Search paste sites via DDG"""
        paste_sites = [
            "pastebin.com",
            "ghostbin.com", 
            "paste.ee",
            "justpaste.it",
            "rentry.co"
        ]
        
        all_emails = []
        for site in paste_sites:
            emails = await self.search_site_specific(phone, site)
            all_emails.extend(emails)
        
        return list(set(all_emails))

class GoogleSearchEngine:
    """Google search engine class"""
    
    def __init__(self):
        pass
    
    async def search_phone_emails(self, phone: str) -> List[str]:
        """Search Google for phone + email patterns"""
        emails = []
        
        search_queries = [
            f'"{phone}" "@gmail.com"',
            f'"{phone}" "@yahoo.com"',
            f'"{phone}" "@hotmail.com"',
            f'"{phone}" "email"',
            f'"{phone}" "contact"',
            f'"{phone}" "@"',
            f'"{phone}" "mail"',
            f'"{phone}" "e-mail"',
        ]
        
        for query in search_queries:
            try:
                # Google search with 10 results per query
                results = google_search(query, num_results=10)
                for url in results:
                    # Extract from URL and try to get page content
                    found_emails = await self._extract_emails_from_url(url)
                    emails.extend(found_emails)
            except Exception as e:
                print(f"Google search error for {query}: {e}")
                continue
        
        return list(set(emails))
    
    async def search_site_specific(self, phone: str, site: str) -> List[str]:
        """Search specific sites using Google"""
        emails = []
        
        query = f'site:{site} "{phone}"'
        try:
            results = google_search(query, num_results=15)
            for url in results:
                found_emails = await self._extract_emails_from_url(url)
                emails.extend(found_emails)
        except Exception as e:
            print(f"Google site search error: {e}")
        
        return list(set(emails))
    
    async def _extract_emails_from_url(self, url: str) -> List[str]:
        """Extract emails from a webpage"""
        emails = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }) as response:
                    if response.status == 200:
                        html = await response.text()
                        found_emails = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', html)
                        emails.extend(found_emails)
        except:
            pass
        return emails
    
    async def search_github_dorks(self, phone: str) -> List[str]:
        """Search GitHub using Google dorks"""
        emails = []
        
        github_dorks = [
            f'site:github.com "{phone}"',
            f'site:gist.github.com "{phone}"',
            f'site:github.com "{phone}" "@"',
        ]
        
        for dork in github_dorks:
            try:
                results = google_search(dork, num_results=10)
                for url in results:
                    found_emails = await self._extract_emails_from_url(url)
                    emails.extend(found_emails)
            except Exception as e:
                print(f"GitHub dork error: {e}")
        
        return list(set(emails))
    
    async def search_social_media(self, phone: str) -> List[str]:
        """Search social media sites for phone"""
        social_sites = [
            "site:linkedin.com",
            "site:twitter.com", 
            "site:facebook.com",
            "site:instagram.com",
        ]
        
        all_emails = []
        for site in social_sites:
            query = f'{site} "{phone}"'
            try:
                results = google_search(query, num_results=5)
                for url in results:
                    found_emails = await self._extract_emails_from_url(url)
                    all_emails.extend(found_emails)
            except:
                continue
        
        return list(set(all_emails))

# UPDATE MAIN MODULE WITH NEW CLASSES
class EmailDiscovery:
    """Main OSINT email discovery module"""
    
    def __init__(self):
        self.breach = BreachSearch()
        self.paste = PasteSiteSearch()
        self.dorking = SearchEngineDorking()
        self.osint = OSINTIndexSearch()
        self.directory = DirectorySearch()
        self.social = SocialPivot()
        self.git = GitRepositorySearch()
        self.test = TestData()
        self.ddg = DDGSearch()
        self.google = GoogleSearchEngine()
    
    async def find_emails(self, phone: str, use_test_data: bool = False) -> Dict:
        """Main method to find emails from phone number"""
        
        if use_test_data:
            return {
                "phone": phone,
                "emails": self.test.create_test_data(phone),
                "sources": ["test_data"],
                "total": 3
            }
        
        all_emails = []
        sources_used = []
        
        # Run all search methods including new ones
        searches = [
            ("pastebin", self.paste.search_pastebin(phone)),
            ("ghostbin", self.paste.search_ghostbin(phone)),
            ("google_dork", self.dorking.google_dork(phone)),
            ("github", self.dorking.github_search(phone)),
            ("numlookup", self.directory.numlookup_search(phone)),
            ("github_profiles", self.social.search_github_profiles(phone)),
            ("ddg_search", self.ddg.search_phone_emails(phone)),
            ("ddg_paste", self.ddg.search_paste_sites(phone)),
            ("google_search", self.google.search_phone_emails(phone)),
            ("google_github", self.google.search_github_dorks(phone)),
            ("google_social", self.google.search_social_media(phone)),
        ]
        
        for source_name, search_task in searches:
            try:
                emails = await search_task
                if emails:
                    all_emails.extend(emails)
                    sources_used.append(source_name)
                    print(f"✅ {source_name}: found {len(emails)} emails")
            except Exception as e:
                print(f"❌ {source_name} failed: {e}")
                continue
        
        # Remove duplicates
        unique_emails = list(set(all_emails))
        
        return {
            "phone": phone,
            "emails": unique_emails,
            "sources": sources_used,
            "total": len(unique_emails)
        }

# INSTALLATION REQUIRED:
# pip install duckduckgo-search googlesearch-python aiohttp

# USAGE EXAMPLE
async def main():
    discover = EmailDiscovery()
    
    # Test with synthetic data first
    test_result = await discover.find_emails("505-341-3228", use_test_data=True)
    print("Test result:", test_result)
    
    print("\n" + "="*50)
    
    # Real search with DDG and Google
    real_result = await discover.find_emails("505-341-3228", use_test_data=False)
    print("Real search result:")
    print(f"Phone: {real_result['phone']}")
    print(f"Total emails found: {real_result['total']}")
    print(f"Sources used: {real_result['sources']}")
    
    if real_result['emails']:
        print("Emails found:")
        for email in real_result['emails']:
            print(f"  - {email}")

if __name__ == "__main__":
    asyncio.run(main())

