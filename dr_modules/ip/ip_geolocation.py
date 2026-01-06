import requests
import socket
from ipwhois import IPWhois
import dns.resolver

class IPGeolocation:
    def __init__(self):
        self.sources = {
            'ipapi': 'http://ipapi.co/{ip}/json/',
            'ipapi_com': 'http://ip-api.com/json/{ip}',
            'ipgeolocation': 'https://api.ipgeolocation.io/ipgeo?ip={ip}'
        }
    
    def get_comprehensive_geo(self, ip: str) -> dict:
        """Get geolocation from multiple sources"""
        results = {}
        
        # Source 1: ipapi.co
        try:
            url = self.sources['ipapi'].format(ip=ip)
            response = requests.get(url, timeout=10)
            data = response.json()
            results['ipapi_co'] = {
                'country': data.get('country_name'),
                'city': data.get('city'),
                'isp': data.get('org'),
                'asn': data.get('asn'),
                'coordinates': f"{data.get('latitude')}, {data.get('longitude')}"
            }
        except: pass
        
        # Source 2: ip-api.com
        try:
            url = self.sources['ipapi_com'].format(ip=ip)
            response = requests.get(url, timeout=10)
            data = response.json()
            results['ip_api_com'] = {
                'country': data.get('country'),
                'city': data.get('city'),
                'isp': data.get('isp'),
                'asn': data.get('as'),
                'org': data.get('org')
            }
        except: pass
        
        # Source 3: ipwhois for network info
        try:
            obj = IPWhois(ip)
            whois_data = obj.lookup_rdap()
            results['whois_network'] = {
                'asn': whois_data.get('asn'),
                'network': whois_data.get('network', {}).get('cidr'),
                'org': whois_data.get('asn_description')
            }
        except: pass
        
        return results

# Usage
if __name__ == "__main__":
    geo = IPGeolocation()
    result = geo.get_comprehensive_geo("8.8.8.8")
    print(result)