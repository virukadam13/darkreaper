import requests
import os
from dotenv import load_dotenv
import dns.resolver

load_dotenv()

class ThreatIntelligence:
    def __init__(self):
        self.vt_key = os.getenv('VIRUSTOTAL_API_KEY')
        self.otx_key = os.getenv('OTX_API_KEY')
        self.greynoise_key = os.getenv('GREYNOISE_API_KEY')
        self.session = self._create_session()
    
    def _create_session(self):
        """Create requests session with proper configuration"""
        session = requests.Session()
        
        # Remove proxy configuration if causing issues
        session.trust_env = False  # This ignores system proxy settings
        
        # Set reasonable timeouts
        session.timeout = 15
        return session
    
    def get_comprehensive_threats(self, ip: str) -> dict:
        """Check IP against all threat intelligence sources"""
        results = {}
        
        # Source 1: VirusTotal
        results['virustotal'] = self.check_virustotal(ip)
        
        # Source 2: AlienVault OTX
        results['alienvault_otx'] = self.check_otx(ip)
        
        # Source 3: GreyNoise
        results['greynoise'] = self.check_greynoise(ip)
        
        # Source 4: Blocklists
        results['blocklists'] = self.check_blocklists(ip)
        
        # Source 5: AbuseIPDB
        results['abuseipdb'] = self.check_abuseipdb(ip)
        
        return results
    
    def check_virustotal(self, ip: str) -> dict:
        if not self.vt_key:
            return {'error': 'API key required', 'url': f'https://www.virustotal.com/gui/ip-address/{ip}'}
        
        try:
            url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
            headers = {"x-apikey": self.vt_key}
            response = self.session.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                return {
                    'malicious': stats.get('malicious', 0),
                    'suspicious': stats.get('suspicious', 0),
                    'undetected': stats.get('undetected', 0),
                    'harmless': stats.get('harmless', 0)
                }
            return {'error': f'API status {response.status_code}'}
        except Exception as e:
            return {'error': str(e)}
    
    def check_otx(self, ip: str) -> dict:
        if not self.otx_key:
            return {'error': 'API key required', 'url': f'https://otx.alienvault.com/indicator/ip/{ip}'}
        
        try:
            url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
            headers = {"X-OTX-API-KEY": self.otx_key}
            response = self.session.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return {
                    'pulse_count': data.get('pulse_info', {}).get('count', 0),
                    'reputation': data.get('reputation', 0)
                }
            return {'error': f'API status {response.status_code}'}
        except Exception as e:
            return {'error': str(e)}
    
    def check_greynoise(self, ip: str) -> dict:
        try:
            url = f"https://api.greynoise.io/v3/community/{ip}"
            headers = {"key": self.greynoise_key or 'free'}
            response = self.session.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                return response.json()
            return {'error': f'API status {response.status_code}'}
        except Exception as e:
            return {'error': str(e)}
    
    def check_blocklists(self, ip: str) -> dict:
        blocklists = {
            "spamhaus": f"https://www.spamhaus.org/query/ip/{ip}",
            "blocklist_de": f"https://www.blocklist.de/en/check.html?ip={ip}",
            "project_honeypot": f"https://www.projecthoneypot.org/ip_{ip}"
        }
        return blocklists
    
    def check_abuseipdb(self, ip: str) -> dict:
        return {
            'check_url': f"https://www.abuseipdb.com/check/{ip}",
            'api_docs': 'https://docs.abuseipdb.com/'
        }

# Usage
if __name__ == "__main__":
    ti = ThreatIntelligence()
    result = ti.get_comprehensive_threats("8.8.8.8")
    print(result)