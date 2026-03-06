import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class RapidFashionService:
    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.host = os.getenv("RAPIDAPI_HOST")
        self.url = f"https://{self.host}/v2/results"

    async def analyze_image(self, image_bytes: bytes) -> dict:
        """
        Analyze image using RapidAPI Fashion API to detect apparel.
        """
        if not self.api_key:
            return {"status": "skipped", "reason": "No API key"}

        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.host
        }
        
        files = {
            "image": ("image.jpg", image_bytes, "image/jpeg")
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.url, files=files, headers=headers, timeout=30.0)
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"RapidAPI error: {response.status_code} - {response.text}")
                    return {"status": "error", "code": response.status_code}
        except Exception as e:
            print(f"RapidAPI exception: {str(e)}")
            return {"status": "error", "message": str(e)}

# Singleton instance
rapid_fashion_service = RapidFashionService()

async def analyze_fashion(image_bytes: bytes) -> dict:
    return await rapid_fashion_service.analyze_image(image_bytes)
