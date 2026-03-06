from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="StyleSense AI")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates setup
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main frontend interface"""
    return templates.TemplateResponse(request, "index.html")

@app.post("/api/analyze")
async def analyze_style(
    image: UploadFile = File(...),
    gender: str = Form(...)
):
    """
    Endpoint to receive photo, analyze skin tone, and get styling recommendations
    """
    try:
        from services.image_analyzer import analyze_image
        from services.groq_service import get_recommendations
        from services.rapid_fashion_service import analyze_fashion
        from services.rebrandly_service import get_short_url
        
        # Read uploaded image bytes
        image_bytes = await image.read()
        
        # 1. Analyze skin tone via OpenCV
        skin_tone_result = analyze_image(image_bytes)
        skin_tone_category = skin_tone_result.get("category", "Unknown")
        
        # 2. Detect apparel using RapidAPI (API4AI)
        fashion_data = await analyze_fashion(image_bytes)
        detected_tags = []
        fashion_status = fashion_data.get("status") if isinstance(fashion_data, dict) else None
        if fashion_status == "ok":
            for result in fashion_data.get("results", []):
                for obj in result.get("entities", [{}])[0].get("objects", []):
                    # Get the most confident class
                    classes = obj.get("classes", {})
                    if classes:
                        top_class = max(classes, key=classes.get)
                        detected_tags.append(top_class)
        
        # 3. Get styling recommendations from AI
        recommendations = get_recommendations(skin_tone_category, gender, detected_tags)
        
        # 4. Shorten shopping links via Rebrandly
        if "shopping_links" in recommendations:
            for link in recommendations["shopping_links"]:
                if "url" in link and link["url"].startswith("http"):
                    link["url"] = await get_short_url(link["url"])
        
        return {
            "status": "success",
            "skin_tone": skin_tone_result,
            "gender": gender,
            "detected_apparel": detected_tags,
            "recommendations": recommendations
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/trends")
async def get_trends():
    """
    Endpoint to retrieve latest fashion trends
    """
    try:
        # In a real app, this might call Groq or a database. 
        # For now, we return curated trends based on current 2026 fashion predictions.
        return {
            "status": "success",
            "trends": [
                {
                    "title": "Sustainable Chic",
                    "description": "Eco-friendly materials and upcycled luxury are taking center stage this season.",
                    "tag": "Sustainability"
                },
                {
                    "title": "Digital Lavender",
                    "description": "The serene hue continues to dominate both street style and high fashion runways.",
                    "tag": "Color Trend"
                },
                {
                    "title": "Hyper-Functional Techwear",
                    "description": "Utility meets aesthetics with oversized pockets and weather-resistant fabrics.",
                    "tag": "Style"
                }
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
