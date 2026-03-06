import pytest
from fastapi.testclient import TestClient
from main import app
from io import BytesIO
from PIL import Image
import numpy as np

client = TestClient(app)

def create_test_image(color=(200, 150, 100)):
    """Create a dummy rgb image in memory representing a face color"""
    img = Image.new('RGB', (100, 100), color=color)
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return img_byte_arr

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "StyleSense AI" in response.text

def test_analyze_style():
    test_image = create_test_image()
    
    response = client.post(
        "/api/analyze",
        data={"gender": "Female"},
        files={"image": ("test.jpg", test_image, "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "skin_tone" in data
    assert "recommendations" in data
    assert data["gender"] == "Female"
    
if __name__ == "__main__":
    pytest.main(["-v", "test_app.py"])
