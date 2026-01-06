import whois
import dns.resolver
import requests

class HunterIO:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.hunter.io/v2"
    
    def domain_search(self, domain):
        """Search domain info using Hunter.io (limited free)"""
        try:
            if not self.api_key:
                return {'error': 'API key required for Hunter.io'}
                
            url = f"{self.base_url}/domain-search"
            params = {
                'domain': domain,
                'api_key': self.api_key
            }
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else {'error': f"API error: {response.status_code}"}
        except Exception as e:
            return {'error': str(e)}

class WhoisLookup:
    def __init__(self):
        pass
    
    def get_whois(self, domain):
        """Get WHOIS information using python-whois"""
        try:
            domain_info = whois.whois(domain)
            return {
                'domain_name': domain_info.domain_name,
                'registrar': domain_info.registrar,
                'creation_date': domain_info.creation_date,
                'expiration_date': domain_info.expiration_date,
                'name_servers': domain_info.name_servers,
                'emails': domain_info.emails,
                'status': domain_info.status
            }
        except Exception as e:
            return {'error': str(e)}

class DNSAnalyzer:
    def __init__(self):
        self.resolver = dns.resolver.Resolver()
    
    def get_mx_records(self, domain):
        """Get MX records using dnspython"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return [{'priority': record.preference, 'exchange': str(record.exchange)} for record in mx_records]
        except Exception as e:
            return {'error': str(e)}
    
    def get_all_records(self, domain):
        """Get various DNS records"""
        try:
            records = {}
            record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'SOA']
            
            for record_type in record_types:
                try:
                    answers = dns.resolver.resolve(domain, record_type)
                    records[record_type.lower()] = [str(r) for r in answers]
                except:
                    records[record_type.lower()] = []
            
            return records
        except Exception as e:
            return {'error': str(e)}

class EmailVerifier:
    def __init__(self):
        pass
    
    def verify_domain(self, domain):
        """Basic domain verification"""
        try:
            dns_analyzer = DNSAnalyzer()
            mx_records = dns_analyzer.get_mx_records(domain)
            return {
                'has_mx_records': len(mx_records) > 0 if not isinstance(mx_records, dict) else False,
                'mx_records': mx_records
            }
        except Exception as e:
            return {'error': str(e)}

if __name__ == "__main__":
    print("Testing Domain & Ownership Module...")
    test_domain = "google.com"
    
    # Test HunterIO
    print("\n1. Testing HunterIO...")
    hunter = HunterIO()
    result = hunter.domain_search(test_domain)
    print(f"   Result: {result}")
    
    # Test WhoisLookup
    print("\n2. Testing WhoisLookup...")
    whois_lookup = WhoisLookup()
    result = whois_lookup.get_whois(test_domain)
    print(f"   Domain: {result.get('domain_name', 'N/A')}")
    print(f"   Registrar: {result.get('registrar', 'N/A')}")
    
    # Test DNSAnalyzer
    print("\n3. Testing DNSAnalyzer...")
    dns_analyzer = DNSAnalyzer()
    result = dns_analyzer.get_mx_records(test_domain)
    print(f"   MX Records: {result}")
    
    # Test EmailVerifier
    print("\n4. Testing EmailVerifier...")
    email_verifier = EmailVerifier()
    result = email_verifier.verify_domain(test_domain)
    print(f"   Result: {result}")
    
    print("\nDomain & Ownership module test completed!")