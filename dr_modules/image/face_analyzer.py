# face_analyzer.py
import cv2
import numpy as np

class FaceAnalyzer:
    def __init__(self):
        # Haar cascades for face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.profile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_profileface.xml'
        )
    
    def detect_faces(self, image_path):
        """Detect faces using OpenCV Haar cascades"""
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect frontal faces
        frontal_faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        # Detect profile faces  
        profile_faces = self.profile_cascade.detectMultiScale(gray, 1.1, 4)
        
        return {
            'frontal_faces': [{"x": x, "y": y, "w": w, "h": h} 
                            for (x, y, w, h) in frontal_faces],
            'profile_faces': [{"x": x, "y": y, "w": w, "h": h} 
                            for (x, y, w, h) in profile_faces],
            'total_faces': len(frontal_faces) + len(profile_faces)
        }
    
    def compare_faces_basic(self, image1_path, image2_path):
        """Basic face comparison using histogram matching"""
        faces1 = self.detect_faces(image1_path)['frontal_faces']
        faces2 = self.detect_faces(image2_path)['frontal_faces']
        
        if not faces1 or not faces2:
            return 0.0
        
        # Extract first face from each image
        img1 = cv2.imread(image1_path)
        img2 = cv2.imread(image2_path)
        
        x1, y1, w1, h1 = [faces1[0][k] for k in ['x', 'y', 'w', 'h']]
        x2, y2, w2, h2 = [faces2[0][k] for k in ['x', 'y', 'w', 'h']]
        
        face1 = cv2.resize(img1[y1:y1+h1, x1:x1+w1], (100, 100))
        face2 = cv2.resize(img2[y2:y2+h2, x2:x2+w2], (100, 100))
        
        # Histogram comparison
        hist1 = cv2.calcHist([face1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([face2], [0], None, [256], [0, 256])
        
        return cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    
# Usage
if __name__ == "__main__":
    analyzer = FaceAnalyzer()
    result = analyzer.detect_faces("test.jpg")
    print("Face Detection Result:")
    print(result)