import dns.resolver
import dns.reversename
import requests
from typing import List, Dict

class DNSIntelligence:
    def __init__(self):
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 5
        
    def get_comprehensive_dns(self, ip: str, domain: str = None) -> dict:
        """Get comprehensive DNS intelligence"""
        results = {}
        
        # Source 1: Reverse DNS (PTR)
        results['reverse_dns'] = self.get_reverse_dns(ip)
        
        # Source 2: DNS records if domain provided
        if domain:
            results['dns_records'] = self.get_all_dns_records(domain)
            results['subdomains'] = self.find_subdomains(domain)
        
        # Source 3: Passive DNS from ViewDNS
        results['passive_dns'] = self.get_passive_dns(ip)
        
        return results
    
    def get_reverse_dns(self, ip: str) -> List[str]:
        """Reverse DNS lookup"""
        try:
            rev_name = dns.reversename.from_address(ip)
            answers = self.resolver.resolve(rev_name, 'PTR')
            return [str(r) for r in answers]
        except:
            return []
    
    def get_all_dns_records(self, domain: str) -> Dict:
        """Get all DNS record types"""
        record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME', 'SOA']
        records = {}
        
        for rtype in record_types:
            try:
                answers = self.resolver.resolve(domain, rtype)
                records[rtype] = [str(r) for r in answers]
            except:
                records[rtype] = []
        
        return records
    
    def find_subdomains(self, domain: str) -> List[str]:
        """Find common subdomains"""
        common_subs = ['www', 'mail', 'ftp', 'admin', 'blog', 'api', 'cdn']
        found = []
        
        for sub in common_subs:
            target = f"{sub}.{domain}"
            try:
                self.resolver.resolve(target, 'A')
                found.append(target)
            except:
                continue
        
        return found
    
    def get_passive_dns(self, ip: str) -> Dict:
        """Get passive DNS history from ViewDNS"""
        try:
            # Note: This would require web scraping with proper ToS compliance
            return {
                'viewdns': f"https://viewdns.info/reverseip/?t=1&host={ip}",
                'dnsdumpster': "https://dnsdumpster.com/",
                'crtsh': f"https://crt.sh/?q={ip}"
            }
        except:
            return {}

# Usage
if __name__ == "__main__":
    dns = DNSIntelligence()
    result = dns.get_comprehensive_dns("8.8.8.8", "google.com")
    print(result)