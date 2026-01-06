from ipwhois import IPWhois
import requests
import whois
import dns.resolver

class WHOISASN:
    def get_comprehensive_whois(self, ip: str, domain: str = None) -> dict:
        """Get comprehensive WHOIS and ASN data"""
        results = {}
        
        # Source 1: ipwhois for IP WHOIS
        try:
            obj = IPWhois(ip)
            rdap_data = obj.lookup_rdap()
            results['ip_whois'] = {
                'asn': rdap_data.get('asn'),
                'asn_description': rdap_data.get('asn_description'),
                'network': rdap_data.get('network', {}).get('cidr'),
                'country': rdap_data.get('asn_country_code'),
                'rir': rdap_data.get('nir')
            }
        except: pass
        
        # Source 2: Team Cymru ASN service
        try:
            asn_info = self._team_cymru_asn(ip)
            results['team_cymru'] = asn_info
        except: pass
        
        # Source 3: Domain WHOIS if domain provided
        if domain:
            try:
                domain_info = whois.whois(domain)
                results['domain_whois'] = {
                    'registrar': domain_info.registrar,
                    'creation_date': str(domain_info.creation_date),
                    'expiration_date': str(domain_info.expiration_date)
                }
            except: pass
        
        return results
    
    def _team_cymru_asn(self, ip: str) -> dict:
        """Team Cymru IP to ASN mapping"""
        try:
            # Using DNS query for Team Cymru service
            query_ip = '.'.join(reversed(ip.split('.'))) + '.origin.asn.cymru.com'
            answers = dns.resolver.resolve(query_ip, 'TXT')
            if answers:
                data = str(answers[0]).strip('"').split(' | ')
                return {
                    'asn': data[0],
                    'ip_range': data[1],
                    'country': data[2],
                    'registry': data[3]
                }
        except: 
            return {}

# Usage
if __name__ == "__main__":
    whois_check = WHOISASN()
#    result = whois_check.get_comprehensive_whois("8.8.8.8", "google.com")
    result = whois_check.get_comprehensive_whois("8.8.8.8")
    print(result)