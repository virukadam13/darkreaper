import json
from datetime import datetime
import os
import traceback
import asyncio
from typing import Dict, List, Optional
import sys

# Import the modules you provided
sys.path.append('.')  # Add current directory to path

from .email1.search_engines import GoogleDorking, DuckDuckGo, PastebinSearch, CustomScraper
from .email1.email_validation import MailTester, EmailVerifierTool, Kickbox, ZeroBounce
from .email1.social_media import SocialSearcher, Pipl, EmailRep, HoleheChecker
from .email1.domain_analysis import HunterIO, WhoisLookup, DNSAnalyzer, EmailVerifier
from .email1.darkweb_search import OnionSearch, Ahmia, DarkFailChecker
from .email1.breaches_leaks import HaveIBeenPwned, BreachDirectory, LeakCheck, Dehashed, H8mailLookup, PasteSiteLookup


class EmailResearchHandler:
    def __init__(self):
        # Initialize all modules
        self.social_searcher = SocialSearcher()
        self.pipl = Pipl()
        self.email_rep = EmailRep()
        self.holehe = None  # Will be initialized per email
        
        self.google_dorking = GoogleDorking()
        self.duckduckgo = DuckDuckGo()
        self.pastebin_search = PastebinSearch()
        self.custom_scraper = CustomScraper()
        
        self.mail_tester = MailTester()
        self.email_verifier = EmailVerifierTool()
        self.kickbox = Kickbox()
        self.zerobounce = ZeroBounce()
        
        self.hunter_io = HunterIO()
        self.whois_lookup = WhoisLookup()
        self.dns_analyzer = DNSAnalyzer()
        self.domain_verifier = EmailVerifier()
        
        self.hibp = HaveIBeenPwned()
        self.breach_directory = BreachDirectory()
        self.leak_check = LeakCheck()
        self.dehashed = Dehashed()
        self.h8mail = H8mailLookup()
        self.paste_sites = PasteSiteLookup()
        
        # Initialize darkweb search modules
        self.onion_search = OnionSearch(api_key="sk")
        self.ahmia = Ahmia()
        self.dark_fail = DarkFailChecker()
    
    def validate_email(self, email: str) -> bool:
        """Validate email address format"""
        return '@' in email and '.' in email.split('@')[1]
    
    async def conduct_research(self, email: str, depth: int = 2) -> Dict:
        """
        Conduct sequential email research with progress reporting
        """
        if not self.validate_email(email):
            return {
                "error": "Invalid email address format",
                "input": email,
                "timestamp": datetime.now().isoformat()
            }
        
        start_time = datetime.now()
        results = {
            "meta": {
                "input": email,
                "start_time": start_time.isoformat(),
                "depth": depth,
                "modules_used": []
            },
            "results": {},
            "summary": {
                "entities_found": {},
                "risk_assessment": {}
            }
        }
        
        try:
            # PHASE 1: BASIC VALIDATION & FORMAT CHECK
            print(f"\n{'-'*50}")
            print(f"🔍 RESEARCHING: {email}")
            print(f"{'-'*50}")
            
            # 1. Email Format Validation
            print(f"\n📧 [1/12] Validating email format...")
            validation_result = self.email_verifier.verify_email(email)
            results["results"]["validation"] = validation_result
            results["meta"]["modules_used"].append("EmailVerifierTool")
            
            if not validation_result.get('valid_format', False):
                print("   ❌ Invalid email format")
                return results
            else:
                print("   ✅ Valid email format")
            
            # 2. Domain Verification
            print(f"\n🌐 [2/12] Verifying domain...")
            domain = email.split('@')[1]
            domain_result = self.domain_verifier.verify_domain(domain)
            results["results"]["domain_verification"] = domain_result
            results["meta"]["modules_used"].append("EmailVerifier")
            
            if domain_result.get('has_mx_records', False):
                print("   ✅ Domain has MX records")
            else:
                print("   ⚠️  Domain may not exist or have email service")
            
            # 3. Email Reputation Check
            print(f"\n🛡️ [3/12] Checking email reputation...")
            email_rep_result = self.email_rep.check_email(email)
            results["results"]["email_reputation"] = email_rep_result
            results["meta"]["modules_used"].append("EmailRep")
            
            if 'error' not in email_rep_result:
                print("   ✅ Email reputation data retrieved")
            else:
                print("   ⚠️  Could not retrieve reputation data")
            
            # PHASE 2: BREACHES & LEAKS CHECK
            print(f"\n🔓 [4/12] Checking data breaches...")
            hibp_result = self.hibp.check_email(email)
            results["results"]["have_i_been_pwned"] = hibp_result
            results["meta"]["modules_used"].append("HaveIBeenPwned")
            
            if hibp_result.get('breached', False):
                breach_count = hibp_result.get('breach_count', 0)
                print(f"   🔥 Email found in {breach_count} breaches!")
                results["summary"]["risk_assessment"]["breaches"] = f"Found in {breach_count} breaches"
            else:
                print("   ✅ No known breaches found")
            
            # 5. H8mail Breach Check
            print(f"\n📊 [5/12] Running comprehensive breach check...")
            h8mail_result = self.h8mail.lookup(email)
            results["results"]["h8mail_breaches"] = h8mail_result
            results["meta"]["modules_used"].append("H8mailLookup")
            
            if h8mail_result.get('found', False):
                breach_count = len(h8mail_result.get('data', []))
                print(f"   🔥 Found {breach_count} additional breach records")
            else:
                print("   ✅ No additional breaches found")
            
            # PHASE 3: SOCIAL MEDIA & ONLINE PRESENCE
            print(f"\n👥 [6/12] Searching social media mentions...")
            social_result = self.social_searcher.search_mentions(email)
            results["results"]["social_media_mentions"] = social_result
            results["meta"]["modules_used"].append("SocialSearcher")
            
            if 'error' not in social_result:
                print("   ✅ Social media search completed")
            else:
                print("   ⚠️  Social media search limited")
            
            # 7. Holehe Account Check
            print(f"\n🔎 [7/12] Checking online account registrations...")
            self.holehe = HoleheChecker(email)
            holehe_result = self.holehe.run()
            results["results"]["holehe_accounts"] = holehe_result
            results["meta"]["modules_used"].append("HoleheChecker")
            
            if holehe_result.get('found', False):
                account_count = len(holehe_result.get('data', []))
                print(f"   📱 Found accounts on {account_count} platforms")
                results["summary"]["entities_found"]["platforms"] = holehe_result.get('data', [])
            else:
                print("   ✅ No widespread account registrations found")
            
            # PHASE 4: SEARCH ENGINE & PASTE SITES
            print(f"\n🌐 [8/12] Searching search engines...")
            google_result = self.google_dorking.search_email(email, num_results=5)
            results["results"]["google_dorking"] = google_result
            results["meta"]["modules_used"].append("GoogleDorking")
            
            if google_result.get('results'):
                result_count = len(google_result['results'])
                print(f"   🔍 Found {result_count} search results")
            else:
                print("   ✅ No public search results found")
            
            # 9. DuckDuckGo Search
            print(f"\n🦆 [9/12] Searching DuckDuckGo...")
            ddg_result = self.duckduckgo.search(email, max_results=5)
            results["results"]["duckduckgo"] = ddg_result
            results["meta"]["modules_used"].append("DuckDuckGo")
            
            if ddg_result.get('results'):
                result_count = len(ddg_result['results'])
                print(f"   🔍 Found {result_count} DuckDuckGo results")
            
            # 10. Pastebin Search
            print(f"\n📋 [10/12] Checking paste sites...")
            pastebin_result = self.pastebin_search.search_email(email)
            results["results"]["pastebin"] = pastebin_result
            results["meta"]["modules_used"].append("PastebinSearch")
            
            if isinstance(pastebin_result, list) and len(pastebin_result) > 0:
                print(f"   📄 Found {len(pastebin_result)} paste entries")
                results["summary"]["risk_assessment"]["pastes_found"] = True
            else:
                print("   ✅ No paste entries found")
            
            # PHASE 5: DARK WEB & ADVANCED CHECKS
            print(f"\n🌑 [11/12] Scanning dark web mentions...")
            darkweb_result = await self._conduct_darkweb_research(email)
            results["results"]["darkweb_mentions"] = darkweb_result
            results["meta"]["modules_used"].extend(darkweb_result.get("modules_used", []))
            
            total_darkweb_mentions = sum([
                len(darkweb_result.get("ahmia_results", [])),
                len(darkweb_result.get("onion_search_results", [])),
                len(darkweb_result.get("dark_fail_onions", []))
            ])
            
            if total_darkweb_mentions > 0:
                print(f"   ⚠️  Found {total_darkweb_mentions} dark web mentions")
                results["summary"]["risk_assessment"]["darkweb_mentions"] = total_darkweb_mentions
            else:
                print("   ✅ No dark web mentions found")
            
            # 12. Pipl Person Search
            print(f"\n👤 [12/12] Searching person databases...")
            pipl_result = self.pipl.search_person(email)
            results["results"]["pipl_search"] = pipl_result
            results["meta"]["modules_used"].append("Pipl")
            
            if 'error' not in pipl_result:
                print("   ✅ Person search completed")
            else:
                print("   ℹ️  Pipl search requires API key")
            
            # Generate Summary
            results["summary"]["processing_time"] = str(datetime.now() - start_time)
            results["summary"]["total_modules"] = len(results["meta"]["modules_used"])
            
            # Final risk assessment
            self._generate_risk_assessment(results)
            
        except Exception as e:
            results["error"] = f"Research failed: {str(e)}"
            results["traceback"] = traceback.format_exc()
        
        results["meta"]["end_time"] = datetime.now().isoformat()
        
        print(f"\n{'='*50}")
        print(f"🎯 RESEARCH COMPLETED: {email}")
        print(f"⏰ Processing time: {results['summary']['processing_time']}")
        print(f"📊 Modules used: {results['summary']['total_modules']}")
        print(f"{'='*50}")
        
        return results

    async def _conduct_darkweb_research(self, email: str) -> Dict:
        """Conduct comprehensive dark web research using multiple methods"""
        darkweb_results = {
            "ahmia_results": [],
            "onion_search_results": [],
            "dark_fail_onions": [],
            "modules_used": []
        }
        
        try:
            # Method 1: Ahmia Search
            print("   🔎 Searching Ahmia...")
            ahmia_results = self.ahmia.search(email)
            if ahmia_results:
                darkweb_results["ahmia_results"] = ahmia_results
                darkweb_results["modules_used"].append("Ahmia")
            
            # Method 2: OnionSearch Engine
            print("   🔎 Searching OnionSearch Engine...")
            try:
                onion_results = self.onion_search.search(email, pages=1)
                if onion_results:
                    darkweb_results["onion_search_results"] = onion_results
                    darkweb_results["modules_used"].append("OnionSearch")
            except Exception as e:
                print(f"   ⚠️  OnionSearch failed: {e}")
            
            # Method 3: DarkFail Checker
            print("   🔎 Checking DarkFail...")
            try:
                dark_fail_result = self.dark_fail.run(query=email, auto_verify_gpg=False, fetch_onion_via_tor=False)
                if dark_fail_result and "onions" in dark_fail_result:
                    darkweb_results["dark_fail_onions"] = dark_fail_result["onions"]
                    darkweb_results["modules_used"].append("DarkFailChecker")
            except Exception as e:
                print(f"   ⚠️  DarkFail check failed: {e}")
            
        except Exception as e:
            print(f"   ❌ Dark web research failed: {e}")
            darkweb_results["error"] = str(e)
        
        return darkweb_results
    
    def _generate_risk_assessment(self, results: Dict):
        """Generate risk assessment based on findings"""
        risk_score = 0
        risk_factors = []
        
        # Check for breaches
        hibp = results["results"].get("have_i_been_pwned", {})
        if hibp.get('breached', False):
            risk_score += 3
            risk_factors.append(f"Found in {hibp.get('breach_count', 0)} data breaches")
        
        h8mail = results["results"].get("h8mail_breaches", {})
        if h8mail.get('found', False):
            risk_score += 2
            risk_factors.append("Additional breach records found")
        
        # Check for paste entries
        pastebin = results["results"].get("pastebin", [])
        if isinstance(pastebin, list) and len(pastebin) > 0:
            risk_score += 2
            risk_factors.append("Email found in paste sites")
        
        # Check for dark web mentions
        darkweb = results["results"].get("darkweb_mentions", {})
        total_darkweb_mentions = sum([
            len(darkweb.get("ahmia_results", [])),
            len(darkweb.get("onion_search_results", [])),
            len(darkweb.get("dark_fail_onions", []))
        ])
        if total_darkweb_mentions > 0:
            risk_score += 3
            risk_factors.append(f"Email mentioned {total_darkweb_mentions} times on dark web")
        
        # Check for widespread accounts
        holehe = results["results"].get("holehe_accounts", {})
        if holehe.get('found', False):
            account_count = len(holehe.get('data', []))
            if account_count > 5:
                risk_score += 1
                risk_factors.append(f"Registered on {account_count} platforms")
        
        # Determine risk level
        if risk_score >= 6:
            risk_level = "HIGH"
        elif risk_score >= 3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        results["summary"]["risk_assessment"]["score"] = risk_score
        results["summary"]["risk_assessment"]["level"] = risk_level
        results["summary"]["risk_assessment"]["factors"] = risk_factors
        
        print(f"\n📈 RISK ASSESSMENT: {risk_level} ({risk_score}/10)")
        for factor in risk_factors:
            print(f"   • {factor}")
    
    async def conduct_research_with_output(self, email: str, output_path: str, depth: int = 2) -> Dict:
        """Conduct research and save results to files - COMPATIBLE WITH DARKREAPER"""
        research_data = await self.conduct_research(email, depth)
        
        if "error" in research_data:
            return research_data
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path) if os.path.dirname(output_path) else '.'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON report (exactly as darkreaper expects)
        json_path = f"{output_path}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(research_data, f, indent=2, ensure_ascii=False)
        
        # Generate and save text summary
        txt_path = f"{output_path}_summary.txt"
        self._generate_text_summary(research_data, txt_path)
        
        # Return format that darkreaper expects
        return {
            "success": True,
            "message": "Email research completed and saved",
            "email": email,
            "json_output_path": os.path.abspath(json_path),
            "txt_summary_path": os.path.abspath(txt_path),
            "entity_count": len(research_data.get("summary", {}).get("entities_found", {})),
            "risk_level": research_data.get("summary", {}).get("risk_assessment", {}).get("level", "UNKNOWN")
        }
    
    def _generate_text_summary(self, research_data: Dict, output_path: str):
        """Generate a readable text summary"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"EMAIL RESEARCH REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Email: {research_data['meta']['input']}\n")
            f.write(f"Research Date: {research_data['meta']['start_time']}\n")
            f.write(f"Processing Time: {research_data['summary']['processing_time']}\n")
            f.write(f"Modules Used: {research_data['summary']['total_modules']}\n\n")
            
            # Risk Assessment
            risk_assessment = research_data['summary']['risk_assessment']
            f.write("RISK ASSESSMENT:\n")
            f.write(f"Level: {risk_assessment.get('level', 'UNKNOWN')}\n")
            f.write(f"Score: {risk_assessment.get('score', 0)}/10\n")
            f.write("Factors:\n")
            for factor in risk_assessment.get('factors', []):
                f.write(f"  • {factor}\n")
            f.write("\n")
            
            # Key Findings
            f.write("KEY FINDINGS:\n")
            f.write("-" * 40 + "\n")
            
            # Breaches
            hibp = research_data['results'].get('have_i_been_pwned', {})
            if hibp.get('breached', False):
                f.write(f"• Data Breaches: Found in {hibp.get('breach_count', 0)} breaches\n")
            
            # Accounts
            holehe = research_data['results'].get('holehe_accounts', {})
            if holehe.get('found', False):
                f.write(f"• Online Accounts: Registered on {len(holehe.get('data', []))} platforms\n")
            
            # Search Results
            google = research_data['results'].get('google_dorking', {})
            if google.get('results'):
                f.write(f"• Search Results: {len(google['results'])} public mentions\n")
            
            # Dark Web
            darkweb = research_data['results'].get('darkweb_mentions', {})
            total_darkweb_mentions = sum([
                len(darkweb.get("ahmia_results", [])),
                len(darkweb.get("onion_search_results", [])),
                len(darkweb.get("dark_fail_onions", []))
            ])
            if total_darkweb_mentions > 0:
                f.write(f"• Dark Web: {total_darkweb_mentions} mentions found\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("Report generated by Email Research Module\n")
            f.write("=" * 60 + "\n")


# CRITICAL: These synchronous wrappers MUST exist for darkreaper compatibility
def sync_conduct_research(email: str, depth: int = 2) -> Dict:
    """Synchronous wrapper for async research - REQUIRED BY DARKREAPER"""
    handler = EmailResearchHandler()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(handler.conduct_research(email, depth))
        return result
    finally:
        loop.close()

def sync_conduct_research_with_output(email: str, output_path: str, depth: int = 2) -> Dict:
    """Synchronous wrapper for async research with output - REQUIRED BY DARKREAPER"""
    handler = EmailResearchHandler()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(handler.conduct_research_with_output(email, output_path, depth))
        return result
    finally:
        loop.close()


# Example usage and testing
if __name__ == "__main__":
    # Test the module
    email = "test@example.com"
    
    print("Testing Email Research Module...")
    research = sync_conduct_research(email, depth=2)
    
    # Save report
    handler = EmailResearchHandler()
    output_result = sync_conduct_research_with_output(email, "email_research_report")
    
    print(f"\nResearch completed!")
    print(f"JSON Report: {output_result.get('json_output_path')}")
    print(f"Text Summary: {output_result.get('txt_summary_path')}")
    print(f"Risk Level: {output_result.get('risk_level')}")