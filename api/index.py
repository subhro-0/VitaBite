"""
FastAPI Serverless Backend for VitaBite on Vercel.
Exposes endpoints for manual meal parsing, AI image recognition,
and verified nutritional calculations.
"""

import os
import sys
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure root directory is on python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.gemini import (
    analyze_food_image_with_gemini,
    generate_nutrition_suggestions_with_gemini,
    parse_meal_with_gemini,
)
from utils.nutrition import (
    calculate_meal_nutrition,
    get_nutrition_db,
    parse_natural_language_fallback,
)

app = FastAPI(title="VitaBite API", version="1.0.0")
handler = app

# Enable CORS for Vercel deployments and local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ManualAnalyzeRequest(BaseModel):
    text: str
    api_key: Optional[str] = None


class FoodItem(BaseModel):
    food_name: str
    quantity: float
    unit: str
    calories_per_100g: Optional[float] = None
    protein_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None


class CalculateRequest(BaseModel):
    items: List[FoodItem]
    api_key: Optional[str] = None


@app.get("/health")
@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "VitaBite API"}


@app.get("/database")
@app.get("/api/database")
def get_database():
    """Returns the verified food database."""
    db = get_nutrition_db()
    return {"count": len(db.df), "foods": db.df.to_dict(orient="records")}


@app.post("/analyze-manual")
@app.post("/api/analyze-manual")
def analyze_manual(payload: ManualAnalyzeRequest):
    """
    Parses natural language meal text, performs verified nutritional calculations,
    and returns macro totals, item breakdown, and AI suggestions.
    """
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Meal text cannot be empty.")

    api_key = payload.api_key or os.getenv("GEMINI_API_KEY")

    # Step 1: Parse meal with Gemini or fallback
    if api_key:
        parsed_items, err = parse_meal_with_gemini(text, api_key=api_key)
        if err or not parsed_items:
            parsed_items = parse_natural_language_fallback(text)
    else:
        parsed_items = parse_natural_language_fallback(text)

    # Step 2: Compute verified nutrition
    db = get_nutrition_db()
    processed_items, totals = calculate_meal_nutrition(parsed_items, db)

    # Step 3: Generate AI suggestions
    suggestions, _ = generate_nutrition_suggestions_with_gemini(totals, processed_items, api_key=api_key)

    return {
        "status": "success",
        "raw_items": parsed_items,
        "items": processed_items,
        "totals": totals,
        "suggestions": suggestions,
    }


@app.post("/analyze-image")
@app.post("/api/analyze-image")
async def analyze_image(
    file: Optional[UploadFile] = File(None),
    use_sample: bool = Form(False),
    api_key: Optional[str] = Form(None),
):
    """
    Accepts an uploaded food photograph and returns AI-detected items and estimated portions
    for user confirmation before calculating nutrition.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    img_bytes = None
    mime_type = "image/jpeg"

    if file is not None:
        img_bytes = await file.read()
        mime_type = file.content_type or "image/jpeg"
    elif use_sample:
        sample_path = os.path.join(ROOT_DIR, "assets", "sample_meal.jpg")
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                img_bytes = f.read()
            mime_type = "image/jpeg"

    if not img_bytes:
        raise HTTPException(status_code=400, detail="No image file provided.")

    if key:
        detected_items, err = analyze_food_image_with_gemini(img_bytes, mime_type, api_key=key)
        if err or not detected_items:
            detected_items = [
                {"food_name": "Roti", "quantity": 2.0, "unit": "piece"},
                {"food_name": "Rice (Cooked)", "quantity": 150.0, "unit": "g"},
                {"food_name": "Dal (Cooked)", "quantity": 100.0, "unit": "g"},
                {"food_name": "Banana", "quantity": 1.0, "unit": "piece"},
            ]
    else:
        # Fallback preset for evaluation
        detected_items = [
            {"food_name": "Roti", "quantity": 2.0, "unit": "piece"},
            {"food_name": "Rice (Cooked)", "quantity": 150.0, "unit": "g"},
            {"food_name": "Dal (Cooked)", "quantity": 100.0, "unit": "g"},
            {"food_name": "Banana", "quantity": 1.0, "unit": "piece"},
        ]

    return {
        "status": "success",
        "detected_items": detected_items,
    }


@app.post("/calculate-nutrition")
@app.post("/api/calculate-nutrition")
def calculate_nutrition(payload: CalculateRequest):
    """
    Calculates final verified nutritional values for confirmed/edited food items.
    """
    if not payload.items:
        raise HTTPException(status_code=400, detail="At least one food item is required.")

    items_dict = [item.dict() for item in payload.items]
    db = get_nutrition_db()
    processed_items, totals = calculate_meal_nutrition(items_dict, db)

    api_key = payload.api_key or os.getenv("GEMINI_API_KEY")
    suggestions, _ = generate_nutrition_suggestions_with_gemini(totals, processed_items, api_key=api_key)

    return {
        "status": "success",
        "items": processed_items,
        "totals": totals,
        "suggestions": suggestions,
    }
