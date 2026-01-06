# analysis_engine.py - Complete fix with all required methods
import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime
import re

class AnalysisEngine:
    def __init__(self):
        self.correlation_sources = {
            "cross_referencing": [
                "entity-resolution", 
                "data-point-correlation",
                "confidence-scoring"
            ],
            "timeline_construction": [
                "chronological-analysis",
                "event-sequencing", 
                "pattern-timeline"
            ],
            "relationship_mapping": [
                "network-graph-construction",
                "connection-analysis",
                "influence-mapping"
            ],
            "pattern_recognition": [
                "behavioral-analysis",
                "anomaly-detection",
                "trend-identification"
            ]
        }
    
    async def comprehensive_correlation_analysis(self, all_module_results: Dict) -> Dict:
        """Complete correlation and analysis of all OSINT data"""
        
        # Use await for async operations
        cross_referencing = await self._cross_reference_data(all_module_results)
        timeline_construction = await self._construct_timeline(all_module_results)
        relationship_mapping = await self._map_relationships(all_module_results)
        pattern_recognition = await self._recognize_patterns(all_module_results)
        
        # Generate final intelligence report
        intelligence_report = self._generate_intelligence_report(
            all_module_results, cross_referencing, timeline_construction,
            relationship_mapping, pattern_recognition
        )
        
        return intelligence_report
    
    def quick_analysis(self, all_module_results: Dict) -> Dict:
        """Quick synchronous analysis without complex async operations"""
        try:
            # Extract basic entities
            entities = self._extract_entities(all_module_results)
            
            # Generate simple report
            report = {
                "report_id": f"QUICK_ANALYSIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "subject_phone": all_module_results.get("phone_intelligence", {}).get("phone_number", ""),
                "executive_summary": self._quick_summary(all_module_results, entities),
                "entities_found": {k: len(v) for k, v in entities.items()},
                "risk_assessment": self._quick_risk_assessment(all_module_results),
                "total_entities": sum(len(v) for v in entities.values()),
                "detailed_entities": entities
            }
            
            return report
        except Exception as e:
            return {"error": f"Quick analysis failed: {str(e)}"}

    def _extract_entities(self, all_results: Dict) -> Dict:
        """Extract entities from all module results"""
        entities = {
            "names": set(),
            "emails": set(),
            "locations": set(),
            "usernames": set(),
            "phone_numbers": set(),
            "businesses": set(),
            "social_media": set(),
            "carriers": set(),
            "breaches": set(),
            "darkweb_references": set()
        }
        
        # Extract from phone intelligence
        if "phone_intelligence" in all_results:
            phone_data = all_results["phone_intelligence"]
            if "summary" in phone_data:
                summary = phone_data["summary"]
                entities["phone_numbers"].add(phone_data.get("phone_number", ""))
                if summary.get("carrier") and summary["carrier"] != "Unknown":
                    entities["carriers"].add(summary["carrier"])
                if summary.get("location") and summary["location"] != "Unknown":
                    entities["locations"].add(summary["location"])
        
        # Extract from name discovery
        if "name_discovery" in all_results:
            name_data = all_results["name_discovery"]
            if "names_found" in name_data:
                names_found = name_data["names_found"]
                for confidence_level in ["high_confidence", "medium_confidence", "low_confidence", "all_names"]:
                    if confidence_level in names_found:
                        for name_item in names_found[confidence_level]:
                            if isinstance(name_item, dict) and "name" in name_item:
                                entities["names"].add(name_item["name"])
        
        # Extract from email discovery
        if "email_discovery" in all_results:
            email_data = all_results["email_discovery"]
            if "emails" in email_data:
                for email in email_data["emails"]:
                    if self._is_valid_email(email):
                        entities["emails"].add(email)
        
        # Extract from breach check
        if "breach_check" in all_results:
            breach_data = all_results["breach_check"]
            if "breach_results" in breach_data:
                for breach in breach_data["breach_results"]:
                    if isinstance(breach, dict) and breach.get("status") == "leaked":
                        entities["breaches"].add(breach.get("source", "Unknown"))
        
        # Extract from darkweb search
        if "darkweb_search" in all_results:
            darkweb_data = all_results["darkweb_search"]
            if "ahmia_results" in darkweb_data:
                for result in darkweb_data["ahmia_results"]:
                    if result.get("title"):
                        entities["darkweb_references"].add(result["title"][:100])
        
        # Convert sets to lists
        return {k: list(v) for k, v in entities.items() if v}
    
    def _is_valid_email(self, email: str) -> bool:
        """Basic email validation"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))
    
    def _quick_summary(self, all_results: Dict, entities: Dict) -> Dict:
        """Generate quick summary"""
        phone_data = all_results.get("phone_intelligence", {})
        summary_data = phone_data.get("summary", {})
        
        # Calculate confidence based on data found
        confidence_factors = 0
        if summary_data.get("is_valid"):
            confidence_factors += 1
        if entities.get("names"):
            confidence_factors += 1
        if entities.get("emails"):
            confidence_factors += 1
        if entities.get("locations"):
            confidence_factors += 1
        
        confidence_levels = {0: "Low", 1: "Low", 2: "Medium", 3: "High", 4: "Very High"}
        confidence = confidence_levels.get(confidence_factors, "Low")
        
        return {
            "phone_valid": summary_data.get("is_valid", False),
            "carrier": summary_data.get("carrier", "Unknown"),
            "location": summary_data.get("location", "Unknown"),
            "number_type": summary_data.get("number_type", "Unknown"),
            "names_found": len(entities.get("names", [])),
            "emails_found": len(entities.get("emails", [])),
            "breaches_found": len(entities.get("breaches", [])),
            "darkweb_mentions": len(entities.get("darkweb_references", [])),
            "confidence": confidence,
            "data_quality": "Good" if confidence_factors >= 2 else "Limited"
        }
    
    def _quick_risk_assessment(self, all_results: Dict) -> Dict:
        """Quick risk assessment"""
        risk_level = "Low"
        risk_factors = []
        
        # Check darkweb results
        darkweb_data = all_results.get("darkweb_search", {})
        darkweb_summary = darkweb_data.get("summary", {})
        darkweb_risk = darkweb_summary.get("risk_assessment", {})
        
        if darkweb_risk.get("risk_level") == "HIGH":
            risk_level = "High"
            risk_factors.append("High darkweb exposure")
        elif darkweb_risk.get("risk_level") == "MEDIUM":
            risk_level = "Medium"
            risk_factors.append("Medium darkweb exposure")
        
        # Check breach results  
        breach_data = all_results.get("breach_check", {})
        if breach_data.get("breach_results"):
            for breach in breach_data["breach_results"]:
                if isinstance(breach, dict) and breach.get("status") == "leaked":
                    risk_level = "Medium" if risk_level == "Low" else "High"
                    risk_factors.append(f"Breach detected: {breach.get('source')}")
                    break
        
        # Check phone type
        phone_data = all_results.get("phone_intelligence", {})
        phone_summary = phone_data.get("summary", {})
        if phone_summary.get("number_type") in ["VOIP", "PREMIUM_RATE"]:
            risk_factors.append(f"Suspicious phone type: {phone_summary.get('number_type')}")
            risk_level = "Medium" if risk_level == "Low" else risk_level
        
        if not risk_factors:
            risk_factors.append("No significant risk factors detected")
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "factors_considered": ["darkweb_mentions", "breach_status", "phone_type"],
            "recommendation": self._get_risk_recommendation(risk_level)
        }
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            "Low": "Normal phone number - low risk profile",
            "Medium": "Exercise caution - further verification recommended", 
            "High": "High risk - avoid interaction and conduct thorough investigation"
        }
        return recommendations.get(risk_level, "Unknown risk level")

    # Keep the original methods for compatibility (they can remain empty for now)
    async def _cross_reference_data(self, all_results: Dict) -> Dict:
        return {"source": "cross-referencing", "status": "simplified"}
    
    async def _construct_timeline(self, all_results: Dict) -> Dict:
        return {"source": "timeline-construction", "status": "simplified"}
    
    async def _map_relationships(self, all_results: Dict) -> Dict:
        return {"source": "relationship-mapping", "status": "simplified"}
    
    async def _recognize_patterns(self, all_results: Dict) -> Dict:
        return {"source": "pattern-recognition", "status": "simplified"}
    
    def _generate_intelligence_report(self, all_results: Dict, cross_referencing: Dict,
                                   timeline_construction: Dict, relationship_mapping: Dict,
                                   pattern_recognition: Dict) -> Dict:
        return {"report_type": "comprehensive", "status": "simplified"}

# Update the sync wrapper function
def analyze_correlations(all_module_results: Dict) -> Dict:
    """Synchronous wrapper for correlation analysis"""
    analyzer = AnalysisEngine()
    
    # Use quick analysis to avoid async issues
    try:
        return analyzer.quick_analysis(all_module_results)
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}