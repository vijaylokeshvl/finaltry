import os
import json
from typing import List, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    def get_styling_recommendations(self, skin_tone_category: str, gender: str, detected_objects: Optional[List[str]] = None) -> dict:
        """
        Request style recommendations from Groq LLaMA model based on detected skin tone, gender, and apparel tags.
        Returns a structured dictionary of recommendations.
        """
        if detected_objects is None:
             detected_objects = []
        
        if not self.client:
            return self._mock_recommendations(skin_tone_category, gender)

        tags_str = ", ".join(detected_objects) if detected_objects else "none detected"

        prompt = f"""
        You are an expert personal stylist. 
        User Profile:
        - Gender: {gender}
        - Skin Tone: {skin_tone_category}
        - Currently Wearing (detected): {tags_str}

        Task:
        Provide a comprehensive, stylish recommendation in JSON format.
        CRITICAL: All shopping links must be functional search URLs.
        - Amazon: https://www.amazon.in/s?k=[search+query]
        - Flipkart: https://www.flipkart.com/search?q=[search+query]
        Ensure queries are specific (e.g., "navy+blue+slim+fit+shirt").

        JSON Keys:
        - "summary" (string): Stylist quote.
        - "colors": list of strings (hex or names).
        - "outfit_recommendations": list of strings.
        - "accessories": list of strings.
        - "hairstyles": list of strings.
        - "shopping_links": array of objects with "store", "item", "url".
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional fashion advisor. You only output valid JSON. Use real Indian e-commerce search URL patterns.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1024,
                response_format={"type": "json_object"}
            )
            
            response_content = chat_completion.choices[0].message.content
            if response_content is None:
                return self._mock_recommendations(skin_tone_category, gender)
            return json.loads(response_content)
            
        except Exception as e:
            print(f"Error calling Groq API: {str(e)}")
            return self._mock_recommendations(skin_tone_category, gender)

    def _mock_recommendations(self, skin_tone_category: str, gender: str) -> dict:
        """
        Fallback mock data with VALID search URLs.
        """
        print("Using mock styling recommendations.")
        return {
            "summary": f"Based on your {skin_tone_category} skin tone, we recommend classic and elegant combinations for a {gender}.",
            "colors": ["#1a365d", "#FFFFFF"],
            "outfit_recommendations": ["Navy Blue Blazer with White Shirt"],
            "accessories": ["Silver Watch"],
            "hairstyles": ["Classic Pompadour"],
            "shopping_links": [
                {"store": "Amazon India", "item": "Navy Blue Blazer", "url": "https://www.amazon.in/s?k=navy+blue+blazer"},
                {"store": "Flipkart", "item": "White Slim Fit Shirt", "url": "https://www.flipkart.com/search?q=white+slim+fit+shirt"}
            ]
        }

# Singleton instance
groq_service = GroqService()

def get_recommendations(skin_tone: str, gender: str, detected_objects: Optional[List[str]] = None) -> dict:
    return groq_service.get_styling_recommendations(skin_tone, gender, detected_objects)
