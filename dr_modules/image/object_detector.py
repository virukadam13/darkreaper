# object_detector.py
import cv2
import numpy as np
import os

class ObjectDetector:
    def __init__(self):
        self._load_object_detection_model()
    
    def _load_object_detection_model(self):
        """Load lightweight OpenCV DNN model (MobileNet SSD)"""
        base_path = os.path.dirname(__file__)   # always points to SubModules/
        prototxt = os.path.join(base_path, "MobileNetSSD_deploy.prototxt")
        model = os.path.join(base_path, "MobileNetSSD_deploy.caffemodel")

        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)
        self.object_classes = [
            "background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus",
            "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike",
            "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"
        ]
    
    def detect_objects(self, image_path, confidence_threshold=0.5):
        """Detect objects in image using MobileNet SSD"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        (h, w) = image.shape[:2]
        
        # Prepare input blob
        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)), 
            0.007843, 
            (300, 300), 
            127.5
        )
        
        # Run inference
        self.net.setInput(blob)
        detections = self.net.forward()
        
        objects = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > confidence_threshold:
                class_id = int(detections[0, 0, i, 1])
                
                # Skip background class
                if class_id == 0:
                    continue
                
                # Calculate bounding box coordinates
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                
                # Ensure bounding boxes are within image dimensions
                startX = max(0, startX)
                startY = max(0, startY)
                endX = min(w, endX)
                endY = min(h, endY)
                
                objects.append({
                    'label': self.object_classes[class_id],
                    'confidence': float(confidence),
                    'bbox': [startX, startY, endX - startX, endY - startY],
                    'bbox_coords': [startX, startY, endX, endY]
                })
        
        return objects
    
    def detect_people(self, image_path, confidence_threshold=0.5):
        """Detect only people in the image"""
        all_objects = self.detect_objects(image_path, confidence_threshold)
        people = [obj for obj in all_objects if obj['label'] == 'person']
        return people
    
    def detect_vehicles(self, image_path, confidence_threshold=0.5):
        """Detect vehicles in the image"""
        all_objects = self.detect_objects(image_path, confidence_threshold)
        vehicles = [obj for obj in all_objects if obj['label'] in 
                   ['car', 'bus', 'motorbike', 'bicycle', 'aeroplane', 'train', 'boat']]
        return vehicles
    
    def detect_animals(self, image_path, confidence_threshold=0.5):
        """Detect animals in the image"""
        all_objects = self.detect_objects(image_path, confidence_threshold)
        animals = [obj for obj in all_objects if obj['label'] in 
                  ['bird', 'cat', 'dog', 'horse', 'sheep', 'cow']]
        return animals
    
    def detect_furniture(self, image_path, confidence_threshold=0.5):
        """Detect furniture and indoor objects"""
        all_objects = self.detect_objects(image_path, confidence_threshold)
        furniture = [obj for obj in all_objects if obj['label'] in 
                    ['chair', 'diningtable', 'sofa', 'tvmonitor', 'pottedplant', 'bottle']]
        return furniture
    
    def get_detection_summary(self, image_path, confidence_threshold=0.5):
        """Get a summary of detected objects"""
        objects = self.detect_objects(image_path, confidence_threshold)
        
        summary = {}
        for obj in objects:
            label = obj['label']
            if label in summary:
                summary[label] += 1
            else:
                summary[label] = 1
        
        return summary
    
    def draw_detections(self, image_path, output_path=None, confidence_threshold=0.5, 
                       show_labels=True, show_confidence=True):
        """Draw bounding boxes and labels on image"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        
        objects = self.detect_objects(image_path, confidence_threshold)
        
        # Color map for different object types
        color_map = {
            'person': (0, 255, 0),      # Green
            'car': (255, 0, 0),         # Blue
            'bus': (0, 0, 255),         # Red
            'bicycle': (255, 255, 0),   # Cyan
            'motorbike': (0, 255, 255), # Yellow
            'dog': (255, 0, 255),       # Magenta
            'cat': (255, 165, 0),       # Orange
        }
        
        for obj in objects:
            label = obj['label']
            confidence = obj['confidence']
            x, y, w, h = obj['bbox']
            
            # Get color for this object type
            color = color_map.get(label, (255, 255, 255))  # Default white
            
            # Draw bounding box
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            
            if show_labels:
                # Prepare label text
                label_text = label
                if show_confidence:
                    label_text = f"{label}: {confidence:.2f}"
                
                # Calculate text size
                label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                
                # Draw label background
                cv2.rectangle(image, (x, y - label_size[1] - 10), 
                             (x + label_size[0], y), color, -1)
                
                # Draw label text
                cv2.putText(image, label_text, (x, y - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        if output_path:
            cv2.imwrite(output_path, image)
            print(f"Image with detections saved to: {output_path}")
            return output_path
        else:
            # Display image
            cv2.imshow('Object Detection', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            return image
    
    def batch_detect(self, image_paths, confidence_threshold=0.5):
        """Detect objects in multiple images"""
        results = {}
        for image_path in image_paths:
            if os.path.exists(image_path):
                try:
                    results[image_path] = self.detect_objects(image_path, confidence_threshold)
                except Exception as e:
                    results[image_path] = f"Error: {e}"
            else:
                results[image_path] = "File not found"
        
        return results

# Usage examples
if __name__ == "__main__":
    detector = ObjectDetector()
    
    # Test with a sample image
    test_image = "test.jpg"
    
    if os.path.exists(test_image):
        try:
            print("=== Object Detection Results ===")
            
            # 1. Detect all objects
            all_objects = detector.detect_objects(test_image)
            print(f"\n1. All Objects Detected ({len(all_objects)} total):")
            for obj in all_objects:
                print(f"   - {obj['label']}: {obj['confidence']:.2f} at {obj['bbox']}")
            
            # 2. Detect specific categories
            people = detector.detect_people(test_image)
            print(f"\n2. People Detected: {len(people)}")
            
            vehicles = detector.detect_vehicles(test_image)
            print(f"3. Vehicles Detected: {len(vehicles)}")
            
            animals = detector.detect_animals(test_image)
            print(f"4. Animals Detected: {len(animals)}")
            
            # 3. Get summary
            summary = detector.get_detection_summary(test_image)
            print(f"\n5. Detection Summary:")
            for obj_type, count in summary.items():
                print(f"   - {obj_type}: {count}")
            
            # 4. Draw and save results
            print(f"\n6. Saving visualization...")
            output_path = detector.draw_detections(test_image, "detection_result.jpg")
            print(f"   Results saved to: {output_path}")
            
        except Exception as e:
            print(f"Error during detection: {e}")
    else:
        print(f"Test image '{test_image}' not found.")
        print("\nAvailable object classes:")
        for i, class_name in enumerate(detector.object_classes):
            print(f"  {i:2d}. {class_name}")