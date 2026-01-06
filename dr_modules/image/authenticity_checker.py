# authenticity_checker.py
from PIL import Image
import imagehash
import numpy as np
import cv2

class AuthenticityChecker:
    def error_level_analysis(self, image_path):
        """Error Level Analysis for tamper detection"""
        original = cv2.imread(image_path)
        compressed = cv2.imread(image_path, cv2.IMWRITE_JPEG_QUALITY)
        
        # Calculate difference
        difference = cv2.absdiff(original, compressed)
        return np.mean(difference)
    
    def calculate_hashes(self, image_path):
        """Multiple perceptual hashes"""
        with Image.open(image_path) as img:
            return {
                'average_hash': str(imagehash.average_hash(img)),
                'perceptual_hash': str(imagehash.phash(img)),
                'difference_hash': str(imagehash.dhash(img)),
                'wavelet_hash': str(imagehash.whash(img))
            }
    
    def metadata_consistency(self, image_path):
        """Check metadata for inconsistencies"""
        from PIL.ExifTags import TAGS
        img = Image.open(image_path)
        exif_data = img._getexif() or {}
        
        checks = {
            'has_exif': len(exif_data) > 0,
            'software_used': any('photoshop' in str(exif_data.get(tag, '')).lower() 
                               for tag in exif_data.keys() if tag in TAGS),
            'multiple_software': len([v for k, v in exif_data.items() 
                                    if TAGS.get(k) == 'Software']) > 1
        }
        return checks
    
    def comprehensive_check(self, image_path):
        """All authenticity checks"""
        return {
            'ela_score': self.error_level_analysis(image_path),
            'image_hashes': self.calculate_hashes(image_path),
            'metadata_check': self.metadata_consistency(image_path),
            'file_integrity': self.file_structure_check(image_path)
        }
    
    def file_structure_check(self, image_path):
        """Basic file structure validation"""
        try:
            with Image.open(image_path) as img:
                img.verify()  # Verify file integrity
            return {'valid': True}
        except Exception as e:
            return {'valid': False, 'error': str(e)}
        

# Usage
if __name__ == "__main__":
    checker = AuthenticityChecker()
    result = checker.comprehensive_check("/home/viru/working/stegosteg.jpg")
    print("Authenticity Check Result:")
    print(result)