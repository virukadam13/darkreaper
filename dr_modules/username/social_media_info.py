# platform_specific_intel.py
import os
import json
import re
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import instaloader  # For Instagram
import tweepy      # For Twitter
#import linkedin_api
#from linkedin_api import LinkedIn
#import python_linkedin  # For LinkedIn
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import asyncio

@dataclass
class PlatformStrategy:
    name: str
    api_module: Any = None
    library_module: Any = None
    scraping_config: Dict = None
    requires_js: bool = False

class PlatformSpecificIntelligence:
    """
    Platform-specific intelligence with fallback strategy:
    API → Library → Playwright Scraping
    """
    
    def __init__(self):
        self.platform_strategies = self._initialize_strategies()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def _initialize_strategies(self) -> Dict[str, PlatformStrategy]:
        """Initialize platform-specific strategies"""
        strategies = {}
        
        # ===== INSTAGRAM =====
        strategies['instagram.com'] = PlatformStrategy(
            name='Instagram',
            api_module=None,  # Instagram API requires approval
            library_module=instaloader.Instaloader() if self._check_instaloader() else None,
            scraping_config={
                'url': 'https://www.instagram.com/{username}/',
                'selectors': {
                    'name': 'header section h1',
                    'bio': 'header section div.-vDIg',
                    'followers': 'header section ul li:nth-child(2) span',
                    'following': 'header section ul li:nth-child(3) span',
                    'posts': 'header section ul li:nth-child(1) span',
                    'profile_pic': 'header img[data-testid="user-avatar"]'
                }
            },
            requires_js=True
        )
        
        # ===== TWITTER =====
        strategies['twitter.com'] = PlatformStrategy(
            name='Twitter',
            api_module=self._init_twitter_api(),
            library_module=None,
            scraping_config={
                'url': 'https://twitter.com/{username}',
                'selectors': {
                    'name': 'div[data-testid="UserProfileHeader_Items"] > span',
                    'bio': 'div[data-testid="UserDescription"]',
                    'followers': 'a[href$="/followers"] span',
                    'following': 'a[href$="/following"] span',
                    'join_date': 'span[data-testid="UserJoinDate"]',
                    'location': 'div[data-testid="UserProfileHeader_Items"] > span:nth-child(2)'
                }
            },
            requires_js=False
        )
        
        # ===== FACEBOOK =====
        strategies['facebook.com'] = PlatformStrategy(
            name='Facebook',
            api_module=None,  # Facebook API requires approval
            library_module=None,
            scraping_config={
                'url': 'https://www.facebook.com/{username}',
                'selectors': {
                    'name': 'h1',
                    'about': 'div[data-testid="profile_about_section"]',
                    'friends': 'a[href$="/friends"] span',
                    'profile_pic': 'image[aria-label="{username}"]'
                }
            },
            requires_js=True
        )
        
        # ===== LINKEDIN =====
        strategies['linkedin.com'] = PlatformStrategy(
            name='LinkedIn',
            api_module=None,  # LinkedIn API requires approval
            library_module=python_linkedin.LinkedIn() if self._check_linkedin_lib() else None,
            scraping_config={
                'url': 'https://www.linkedin.com/in/{username}',
                'selectors': {
                    'name': 'h1',
                    'headline': 'div.text-heading-xlarge',
                    'about': 'section[data-test-id="about"]',
                    'experience': 'section[data-test-id="experience"]'
                }
            },
            requires_js=True
        )
        
        # ===== GITHUB =====
        strategies['github.com'] = PlatformStrategy(
            name='GitHub',
            api_module=None,  # GitHub API doesn't require token for public data
            library_module=None,
            scraping_config={
                'url': 'https://github.com/{username}',
                'selectors': {
                    'name': 'span[itemprop="name"]',
                    'bio': 'div[itemprop="description"]',
                    'repos': 'a[href$="?tab=repositories"] span',
                    'stars': 'a[href$="?tab=stars"] span',
                    'contributions': 'h2.f4.text-normal'
                }
            },
            requires_js=False
        )
        
        # Add more platforms as needed...
        
        return strategies
    
    def _check_instaloader(self) -> bool:
        """Check if instaloader is available"""
        try:
            import instaloader
            return True
        except ImportError:
            return False
    
    def _init_twitter_api(self):
        """Initialize Twitter API if token available"""
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        if bearer_token:
            try:
                import tweepy
                client = tweepy.Client(bearer_token=bearer_token)
                return client
            except ImportError:
                return None
        return None
    
    def _check_linkedin_lib(self) -> bool:
        """Check if python-linkedin is available"""
        try:
            import python_linkedin
            return True
        except ImportError:
            return False

    def gather_info(self, username: str, platform: str) -> Dict:
        """
        Gather intelligence using platform-specific strategy
        API → Library → Scraping fallback
        """
        platform = self._normalize_platform(platform)
        
        if platform not in self.platform_strategies:
            return {'error': f'Unsupported platform: {platform}'}
        
        strategy = self.platform_strategies[platform]
        results = {
            'username': username,
            'platform': platform,
            'timestamp': datetime.now().isoformat(),
            'strategy_used': [],
            'data': {},
            'success': False
        }
        
        try:
            # Strategy 1: Try API
            api_data = self._try_api_method(username, platform, strategy)
            if api_data and 'error' not in api_data:
                results['data'].update(api_data)
                results['strategy_used'].append('api')
                results['success'] = True
                return results
            
            # Strategy 2: Try Library
            library_data = self._try_library_method(username, platform, strategy)
            if library_data and 'error' not in library_data:
                results['data'].update(library_data)
                results['strategy_used'].append('library')
                results['success'] = True
                return results
            
            # Strategy 3: Try Scraping
            scraping_data = self._try_scraping_method(username, platform, strategy)
            if scraping_data and 'error' not in scraping_data:
                results['data'].update(scraping_data)
                results['strategy_used'].append('scraping')
                results['success'] = True
                return results
            
            # All methods failed
            results['error'] = 'All data gathering methods failed'
            results['details'] = {
                'api_error': api_data.get('error') if api_data else 'Not attempted',
                'library_error': library_data.get('error') if library_data else 'Not attempted',
                'scraping_error': scraping_data.get('error') if scraping_data else 'Not attempted'
            }
            
        except Exception as e:
            results['error'] = f'Platform intelligence failed: {str(e)}'
        
        return results

    def _try_api_method(self, username: str, platform: str, strategy: PlatformStrategy) -> Dict:
        """Try to get data via official API"""
        if not strategy.api_module:
            return {'error': 'API not configured'}
        
        try:
            if platform == 'twitter.com':
                return self._get_twitter_via_api(username, strategy.api_module)
            # Add other API methods here
            
            return {'error': 'API method not implemented for this platform'}
        except Exception as e:
            return {'error': f'API method failed: {str(e)}'}

    def _try_library_method(self, username: str, platform: str, strategy: PlatformStrategy) -> Dict:
        """Try to get data via Python library"""
        if not strategy.library_module:
            return {'error': 'Library not available'}
        
        try:
            if platform == 'instagram.com':
                return self._get_instagram_via_library(username, strategy.library_module)
            elif platform == 'linkedin.com':
                return self._get_linkedin_via_library(username, strategy.library_module)
            # Add other library methods here
            
            return {'error': 'Library method not implemented for this platform'}
        except Exception as e:
            return {'error': f'Library method failed: {str(e)}'}

    def _try_scraping_method(self, username: str, platform: str, strategy: PlatformStrategy) -> Dict:
        """Try to get data via web scraping"""
        if not strategy.scraping_config:
            return {'error': 'Scraping not configured'}
        
        try:
            url = strategy.scraping_config['url'].format(username=username)
            selectors = strategy.scraping_config['selectors']
            
            if strategy.requires_js:
                return self._scrape_with_playwright(url, selectors)
            else:
                return self._scrape_with_requests(url, selectors)
        except Exception as e:
            return {'error': f'Scraping failed: {str(e)}'}

    # ===== PLATFORM-SPECIFIC METHODS =====

    def _get_twitter_via_api(self, username: str, api_client) -> Dict:
        """Get Twitter data via API"""
        try:
            user = api_client.get_user(username=username, user_fields=[
                'description', 'public_metrics', 'verified', 'created_at', 'location'
            ])
            
            if user.data:
                return {
                    'name': user.data.name,
                    'bio': user.data.description,
                    'followers': user.data.public_metrics['followers_count'],
                    'following': user.data.public_metrics['following_count'],
                    'verified': user.data.verified,
                    'created_at': user.data.created_at,
                    'location': user.data.location
                }
            return {'error': 'User not found via API'}
        except Exception as e:
            return {'error': f'Twitter API error: {str(e)}'}

    def _get_instagram_via_library(self, username: str, loader) -> Dict:
        """Get Instagram data via Instaloader"""
        try:
            profile = instaloader.Profile.from_username(loader.context, username)
            return {
                'name': profile.full_name,
                'bio': profile.biography,
                'followers': profile.followers,
                'following': profile.followees,
                'posts': profile.mediacount,
                'is_private': profile.is_private,
                'is_verified': profile.is_verified,
                'profile_pic': profile.profile_pic_url
            }
        except instaloader.ProfileNotExistsException:
            return {'error': 'Instagram profile not found'}
        except Exception as e:
            return {'error': f'Instaloader error: {str(e)}'}

    def _get_linkedin_via_library(self, username: str, linkedin_client) -> Dict:
        """Get LinkedIn data via library"""
        try:
            # This would require proper LinkedIn API setup
            profile = linkedin_client.get_profile(member_id=username)
            return {
                'name': profile.get('firstName', '') + ' ' + profile.get('lastName', ''),
                'headline': profile.get('headline', ''),
                'industry': profile.get('industry', ''),
                'location': profile.get('location', {}).get('name', '')
            }
        except Exception as e:
            return {'error': f'LinkedIn library error: {str(e)}'}

    def _scrape_with_playwright(self, url: str, selectors: Dict) -> Dict:
        """Scrape JavaScript-rendered pages"""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                page.goto(url, timeout=15000)
                
                # Wait for selectors to load
                for selector in selectors.values():
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                    except:
                        continue
                
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                browser.close()
                
                return self._extract_with_selectors(soup, selectors)
        except Exception as e:
            return {'error': str(e)}

    def _scrape_with_requests(self, url: str, selectors: Dict) -> Dict:
        """Scrape simple HTML pages"""
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                return {'error': f'HTTP {response.status_code}'}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_with_selectors(soup, selectors)
        except Exception as e:
            return {'error': str(e)}

    def _extract_with_selectors(self, soup: BeautifulSoup, selectors: Dict) -> Dict:
        """Extract data using CSS selectors"""
        data = {}
        for key, selector in selectors.items():
            try:
                element = soup.select_one(selector)
                if element:
                    if key == 'profile_pic' and element.get('src'):
                        data[key] = element.get('src', '').strip()
                    else:
                        data[key] = element.get_text().strip()
            except:
                continue
        return data

    def _normalize_platform(self, platform: str) -> str:
        """Normalize platform name"""
        platform = platform.lower().replace('www.', '').replace('https://', '').replace('http://', '')
        
        # Map aliases to full domain names
        aliases = {
            'instagram': 'instagram.com',
            'twitter': 'twitter.com',
            'facebook': 'facebook.com',
            'linkedin': 'linkedin.com',
            'github': 'github.com'
        }
        
        return aliases.get(platform, platform)

    def batch_gather_info(self, username: str, platforms: List[str]) -> Dict:
        """Gather info across multiple platforms"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_platform = {
                executor.submit(self.gather_info, username, platform): platform
                for platform in platforms
            }
            
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                results[platform] = future.result()
        
        return results

# Installation requirements helper
def get_installation_commands() -> Dict[str, str]:
    """Get installation commands for required libraries"""
    return {
        'instaloader': 'pip install instaloader',
        'tweepy': 'pip install tweepy',
        'playwright': 'playwright install chromium',
        'python-linkedin': 'pip install python-linkedin'
    }

# Example usage
if __name__ == "__main__":
    intel = PlatformSpecificIntelligence()
    
    # Test Instagram with different methods
    result = intel.gather_info("viru_kadam_13", "instagram")
    print(json.dumps(result, indent=2))
    
    # Check what installation is needed
    print("\nInstallation commands:")
    for lib, cmd in get_installation_commands().items():
        print(f"{lib}: {cmd}")