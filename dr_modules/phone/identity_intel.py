import asyncio
from typing import Dict, List
from ddgs import DDGS
import spacy
import re
import json

class NLPNameFinder:
    """Simple NLP name discovery from phone numbers using DDGS and spaCy NER"""
    
    def __init__(self, spacy_model: str = "en_core_web_md"):
        self.ddgs = DDGS()
        # Load larger spaCy model for better NER
        try:
            self.nlp = spacy.load(spacy_model)
            print(f"✅ spaCy NER model '{spacy_model}' loaded successfully")
        except OSError:
            print(f"❌ spaCy model '{spacy_model}' not found.")
            print(f"💡 Install it with: python -m spacy download {spacy_model}")
            # Fallback to sm model
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("✅ Fallback to 'en_core_web_sm' model")
            except OSError:
                print("❌ No spaCy model available. Install with: python -m spacy download en_core_web_sm")
                raise
        
    def generate_search_queries(self, phone_number: str) -> List[str]:
        """Generate simple search queries for name finding"""
        clean_phone = re.sub(r'[^\d+]', '', phone_number)
        
        queries = [
            f'"{phone_number}"',
            f'"{clean_phone}" name',
            f'"{clean_phone}" owner', 
            f'"{clean_phone}" who is',
            f'"{clean_phone}" contact',
            f'reverse phone lookup "{clean_phone}"',
            f'who owns "{clean_phone}"',
            f'"{clean_phone}" whitepages',
            f'"{clean_phone}" truepeoplesearch',
            f'"{clean_phone}" person',
            f'phone number "{clean_phone}" name',
            f'"{clean_phone}" caller ID',
            f'"{clean_phone}" directory',
            f'"{clean_phone}" email',
            f'"{clean_phone}" address',
            f'contact "{clean_phone}"',
        ]
        return queries
    
    def search_with_ddgs(self, queries: List[str], max_results: int = 5) -> List[Dict]:
        """Search using DuckDuckGo"""
        all_results = []
        
        for query in queries:
            try:
                results = list(self.ddgs.text(query, max_results=max_results))
                for result in results:
                    all_results.append({
                        'title': result.get('title', ''),
                        'content': result.get('body', ''),
                        'url': result.get('href', ''),
                        'query': query
                    })
                print(f"✅ Found {len(results)} results for: {query}")
            except Exception as e:
                print(f"❌ Search failed for '{query}': {e}")
                continue
                
        return all_results
    
    def extract_names_with_spacy(self, search_results: List[Dict], phone_number: str) -> Dict:
        """Use spaCy NER to extract names from search results"""
        if not search_results:
            return {"names": [], "error": "No search results"}
        
        all_names = set()
        
        print("🔍 Using spaCy NER to extract names from search results...")
        
        for i, result in enumerate(search_results):
            # Combine title and content for analysis
            text = f"{result['title']} {result['content']}"
            
            # Process with spaCy (using the larger model)
            doc = self.nlp(text)
            
            # Extract PERSON entities - the larger model is much better at this
            names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
            
            # Filter and validate names
            for name in names:
                cleaned_name = self._clean_and_validate_name(name)
                if cleaned_name:
                    all_names.add(cleaned_name)
            
            # Debug: Show names found in this result
            if names:
                print(f"   Result {i+1}: Found {len(names)} potential names: {names}")
        
        # Convert set to list
        final_names = list(all_names)
        print(f"📝 spaCy extracted {len(final_names)} unique names: {final_names}")
        
        return {"names": final_names}
    
    def _clean_and_validate_name(self, name: str) -> str:
        """Clean and validate extracted names"""
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Basic validation rules
        words = name.split()
        
        # Must have at least 2 words (first and last name)
        if len(words) < 2:
            return ""
        
        # Check if it's likely a person name (not company, etc.)
        invalid_patterns = [
            r'\b(inc|llc|corp|company|ltd|co|org)\b',
            r'\b(admin|support|contact|sales|help|info)\b',
            r'\b(customer|service|web|online|home|about)\b',
            r'\b(privacy|policy|terms|conditions)\b',
        ]
        
        name_lower = name.lower()
        for pattern in invalid_patterns:
            if re.search(pattern, name_lower):
                return ""
        
        # Name shouldn't be too long (more than 4 words is probably not a person name)
        if len(words) > 4:
            return ""
        
        return name
    
    def validate_names(self, names: List[str], search_results: List[Dict]) -> List[Dict]:
        """Validate names by checking occurrence in search results"""
        validated = []
        
        print(f"🔍 Validating {len(names)} potential names...")
        
        for name in names:
            if not name:
                continue
                
            # Count occurrences in search results
            count = 0
            sources = []
            
            for result in search_results:
                text = f"{result['title']} {result['content']}".lower()
                if name.lower() in text:
                    count += 1
                    sources.append(result['query'])
            
            print(f"   Name: '{name}' - Found in {count} sources")
            
            if count > 0:
                confidence = min(count / len(search_results) * 2, 1.0)
                validated.append({
                    'name': name,
                    'confidence': round(confidence, 2),
                    'occurrences': count,
                    'sources': list(set(sources))[:3]
                })
            else:
                print(f"   ❌ '{name}' not found in any search results")
        
        # Sort by confidence
        validated.sort(key=lambda x: x['confidence'], reverse=True)
        print(f"✅ Final validated names: {len(validated)}")
        return validated
    
    async def find_names(self, phone_number: str) -> Dict:
        """Main method to find names from phone number"""
        
        print(f"🔍 Starting search for: {phone_number}")
        
        # Step 1: Generate and run searches
        queries = self.generate_search_queries(phone_number)
        print(f"📋 Generated {len(queries)} search queries")
        
        search_results = self.search_with_ddgs(queries)
        print(f"📊 Total search results: {len(search_results)}")
        
        if not search_results:
            return {
                "phone_number": phone_number,
                "names": [],
                "error": "No search results found",
                "search_metrics": {
                    "queries_used": len(queries),
                    "results_found": 0
                },
                "summary": {
                    "status": "No search results found",
                    "recommendation": "Try different search terms or check internet connection"
                }
            }
        
        # Step 2: Extract names with spaCy NER
        nlp_result = self.extract_names_with_spacy(search_results, phone_number)
        raw_names = nlp_result.get("names", [])
        print(f"📝 spaCy extracted {len(raw_names)} potential names")
        
        # Step 3: Validate names
        validated_names = self.validate_names(raw_names, search_results)
        print(f"✅ Validated {len(validated_names)} names")
        
        # Step 4: Prepare results
        high_confidence = [n for n in validated_names if n['confidence'] > 0.5]
        medium_confidence = [n for n in validated_names if 0.3 <= n['confidence'] <= 0.5]
        low_confidence = [n for n in validated_names if n['confidence'] < 0.3]
        
        result = {
            "phone_number": phone_number,
            "names_found": {
                "high_confidence": high_confidence,
                "medium_confidence": medium_confidence,
                "low_confidence": low_confidence,
                "all_names": validated_names
            },
            "search_metrics": {
                "queries_used": len(queries),
                "results_found": len(search_results),
                "unique_names_found": len(validated_names)
            },
            "summary": self._generate_summary(validated_names),
            "raw_names_count": len(raw_names)
        }
        
        return result
    
    def _generate_summary(self, names: List[Dict]) -> Dict:
        """Generate simple summary"""
        if not names:
            return {
                "status": "No names found",
                "recommendation": "The phone number may not be publicly listed or try different search strategies"
            }
        
        top_name = names[0]
        
        if top_name['confidence'] > 0.7:
            status = "High confidence match found"
        elif top_name['confidence'] > 0.4:
            status = "Possible match found"
        else:
            status = "Low confidence findings"
        
        return {
            "status": status,
            "primary_candidate": top_name['name'],
            "primary_confidence": top_name['confidence'],
            "total_names_found": len(names),
            "recommendation": "Verify with additional sources"
        }


# Synchronous wrapper
def find_names_from_phone(phone_number: str, spacy_model: str = "en_core_web_md") -> Dict:
    """Simple synchronous wrapper"""
    finder = NLPNameFinder(spacy_model=spacy_model)
    return asyncio.run(finder.find_names(phone_number))


# Test the spaCy NER separately
def test_spacy_ner():
    """Test spaCy NER with example text"""
    print("🧪 Testing spaCy NER with example text...")
    
    try:
        nlp = spacy.load("en_core_web_md")
        test_text = "Contact Ramesh Kumar or Priya Sharma at +91 9876543210 for more information about the project with John Doe and Maria Garcia."
        doc = nlp(test_text)
        names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        print(f"✅ Test Results: {names}")
        # Expected: ['Ramesh Kumar', 'Priya Sharma', 'John Doe', 'Maria Garcia']
        return names
    except Exception as e:
        print(f"❌ NER test failed: {e}")
        return []


# Example usage with proper error handling
if __name__ == "__main__":
    # First, test spaCy NER
    test_spacy_ner()
    print()
    
    # Check if larger model is available, otherwise use sm
    try:
        spacy.load("en_core_web_md")
        model_to_use = "en_core_web_md"
        print("✅ Using en_core_web_md model (better accuracy)")
    except OSError:
        try:
            spacy.load("en_core_web_sm")
            model_to_use = "en_core_web_sm" 
            print("⚠️  Using en_core_web_sm model (en_core_web_md not available)")
            print("💡 For better results, install: python -m spacy download en_core_web_md")
        except OSError:
            print("❌ No spaCy models available. Install with: python -m spacy download en_core_web_sm")
            exit(1)
    
    # Test with a phone number
    test_phone = "7038052820"  # You can change this to a real number
    
    print(f"🔍 Searching for names for: {test_phone}")
    print("Please wait, this may take a minute...\n")
    
    try:
        result = find_names_from_phone(test_phone, spacy_model=model_to_use)
        
        print(f"\n📊 SEARCH RESULTS:")
        print(f"   Phone: {result['phone_number']}")
        print(f"   Queries used: {result['search_metrics']['queries_used']}")
        print(f"   Results found: {result['search_metrics']['results_found']}")
        print(f"   Names found: {result['search_metrics']['unique_names_found']}")
        print(f"   Raw names extracted: {result.get('raw_names_count', 0)}")
        
        # Safe access to summary
        summary = result.get('summary', {})
        print(f"\n🎯 SUMMARY: {summary.get('status', 'Unknown status')}")
        
        # Only show primary candidate if it exists
        if 'primary_candidate' in summary:
            print(f"   Primary Candidate: {summary['primary_candidate']}")
            print(f"   Confidence: {summary.get('primary_confidence', 0):.0%}")
        
        print(f"   Recommendation: {summary.get('recommendation', 'No recommendation')}")
        
        # Display names if found
        names_found = result.get('names_found', {})
        
        if names_found.get('high_confidence'):
            print(f"\n✅ HIGH CONFIDENCE NAMES:")
            for name_data in names_found['high_confidence']:
                print(f"   • {name_data['name']} ({name_data['confidence']:.0%} confidence)")
                print(f"     Found in {name_data['occurrences']} sources")
        
        if names_found.get('medium_confidence'):
            print(f"\n⚠️  MEDIUM CONFIDENCE NAMES:")
            for name_data in names_found['medium_confidence']:
                print(f"   • {name_data['name']} ({name_data['confidence']:.0%} confidence)")
        
        if names_found.get('low_confidence') and (not names_found.get('high_confidence') and not names_found.get('medium_confidence')):
            print(f"\n🔍 LOW CONFIDENCE NAMES (for reference):")
            for name_data in names_found['low_confidence'][:5]:  # Show only top 5
                print(f"   • {name_data['name']} ({name_data['confidence']:.0%} confidence)")
            
        if not any([names_found.get('high_confidence'), names_found.get('medium_confidence'), names_found.get('low_confidence')]):
            print(f"\n❌ No names found. This could mean:")
            print(f"   - The number is not publicly listed")
            print(f"   - The number belongs to a business")
            print(f"   - Privacy settings prevent discovery")
            print(f"   - Try searching with area code variations")
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
        import traceback
        traceback.print_exc()