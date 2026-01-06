import ipaddress
import requests
import dns.resolver
from ipwhois import IPWhois
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CDNCloudDetector:
    def __init__(self):
        # Cloud IP ranges (simplified)
        self.cloud_ranges = {
            'aws': ['13.32.0.0/15', '15.230.0.0/15', '52.0.0.0/8'],
            'azure': ['13.64.0.0/11', '20.0.0.0/8', '40.0.0.0/8'],
            'google_cloud': ['8.8.8.8/32', '34.0.0.0/8', '35.0.0.0/8'],
            'cloudflare': ['103.21.244.0/22', '104.16.0.0/13', '172.64.0.0/13'],
            'akamai': ['23.0.0.0/12', '95.100.0.0/15']
        }
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification for testing
    
    def detect_comprehensive_cloud(self, ip: str, domain: str = None) -> dict:
        """Comprehensive CDN and cloud detection"""
        results = {}
        
        # Method 1: IP range matching
        results['ip_range_check'] = self.check_ip_ranges(ip)
        
        # Method 2: DNS-based detection
        if domain:
            results['dns_detection'] = self.dns_based_detection(domain)
        
        # Method 3: HTTP header analysis
        if domain:
            results['http_analysis'] = self.analyze_http_headers(domain)
        
        # Method 4: ASN analysis
        results['asn_analysis'] = self.asn_based_detection(ip)
        
        return results
    
    def check_ip_ranges(self, ip: str) -> dict:
        detected = []
        try:
            ip_obj = ipaddress.ip_address(ip)
            for provider, ranges in self.cloud_ranges.items():
                for range_str in ranges:
                    if ip_obj in ipaddress.ip_network(range_str, strict=False):
                        detected.append(provider)
                        break
        except Exception as e:
            return {'error': str(e)}
        
        return {'detected_providers': detected, 'is_cloud': len(detected) > 0}
    
    def dns_based_detection(self, domain: str) -> dict:
        try:
            # Check for common CDN CNAMEs
            cname_checks = {
                'cloudflare': ['cloudflare'],
                'aws': ['cloudfront', 'amazonaws'],
                'akamai': ['akamaiedge', 'akamai'],
                'fastly': ['fastly']
            }
            results = {}
            
            try:
                answers = dns.resolver.resolve(domain, 'CNAME')
                for rdata in answers:
                    target = str(rdata.target).lower()
                    for provider, indicators in cname_checks.items():
                        for indicator in indicators:
                            if indicator in target:
                                results[provider] = True
            except:
                pass
            
            return results
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_http_headers(self, domain: str) -> dict:
        try:
            response = self.session.get(f"https://{domain}", timeout=10)
            headers = dict(response.headers)
            
            cdn_indicators = {}
            server = headers.get('Server', '').lower()
            via = headers.get('Via', '').lower()
            x_powered_by = headers.get('X-Powered-By', '').lower()
            
            # Check multiple header fields
            all_headers = server + ' ' + via + ' ' + x_powered_by
            
            if 'cloudflare' in all_headers:
                cdn_indicators['cloudflare'] = True
            if 'akamai' in all_headers:
                cdn_indicators['akamai'] = True
            if 'aws' in all_headers or 'cloudfront' in all_headers:
                cdn_indicators['aws'] = True
            if 'google' in all_headers:
                cdn_indicators['google'] = True
            
            return cdn_indicators
        except Exception as e:
            return {'error': str(e)}
    
    def asn_based_detection(self, ip: str) -> dict:
        try:
            obj = IPWhois(ip)
            whois_data = obj.lookup_rdap()
            asn_desc = whois_data.get('asn_description', '').lower()
            asn = whois_data.get('asn', '')
            
            cloud_indicators = {}
            if 'google' in asn_desc or asn == '15169':
                cloud_indicators['google'] = True
            if 'amazon' in asn_desc or asn in ['16509', '14618']:
                cloud_indicators['aws'] = True
            if 'microsoft' in asn_desc or asn in ['8075', '8068']:
                cloud_indicators['azure'] = True
            if 'cloudflare' in asn_desc or asn == '13335':
                cloud_indicators['cloudflare'] = True
            
            return cloud_indicators
        except Exception as e:
            return {'error': str(e)}

# Usage
if __name__ == "__main__":
    cdn = CDNCloudDetector()
    result = cdn.detect_comprehensive_cloud("8.8.8.8", "google.com")
    print(result)