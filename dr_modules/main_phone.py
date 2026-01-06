import json
import re
import asyncio
import traceback
from datetime import datetime
from typing import Dict, List, Optional
from colorama import Fore, Style, init

# Import the required modules (make sure these are available)
try:
    from .phone.phone_intel import PhoneNumberIntelligence, analyze_phone_number
    from .phone.identity_intel import NLPNameFinder, find_names_from_phone
    from .phone.email_discovery import EmailDiscovery
    from .phone.dorking_ph import MultiSearchEngine, search_phone_all_engines
    from .phone.breach_check_ph import LeakCheckAPI, BreachDirectoryScraper
    from .phone.analysis_engine import AnalysisEngine, analyze_correlations
    from .phone.darkweb_search import Ahmia, OnionSearch, DarkFailChecker  # Added DarkFailChecker
except ImportError as e:
    print(f"Warning: Some modules not available - {e}")

# Initialize colorama for colored output
init()

class PhoneResearchHandler:
    def __init__(self):
        self.validator = OSINTValidator()
        # Initialize darkweb search modules
        self.ahmia_searcher = Ahmia()
        self.onion_searcher = OnionSearch(api_key="sk")
        self.darkfail_checker = DarkFailChecker()  # Initialize DarkFail checker
        
    def validate_phone(self, phone_number: str) -> bool:
        """Validate phone number format"""
        return self.validator.is_valid_phone(phone_number)
    
    async def conduct_research(self, phone_number: str, depth: int = 2) -> Dict:
        """
        Coordinate phone number research across multiple modules sequentially
        with progress display
        
        Args:
            phone_number: Phone number to research
            depth: How many levels deep to chain research (1-3)
            
        Returns:
            Dictionary containing SpiderFoot-style report
        """
        if not self.validate_phone(phone_number):
            return {
                "error": "Invalid phone number format",
                "input": phone_number,
                "timestamp": datetime.now().isoformat()
            }
        
        start_time = datetime.now()
        results = {
            "meta": {
                "input": phone_number,
                "start_time": start_time.isoformat(),
                "depth": depth,
                "modules": [
                    "PhoneNumberIntelligence",
                    "NLPNameFinder", 
                    "EmailDiscovery",
                    "MultiSearchEngine",
                    "BreachCheck",
                    "DarkwebSearch",
                    "AnalysisEngine"
                ]
            },
            "raw": {},
            "entities": {},
            "relationships": []
        }
        
        try:
            # Step 1: Basic Phone Intelligence
            print(f"\n{Fore.CYAN}[1/7] Running Phone Number Intelligence...{Style.RESET_ALL}")
            phone_intel = await self._run_phone_intelligence(phone_number)
            results["raw"]["phone_intelligence"] = phone_intel
            self._display_findings("Phone Intelligence", phone_intel)
            
            # Step 2: Name Discovery
            print(f"\n{Fore.CYAN}[2/7] Running Name Discovery...{Style.RESET_ALL}")
            name_result = await self._run_name_discovery(phone_number)
            results["raw"]["name_discovery"] = name_result
            self._display_findings("Name Discovery", name_result)
            
            # Step 3: Email Discovery
            print(f"\n{Fore.CYAN}[3/7] Running Email Discovery...{Style.RESET_ALL}")
            email_result = await self._run_email_discovery(phone_number)
            results["raw"]["email_discovery"] = email_result
            self._display_findings("Email Discovery", email_result)
            
            # Step 4: Multi-Engine Search
            print(f"\n{Fore.CYAN}[4/7] Running Multi-Engine Search...{Style.RESET_ALL}")
            search_result = await self._run_search_engine(phone_number)
            results["raw"]["search_engine"] = search_result
            self._display_findings("Search Engine", search_result)
            
            # Step 5: Breach Check
            print(f"\n{Fore.CYAN}[5/7] Running Breach Check...{Style.RESET_ALL}")
            breach_result = await self._run_breach_check(phone_number)
            results["raw"]["breach_check"] = breach_result
            self._display_findings("Breach Check", breach_result)
            
            # Step 6: Darkweb Search
            print(f"\n{Fore.CYAN}[6/7] Running Darkweb Search...{Style.RESET_ALL}")
            darkweb_result = await self._run_darkweb_search(phone_number)
            results["raw"]["darkweb_search"] = darkweb_result
            self._display_findings("Darkweb Search", darkweb_result)
            
            # Step 7: Analysis Engine
            print(f"\n{Fore.CYAN}[7/7] Running Analysis Engine...{Style.RESET_ALL}")
            analysis_result = await self._run_analysis_engine(results["raw"])
            results["raw"]["analysis"] = analysis_result
            self._display_findings("Analysis", analysis_result)
            
        except Exception as e:
            error_msg = f"Research failed: {str(e)}\n{traceback.format_exc()}"
            print(f"{Fore.RED}Error: {error_msg}{Style.RESET_ALL}")
            return {
                "error": error_msg,
                "input": phone_number,
                "timestamp": datetime.now().isoformat()
            }
        
        # Extract and standardize entities
        results["entities"] = self._extract_entities(results["raw"])
        
        # Build relationships between entities
        results["relationships"] = self._build_relationships(results["entities"])
        
        # Add final metadata
        results["meta"]["end_time"] = datetime.now().isoformat()
        results["meta"]["processing_time"] = str(datetime.now() - start_time)
        results["meta"]["entity_counts"] = {
            k: len(v) for k, v in results["entities"].items()
        }
        
        print(f"\n{Fore.GREEN}✅ Research completed!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Total processing time: {results['meta']['processing_time']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Total entities found: {sum(len(v) for v in results['entities'].values())}{Style.RESET_ALL}")
        
        return results
    
    async def _run_phone_intelligence(self, phone_number: str) -> Dict:
        """Run phone number intelligence analysis"""
        try:
            # Try async version first, fallback to sync
            try:
                analyzer = PhoneNumberIntelligence()
                result = await analyzer.comprehensive_phone_analysis(phone_number)
            except:
                # Fallback to sync version
                result = analyze_phone_number(phone_number)
            return result
        except Exception as e:
            return {"error": f"Phone intelligence failed: {str(e)}"}
    
    async def _run_name_discovery(self, phone_number: str) -> Dict:
        """Run name discovery"""
        try:
            # Try async version first, fallback to sync
            try:
                name_finder = NLPNameFinder()
                result = await name_finder.find_names(phone_number)
            except:
                # Fallback to sync version
                result = find_names_from_phone(phone_number)
            return result
        except Exception as e:
            return {"error": f"Name discovery failed: {str(e)}"}
    
    async def _run_email_discovery(self, phone_number: str) -> Dict:
        """Run email discovery"""
        try:
            email_discovery = EmailDiscovery()
            result = await email_discovery.find_emails(phone_number, use_test_data=False)
            return result
        except Exception as e:
            return {"error": f"Email discovery failed: {str(e)}"}
    
    async def _run_search_engine(self, phone_number: str) -> Dict:
        """Run multi-engine search"""
        try:
            search_engine = MultiSearchEngine()
            result = search_engine.search_all(f'"{phone_number}"')
            return result
        except Exception as e:
            return {"error": f"Search engine failed: {str(e)}"}
    
    async def _run_breach_check(self, phone_number: str) -> Dict:
        """Run breach checking"""
        try:
            leakcheck_key = "2"  # From breach_check_ph.py
            
            apis = [
                LeakCheckAPI(leakcheck_key, phone_number),
                BreachDirectoryScraper(phone_number),
            ]
            
            results = []
            for api in apis:
                result = api.check()
                results.append(result)
            
            return {
                "breach_results": results,
                "total_checks": len(results)
            }
        except Exception as e:
            return {"error": f"Breach check failed: {str(e)}"}
    
    async def _run_darkweb_search(self, phone_number: str) -> Dict:
        """Run comprehensive darkweb search using multiple methods"""
        try:
            darkweb_results = {
                "ahmia_results": [],
                "onion_search_results": [],
                "darkfail_results": [],
                "search_terms": [],
                "total_results": 0,
                "sources": ["Ahmia", "OnionSearchEngine", "DarkFail"],
                "note": "Safe clearnet search for darkweb references - no Tor access required"
            }
            
            # Generate search terms
            search_terms = [
                phone_number,
                phone_number.replace("+", ""),
                phone_number.replace(" ", ""),
                f"phone {phone_number}",
                f"contact {phone_number}",
                f"telegram {phone_number}",
                f"signal {phone_number}",
                f"whatsapp {phone_number}"
            ]
            darkweb_results["search_terms"] = search_terms
            
            # Search with Ahmia
            ahmia_results = []
            for term in search_terms:
                results = self.ahmia_searcher.search(term)
                if results:
                    ahmia_results.extend(results)
            
            # Remove duplicates from Ahmia results
            unique_ahmia = []
            seen_ahmia = set()
            for result in ahmia_results:
                result_key = f"{result.get('title', '')}_{result.get('link', '')}"
                if result_key not in seen_ahmia:
                    seen_ahmia.add(result_key)
                    unique_ahmia.append(result)
            
            darkweb_results["ahmia_results"] = unique_ahmia
            
            # Search with OnionSearch (if API key is available)
            onion_results = []
            try:
                for term in search_terms[:3]:  # Limit to first 3 terms to avoid rate limiting
                    results = self.onion_searcher.search(term, pages=1)
                    if results:
                        onion_results.extend(results)
                
                # Remove duplicates from OnionSearch results
                unique_onion = []
                seen_onion = set()
                for result in onion_results:
                    if isinstance(result, dict):
                        result_key = f"{result.get('title', '')}_{result.get('url', '')}"
                        if result_key not in seen_onion:
                            seen_onion.add(result_key)
                            unique_onion.append(result)
                
                darkweb_results["onion_search_results"] = unique_onion
            except Exception as e:
                darkweb_results["onion_search_error"] = f"OnionSearch failed: {str(e)}"
            
            # Search with DarkFail for phone number mentions
            darkfail_results = []
            try:
                # Run DarkFail checker to get current darkweb site listings
                darkfail_data = self.darkfail_checker.run(
                    query=phone_number, 
                    save_json=None,  # Don't save JSON file
                    auto_verify_gpg=False, 
                    fetch_onion_via_tor=False
                )
                
                # Check if phone number appears in any darkfail context
                if "onions" in darkfail_data:
                    for onion_data in darkfail_data["onions"]:
                        context = onion_data.get("context", "").lower()
                        # Check if phone number appears in the context
                        phone_clean = phone_number.replace("+", "").replace(" ", "")
                        if phone_clean in context or phone_number in context:
                            darkfail_results.append({
                                "onion": onion_data["onion"],
                                "context": onion_data["context"],
                                "match_type": "context_mention"
                            })
                
                darkweb_results["darkfail_results"] = darkfail_results
                darkweb_results["darkfail_metadata"] = {
                    "total_onions_scanned": len(darkfail_data.get("onions", [])),
                    "phone_mentions_found": len(darkfail_results)
                }
                
            except Exception as e:
                darkweb_results["darkfail_error"] = f"DarkFail search failed: {str(e)}"
            
            # Calculate total results
            total_results = len(unique_ahmia) + len(unique_onion) + len(darkfail_results)
            darkweb_results["total_results"] = total_results
            
            # Add summary information
            darkweb_results["summary"] = {
                "ahmia_results_count": len(unique_ahmia),
                "onion_search_results_count": len(unique_onion),
                "darkfail_mentions_count": len(darkfail_results),
                "darkweb_mentions_found": total_results > 0,
                "risk_assessment": self._assess_darkweb_risk(unique_ahmia, unique_onion, darkfail_results)
            }
            
            return darkweb_results
            
        except Exception as e:
            return {"error": f"Darkweb search failed: {str(e)}"}
    
    def _assess_darkweb_risk(self, ahmia_results: List, onion_results: List, darkfail_results: List) -> Dict:
        """Assess risk level based on darkweb findings"""
        total_mentions = len(ahmia_results) + len(onion_results) + len(darkfail_results)
        
        risk_level = "LOW"
        if total_mentions == 0:
            risk_level = "NONE"
        elif total_mentions <= 2:
            risk_level = "LOW"
        elif total_mentions <= 5:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        # Check for high-risk keywords in results
        high_risk_keywords = ['leak', 'breach', 'hack', 'dump', 'database', 'password', 'credentials']
        medium_risk_keywords = ['contact', 'phone', 'number', 'telegram', 'signal']
        
        high_risk_count = 0
        medium_risk_count = 0
        
        # Check all results for risk keywords
        all_results = ahmia_results + onion_results
        for result in all_results:
            title = result.get('title', '').lower() + result.get('snippet', '').lower()
            for keyword in high_risk_keywords:
                if keyword in title:
                    high_risk_count += 1
                    break
            for keyword in medium_risk_keywords:
                if keyword in title:
                    medium_risk_count += 1
                    break
        
        # Adjust risk level based on keyword analysis
        if high_risk_count > 0:
            risk_level = "HIGH"
        elif medium_risk_count >= 2:
            risk_level = "MEDIUM"
        
        return {
            "risk_level": risk_level,
            "total_mentions": total_mentions,
            "high_risk_keywords_found": high_risk_count,
            "medium_risk_keywords_found": medium_risk_count,
            "explanation": self._get_risk_explanation(risk_level)
        }
    
    def _get_risk_explanation(self, risk_level: str) -> str:
        """Get explanation for risk level"""
        explanations = {
            "NONE": "No darkweb mentions found - low exposure risk",
            "LOW": "Minimal darkweb presence - typical for legitimate contact information",
            "MEDIUM": "Moderate darkweb presence - may indicate targeted exposure or data sharing",
            "HIGH": "Significant darkweb presence - potential data breach or malicious targeting"
        }
        return explanations.get(risk_level, "Unknown risk level")
    
    # In main_phone.py, update the _run_analysis_engine method:
    async def _run_analysis_engine(self, raw_data: Dict) -> Dict:
        """Run analysis engine on collected data"""
        try:
            analyzer = AnalysisEngine()
            # Use quick analysis to avoid async issues
            result = analyzer.quick_analysis(raw_data)
            return result
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _display_findings(self, module_name: str, findings: Dict):
        """Display findings from each module in a user-friendly format"""
        print(f"{Fore.GREEN}✅ {module_name} completed{Style.RESET_ALL}")
        
        if "error" in findings:
            print(f"{Fore.RED}   Error: {findings['error']}{Style.RESET_ALL}")
            return
        
        if module_name == "Phone Intelligence":
            if "summary" in findings:
                summary = findings["summary"]
                print(f"   {Fore.YELLOW}Valid:{Style.RESET_ALL} {summary.get('is_valid', 'Unknown')}")
                print(f"   {Fore.YELLOW}Carrier:{Style.RESET_ALL} {summary.get('carrier', 'Unknown')}")
                print(f"   {Fore.YELLOW}Location:{Style.RESET_ALL} {summary.get('location', 'Unknown')}")
                print(f"   {Fore.YELLOW}Type:{Style.RESET_ALL} {summary.get('number_type', 'Unknown')}")
        
        elif module_name == "Name Discovery":
            if "names_found" in findings:
                names_data = findings["names_found"]
                high_conf = names_data.get("high_confidence", [])
                if high_conf:
                    print(f"   {Fore.YELLOW}High confidence names:{Style.RESET_ALL}")
                    for name_data in high_conf[:3]:
                        print(f"     • {name_data['name']} ({name_data['confidence']:.0%})")
                else:
                    print(f"   {Fore.YELLOW}No high-confidence names found{Style.RESET_ALL}")
        
        elif module_name == "Email Discovery":
            if "emails" in findings:
                emails = findings["emails"]
                if emails:
                    print(f"   {Fore.YELLOW}Emails found:{Style.RESET_ALL} {len(emails)}")
                    for email in emails[:3]:
                        print(f"     • {email}")
                else:
                    print(f"   {Fore.YELLOW}No emails found{Style.RESET_ALL}")
        
        elif module_name == "Search Engine":
            total_results = 0
            for engine, data in findings.items():
                if isinstance(data, dict) and "results_count" in data:
                    total_results += data["results_count"]
            print(f"   {Fore.YELLOW}Total search results:{Style.RESET_ALL} {total_results}")
        
        elif module_name == "Breach Check":
            if "breach_results" in findings:
                breaches = findings["breach_results"]
                leaked_count = sum(1 for b in breaches if isinstance(b, dict) and b.get("status") == "leaked")
                print(f"   {Fore.YELLOW}Breach status:{Style.RESET_ALL} {leaked_count} breaches found")
        
        elif module_name == "Darkweb Search":
            if "summary" in findings:
                summary = findings["summary"]
                ahmia_count = summary.get("ahmia_results_count", 0)
                onion_count = summary.get("onion_search_results_count", 0)
                darkfail_count = summary.get("darkfail_mentions_count", 0)
                total = ahmia_count + onion_count + darkfail_count
                risk_assessment = summary.get("risk_assessment", {})
                
                print(f"   {Fore.YELLOW}Darkweb references found:{Style.RESET_ALL} {total}")
                print(f"   {Fore.YELLOW}Sources:{Style.RESET_ALL} Ahmia ({ahmia_count}), OnionSearch ({onion_count}), DarkFail ({darkfail_count})")
                print(f"   {Fore.YELLOW}Risk Level:{Style.RESET_ALL} {risk_assessment.get('risk_level', 'Unknown')}")
                
                # Show risk explanation
                risk_explanation = risk_assessment.get('explanation', '')
                if risk_explanation:
                    print(f"   {Fore.YELLOW}Risk Assessment:{Style.RESET_ALL} {risk_explanation}")
                
                # Show sample results from Ahmia
                if findings.get("ahmia_results"):
                    print(f"   {Fore.YELLOW}Sample Ahmia results:{Style.RESET_ALL}")
                    for result in findings["ahmia_results"][:2]:
                        title = result.get('title', 'No title')[:50] + "..." if len(result.get('title', '')) > 50 else result.get('title', 'No title')
                        print(f"     • {title}")
                        print(f"       {result.get('link', 'No link')}")
                
                # Show sample results from OnionSearch
                if findings.get("onion_search_results"):
                    print(f"   {Fore.YELLOW}Sample OnionSearch results:{Style.RESET_ALL}")
                    for result in findings["onion_search_results"][:2]:
                        title = result.get('title', 'No title')[:50] + "..." if len(result.get('title', '')) > 50 else result.get('title', 'No title')
                        print(f"     • {title}")
                        print(f"       {result.get('url', 'No URL')}")
                
                # Show DarkFail mentions if any
                if findings.get("darkfail_results"):
                    print(f"   {Fore.YELLOW}DarkFail mentions:{Style.RESET_ALL}")
                    for result in findings["darkfail_results"][:2]:
                        print(f"     • {result['onion']}")
                        context_preview = result['context'][:80] + "..." if len(result['context']) > 80 else result['context']
                        print(f"       Context: {context_preview}")
                
                print(f"   {Fore.GREEN}Note: Safe clearnet search - no Tor access required{Style.RESET_ALL}")
        
        elif module_name == "Analysis":
            if "executive_summary" in findings:
                summary = findings["executive_summary"]
                print(f"   {Fore.YELLOW}Risk level:{Style.RESET_ALL} {summary.get('risk_level', 'Unknown')}")
                print(f"   {Fore.YELLOW}Confidence:{Style.RESET_ALL} {summary.get('confidence_level', 'Unknown')}")
    
    def _extract_entities(self, raw_data: Dict) -> Dict:
        """
        Extract and standardize entities from raw module outputs
        """
        entities = {
            "phone_numbers": set(),
            "emails": set(),
            "usernames": set(),
            "names": set(),
            "locations": set(),
            "carriers": set(),
            "social_media": set(),
            "domains": set(),
            "breaches": set(),
            "darkweb_references": set(),
            "onion_sites": set(),
            "darkfail_mentions": set()
        }
        
        # Extract from phone intelligence
        if "phone_intelligence" in raw_data:
            data = raw_data["phone_intelligence"]
            if "summary" in data:
                summary = data["summary"]
                if summary.get("is_valid"):
                    entities["phone_numbers"].add(data.get("phone_number", ""))
                if summary.get("carrier") and summary["carrier"] != "Unknown":
                    entities["carriers"].add(summary["carrier"])
                if summary.get("location") and summary["location"] != "Unknown":
                    entities["locations"].add(summary["location"])
        
        # Extract from name discovery
        if "name_discovery" in raw_data:
            data = raw_data["name_discovery"]
            if "names_found" in data:
                names_data = data["names_found"]
                for confidence_level in ["high_confidence", "medium_confidence", "low_confidence"]:
                    for name_data in names_data.get(confidence_level, []):
                        if isinstance(name_data, dict) and "name" in name_data:
                            entities["names"].add(name_data["name"])
        
        # Extract from email discovery
        if "email_discovery" in raw_data:
            data = raw_data["email_discovery"]
            if "emails" in data:
                for email in data["emails"]:
                    if self.validator.is_valid_email(email):
                        entities["emails"].add(email)
        
        # Extract from breach check
        if "breach_check" in raw_data:
            data = raw_data["breach_check"]
            if "breach_results" in data:
                for breach in data["breach_results"]:
                    if isinstance(breach, dict) and breach.get("status") == "leaked":
                        entities["breaches"].add(breach.get("source", "Unknown"))
        
        # Extract from darkweb search
        if "darkweb_search" in raw_data:
            data = raw_data["darkweb_search"]
            
            # Extract from Ahmia results
            if "ahmia_results" in data:
                for result in data["ahmia_results"]:
                    if result.get("title"):
                        entities["darkweb_references"].add(result["title"])
                    if result.get("link"):
                        # Extract .onion domains
                        if ".onion" in result["link"]:
                            domain_match = re.search(r'https?://([^/]+)', result["link"])
                            if domain_match:
                                entities["onion_sites"].add(domain_match.group(1))
            
            # Extract from OnionSearch results
            if "onion_search_results" in data:
                for result in data["onion_search_results"]:
                    if isinstance(result, dict):
                        if result.get("title"):
                            entities["darkweb_references"].add(result["title"])
                        if result.get("url") and ".onion" in result["url"]:
                            domain_match = re.search(r'https?://([^/]+)', result["url"])
                            if domain_match:
                                entities["onion_sites"].add(domain_match.group(1))
            
            # Extract from DarkFail results
            if "darkfail_results" in data:
                for result in data["darkfail_results"]:
                    if result.get("onion"):
                        entities["onion_sites"].add(result["onion"])
                    if result.get("context"):
                        # Add context as darkfail mention
                        entities["darkfail_mentions"].add(result["context"][:100] + "..." if len(result["context"]) > 100 else result["context"])
        
        # Convert sets to lists for JSON serialization
        return {k: list(v) for k, v in entities.items() if v}
    
    def _build_relationships(self, entities: Dict) -> List[Dict]:
        """
        Build relationships between extracted entities
        """
        relationships = []
        phone = entities.get("phone_numbers", [None])[0] if entities.get("phone_numbers") else None
        
        if not phone:
            return relationships
        
        # Phone to names
        for name in entities.get("names", []):
            relationships.append({
                "source": phone,
                "target": name,
                "type": "name_association",
                "source_module": "NLPNameFinder"
            })
        
        # Phone to emails
        for email in entities.get("emails", []):
            relationships.append({
                "source": phone,
                "target": email,
                "type": "email_association", 
                "source_module": "EmailDiscovery"
            })
        
        # Phone to locations
        for location in entities.get("locations", []):
            relationships.append({
                "source": phone,
                "target": location,
                "type": "location_association",
                "source_module": "PhoneNumberIntelligence"
            })
        
        # Phone to darkweb references
        for ref in entities.get("darkweb_references", []):
            relationships.append({
                "source": phone,
                "target": ref[:100] + "..." if len(ref) > 100 else ref,
                "type": "darkweb_mention",
                "source_module": "DarkwebSearch"
            })
        
        # Phone to onion sites
        for onion in entities.get("onion_sites", []):
            relationships.append({
                "source": phone,
                "target": onion,
                "type": "onion_site_mention",
                "source_module": "DarkwebSearch"
            })
        
        # Phone to darkfail mentions
        for mention in entities.get("darkfail_mentions", []):
            relationships.append({
                "source": phone,
                "target": mention,
                "type": "darkfail_context_mention",
                "source_module": "DarkwebSearch"
            })
        
        return relationships
    
    async def conduct_research_with_output(self, phone_number: str, output_path: str, depth: int = 2) -> Dict:
        """
        Conduct research and save to specified output path
        
        Args:
            phone_number: Phone number to research
            output_path: Output base path (without extension)
            depth: Research depth
            
        Returns:
            Dictionary with save confirmation
        """
        research_data = await self.conduct_research(phone_number, depth)
        
        if "error" in research_data:
            return research_data
        
        # Generate file paths
        json_path = f"{output_path}.json"
        txt_path = f"{output_path}_summary.txt"
        
        # Save JSON report
        with open(json_path, 'w') as f:
            json.dump(research_data, f, indent=2)
        
        # Generate and save text summary
        summary = self._generate_text_summary(research_data)
        with open(txt_path, 'w') as f:
            f.write(summary)
        
        return {
            "success": True,
            "message": "Research completed and saved",
            "phone_number": phone_number,
            "json_output_path": json_path,
            "txt_summary_path": txt_path,
            "entity_count": sum(len(v) for v in research_data["entities"].values())
        }
    
    def _generate_text_summary(self, research_data: Dict) -> str:
        """Generate human-readable text summary"""
        summary = []
        summary.append("PHONE NUMBER RESEARCH REPORT")
        summary.append("=" * 50)
        summary.append(f"Phone: {research_data['meta']['input']}")
        summary.append(f"Processed: {research_data['meta']['end_time']}")
        summary.append(f"Duration: {research_data['meta']['processing_time']}")
        summary.append("")
        
        # Entities summary
        entities = research_data['entities']
        summary.append("ENTITIES FOUND:")
        summary.append("-" * 30)
        for entity_type, items in entities.items():
            if items:
                summary.append(f"{entity_type.replace('_', ' ').title()}: {len(items)}")
                for item in items[:3]:  # Show first 3 items
                    summary.append(f"  • {item}")
                if len(items) > 3:
                    summary.append(f"  ... and {len(items) - 3} more")
                summary.append("")
        
        # Relationships
        relationships = research_data['relationships']
        if relationships:
            summary.append("RELATIONSHIPS:")
            summary.append("-" * 30)
            for rel in relationships[:5]:  # Show first 5 relationships
                summary.append(f"  {rel['source']} -> {rel['target']} ({rel['type']})")
        
        return "\n".join(summary)

    def generate_spiderfoot_report(self, research_data: Dict) -> Dict:
        """
        Format research data into SpiderFoot-style report
        Compatible with AIGT.py expected format
        """
        if "error" in research_data:
            return research_data
        
        return {
            "meta": research_data["meta"],
            "results": {
                "raw_data": research_data["raw"],
                "entities": research_data["entities"],
                "relationships": research_data["relationships"]
            },
            "summary": {
                "input": research_data["meta"]["input"],
                "total_entities": sum(len(v) for v in research_data["entities"].values()),
                "entity_types": list(research_data["entities"].keys()),
                "total_relationships": len(research_data["relationships"]),
                "processing_time": research_data["meta"]["processing_time"]
            }
        }

# Required validator class
class OSINTValidator:
    def __init__(self):
        pass
    
    def is_valid_phone(self, phone_number: str) -> bool:
        """Validate phone number format"""
        pattern = r'^\+?[\d\s\-\(\)]{8,}\d$'
        return bool(re.match(pattern, phone_number))
    
    def is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

# Synchronous wrappers for AIGT integration
def sync_conduct_research(phone_number: str, depth: int = 2) -> Dict:
    """Synchronous wrapper for async research"""
    handler = PhoneResearchHandler()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(handler.conduct_research(phone_number, depth))
        return result
    finally:
        loop.close()

def sync_conduct_research_with_output(phone_number: str, output_path: str, depth: int = 2) -> Dict:
    """Synchronous wrapper for async research with output"""
    handler = PhoneResearchHandler()
    return asyncio.run(handler.conduct_research_with_output(phone_number, output_path, depth))

# Example usage and testing
if __name__ == "__main__":
    # Test the module
    handler = PhoneResearchHandler()
    
    # Test with a phone number
    test_phone = "+1234567890"  # Replace with actual test number
    
    print(f"Starting research for: {test_phone}")
    
    # Test without output path (terminal display only)
    research = asyncio.run(handler.conduct_research(test_phone, depth=2))
    
    # Test with output path
    result = asyncio.run(handler.conduct_research_with_output(test_phone, "test_output", 2))
    print(f"\nSave result: {result}")
