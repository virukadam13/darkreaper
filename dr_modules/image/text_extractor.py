# text_extractor.py
import pytesseract
from PIL import Image
import requests
import json
import re

class TextExtractor:
    def local_tesseract(self, image_path):
        """Local Tesseract OCR"""
        try:
            text = pytesseract.image_to_string(image_path)
            return {'success': True, 'text': text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def ocr_space_api(self, image_path):
        """OCR.Space Free API"""
        api_key = 'helloworld'  # Free demo key
        url = 'https://api.ocr.space/parse/image'
        
        with open(image_path, 'rb') as f:
            response = requests.post(url,
                files={image_path: f},
                data={'apikey': api_key, 'language': 'eng'}
            )
        
        if response.status_code == 200:
            result = response.json()
            if result['IsErroredOnProcessing']:
                return {'success': False, 'error': result['ErrorMessage']}
            else:
                text = result['ParsedResults'][0]['ParsedText']
                return {'success': True, 'text': text}
        return {'success': False, 'error': 'API request failed'}
    
    def extract_pii(self, text):
        """Extract PII from OCR text"""
        patterns = {
            'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phones': r'(\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})',
            'urls': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        }
        
        pii = {}
        for pii_type, pattern in patterns.items():
            pii[pii_type] = re.findall(pattern, text)
        
        return pii
    
    def extract_all_text(self, image_path):
        """Try all OCR methods"""
        local_result = self.local_tesseract(image_path)
        api_result = self.ocr_space_api(image_path)
        
        best_text = local_result.get('text', '') if local_result['success'] else api_result.get('text', '')
        
        return {
            'local_ocr': local_result,
            'api_ocr': api_result,
            'pii': self.extract_pii(best_text),
            'best_text': best_text
        }
    

# Usage
if __name__ == "__main__":
    extractor = TextExtractor()
    result = extractor.extract_all_text("test.jpg")
    print("Text Extraction Result:")
    print(result)