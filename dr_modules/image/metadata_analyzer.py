# metadata_analyzer.py
import exifread
import piexif
from PIL import Image
import os
import subprocess  # For ExifTool CLI

class MetadataAnalyzer:
    def extract_exifread(self, image_path):
        """Pure Python EXIF extraction"""
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)
        return {str(tag): str(value) for tag, value in tags.items() 
                if tag not in ('JPEGThumbnail', 'TIFFThumbnail')}
    
    def extract_piexif(self, image_path):
        """EXIF manipulation"""
        try:
            exif_dict = piexif.load(image_path)
            return exif_dict
        except:
            return {}
    
    def exif_tool_cli(self, image_path):
        """Use ExifTool CLI (most comprehensive)"""
        try:
            result = subprocess.run(['exiftool', image_path], 
                                  capture_output=True, text=True)
            return result.stdout
        except:
            return "ExifTool not installed"
    
    def extract_all(self, image_path):
        """Comprehensive metadata extraction"""
        return {
            'exifread': self.extract_exifread(image_path),
            'piexif': self.extract_piexif(image_path),
            'exiftool': self.exif_tool_cli(image_path),
            'file_info': {
                'size': os.path.getsize(image_path),
                'format': Image.open(image_path).format
            }
        }
    

if __name__ == "__main__":
    analyzer = MetadataAnalyzer()
    
    # Test with an image
    image_path = "test.jpg"
    
    print("=== Metadata Analysis ===")
    print("EXIFRead Results:")
    exif_data = analyzer.extract_exifread(image_path)
    for key in list(exif_data.keys())[:5]:  # Show first 5 items
        print(f"  {key}: {exif_data[key]}")
    
    print("\nPiexif Results:")
    piexif_data = analyzer.extract_piexif(image_path)
    print(f"  EXIF segments: {list(piexif_data.keys())}")
    
    print("\nExifTool Results:")
    exiftool_output = analyzer.exif_tool_cli(image_path)
    print(f"  {exiftool_output[:200]}...")  # First 200 chars