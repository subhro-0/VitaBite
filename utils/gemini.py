"""Google Gemini API integration for VitaBite using the official google-genai SDK."""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Model names
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"


def get_api_key(custom_key: Optional[str] = None) -> Optional[str]:
    """Retrieves API key from parameter or environment."""
    if custom_key and custom_key.strip():
        return custom_key.strip()
    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    return env_key if env_key else None


def clean_json_text(text: str) -> str:
    """Strips markdown code blocks and returns raw JSON text."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def parse_meal_with_gemini(
    text: str,
    api_key: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Uses Gemini API to interpret natural language meal descriptions.
    Returns: (parsed_items_list, error_message)
    """
    key = get_api_key(api_key)
    if not key:
        return [], "No GEMINI_API_KEY configured."

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)

        prompt = f"""
You are an expert nutrition assistant for an Indian & global diet tracker named VitaBite.
Parse the following meal description into individual food items with quantities and units:
User Input: "{text}"

Rules:
1. Extract every distinct food item.
2. Estimate reasonable quantity (float or int) and unit (e.g. "piece", "g", "cup", "bowl", "tbsp", "glass").
3. For foods that might not be standard staples, provide estimated values per 100g (calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g).
4. Return ONLY a valid JSON list of objects. No intro, no outro, no markdown formatting outside JSON.

JSON Schema format:
[
  {{
    "food_name": "Roti",
    "quantity": 2.0,
    "unit": "piece",
    "calories_per_100g": 264.0,
    "protein_per_100g": 9.0,
    "carbs_per_100g": 55.0,
    "fat_per_100g": 2.5
  }}
]
"""
        response = client.models.generate_content(
            model=DEFAULT_GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
        )

        raw_output = clean_json_text(response.text)
        items = json.loads(raw_output)
        if isinstance(items, list):
            return items, None
        elif isinstance(items, dict) and "items" in items:
            return items["items"], None
        return [], "Invalid JSON structure received from AI."

    except Exception as e:
        return [], str(e)


def analyze_food_image_with_gemini(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    api_key: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Uses Gemini Vision to recognize food items and estimated portions from a photograph.
    Returns: (detected_items_list, error_message)
    """
    key = get_api_key(api_key)
    if not key:
        return [], "No GEMINI_API_KEY configured. Please provide your Gemini API key in the sidebar or .env file."

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)

        prompt = """
You are VitaBite AI, an expert food recognition computer vision model.
Analyze this meal photograph carefully:
1. Identify all visible food items on the plate/table (e.g., Roti, Cooked Rice, Dal, Paneer Curry, Salad, Banana, Curd, etc.).
2. Estimate the serving quantity and unit based on visual visual volume (e.g. 2 piece, 150 g, 1 bowl, 1 cup).
3. If an item is common, use standard names (e.g. "Roti", "Rice (Cooked)", "Dal (Cooked)", "Paneer", "Curd").
4. Provide estimated nutritional values per 100g (calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g).
5. Output ONLY a valid JSON list.

Example format:
[
  {
    "food_name": "Roti",
    "quantity": 2.0,
    "unit": "piece",
    "calories_per_100g": 264.0,
    "protein_per_100g": 9.0,
    "carbs_per_100g": 55.0,
    "fat_per_100g": 2.5
  }
]
"""
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        response = client.models.generate_content(
            model=DEFAULT_GEMINI_MODEL,
            contents=[image_part, prompt],
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )

        raw_output = clean_json_text(response.text)
        items = json.loads(raw_output)
        if isinstance(items, list):
            return items, None
        elif isinstance(items, dict) and "items" in items:
            return items["items"], None
        return [], "Invalid JSON structure from image analysis."

    except Exception as e:
        return [], str(e)


def generate_nutrition_suggestions_with_gemini(
    meal_totals: Dict[str, float],
    items: List[Dict[str, Any]],
    api_key: Optional[str] = None
) -> Tuple[Dict[str, str], Optional[str]]:
    """
    Generates structured AI nutrition suggestions based on the meal's macro breakdown.
    Categories:
    - protein_status: Is the meal high, moderate, or low in protein?
    - meal_improvements: What can be improved?
    - affordable_alternatives: Budget-friendly alternatives (sattu, soya chunks, curd, eggs, etc.)
    - balanced_additions: Simple additions to balance the meal.
    """
    key = get_api_key(api_key)
    if not key:
        return generate_rule_based_suggestions(meal_totals, items), None

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)

        items_summary = ", ".join([f"{i.get('display_name', i.get('food_name'))} ({i.get('quantity')} {i.get('unit')})" for i in items])
        prompt = f"""
You are an expert, encouraging nutrition advisor for VitaBite.
Analyze this meal:
Items: {items_summary}
Total Calories: {meal_totals.get('calories', 0)} kcal
Protein: {meal_totals.get('protein', 0)} g
Carbohydrates: {meal_totals.get('carbohydrates', 0)} g
Fat: {meal_totals.get('fat', 0)} g

Requirements:
- Keep advice short, practical, minimalist, and easy to understand.
- Emphasize common Indian & accessible dietary staples.
- DO NOT provide medical diagnoses or claim to detect nutritional deficiencies from a single meal.
- Return ONLY a JSON object with exactly these 4 keys:
  "protein_status": "<Short assessment of protein adequacy>",
  "meal_improvements": "<1-2 concise improvements>",
  "affordable_alternatives": "<Budget-friendly smart substitutes like sattu, soya chunks, curd, boiled eggs>",
  "balanced_additions": "<Simple items like cucumber slices, a small cup of curd, or roasted seeds>"
"""
        response = client.models.generate_content(
            model=DEFAULT_GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json"
            )
        )

        raw_output = clean_json_text(response.text)
        suggestions = json.loads(raw_output)
        return suggestions, None

    except Exception:
        # Fallback to smart rule-based suggestions on any API issue
        return generate_rule_based_suggestions(meal_totals, items), None


def generate_rule_based_suggestions(
    meal_totals: Dict[str, float],
    items: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    High-quality offline rule-based nutrition suggestions based on verified macronutrient ratios.
    Ensures the website remains 100% functional even when no API key is set.
    """
    cals = meal_totals.get("calories", 0.0)
    protein = meal_totals.get("protein", 0.0)
    carbs = meal_totals.get("carbohydrates", 0.0)
    fat = meal_totals.get("fat", 0.0)

    # Protein percentage of calories (protein = 4 kcal/g)
    protein_cals = protein * 4.0
    protein_pct = (protein_cals / cals * 100.0) if cals > 0 else 0.0

    # 1. Protein status
    if protein_pct < 12.0:
        protein_status = f"Low in protein ({protein}g, representing ~{round(protein_pct)}% of meal energy). For sustained satiety and muscle maintenance, aim for 15-25g per main meal."
    elif protein_pct <= 22.0:
        protein_status = f"Moderate and balanced protein ({protein}g, representing ~{round(protein_pct)}% of meal energy). Meets standard maintenance recommendations."
    else:
        protein_status = f"High protein meal ({protein}g, representing ~{round(protein_pct)}% of meal energy). Excellent for muscle recovery and metabolic satiety."

    # 2. Meal Improvements
    if carbs > 90 and protein < 15:
        meal_improvements = "The meal is heavily carbohydrate-dense. Consider slightly moderating the portion of refined grains and pairing them with high-protein sides."
    elif fat > 30:
        meal_improvements = "Relatively elevated in dietary fats. Ensure oils and ghee are measured carefully to keep caloric density optimal."
    else:
        meal_improvements = "Good macro distribution. Ensure adequate hydration and chew slowly to support digestive comfort."

    # 3. Affordable alternatives
    affordable_alternatives = (
        "Incorporate sattu (roasted gram flour) drinks, boiled soya chunks (over 50% protein by dry weight), "
        "boiled eggs, or homemade paneer/curd for high-value protein on a modest budget."
    )

    # 4. Balanced additions
    balanced_additions = (
        "Add a side of sliced cucumbers, tomatoes, or a katori of fresh curd/dahi for dietary fiber, "
        "electrolytes, and gut-friendly probiotics."
    )

    return {
        "protein_status": protein_status,
        "meal_improvements": meal_improvements,
        "affordable_alternatives": affordable_alternatives,
        "balanced_additions": balanced_additions,
    }
