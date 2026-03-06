import cv2
import numpy as np
import io
from PIL import Image

class ImageAnalyzer:
    def __init__(self):
        # We will use the haarcascade for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def analyze_skin_tone(self, image_data: bytes) -> dict:
        """
        Analyzes the uploaded image to detect skin tone.
        Returns a dictionary with category and confidence.
        """
        try:
            # Convert bytes to cv2 image
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {"category": "Unknown", "confidence": 0.0, "error": "Invalid image"}

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

            # If no face is detected, we'll just try to guess from the center of the image
            if len(faces) == 0:
                h, w = img.shape[:2]
                face_region = img[int(h*0.3):int(h*0.7), int(w*0.3):int(w*0.7)]
            else:
                x, y, w, h = faces[0]
                # extract face region
                face_region = img[y:y+h, x:x+w]

            # Convert to RGB (OpenCV uses BGR)
            face_rgb = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)
            
            # Simple dominant color / average color extraction for the face region
            # We reshape to a list of pixels
            pixels = face_rgb.reshape(-1, 3)
            # Remove very dark and very bright pixels to focus on skin
            mask = (pixels[:, 0] > 40) & (pixels[:, 1] > 40) & (pixels[:, 2] > 40) & \
                   (pixels[:, 0] < 250) & (pixels[:, 1] < 250) & (pixels[:, 2] < 250)
            
            filtered_pixels = pixels[mask]
            if len(filtered_pixels) == 0:
                 filtered_pixels = pixels # fallback
                 
            avg_color = np.mean(filtered_pixels, axis=0)
            r, g, b = avg_color[0], avg_color[1], avg_color[2]

            category = self._categorize_skin_tone(r, g, b)
            
            return {
                "category": category["name"],
                "confidence": 0.85,
                "rgb": [int(r), int(g), int(b)]
            }
        except Exception as e:
            print(f"Error in image analysis: {str(e)}")
            return {"category": "Medium", "confidence": 0.5, "error": str(e)}

    def _categorize_skin_tone(self, r: float, g: float, b: float) -> dict:
        """
        Basic heuristic to categorize skin tone based on average RGB.
        """
        # Very simplified heuristic
        intensity = (r + g + b) / 3
        
        if intensity > 190:
            return {"name": "Fair"}
        elif intensity > 140:
            return {"name": "Medium"}
        elif intensity > 90:
            return {"name": "Olive"}
        else:
            return {"name": "Deep"}

# Singleton instance
analyzer = ImageAnalyzer()

def analyze_image(image_data: bytes) -> dict:
    return analyzer.analyze_skin_tone(image_data)
