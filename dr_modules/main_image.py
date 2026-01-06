# main_image_sequential.py
import json
import re
import os
import numpy as np
import asyncio
import time
import traceback
from datetime import datetime
from typing import Dict, List, Set

# Import the provided modules
from .image.text_extractor import TextExtractor
from .image.steganography_detector import SteganographyDetector
from .image.reverse_image_searcher import ReverseImageSearcher
from .image.object_detector import ObjectDetector
from .image.metadata_analyzer import MetadataAnalyzer
from .image.geolocation_analyzer import GeolocationAnalyzer
from .image.face_analyzer import FaceAnalyzer
from .image.authenticity_checker import AuthenticityChecker

class ImageResearchHandler:
    def __init__(self):
        """
        Sequential image research handler with progress display
        """
        self.text_extractor = TextExtractor()
        self.steg_detector = SteganographyDetector()
        self.reverse_searcher = ReverseImageSearcher()
        self.object_detector = ObjectDetector()
        self.metadata_analyzer = MetadataAnalyzer()
        self.geolocation_analyzer = GeolocationAnalyzer()
        self.face_analyzer = FaceAnalyzer()
        self.authenticity_checker = AuthenticityChecker()
        
        self.current_findings = []

    async def conduct_research(self, image_path: str, depth: int = 2) -> Dict:
        """
        Conduct sequential image research with progress display
        
        Args:
            image_path: Path/URL to the image
            depth: Investigation depth (1-3)
            
        Returns:
            Dictionary with comprehensive image analysis report
        """
        start_time = datetime.now()
        results = {
            "meta": {
                "input": image_path,
                "start_time": start_time.isoformat(),
                "depth": depth,
                "modules": [
                    "FileValidation",
                    "TextExtractor",
                    "MetadataAnalyzer",
                    "ObjectDetector", 
                    "FaceAnalyzer",
                    "AuthenticityChecker",
                    "SteganographyDetector",
                    "ReverseImageSearch",
                    "GeolocationAnalyzer"
                ]
            },
            "raw": {},
            "entities": {},
            "relationships": [],
            "findings": []
        }

        try:
            # 1. File Validation & Basic Info
            self._show_progress("🔍 Validating image file...")
            file_info = self._validate_file(image_path)
            results["raw"]["file_validation"] = file_info
            self._add_finding("file_validation", file_info)
            
            # 2. Text Extraction
            self._show_progress("📝 Extracting text from image...")
            text_results = self.text_extractor.extract_all_text(image_path)
            results["raw"]["text_extraction"] = text_results
            self._add_finding("text_extraction", text_results)
            
            # 3. Metadata Analysis
            self._show_progress("📊 Analyzing image metadata...")
            metadata_results = self.metadata_analyzer.extract_all(image_path)
            results["raw"]["metadata_analysis"] = metadata_results
            self._add_finding("metadata_analysis", metadata_results)
            
            # 4. Object Detection
            self._show_progress("🎯 Detecting objects in image...")
            object_results = self._run_object_detection(image_path)
            results["raw"]["object_detection"] = object_results
            self._add_finding("object_detection", object_results)
            
            # 5. Face Detection
            self._show_progress("👤 Detecting faces in image...")
            face_results = self.face_analyzer.detect_faces(image_path)
            results["raw"]["face_detection"] = face_results
            self._add_finding("face_detection", face_results)
            
            # 6. Authenticity Check
            self._show_progress("🔎 Checking image authenticity...")
            authenticity_results = self.authenticity_checker.comprehensive_check(image_path)
            results["raw"]["authenticity_check"] = authenticity_results
            self._add_finding("authenticity_check", authenticity_results)
            
            # 7. Steganography Detection
            self._show_progress("🕵️ Checking for hidden data...")
            steg_results = self.steg_detector.comprehensive_check(image_path)
            results["raw"]["steganography_detection"] = steg_results
            self._add_finding("steganography_detection", steg_results)
            
            # 8. Reverse Image Search
            self._show_progress("🌐 Performing reverse image search...")
            reverse_search_results = self.reverse_searcher.search_all_engines(image_path)
            results["raw"]["reverse_image_search"] = reverse_search_results
            self._add_finding("reverse_image_search", reverse_search_results)
            
            # 9. Geolocation Analysis (if GPS data found)
            self._show_progress("🗺️ Analyzing geolocation data...")
            geolocation_results = self._run_geolocation_analysis(metadata_results)
            results["raw"]["geolocation_analysis"] = geolocation_results
            self._add_finding("geolocation_analysis", geolocation_results)

        except Exception as e:
            error_msg = f"Research failed: {str(e)}\n{traceback.format_exc()}"
            self._show_progress(f"❌ {error_msg}", is_error=True)
            return {
                "error": error_msg,
                "input": image_path,
                "timestamp": datetime.now().isoformat()
            }

        # Extract and standardize entities
        results["entities"] = self._extract_entities(results["raw"])
        
        # Build relationships
        results["relationships"] = self._build_relationships(results["entities"])
        
        # Add findings and metadata
        results["findings"] = self.current_findings
        results["meta"]["end_time"] = datetime.now().isoformat()
        results["meta"]["processing_time"] = str(datetime.now() - start_time)
        results["meta"]["entity_counts"] = {
            k: len(v) for k, v in results["entities"].items()
        }

        self._show_progress("✅ Image research completed!", is_final=True)
        return results

    def _show_progress(self, message: str, is_error: bool = False, is_final: bool = False):
        """Display progress with emojis and formatting"""
        if is_error:
            print(f"❌ {message}")
        elif is_final:
            print(f"\n🎉 {message}")
        else:
            print(f"🔍 {message}")
        
        # Add small delay for better readability
        if not is_final and not is_error:
            time.sleep(0.5)

    def _convert_numpy_types(self, obj):
        """Convert NumPy types to native Python types for JSON serialization"""
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._convert_numpy_types(item) for item in obj)
        else:
            return obj

    def _add_finding(self, module: str, data: Dict):
        """Add significant findings to the findings list"""
        finding = {
            "module": module,
            "timestamp": datetime.now().isoformat(),
            "significant_data": {}
        }
        
        if module == "text_extraction" and "best_text" in data:
            text = data["best_text"]
            if text and len(text.strip()) > 0:
                finding["significant_data"]["extracted_text"] = text[:200] + "..." if len(text) > 200 else text
                self._show_progress(f"📝 Found text: {text[:50]}..." if len(text) > 50 else f"📝 Found text: {text}")
        
        elif module == "metadata_analysis" and "exifread" in data:
            exif_data = data["exifread"]
            if exif_data:
                gps_data = self._extract_gps_from_exif(exif_data)
                if gps_data:
                    finding["significant_data"]["gps_coordinates"] = gps_data
                    self._show_progress(f"🗺️ Found GPS coordinates: {gps_data}")
                
                if "Image Software" in exif_data:
                    self._show_progress(f"🛠️ Software used: {exif_data['Image Software']}")
        
        elif module == "object_detection" and "objects" in data:
            objects = data["objects"]
            if objects:
                object_types = [obj["label"] for obj in objects]
                finding["significant_data"]["detected_objects"] = object_types
                self._show_progress(f"🎯 Detected objects: {', '.join(set(object_types))}")
        
        elif module == "face_detection" and "total_faces" in data:
            face_count = data["total_faces"]
            if face_count > 0:
                finding["significant_data"]["faces_detected"] = face_count
                self._show_progress(f"👤 Detected {face_count} face(s)")
        
        elif module == "authenticity_check" and "ela_score" in data:
            ela_score = data["ela_score"]
            if ela_score > 10:  # Threshold for potential manipulation
                finding["significant_data"]["high_ela_score"] = ela_score
                self._show_progress(f"⚠️ High ELA score detected: {ela_score} (possible manipulation)")
        
        # elif module == "steganography_detection":
        #     for method, result in data.items():
        #         if result.get('found'):
        #             finding["significant_data"][f"steg_{method}"] = True
        #             self._show_progress(f"🕵️ Hidden data found with {method}")

        elif module == "steganography_detection":
            for method, result in data.items():
                # Handle both dict (normal) and list (like appended_signatures)
                if isinstance(result, dict) and result.get('found'):
                    finding["significant_data"][f"steg_{method}"] = True
                    self._show_progress(f"🕵️ Hidden data found with {method}")
                elif isinstance(result, list):
                    for entry in result:
                        if isinstance(entry, dict) and entry.get('found'):
                            finding["significant_data"][f"steg_{method}"] = True
                            self._show_progress(f"🕵️ Hidden data found in {method} (list entry)")

        
        elif module == "reverse_image_search":
            successful_searches = [engine for engine, result in data.items() 
                                 if result.get('status') == 'success']
            if successful_searches:
                finding["significant_data"]["successful_searches"] = successful_searches
                self._show_progress(f"🌐 Found matches on: {', '.join(successful_searches)}")
        
        if finding["significant_data"]:
            self.current_findings.append(finding)

    def _validate_file(self, image_path: str) -> Dict:
        """Validate image file and get basic info"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        file_size = os.path.getsize(image_path)
        if file_size == 0:
            raise ValueError(f"Image file is empty: {image_path}")
        
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                format = img.format
                size = img.size
                mode = img.mode
        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")
        
        return {
            "file_exists": True,
            "file_size": file_size,
            "image_format": format,
            "image_dimensions": size,
            "color_mode": mode,
            "file_path": os.path.abspath(image_path)
        }

    def _run_object_detection(self, image_path: str) -> Dict:
        """Run object detection with error handling"""
        try:
            objects = self.object_detector.detect_objects(image_path)
            summary = self.object_detector.get_detection_summary(image_path)
            
            return {
                "objects": objects,
                "summary": summary,
                "people_count": len(self.object_detector.detect_people(image_path)),
                "vehicles_count": len(self.object_detector.detect_vehicles(image_path)),
                "animals_count": len(self.object_detector.detect_animals(image_path))
            }
        except Exception as e:
            return {"error": f"Object detection failed: {str(e)}"}

    def _run_geolocation_analysis(self, metadata_results: Dict) -> Dict:
        """Extract and analyze geolocation data from metadata"""
        gps_data = self._extract_gps_from_metadata(metadata_results)
        
        if not gps_data:
            return {"gps_data": None, "message": "No GPS coordinates found"}
        
        try:
            lat, lon = gps_data
            geolocation_results = self.geolocation_analyzer.comprehensive_geolocation(lat, lon)
            return {
                "gps_coordinates": gps_data,
                "location_data": geolocation_results
            }
        except Exception as e:
            return {
                "gps_coordinates": gps_data,
                "error": f"Geolocation analysis failed: {str(e)}"
            }

    def _extract_gps_from_metadata(self, metadata_results: Dict) -> tuple:
        """Extract GPS coordinates from various metadata sources"""
        # Try exifread first
        if "exifread" in metadata_results:
            exif_data = metadata_results["exifread"]
            gps_data = self._extract_gps_from_exif(exif_data)
            if gps_data:
                return gps_data
        
        # Try exiftool output
        if "exiftool" in metadata_results:
            exiftool_output = metadata_results["exiftool"]
            if "GPS Latitude" in exiftool_output and "GPS Longitude" in exiftool_output:
                # Parse exiftool GPS format
                lat_match = re.search(r"GPS Latitude\s*:\s*([\d\.]+)", exiftool_output)
                lon_match = re.search(r"GPS Longitude\s*:\s*([\d\.]+)", exiftool_output)
                if lat_match and lon_match:
                    return float(lat_match.group(1)), float(lon_match.group(1))
        
        return None

    def _extract_gps_from_exif(self, exif_data: Dict) -> tuple:
        """Extract GPS coordinates from EXIF data"""
        gps_keys = [key for key in exif_data.keys() if 'gps' in key.lower()]
        
        for key in gps_keys:
            value = exif_data[key]
            if 'latitude' in key.lower() and value:
                try:
                    # Simple coordinate extraction - you might need more complex parsing
                    if isinstance(value, str) and ',' in value:
                        coords = value.split(',')
                        if len(coords) == 2:
                            lat = float(coords[0].strip())
                            lon = float(coords[1].strip())
                            return (lat, lon)
                except (ValueError, IndexError):
                    continue
        
        return None

    def _extract_entities(self, raw_data: Dict) -> Dict:
        """Extract and standardize entities from all module outputs"""
        entities = {
            "images": set(),
            "usernames": set(),
            "emails": set(),
            "phones": set(),
            "locations": set(),
            "social_media": set(),
            "objects": set(),
            "faces": set(),
            "hashes": set(),
            "websites": set(),
            "software": set()
        }

        # Extract from text
        if "text_extraction" in raw_data:
            text_data = raw_data["text_extraction"]
            if "best_text" in text_data and text_data["best_text"]:
                text = text_data["best_text"]
                entities["usernames"].update(self._extract_usernames(text))
                entities["emails"].update(self._extract_emails(text))
                entities["phones"].update(self._extract_phones(text))
                entities["websites"].update(self._extract_urls(text))

        # Extract from metadata
        if "metadata_analysis" in raw_data:
            meta_data = raw_data["metadata_analysis"]
            if "exifread" in meta_data:
                exif = meta_data["exifread"]
                if "Image Software" in exif:
                    entities["software"].add(exif["Image Software"])

        # Extract objects
        if "object_detection" in raw_data:
            obj_data = raw_data["object_detection"]
            if "objects" in obj_data:
                entities["objects"].update([obj["label"] for obj in obj_data["objects"]])

        # Extract faces
        if "face_detection" in raw_data:
            face_data = raw_data["face_detection"]
            if face_data["total_faces"] > 0:
                entities["faces"].add(f"faces_found:{face_data['total_faces']}")

        # Extract from reverse search
        if "reverse_image_search" in raw_data:
            search_data = raw_data["reverse_image_search"]
            for engine, result in search_data.items():
                if result.get('status') == 'success' and result.get('url'):
                    entities["websites"].add(result['url'])

        return {k: list(v) for k, v in entities.items() if v}

    def _build_relationships(self, entities: Dict) -> List[Dict]:
        """Build relationships between extracted entities"""
        relationships = []
        
        # Image to objects
        for obj in entities.get("objects", []):
            relationships.append({
                "source": "main_image",
                "target": obj,
                "type": "contains_object",
                "source_module": "ObjectDetector"
            })

        # Image to locations
        for location in entities.get("locations", []):
            relationships.append({
                "source": "main_image", 
                "target": location,
                "type": "geolocation",
                "source_module": "MetadataAnalyzer"
            })

        return relationships

    # Helper extraction methods
    def _extract_usernames(self, text: str) -> Set[str]:
        return {u.lower() for u in re.findall(r'@([a-zA-Z0-9_\-\.]+)', text)}

    def _extract_emails(self, text: str) -> Set[str]:
        return {e.lower() for e in re.findall(r'[\w\.-]+@[\w\.-]+', text)}

    def _extract_phones(self, text: str) -> Set[str]:
        return {p for p in re.findall(r'(\+?\d[\d\s\-\(\)]{8,}\d)', text)}

    def _extract_urls(self, text: str) -> Set[str]:
        return {u for u in re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)}

    async def conduct_research_with_output(self, image_path: str, output_path: str, depth: int = 2) -> Dict:
        """
        Conduct image research and save to specified output path
        Compatible with darkreaper.py command structure
        """
        print(f"🖼️ Starting sequential image research for: {image_path}")
        print("=" * 60)
        
        research_data = await self.conduct_research(image_path, depth)
        
        if "error" in research_data:
            return research_data
        
        # Create output directory if needed
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
            
            # Save JSON report
            json_path = f"{output_path}.json"
            with open(json_path, 'w') as f:
                research_data_serializable = self._convert_numpy_types(research_data)
                json.dump(research_data_serializable, f, indent=2)
            
            # Generate and save summary
            txt_path = f"{output_path}_summary.txt"
            self._generate_summary(research_data, txt_path)
            
            print(f"\n💾 Results saved:")
            print(f"   📄 JSON Report: {os.path.abspath(json_path)}")
            print(f"   📝 Text Summary: {os.path.abspath(txt_path)}")
            
            return {
                "success": True,
                "message": "Image research completed and saved",
                "image_path": image_path,
                "json_output_path": os.path.abspath(json_path),
                "txt_summary_path": os.path.abspath(txt_path),
                "entity_count": sum(len(v) for v in research_data["entities"].values()) if "entities" in research_data else 0
            }
        else:
            # No output path specified, just return the data
            return {
                "success": True,
                "message": "Image research completed",
                "image_path": image_path,
                "research_data": research_data,
                "entity_count": sum(len(v) for v in research_data["entities"].values()) if "entities" in research_data else 0
            }

    def _generate_summary(self, research_data: Dict, output_txt_path: str):
        """Generate comprehensive summary for image research"""
        if "error" in research_data:
            summary = research_data["error"]
        else:
            summary = f"IMAGE RESEARCH SUMMARY\n"
            summary += "=" * 50 + "\n\n"
            summary += f"Image: {research_data['meta']['input']}\n"
            summary += f"Processing Time: {research_data['meta']['processing_time']}\n\n"
            
            # Key findings section
            summary += "KEY FINDINGS:\n"
            summary += "-" * 30 + "\n"
            
            entities = research_data.get("entities", {})
            if entities:
                for entity_type, items in entities.items():
                    if items:
                        summary += f"{entity_type.upper()}: {len(items)} found\n"
                        for item in items[:3]:  # Show first 3 items
                            summary += f"  • {item}\n"
                        if len(items) > 3:
                            summary += f"  • ... and {len(items) - 3} more\n"
                        summary += "\n"
            else:
                summary += "No significant entities found.\n"
            
            # Findings from modules
            findings = research_data.get("findings", [])
            if findings:
                summary += "\nMODULE FINDINGS:\n"
                summary += "-" * 30 + "\n"
                for finding in findings:
                    if finding["significant_data"]:
                        summary += f"{finding['module']}:\n"
                        for key, value in finding["significant_data"].items():
                            summary += f"  • {key}: {value}\n"
                        summary += "\n"
        
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(summary)

# Synchronous wrappers for CLI compatibility (matching darkreaper.py structure)
def sync_conduct_research(image_path: str, depth: int = 2) -> Dict:
    """Synchronous wrapper for sequential research"""
    handler = ImageResearchHandler()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(handler.conduct_research(image_path, depth))
        return result
    finally:
        loop.close()

def sync_conduct_research_with_output(image_path: str, output_path: str, depth: int = 2) -> Dict:
    """Synchronous wrapper for sequential research with output"""
    handler = ImageResearchHandler()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(handler.conduct_research_with_output(image_path, output_path, depth))
        return result
    finally:
        loop.close()

# Example Usage
if __name__ == "__main__":
    handler = ImageResearchHandler()
    
    # Conduct research
    report = sync_conduct_research("test.jpg", depth=2)
    
    # Save report
    with open("sequential_image_research_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n🎯 Research completed! Check 'sequential_image_research_report.json' for full results.")