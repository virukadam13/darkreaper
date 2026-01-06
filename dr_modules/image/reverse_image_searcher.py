# reverse_image_searcher.py
import requests
import base64
import json
import time
import os
import webbrowser
from urllib.parse import urljoin, urlencode
from bs4 import BeautifulSoup

class ReverseImageSearcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.timeout = 30
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def check_image_file(self, image_path):
        """Verify the image file exists and is valid"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        file_size = os.path.getsize(image_path)
        if file_size == 0:
            raise ValueError(f"Image file is empty: {image_path}")
        
        # Check if file is too large (over 10MB)
        if file_size > 10 * 1024 * 1024:
            raise ValueError(f"Image file too large: {file_size} bytes (max 10MB)")
        
        return True

    def google_images_search(self, image_path):
        """Google Images reverse search with better handling"""
        try:
            self.check_image_file(image_path)
            
            # Step 1: Upload image and get the search URL
            upload_url = "https://www.google.com/searchbyimage/upload"
            
            with open(image_path, 'rb') as f:
                files = {'encoded_image': (os.path.basename(image_path), f, 'image/jpeg')}
                response = self.session.post(
                    upload_url,
                    files=files,
                    timeout=self.timeout,
                    allow_redirects=False
                )
            
            if response.status_code in [200, 302, 303]:
                result_url = response.url
                if 'Location' in response.headers:
                    result_url = response.headers['Location']
                    if not result_url.startswith('http'):
                        result_url = urljoin('https://www.google.com', result_url)
                
                # Make a request to the result URL to get the final search URL
                if result_url != response.url:
                    final_response = self.session.get(result_url, timeout=self.timeout)
                    result_url = final_response.url
                
                return {
                    'url': result_url,
                    'status': 'success',
                    'message': 'Google reverse image search completed'
                }
            else:
                return {
                    'url': '',
                    'status': 'error',
                    'message': f'Google upload failed with status: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'url': '',
                'status': 'error',
                'message': f'Google error: {str(e)}'
            }
    
    def yandex_search(self, image_path):
        """Yandex Images reverse search with improved handling"""
        try:
            self.check_image_file(image_path)
            
            search_url = "https://yandex.com/images/search"
            
            with open(image_path, 'rb') as f:
                files = {'upfile': ('image.jpg', f, 'image/jpeg')}
                response = self.session.post(
                    search_url, 
                    files=files, 
                    timeout=self.timeout,
                    allow_redirects=True
                )
            
            if response.status_code == 200:
                return {
                    'url': response.url,
                    'status': 'success',
                    'message': 'Yandex reverse image search completed'
                }
            else:
                return {
                    'url': '',
                    'status': 'error', 
                    'message': f'Yandex search failed with status: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'url': '',
                'status': 'error',
                'message': f'Yandex error: {str(e)}'
            }
    
    def bing_visual_search(self, image_path):
        """Bing Visual Search with improved implementation"""
        try:
            self.check_image_file(image_path)
            
            # First, get the upload page
            search_url = "https://www.bing.com/images/search"
            
            with open(image_path, 'rb') as f:
                # Read image and encode as base64 for the form data approach
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Use the visual search form
            params = {
                'view': 'detailv2',
                'iss': 'sbiupload',
                'FORM': 'IRSBIQ'
            }
            
            # Create the form data
            form_data = {
                'imageBin': base64_image,
                'imageUrl': '',
                'sbifnm': os.path.basename(image_path)
            }
            
            response = self.session.post(
                search_url,
                data=form_data,
                params=params,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                return {
                    'url': response.url,
                    'status': 'success',
                    'message': 'Bing visual search completed'
                }
            else:
                return {
                    'url': '',
                    'status': 'error',
                    'message': f'Bing search failed with status: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'url': '',
                'status': 'error',
                'message': f'Bing error: {str(e)}'
            }
    
    def tineye_search_alternative(self, image_path):
        """Alternative TinEye approach with different headers"""
        try:
            self.check_image_file(image_path)
            
            # Try different TinEye endpoints
            endpoints = [
                "https://tineye.com/search",
                "https://www.tineye.com/search"
            ]
            
            for endpoint in endpoints:
                try:
                    with open(image_path, 'rb') as f:
                        files = {'image': f}
                        
                        # Use different headers for TinEye
                        tineye_headers = self.headers.copy()
                        tineye_headers['Referer'] = 'https://tineye.com/'
                        tineye_headers['Origin'] = 'https://tineye.com'
                        
                        response = self.session.post(
                            endpoint,
                            files=files,
                            headers=tineye_headers,
                            timeout=self.timeout,
                            allow_redirects=True
                        )
                    
                    if response.status_code == 200:
                        return {
                            'url': response.url,
                            'status': 'success',
                            'message': 'TinEye search completed'
                        }
                    elif response.status_code == 403:
                        continue  # Try next endpoint
                        
                except Exception:
                    continue
            
            return {
                'url': '',
                'status': 'error',
                'message': 'TinEye blocked automated requests (403 Forbidden). Use manual upload at https://tineye.com'
            }
                
        except Exception as e:
            return {
                'url': '',
                'status': 'error',
                'message': f'TinEye error: {str(e)}'
            }
    
    def baidu_image_search(self, image_path):
        """Baidu Images reverse search (Chinese search engine)"""
        try:
            self.check_image_file(image_path)
            
            search_url = "https://image.baidu.com/n/pc_search"
            
            with open(image_path, 'rb') as f:
                files = {'image': (os.path.basename(image_path), f, 'image/jpeg')}
                response = self.session.post(
                    search_url,
                    files=files,
                    timeout=self.timeout,
                    allow_redirects=True
                )
            
            if response.status_code == 200:
                return {
                    'url': response.url,
                    'status': 'success',
                    'message': 'Baidu image search completed'
                }
            else:
                return {
                    'url': '',
                    'status': 'error',
                    'message': f'Baidu search failed with status: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'url': '',
                'status': 'error',
                'message': f'Baidu error: {str(e)}'
            }
    
    def search_all_engines(self, image_path):
        """Search all available reverse image engines"""
        print(f"Starting reverse image search for: {image_path}")
        print("=" * 60)
        
        results = {}
        
        # Google Images
        print("🔍 Searching Google Images...")
        google_result = self.google_images_search(image_path)
        results['google'] = google_result
        print(f"   → {google_result['message']}")
        if google_result['url']:
            print(f"   🔗 {google_result['url']}")
        time.sleep(2)
        
        # Yandex
        print("🔍 Searching Yandex Images...")
        yandex_result = self.yandex_search(image_path)
        results['yandex'] = yandex_result
        print(f"   → {yandex_result['message']}")
        if yandex_result['url']:
            print(f"   🔗 {yandex_result['url']}")
        time.sleep(2)
        
        # Bing
        print("🔍 Searching Bing Visual Search...")
        bing_result = self.bing_visual_search(image_path)
        results['bing'] = bing_result
        print(f"   → {bing_result['message']}")
        if bing_result['url']:
            print(f"   🔗 {bing_result['url']}")
        time.sleep(2)
        
        # TinEye (alternative approach)
        print("🔍 Searching TinEye...")
        tineye_result = self.tineye_search_alternative(image_path)
        results['tineye'] = tineye_result
        print(f"   → {tineye_result['message']}")
        if tineye_result['url']:
            print(f"   🔗 {tineye_result['url']}")
        time.sleep(2)
        
        # Baidu (optional)
        print("🔍 Searching Baidu Images...")
        baidu_result = self.baidu_image_search(image_path)
        results['baidu'] = baidu_result
        print(f"   → {baidu_result['message']}")
        if baidu_result['url']:
            print(f"   🔗 {baidu_result['url']}")
        
        return results
    
    def open_results_in_browser(self, results):
        """Open successful search results in web browser"""
        successful_searches = []
        
        for engine, result in results.items():
            if result['status'] == 'success' and result['url']:
                successful_searches.append((engine, result['url']))
        
        if successful_searches:
            print(f"\n🌐 Opening {len(successful_searches)} results in browser...")
            for engine, url in successful_searches:
                print(f"   Opening {engine}: {url}")
                webbrowser.open_new_tab(url)
                time.sleep(1)  # Small delay between opening tabs
            return True
        else:
            print("\n❌ No successful search results to open in browser.")
            return False
    
    def save_results(self, results, output_file="search_results.txt"):
        """Save search results to a file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("REVERSE IMAGE SEARCH RESULTS\n")
            f.write("=" * 50 + "\n\n")
            
            for engine, result in results.items():
                f.write(f"{engine.upper()}:\n")
                f.write(f"  Status: {result['status']}\n")
                f.write(f"  Message: {result['message']}\n")
                if result['url']:
                    f.write(f"  URL: {result['url']}\n")
                f.write("\n")
        
        print(f"✅ Results saved to: {output_file}")
        return output_file

# Usage with enhanced features
if __name__ == "__main__":
    searcher = ReverseImageSearcher()
    
    # Test image path
    image_path = "test.jpg"
    
    # Check if test image exists
    if not os.path.exists(image_path):
        print(f"❌ Test image '{image_path}' not found!")
        print("Please create a test image file or specify a different path.")
        exit(1)
    
    try:
        print(f"🖼️  Searching with image: {image_path}")
        print(f"📊 File size: {os.path.getsize(image_path)} bytes")
        print(f"📁 File path: {os.path.abspath(image_path)}")
        
        # Perform searches
        results = searcher.search_all_engines(image_path)
        
        # Display summary
        print("\n" + "=" * 60)
        print("🎯 REVERSE IMAGE SEARCH SUMMARY")
        print("=" * 60)
        
        successful = 0
        for engine, result in results.items():
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"\n{status_icon} {engine.upper()}:")
            print(f"   {result['message']}")
            if result['url']:
                print(f"   🔗 {result['url']}")
            
            if result['status'] == 'success':
                successful += 1
        
        print(f"\n📈 Success rate: {successful}/{len(results)} engines")
        
        # Save results
        output_file = searcher.save_results(results)
        
        # Ask user if they want to open results in browser
        if successful > 0:
            try:
                choice = input("\n🌐 Do you want to open the results in your browser? (y/n): ").lower().strip()
                if choice in ['y', 'yes']:
                    searcher.open_results_in_browser(results)
            except KeyboardInterrupt:
                print("\n⏹️  Browser opening cancelled.")
        
        print("\n💡 TIPS:")
        print("   • Copy and paste URLs manually if browser doesn't open automatically")
        print("   • TinEye often blocks automated requests - use their website directly")
        print("   • Results quality depends on image uniqueness and online presence")
        print("   • Try different images for better results")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()