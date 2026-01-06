import ssl
import socket
import OpenSSL
from datetime import datetime
import requests
import re
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SSLAnalyzer:
    def get_comprehensive_ssl(self, hostname: str, port: int = 443) -> dict:
        """Comprehensive SSL certificate analysis"""
        results = {}
        
        # Source 1: Direct SSL certificate extraction
        results['certificate_info'] = self.get_certificate_info(hostname, port)
        
        # Source 2: crt.sh for certificate history
        results['certificate_history'] = self.get_crt_sh(hostname)
        
        # Source 3: Censys (if API key available)
        results['censys'] = self.get_censys_info(hostname)
        
        return results
    
    def get_certificate_info(self, hostname: str, port: int = 443) -> dict:
        try:
            # Create SSL context correctly
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert_der = ssock.getpeercert(True)
                    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_der)
                    
                    # Convert bytes to strings for subject and issuer
                    subject = {}
                    for component in cert.get_subject().get_components():
                        key = component[0].decode('utf-8') if isinstance(component[0], bytes) else component[0]
                        value = component[1].decode('utf-8') if isinstance(component[1], bytes) else component[1]
                        subject[key] = value
                    
                    issuer = {}
                    for component in cert.get_issuer().get_components():
                        key = component[0].decode('utf-8') if isinstance(component[0], bytes) else component[0]
                        value = component[1].decode('utf-8') if isinstance(component[1], bytes) else component[1]
                        issuer[key] = value
                    
                    return {
                        'subject': subject,
                        'issuer': issuer,
                        'version': cert.get_version() + 1,  # OpenSSL version is 0-based
                        'serial': str(cert.get_serial_number()),
                        'not_before': cert.get_notBefore().decode('utf-8'),
                        'not_after': cert.get_notAfter().decode('utf-8'),
                        'signature_algorithm': cert.get_signature_algorithm().decode('utf-8') if isinstance(cert.get_signature_algorithm(), bytes) else str(cert.get_signature_algorithm()),
                        'subject_alt_names': self._extract_sans(cert)
                    }
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_sans(self, cert) -> list:
        sans = []
        for i in range(cert.get_extension_count()):
            try:
                ext = cert.get_extension(i)
                ext_name = ext.get_short_name()
                if isinstance(ext_name, bytes):
                    ext_name = ext_name.decode('utf-8')
                
                if 'subjectAltName' in str(ext_name):
                    ext_value = str(ext)
                    sans.extend(re.findall(r'DNS:([^\s,]+)', ext_value))
            except:
                continue
        return sans
    
    def get_crt_sh(self, hostname: str) -> dict:
        try:
            url = f"https://crt.sh/?q={hostname}&output=json"
            response = requests.get(url, timeout=15, verify=False)
            if response.status_code == 200:
                certificates = response.json()
                return {
                    'total_certificates': len(certificates),
                    'sample_certs': certificates[:3] if certificates else []
                }
            return {'error': f'API status {response.status_code}'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_censys_info(self, hostname: str) -> dict:
        return {
            'info': 'Censys API requires authentication',
            'website': 'https://search.censys.io/',
            'search_url': f'https://search.censys.io/search?q={hostname}'
        }

# Usage
if __name__ == "__main__":
    ssl_analyzer = SSLAnalyzer()
    result = ssl_analyzer.get_comprehensive_ssl("github.com")
    print(result)