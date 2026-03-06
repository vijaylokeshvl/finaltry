import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class RebrandlyService:
    def __init__(self):
        self.api_key = os.getenv("REBRANDLY_API_KEY")
        self.base_url = "https://api.rebrandly.com/v1/links"

    async def shorten_url(self, destination: str) -> str:
        """
        Shorten a URL using Rebrandly API.
        """
        if not self.api_key:
            return destination
            
        headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
        
        payload = {
            "destination": destination
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    return f"https://{data.get('shortUrl', destination)}"
                else:
                    print(f"Rebrandly error: {response.status_code} - {response.text}")
                    return destination
        except Exception as e:
            print(f"Rebrandly exception: {str(e)}")
            return destination

# Singleton instance
rebrandly_service = RebrandlyService()

async def get_short_url(url: str) -> str:
    return await rebrandly_service.shorten_url(url)
