import requests
import json
import subprocess
import re
from datetime import datetime
import sys

class SocialSearcher:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://social-searcher.com/api/"
    
    def search_mentions(self, query, network='all'):
        """Search for mentions across social media"""
        try:
            params = {
                'q': query,
                'type': 'email',
                'network': network,
            }
            if self.api_key:
                params['key'] = self.api_key
                
            response = requests.get(f"{self.base_url}search.php", params=params)
            return response.json() if response.status_code == 200 else {'error': f"API error: {response.status_code}"}
        except Exception as e:
            return {'error': str(e)}

class Pipl:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.pipl.com/search/"
    
    def search_person(self, email):
        """Search Pipl for person information (limited free)"""
        try:
            if not self.api_key:
                return {'error': 'API key required for Pipl'}
                
            params = {
                'email': email,
                'key': self.api_key
            }
            response = requests.get(self.base_url, params=params)
            return response.json() if response.status_code == 200 else {'error': f"API error: {response.status_code}"}
        except Exception as e:
            return {'error': str(e)}

class EmailRep:
    def __init__(self):
        self.base_url = "https://emailrep.io"
    
    def check_email(self, email):
        """Check email reputation using EmailRep API"""
        try:
            response = requests.get(f"{self.base_url}/{email}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {'error': 'Email not found in EmailRep database'}
            else:
                return {'error': f"API error: {response.status_code}"}
        except Exception as e:
            return {'error': str(e)}

class HoleheChecker:
    def __init__(self, email):
        self.email = email

    def run(self):
        try:
            cmd = ["holehe", self.email, "--only-used"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return {"error": result.stderr.strip() or "Holehe execution failed"}

            output = result.stdout.strip()
            if not output:
                return {"error": "No output from Holehe"}

            # Extract all [+] found sites
            found_sites = re.findall(r"\[\+\]\s*([^\n\r]+)", output)

            # Extract email from header (the first few lines)
            email_match = re.search(r"\*+\s*([\w\.-]+@[\w\.-]+)\s*\*+", output)
            email_in_output = email_match.group(1) if email_match else self.email

            # Extract summary info like "123 websites checked in 11.83 seconds"
            summary_match = re.search(r"(\d+)\s+websites checked in\s+([\d\.]+)\s+seconds", output)
            summary = {
                "total_sites_checked": int(summary_match.group(1)) if summary_match else None,
                "scan_time_seconds": float(summary_match.group(2)) if summary_match else None,
            }

            return {
                "source": "holehe",
                "email": email_in_output,
                "found": bool(found_sites),
                "data": [{"site": site.strip()} for site in found_sites],
                "summary": summary,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {"error": str(e)}




if __name__ == "__main__":
    print("Testing Social Media & Online Presence Module...")
    test_email = "johndoe@gmail.com"
    
    
    # Test SocialSearcher
    print("\n2. Testing SocialSearcher...")
    social_searcher = SocialSearcher()
    result = social_searcher.search_mentions(test_email)
    print(f"   Result: {result}")
    
    # Test Pipl
    print("\n3. Testing Pipl...")
    pipl = Pipl()
    result = pipl.search_person(test_email)
    print(f"   Result: {result}")
    
    # Test EmailRep
    print("\n4. Testing EmailRep...")
    email_rep = EmailRep()
    result = email_rep.check_email(test_email)
    print(f"   Result: {result}")
    
    #check holehe
    checker = HoleheChecker(test_email)
    result = checker.run()
    print(json.dumps(result, indent=2))

    print("\nSocial Media module test completed!")