import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
import asyncio
import aiohttp
from typing import Dict, List
import re
from datetime import datetime

class PhoneNumberIntelligence:
    def __init__(self):
        self.free_sources = {
            "local_parsing": [
                "phonenumbers-library",  # Python library
                "manual-validation"
            ],
            "api_services": [
                "numverify-free",
                "abstractapi-free", 
                "veriphone-free"
            ],
            "web_scraping": [
                "phoneinfoga-free",
                "national-cell-directory",
                "phonebook-cz"
            ],
            "carrier_analysis": [
                "advanced-analysis"
            ]
        }
        
        # Free API endpoints (no keys required or free tiers)
        self.apis = {
            "numverify": "http://apilayer.net/api/validate?access_key=free&number={phone}",
            "abstractapi": "https://phonevalidation.abstractapi.com/v1/?api_key=free&phone={phone}",
            "veriphone": "https://api.veriphone.io/v2/verify?phone={phone}"
        }
    
    async def comprehensive_phone_analysis(self, phone_number: str) -> Dict:
        """Complete phone number intelligence gathering"""
        
        # Run all free methods
        local_parsing = self._local_phone_parsing(phone_number)
        api_validation_task = self._api_validation_checks(phone_number)
        web_scraping_task = self._web_scraping_checks(phone_number)
        carrier_analysis = self._carrier_geolocation_analysis(phone_number)
        
        # Wait for async tasks
        api_results, web_results = await asyncio.gather(
            api_validation_task, 
            web_scraping_task,
            return_exceptions=True
        )
        
        results = [local_parsing, api_results, web_results, carrier_analysis]
        
        return self._consolidate_results(phone_number, results)
    
    def _local_phone_parsing(self, phone_number: str) -> Dict:
        """Free local parsing using phonenumbers library"""
        try:
            parsed = phonenumbers.parse(phone_number, None)
            
            return {
                "source": "phonenumbers-library",
                "valid": phonenumbers.is_valid_number(parsed),
                "format_e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
                "format_international": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                "format_national": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
                "country_code": parsed.country_code,
                "carrier": carrier.name_for_number(parsed, "en") or "Unknown",
                "region": geocoder.description_for_number(parsed, "en") or "Unknown",
                "timezones": timezone.time_zones_for_number(parsed) or ["Unknown"],
                "number_type": self._get_number_type(parsed),
                "is_possible": phonenumbers.is_possible_number(parsed)
            }
        except Exception as e:
            return {"error": f"Local parsing failed: {str(e)}"}
    
    async def _api_validation_checks(self, phone_number: str) -> Dict:
        """Free API validation services"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # NumVerify (free tier)
            tasks.append(self._call_api(session, "numverify", phone_number))
            
            # AbstractAPI (free tier)
            tasks.append(self._call_api(session, "abstractapi", phone_number))
            
            # VeriPhone (free tier)
            tasks.append(self._call_api(session, "veriphone", phone_number))
            
            api_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                "source": "free-apis",
                "numverify": api_results[0] if not isinstance(api_results[0], Exception) else {"error": str(api_results[0])},
                "abstractapi": api_results[1] if not isinstance(api_results[1], Exception) else {"error": str(api_results[1])},
                "veriphone": api_results[2] if not isinstance(api_results[2], Exception) else {"error": str(api_results[2])}
            }
    
    async def _call_api(self, session: aiohttp.ClientSession, api_name: str, phone: str) -> Dict:
        """Make API call to free validation service"""
        try:
            url = self.apis[api_name].format(phone=phone)
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def _web_scraping_checks(self, phone_number: str) -> Dict:
        """Free web scraping from public directories"""
        try:
            # Simulate web scraping results
            await asyncio.sleep(0.1)  # Simulate some async work
            return {
                "source": "web-scraping",
                "phoneinfoga": {"available": False, "note": "Service simulation"},
                "national_directory": {"listed": False, "note": "Web scraping simulation"},
                "phonebook_cz": {"listed": False, "note": "International directory simulation"}
            }
        except Exception as e:
            return {"error": f"Web scraping failed: {str(e)}"}
    
    def _carrier_geolocation_analysis(self, phone_number: str) -> Dict:
        """Advanced carrier and geolocation analysis"""
        try:
            parsed = phonenumbers.parse(phone_number, None)
            
            # Carrier detection
            carrier_name = carrier.name_for_number(parsed, "en") or "Unknown"
            
            # Geolocation data
            region = geocoder.description_for_number(parsed, "en") or "Unknown"
            
            # Timezone analysis
            timezones = timezone.time_zones_for_number(parsed) or ["Unknown"]
            
            # Number type analysis
            number_type = self._get_number_type(parsed)
            
            return {
                "source": "advanced-analysis",
                "carrier": carrier_name,
                "region": region,
                "timezones": timezones,
                "number_type": number_type,
                "country_code": parsed.country_code,
                "national_number": parsed.national_number,
                "is_mobile": number_type == "MOBILE"
            }
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _get_number_type(self, parsed_number) -> str:
        """Determine phone number type"""
        from phonenumbers import PhoneNumberType
        
        type_map = {
            PhoneNumberType.MOBILE: "MOBILE",
            PhoneNumberType.FIXED_LINE: "LANDLINE", 
            PhoneNumberType.FIXED_LINE_OR_MOBILE: "FIXED_OR_MOBILE",
            PhoneNumberType.TOLL_FREE: "TOLL_FREE",
            PhoneNumberType.PREMIUM_RATE: "PREMIUM_RATE",
            PhoneNumberType.SHARED_COST: "SHARED_COST",
            PhoneNumberType.VOIP: "VOIP",
            PhoneNumberType.PERSONAL_NUMBER: "PERSONAL_NUMBER",
            PhoneNumberType.PAGER: "PAGER",
            PhoneNumberType.UAN: "UAN",
            PhoneNumberType.VOICEMAIL: "VOICEMAIL",
            PhoneNumberType.UNKNOWN: "UNKNOWN"
        }
        
        return type_map.get(phonenumbers.number_type(parsed_number), "UNKNOWN")
    
    def _consolidate_results(self, phone_number: str, results: List) -> Dict:
        """Consolidate all intelligence into final report"""
        consolidated = {
            "phone_number": phone_number,
            "timestamp": datetime.now().isoformat(),
            "sources_used": list(self.free_sources.keys()),
            "summary": {},
            "detailed_results": {}
        }
        
        # Define source mapping for each result type
        source_mapping = [
            "local_parsing",
            "api_services", 
            "web_scraping",
            "carrier_analysis"
        ]
        
        # Process each result type
        for i, result in enumerate(results):
            if isinstance(result, dict) and "error" not in result:
                source_key = source_mapping[i]
                consolidated["detailed_results"][source_key] = result
        
        # Create summary
        consolidated["summary"] = self._generate_summary(consolidated["detailed_results"])
        
        return consolidated
    
    def _generate_summary(self, detailed_results: Dict) -> Dict:
        """Generate executive summary"""
        summary = {
            "is_valid": False,
            "carrier": "Unknown",
            "location": "Unknown", 
            "number_type": "Unknown",
            "confidence_score": 0,
            "risk_assessment": "Unknown"
        }
        
        # Extract best available data from multiple sources
        if "local_parsing" in detailed_results:
            local = detailed_results["local_parsing"]
            summary["is_valid"] = local.get("valid", False)
            summary["carrier"] = local.get("carrier", "Unknown")
            summary["location"] = local.get("region", "Unknown")
            summary["number_type"] = local.get("number_type", "Unknown")
        
        # Also check carrier_analysis for additional data
        if "carrier_analysis" in detailed_results:
            carrier_data = detailed_results["carrier_analysis"]
            if summary["carrier"] == "Unknown":
                summary["carrier"] = carrier_data.get("carrier", "Unknown")
            if summary["location"] == "Unknown":
                summary["location"] = carrier_data.get("region", "Unknown")
            if summary["number_type"] == "Unknown":
                summary["number_type"] = carrier_data.get("number_type", "Unknown")
        
        # Calculate confidence score
        confidence_factors = []
        if summary["is_valid"]:
            confidence_factors.append(0.3)
        if summary["carrier"] != "Unknown":
            confidence_factors.append(0.3)
        if summary["location"] != "Unknown":
            confidence_factors.append(0.2)
        if summary["number_type"] != "Unknown":
            confidence_factors.append(0.2)
            
        summary["confidence_score"] = sum(confidence_factors)
        
        # Risk assessment
        if summary["number_type"] in ["PREMIUM_RATE", "SHARED_COST"]:
            summary["risk_assessment"] = "High - Premium rate number"
        elif summary["number_type"] == "VOIP":
            summary["risk_assessment"] = "Medium - VoIP service"
        else:
            summary["risk_assessment"] = "Low - Standard number"
        
        return summary

# Synchronous wrapper for easy use
def analyze_phone_number(phone_number: str) -> Dict:
    """Synchronous wrapper for phone analysis"""
    analyzer = PhoneNumberIntelligence()
    return asyncio.run(analyzer.comprehensive_phone_analysis(phone_number))

# Example usage
if __name__ == "__main__":
    # Use a more realistic test number
    result = analyze_phone_number("+917038052820")  # Example US number
    print("Phone Intelligence Results:")
    print(f"Valid: {result['summary']['is_valid']}")
    print(f"Carrier: {result['summary']['carrier']}")
    print(f"Location: {result['summary']['location']}")
    print(f"Type: {result['summary']['number_type']}")
    print(f"Confidence: {result['summary']['confidence_score']:.1%}")
    print("\nDetailed Results:")
    for source, data in result['detailed_results'].items():
        print(f"\n{source}:")
        for key, value in list(data.items())[:5]:  # Show first 3 items
            print(f"  {key}: {value}")