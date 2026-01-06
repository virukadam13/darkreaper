import re
import requests
import dns.resolver
import socket
from typing import Dict, Any, List

class MailTester:
    def __init__(self):
        pass
    
    def test_email(self, email: str) -> Dict[str, Any]:
        """Test email using MailTester approach"""
        try:
            if '@' not in email:
                return {'error': 'Invalid email format - missing @ symbol'}
                
            domain = email.split('@')[1]
            mx_records = dns.resolver.resolve(domain, 'MX')
            return {
                'valid_mx': len(mx_records) > 0,
                'domain': domain,
                'mx_records': [str(record.exchange) for record in mx_records]
            }
        except dns.resolver.NXDOMAIN:
            return {'error': f'Domain {domain} does not exist'}
        except dns.resolver.NoAnswer:
            return {'error': f'No MX records found for domain {domain}'}
        except dns.resolver.Timeout:
            return {'error': 'DNS query timed out'}
        except Exception as e:
            return {'error': f'DNS resolution failed: {str(e)}'}

class EmailVerifierTool:
    def __init__(self):
        self.disposable_domains = self.load_disposable_domains()
    
    def load_disposable_domains(self) -> set:
        """Load a more comprehensive list of disposable email domains"""
        return {
            'tempmail.com', 'guerrillamail.com', 'mailinator.com',
            '10minutemail.com', 'throwawaymail.com', 'yopmail.com',
            'fakeinbox.com', 'trashmail.com', 'dispostable.com',
            'temp-mail.org', 'getairmail.com', 'mohmal.com'
        }
    
    def verify_email(self, email: str) -> Dict[str, Any]:
        """Comprehensive email verification"""
        try:
            # Basic format validation
            if not email or '@' not in email:
                return {
                    'valid_format': False,
                    'valid_domain': False,
                    'disposable': False,
                    'email': email
                }
            
            # Enhanced format validation
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            is_valid_format = bool(re.match(pattern, email))
            
            # Domain validation
            domain = email.split('@')[1]
            valid_domain = False
            
            if is_valid_format:
                try:
                    # Try multiple DNS record types
                    dns.resolver.resolve(domain, 'MX')
                    valid_domain = True
                except dns.resolver.NXDOMAIN:
                    # Domain doesn't exist
                    valid_domain = False
                except dns.resolver.NoAnswer:
                    # No MX records, try A records
                    try:
                        dns.resolver.resolve(domain, 'A')
                        valid_domain = True
                    except:
                        valid_domain = False
                except:
                    valid_domain = False
            
            return {
                'valid_format': is_valid_format,
                'valid_domain': valid_domain,
                'disposable': self.is_disposable_email(domain),
                'email': email,
                'domain': domain
            }
        except Exception as e:
            return {'error': str(e), 'email': email}
    
    def is_disposable_email(self, domain: str) -> bool:
        """Check if domain is from disposable email service"""
        return domain.lower() in self.disposable_domains
    
    def add_disposable_domain(self, domain: str):
        """Add a domain to the disposable list"""
        self.disposable_domains.add(domain.lower())

class Kickbox:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.kickbox.com/v2"
    
    def verify_email(self, email: str) -> Dict[str, Any]:
        """Verify email using Kickbox API (limited free)"""
        try:
            if not self.api_key:
                return {
                    'error': 'API key required for Kickbox',
                    'email': email,
                    'suggestion': 'Get free API key from https://kickbox.com'
                }
                
            url = f"{self.base_url}/verify"
            params = {
                'email': email,
                'apikey': self.api_key
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'result': result,
                    'email': email
                }
            else:
                return {
                    'error': f"API error: {response.status_code}",
                    'email': email
                }
        except requests.Timeout:
            return {'error': 'Request timeout', 'email': email}
        except Exception as e:
            return {'error': str(e), 'email': email}

class ZeroBounce:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.zerobounce.net/v2"
    
    def validate_email(self, email: str) -> Dict[str, Any]:
        """Validate email using ZeroBounce (trial)"""
        try:
            if not self.api_key:
                return {
                    'error': 'API key required for ZeroBounce',
                    'email': email,
                    'suggestion': 'Get free trial from https://zerobounce.net'
                }
                
            url = f"{self.base_url}/validate"
            params = {
                'email': email,
                'api_key': self.api_key
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'result': result,
                    'email': email
                }
            else:
                return {
                    'error': f"API error: {response.status_code}",
                    'email': email
                }
        except requests.Timeout:
            return {'error': 'Request timeout', 'email': email}
        except Exception as e:
            return {'error': str(e), 'email': email}

def test_email_validation():
    """Comprehensive test function"""
    print("Testing Enhanced Email Validation Module...")
    
    # Test with various email formats
    test_emails = [
        "johndoe@gmail.com",           # Valid
        "johndoe@@gmail.com",          # Invalid format
        "test@tempmail.com",           # Disposable
        "invalid@nonexistentdomain12345.com",  # Non-existent domain
        "missingdomain@",              # Invalid
        "valid.email+tag@gmail.com",   # Valid with tag
    ]
    
    # Test EmailVerifierTool
    print("\n1. Testing EmailVerifierTool...")
    email_verifier = EmailVerifierTool()
    
    for email in test_emails:
        result = email_verifier.verify_email(email)
        print(f"   {email}:")
        print(f"     Format: {result.get('valid_format', 'N/A')}")
        print(f"     Domain: {result.get('valid_domain', 'N/A')}")
        print(f"     Disposable: {result.get('disposable', 'N/A')}")
        if 'error' in result:
            print(f"     Error: {result['error']}")
        print()
    
    # Test MailTester with valid domains
    print("\n2. Testing MailTester with valid domains...")
    mail_tester = MailTester()
    valid_test_emails = [email for email in test_emails if '@' in email and not email.endswith('@')]
    
    for email in valid_test_emails[:2]:  # Test first 2 to avoid too many DNS queries
        result = mail_tester.test_email(email)
        print(f"   {email}: {result}")
    
    # Test API services (without keys)
    print("\n3. Testing API Services (without keys)...")
    kickbox = Kickbox()
    zerobounce = ZeroBounce()
    
    api_test_email = "test@gmail.com"
    kb_result = kickbox.verify_email(api_test_email)
    zb_result = zerobounce.validate_email(api_test_email)
    
    print(f"   Kickbox: {kb_result.get('error', 'N/A')}")
    print(f"   ZeroBounce: {zb_result.get('error', 'N/A')}")
    
    print("\nEnhanced Validation module test completed!")

# if __name__ == "__main__":
#     test_email_validation()

if __name__ == "__main__":
    print("Testing Validation & Reputation Module...")
    test_email = "johndoe@gmail.com"
    disposable_email = "test@tempmail.com"
    
    # Test MailTester
    print("\n1. Testing MailTester...")
    mail_tester = MailTester()
    result = mail_tester.test_email(test_email)
    print(f"   Result: {result}")
    
    # Test EmailVerifierTool
    print("\n2. Testing EmailVerifierTool...")
    email_verifier = EmailVerifierTool()
    result1 = email_verifier.verify_email(test_email)
    result2 = email_verifier.verify_email(disposable_email)
    print(f"   Valid email: {result1}")
    print(f"   Disposable email: {result2}")
    
    # Test Kickbox
    print("\n3. Testing Kickbox...")
    kickbox = Kickbox()
    result = kickbox.verify_email(test_email)
    print(f"   Result: {result}")
    
    # Test ZeroBounce
    print("\n4. Testing ZeroBounce...")
    zerobounce = ZeroBounce()
    result = zerobounce.validate_email(test_email)
    print(f"   Result: {result}")
    
    print("\nValidation & Reputation module test completed!")