# main_ip_sequential.py - SEQUENTIAL VERSION WITH PROGRESS DISPLAY
import json
import os
import time
from datetime import datetime
from typing import Dict, List
from .ip.ip_geolocation import IPGeolocation
from .ip.ip_whois_asn import WHOISASN
from .ip.ip_threatintel import ThreatIntelligence
from .ip.ip_ssl_cert import SSLAnalyzer
from .ip.ip_dns_intel import DNSIntelligence
from .ip.ip_cloud_cdn import CDNCloudDetector
from .ip.darkweb_search import ahmia_search


class IPResearchHandler:
    def __init__(self):
        """
        Initialize all IP intelligence modules for sequential execution
        """
        self.geo = IPGeolocation()
        self.whois = WHOISASN()
        self.threat = ThreatIntelligence()
        self.ssl = SSLAnalyzer()
        self.dns = DNSIntelligence()
        self.cdn = CDNCloudDetector()
        
        # Module execution order - optimized for dependencies
        self.modules_order = [
            ("Geolocation & Basic Info", self._run_geolocation),
            ("WHOIS & ASN Lookup", self._run_whois_asn),
            ("DNS Intelligence", self._run_dns_intel),
            ("SSL Certificate Analysis", self._run_ssl_analysis),
            ("CDN & Cloud Detection", self._run_cdn_detection),
            ("Threat Intelligence", self._run_threat_intel),
            ("Dark Web Search", self._run_darkweb_search)
        ]

    def validate_ip(self, ip_address: str) -> bool:
        """Validate IP address format"""
        try:
            parts = ip_address.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not part.isdigit() or not 0 <= int(part) <= 255:
                    return False
            return True
        except:
            return False

    def conduct_comprehensive_research(self, ip_address: str) -> Dict:
        """
        Conduct comprehensive IP research sequentially with progress display
        
        Args:
            ip_address: IP address to research
            
        Returns:
            Dictionary containing complete research results
        """
        if not self.validate_ip(ip_address):
            return {
                "error": "Invalid IP address format",
                "input": ip_address,
                "timestamp": datetime.now().isoformat()
            }
        
        start_time = datetime.now()
        results = {
            "meta": {
                "input": ip_address,
                "start_time": start_time.isoformat(),
                "modules": [name for name, _ in self.modules_order],
                "execution_type": "sequential"
            },
            "geolocation": {},
            "whois_asn": {},
            "dns_intelligence": {},
            "ssl_analysis": {},
            "cdn_detection": {},
            "threat_intelligence": {},
            "darkweb_search": {},
            "entities": {},
            "relationships": []
        }
        
        print(f"\n🔍 Starting comprehensive IP research for: {ip_address}")
        print("=" * 60)
        
        try:
            # Execute modules sequentially
            for module_name, module_func in self.modules_order:
                print(f"\n[{len(results['entities'])+1}/{len(self.modules_order)}] Running {module_name}...")
                
                start_module = time.time()
                module_results = module_func(ip_address)
                module_time = time.time() - start_module
                
                # Store results in appropriate section
                if module_name == "Geolocation & Basic Info":
                    results["geolocation"] = module_results
                elif module_name == "WHOIS & ASN Lookup":
                    results["whois_asn"] = module_results
                elif module_name == "DNS Intelligence":
                    results["dns_intelligence"] = module_results
                elif module_name == "SSL Certificate Analysis":
                    results["ssl_analysis"] = module_results
                elif module_name == "CDN & Cloud Detection":
                    results["cdn_detection"] = module_results
                elif module_name == "Threat Intelligence":
                    results["threat_intelligence"] = module_results
                elif module_name == "Dark Web Search":
                    results["darkweb_search"] = module_results
                
                # Display immediate findings
                self._display_module_findings(module_name, module_results, module_time)
                
                # Update entities after each module
                results["entities"] = self._extract_entities(results)
            
            # Build relationships after all data is collected
            results["relationships"] = self._build_relationships(results["entities"])
            
            print(f"\n✅ Research completed successfully!")
            
        except Exception as e:
            error_msg = f"Research failed: {str(e)}"
            print(f"❌ {error_msg}")
            results["error"] = error_msg
        
        # Add final metadata
        results["meta"]["end_time"] = datetime.now().isoformat()
        results["meta"]["processing_time"] = str(datetime.now() - start_time)
        results["meta"]["entity_counts"] = {
            k: len(v) for k, v in results["entities"].items()
        }
        
        return results

    def _run_geolocation(self, ip_address: str) -> Dict:
        """Run geolocation analysis"""
        try:
            geo_data = self.geo.get_comprehensive_geo(ip_address)
            return {
                "sources": list(geo_data.keys()),
                "data": geo_data,
                "summary": self._summarize_geolocation(geo_data)
            }
        except Exception as e:
            return {"error": str(e), "summary": "Geolocation failed"}

    def _run_whois_asn(self, ip_address: str) -> Dict:
        """Run WHOIS and ASN lookup"""
        try:
            whois_data = self.whois.get_comprehensive_whois(ip_address)
            return {
                "sources": list(whois_data.keys()),
                "data": whois_data,
                "summary": self._summarize_whois(whois_data)
            }
        except Exception as e:
            return {"error": str(e), "summary": "WHOIS/ASN lookup failed"}

    def _run_dns_intel(self, ip_address: str) -> Dict:
        """Run DNS intelligence gathering"""
        try:
            # Get reverse DNS first
            reverse_dns = self.dns.get_reverse_dns(ip_address)
            
            # Get DNS records for discovered domains
            domain_records = {}
            if reverse_dns:
                for domain in reverse_dns[:2]:  # Limit to first 2 domains
                    # Extract clean domain name from PTR record
                    clean_domain = domain.rstrip('.')
                    if clean_domain:
                        records = self.dns.get_all_dns_records(clean_domain)
                        domain_records[clean_domain] = records
            
            dns_data = {
                "reverse_dns": reverse_dns,
                "domain_records": domain_records
            }
            
            return {
                "data": dns_data,
                "summary": self._summarize_dns(dns_data)
            }
        except Exception as e:
            return {"error": str(e), "summary": "DNS intelligence failed"}

    def _run_ssl_analysis(self, ip_address: str) -> Dict:
        """Run SSL certificate analysis"""
        try:
            # Try common SSL ports
            ssl_data = {}
            for port in [443, 8443]:
                try:
                    cert_info = self.ssl.get_certificate_info(ip_address, port)
                    if cert_info and 'error' not in cert_info:
                        ssl_data[f"port_{port}"] = cert_info
                        break
                except:
                    continue
            
            if not ssl_data:
                ssl_data = {"error": "No SSL certificates found on common ports"}
            
            return {
                "data": ssl_data,
                "summary": self._summarize_ssl(ssl_data)
            }
        except Exception as e:
            return {"error": str(e), "summary": "SSL analysis failed"}

    def _run_cdn_detection(self, ip_address: str) -> Dict:
        """Run CDN and cloud detection"""
        try:
            # Get domains from previous results to help CDN detection
            domains = []
            if hasattr(self, '_last_reverse_dns'):
                domains = self._last_reverse_dns[:1]  # Use first domain if available
            
            cdn_data = self.cdn.detect_comprehensive_cloud(ip_address, domains[0] if domains else None)
            
            return {
                "data": cdn_data,
                "summary": self._summarize_cdn(cdn_data)
            }
        except Exception as e:
            return {"error": str(e), "summary": "CDN detection failed"}

    def _run_threat_intel(self, ip_address: str) -> Dict:
        """Run threat intelligence gathering"""
        try:
            threat_data = self.threat.get_comprehensive_threats(ip_address)
            
            return {
                "sources": list(threat_data.keys()),
                "data": threat_data,
                "summary": self._summarize_threat(threat_data)
            }
        except Exception as e:
            return {"error": str(e), "summary": "Threat intelligence failed"}

    def _run_darkweb_search(self, ip_address: str) -> Dict:
        """Run dark web search"""
        try:
            darkweb_results = ahmia_search(ip_address)
            
            return {
                "results": darkweb_results or [],
                "summary": self._summarize_darkweb(darkweb_results)
            }
        except Exception as e:
            return {"error": str(e), "summary": "Dark web search failed"}

    def _display_module_findings(self, module_name: str, results: Dict, execution_time: float):
        """Display immediate findings from each module"""
        summary = results.get('summary', 'No summary available')
        
        print(f"   ⏱️  Time: {execution_time:.2f}s")
        print(f"   📊 Findings: {summary}")
        
        # Show key data points for important modules
        if module_name == "Geolocation & Basic Info" and 'data' in results:
            geo_data = results['data']
            for source, data in geo_data.items():
                if data and isinstance(data, dict):
                    location = data.get('country') or data.get('city')
                    if location:
                        print(f"   📍 Location: {location}")
                        break
        
        elif module_name == "WHOIS & ASN Lookup" and 'data' in results:
            whois_data = results['data']
            asn_info = whois_data.get('ip_whois', {}).get('asn_description') or whois_data.get('team_cymru', {}).get('asn')
            if asn_info:
                print(f"   🏢 ASN/Org: {asn_info}")
        
        elif module_name == "Threat Intelligence" and 'data' in results:
            threat_data = results['data']
            vt_malicious = threat_data.get('virustotal', {}).get('malicious', 0)
            if vt_malicious > 0:
                print(f"   ⚠️  VirusTotal: {vt_malicious} malicious detection(s)")

    # Summary methods for each module type
    def _summarize_geolocation(self, geo_data: Dict) -> str:
        locations = []
        for source, data in geo_data.items():
            if data and isinstance(data, dict):
                loc_parts = []
                if data.get('city'):
                    loc_parts.append(data['city'])
                if data.get('country'):
                    loc_parts.append(data['country'])
                if loc_parts:
                    locations.append(f"{source}: {', '.join(loc_parts)}")
        
        return f"Located in {', '.join(locations)}" if locations else "Location unknown"

    def _summarize_whois(self, whois_data: Dict) -> str:
        asn_info = whois_data.get('ip_whois', {}).get('asn_description') or whois_data.get('team_cymru', {}).get('asn')
        network = whois_data.get('ip_whois', {}).get('network')
        
        parts = []
        if asn_info:
            parts.append(f"ASN: {asn_info}")
        if network:
            parts.append(f"Network: {network}")
        
        return ', '.join(parts) if parts else "No WHOIS data found"

    def _summarize_dns(self, dns_data: Dict) -> str:
        reverse_dns = dns_data.get('reverse_dns', [])
        domain_count = len(dns_data.get('domain_records', {}))
        
        if reverse_dns:
            return f"{len(reverse_dns)} reverse DNS records, {domain_count} domains analyzed"
        return "No reverse DNS records found"

    def _summarize_ssl(self, ssl_data: Dict) -> str:
        for port, cert in ssl_data.items():
            if cert and 'subject' in cert:
                subject = cert['subject'].get('CN', 'Unknown')
                return f"SSL certificate found: {subject}"
        return "No SSL certificates found"

    def _summarize_cdn(self, cdn_data: Dict) -> str:
        providers = []
        ip_check = cdn_data.get('ip_range_check', {}).get('detected_providers', [])
        if ip_check:
            providers.extend(ip_check)
        
        if providers:
            return f"Detected CDN/Cloud: {', '.join(providers)}"
        return "No CDN/cloud provider detected"

    def _summarize_threat(self, threat_data: Dict) -> str:
        threats = []
        vt_malicious = threat_data.get('virustotal', {}).get('malicious', 0)
        if vt_malicious > 0:
            threats.append(f"VT: {vt_malicious} malicious")
        
        otx_pulses = threat_data.get('alienvault_otx', {}).get('pulse_count', 0)
        if otx_pulses > 0:
            threats.append(f"OTX: {otx_pulses} pulses")
        
        return ', '.join(threats) if threats else "No known threats detected"

    def _summarize_darkweb(self, darkweb_data: List) -> str:
        if darkweb_data:
            return f"Found {len(darkweb_data)} dark web mentions"
        return "No dark web mentions found"

    def _extract_entities(self, research_data: Dict) -> Dict:
        """Extract entities from research data"""
        entities = {
            "ip_addresses": set(),
            "asns": set(),
            "networks": set(),
            "organizations": set(),
            "locations": set(),
            "domains": set(),
            "threats": set(),
            "cdn_providers": set()
        }

        # Extract from geolocation
        geo = research_data.get("geolocation", {}).get("data", {})
        for source, data in geo.items():
            if data and isinstance(data, dict):
                if data.get('country'):
                    entities["locations"].add(data['country'])
                if data.get('city'):
                    entities["locations"].add(data['city'])
                if data.get('isp'):
                    entities["organizations"].add(data['isp'])
                if data.get('asn'):
                    entities["asns"].add(data['asn'])

        # Extract from WHOIS/ASN
        whois_data = research_data.get("whois_asn", {}).get("data", {})
        if whois_data.get('ip_whois', {}).get('asn'):
            entities["asns"].add(whois_data['ip_whois']['asn'])
        if whois_data.get('ip_whois', {}).get('network'):
            entities["networks"].add(whois_data['ip_whois']['network'])
        if whois_data.get('ip_whois', {}).get('asn_description'):
            entities["organizations"].add(whois_data['ip_whois']['asn_description'])

        # Extract from DNS
        dns_data = research_data.get("dns_intelligence", {}).get("data", {})
        entities["domains"].update(dns_data.get("reverse_dns", []))

        # Extract from CDN detection
        cdn_data = research_data.get("cdn_detection", {}).get("data", {})
        providers = cdn_data.get('ip_range_check', {}).get('detected_providers', [])
        entities["cdn_providers"].update(providers)

        # Extract from threat intelligence
        threat_data = research_data.get("threat_intelligence", {}).get("data", {})
        if threat_data.get('virustotal', {}).get('malicious', 0) > 0:
            entities["threats"].add("virustotal_malicious")
        if threat_data.get('alienvault_otx', {}).get('pulse_count', 0) > 0:
            entities["threats"].add("alienvault_pulses")

        # Add main IP address
        entities["ip_addresses"].add(research_data["meta"]["input"])

        return {k: list(v) for k, v in entities.items() if v}

    def _build_relationships(self, entities: Dict) -> List[Dict]:
        """Build relationships between entities"""
        relationships = []
        ip_addr = entities.get("ip_addresses", [None])[0]

        if not ip_addr:
            return relationships

        # IP to Location relationships
        for location in entities.get("locations", []):
            relationships.append({
                "source": ip_addr,
                "target": location,
                "type": "geolocation",
                "source_module": "IPGeolocation"
            })

        # IP to ASN relationships
        for asn in entities.get("asns", []):
            relationships.append({
                "source": ip_addr,
                "target": f"AS{asn}",
                "type": "asn_assignment",
                "source_module": "WHOISASN"
            })

        # IP to Domain relationships
        for domain in entities.get("domains", []):
            relationships.append({
                "source": ip_addr,
                "target": domain,
                "type": "reverse_dns",
                "source_module": "DNSIntelligence"
            })

        # IP to CDN relationships
        for cdn in entities.get("cdn_providers", []):
            relationships.append({
                "source": ip_addr,
                "target": cdn,
                "type": "cdn_provider",
                "source_module": "CDNCloudDetector"
            })

        return relationships

    def generate_comprehensive_report(self, research_data: Dict) -> str:
        """Generate human-readable report"""
        if "error" in research_data:
            return f"Error: {research_data['error']}"

        report = []
        report.append("=" * 80)
        report.append(f"SEQUENTIAL IP RESEARCH REPORT")
        report.append("=" * 80)
        report.append(f"Target: {research_data['meta']['input']}")
        report.append(f"Generated: {research_data['meta']['end_time']}")
        report.append(f"Processing Time: {research_data['meta']['processing_time']}")
        report.append("=" * 80)

        # Module results
        modules = [
            ("Geolocation", research_data.get("geolocation", {})),
            ("WHOIS & ASN", research_data.get("whois_asn", {})),
            ("DNS Intelligence", research_data.get("dns_intelligence", {})),
            ("SSL Analysis", research_data.get("ssl_analysis", {})),
            ("CDN Detection", research_data.get("cdn_detection", {})),
            ("Threat Intelligence", research_data.get("threat_intelligence", {})),
            ("Dark Web Search", research_data.get("darkweb_search", {}))
        ]

        for name, data in modules:
            report.append(f"\n{name.upper()}")
            report.append("-" * 40)
            summary = data.get('summary', 'No data')
            report.append(f"Summary: {summary}")
            if data.get('error'):
                report.append(f"Error: {data['error']}")

        # Entity summary
        report.append("\nENTITY SUMMARY")
        report.append("-" * 40)
        for entity_type, items in research_data.get("entities", {}).items():
            if items:
                report.append(f"{entity_type.replace('_', ' ').title()}: {len(items)}")

        report.append("\n" + "=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)

        return "\n".join(report)

    def conduct_research_with_output(self, ip_address: str, output_path: str, depth: int = 1) -> Dict:
        """Conduct research and save results to files"""
        research_data = self.conduct_comprehensive_research(ip_address)
        
        if "error" in research_data:
            return research_data
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # Save JSON report
        json_path = f"{output_path}.json"
        with open(json_path, 'w') as f:
            json.dump(research_data, f, indent=2)
        
        # Generate and save text report
        txt_path = f"{output_path}_report.txt"
        text_report = self.generate_comprehensive_report(research_data)
        with open(txt_path, 'w') as f:
            f.write(text_report)
        
        return {
            "success": True,
            "message": "IP research completed and saved",
            "ip_address": ip_address,
            "json_output_path": os.path.abspath(json_path),
            "txt_report_path": os.path.abspath(txt_path),
            "entity_count": sum(len(v) for v in research_data["entities"].values())
        }


# Example usage
if __name__ == "__main__":
    handler = IPResearchHandler()
    
    # Test with Google DNS
    target_ip = "8.8.8.8"
    
    print("🧪 Testing Sequential IP Research Handler")
    print("=" * 50)
    
    research_data = handler.conduct_comprehensive_research(target_ip)
    
    # Generate and print report
    report = handler.generate_comprehensive_report(research_data)
    print(report)
    
    # Save results
    result = handler.conduct_research_with_output(target_ip, "test_ip_research")
    print(f"\nSaved results: {result}")