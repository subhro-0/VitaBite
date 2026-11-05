"""Nutrition calculation and database querying utilities for VitaBite."""

import os
import re
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd

# Default path for nutrition dataset
DEFAULT_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nutrition_data.csv")

# Known alias dictionary mapping common user terms to exact dataset names
FOOD_ALIASES: Dict[str, str] = {
    # Roti & Breads
    "roti": "Roti / Chapati",
    "rotis": "Roti / Chapati",
    "chapati": "Roti / Chapati",
    "chapatis": "Roti / Chapati",
    "phulka": "Roti / Chapati",
    "fulka": "Roti / Chapati",
    "roties": "Roti / Chapati",
    "bread": "Brown Bread",
    "brown bread": "Brown Bread",
    "white bread": "White Bread",
    
    # Rice
    "rice": "Rice (Cooked)",
    "cooked rice": "Rice (Cooked)",
    "boiled rice": "Rice (Cooked)",
    "white rice": "Rice (Cooked)",
    "steamed rice": "Rice (Cooked)",
    "chawal": "Rice (Cooked)",
    "raw rice": "Rice (Raw)",
    "uncooked rice": "Rice (Raw)",
    
    # Dal & Lentils
    "dal": "Dal / Lentils (Cooked)",
    "daal": "Dal / Lentils (Cooked)",
    "dhal": "Dal / Lentils (Cooked)",
    "cooked dal": "Dal / Lentils (Cooked)",
    "lentils": "Dal / Lentils (Cooked)",
    "lentil soup": "Dal / Lentils (Cooked)",
    "yellow dal": "Dal / Lentils (Cooked)",
    "tadka dal": "Dal / Lentils (Cooked)",
    "raw dal": "Dal / Lentils (Raw)",
    "uncooked dal": "Dal / Lentils (Raw)",
    "khichdi": "Moong Dal Khichdi (Cooked)",
    "moong dal khichdi": "Moong Dal Khichdi (Cooked)",
    "rajma": "Rajma / Kidney Beans (Cooked)",
    "kidney beans": "Rajma / Kidney Beans (Cooked)",
    
    # Protein & Dairy
    "sattu": "Sattu (Roasted Gram Flour)",
    "roasted gram flour": "Sattu (Roasted Gram Flour)",
    "paneer": "Paneer (Raw)",
    "raw paneer": "Paneer (Raw)",
    "cottage cheese": "Paneer (Raw)",
    "cooked paneer": "Paneer (Cooked / Sautéed)",
    "paneer bhurji": "Paneer (Cooked / Sautéed)",
    "soya": "Soya Chunks (Boiled)",
    "soya chunks": "Soya Chunks (Boiled)",
    "soy chunks": "Soya Chunks (Boiled)",
    "cooked soya": "Soya Chunks (Boiled)",
    "raw soya chunks": "Soya Chunks (Raw)",
    "curd": "Curd / Yogurt (Plain)",
    "dahi": "Curd / Yogurt (Plain)",
    "yogurt": "Curd / Yogurt (Plain)",
    "plain yogurt": "Curd / Yogurt (Plain)",
    "milk": "Milk (Cow / Toned)",
    "toned milk": "Milk (Cow / Toned)",
    "cow milk": "Milk (Cow / Toned)",
    "full cream milk": "Milk (Full Cream)",
    "buffalo milk": "Milk (Full Cream)",
    "egg": "Egg (Boiled)",
    "eggs": "Egg (Boiled)",
    "boiled egg": "Egg (Boiled)",
    "boiled eggs": "Egg (Boiled)",
    "egg white": "Egg White (Boiled)",
    "egg whites": "Egg White (Boiled)",
    "chicken": "Chicken Breast (Cooked)",
    "chicken breast": "Chicken Breast (Cooked)",
    "boiled chicken": "Chicken Breast (Cooked)",
    "cooked chicken": "Chicken Breast (Cooked)",
    "fish": "Fish Curry",
    "fish curry": "Fish Curry",
    
    # Breakfast & Snacks
    "oats": "Oats (Rolled / Raw)",
    "raw oats": "Oats (Rolled / Raw)",
    "oatmeal": "Oats Porridge (Cooked)",
    "oats porridge": "Oats Porridge (Cooked)",
    "peanut butter": "Peanut Butter",
    "chana": "Chana / Chickpeas (Boiled)",
    "chickpeas": "Chana / Chickpeas (Boiled)",
    "boiled chana": "Chana / Chickpeas (Boiled)",
    "idli": "Idli (Steamed)",
    "idlis": "Idli (Steamed)",
    "dosa": "Dosa (Plain)",
    "dosas": "Dosa (Plain)",
    "poha": "Poha (Cooked)",
    "upma": "Upma (Cooked)",
    
    # Fruits & Vegetables
    "potato": "Potato (Boiled)",
    "potatoes": "Potato (Boiled)",
    "boiled potato": "Potato (Boiled)",
    "boiled potatoes": "Potato (Boiled)",
    "aloo": "Potato (Boiled)",
    "banana": "Banana",
    "bananas": "Banana",
    "kela": "Banana",
    "apple": "Apple",
    "apples": "Apple",
    "almond": "Almonds",
    "almonds": "Almonds",
    "badam": "Almonds",
    "cucumber": "Cucumber",
    "tomato": "Tomato",
    "tomatoes": "Tomato",
}

# Unit standard weights in grams (generic fallback)
GENERIC_UNIT_WEIGHTS: Dict[str, float] = {
    "g": 1.0,
    "gram": 1.0,
    "grams": 1.0,
    "gm": 1.0,
    "gms": 1.0,
    "kg": 1000.0,
    "ml": 1.0,
    "cup": 150.0,
    "cups": 150.0,
    "bowl": 150.0,
    "bowls": 150.0,
    "katori": 150.0,
    "tbsp": 15.0,
    "tablespoon": 15.0,
    "tablespoons": 15.0,
    "tsp": 5.0,
    "teaspoon": 5.0,
    "teaspoons": 5.0,
    "glass": 200.0,
    "plate": 250.0,
    "serving": 100.0,
    "servings": 100.0,
    "slice": 30.0,
    "slices": 30.0,
    "piece": 50.0,
    "pieces": 50.0,
    "nos": 50.0,
    "no": 50.0,
}


import io

EMBEDDED_NUTRITION_CSV = """food_name,category,state,serving_unit,serving_weight_g,calories_per_100g,protein_per_100g,carbs_per_100g,fat_per_100g
Roti / Chapati,Grains,Cooked,piece,35,264.0,9.0,55.0,2.5
Rice (Cooked),Grains,Cooked,cup,158,130.0,2.7,28.2,0.3
Rice (Raw),Grains,Raw,cup,185,365.0,7.1,80.0,0.7
Dal / Lentils (Cooked),Pulses,Cooked,bowl,150,116.0,7.0,19.0,2.0
Dal / Lentils (Raw),Pulses,Raw,cup,100,343.0,24.0,60.0,1.5
Sattu (Roasted Gram Flour),Flours,Raw,tbsp,15,413.0,25.6,65.0,5.2
Paneer (Raw),Dairy,Raw,slice,40,296.0,18.3,4.5,23.0
Paneer (Cooked / Sautéed),Dairy,Cooked,serving,100,320.0,19.0,5.0,25.0
Soya Chunks (Raw),Protein,Raw,cup,50,345.0,52.0,33.0,0.5
Soya Chunks (Boiled),Protein,Cooked,cup,120,115.0,17.3,11.0,0.2
Milk (Cow / Toned),Dairy,Liquid,glass,200,61.0,3.2,4.8,3.3
Milk (Full Cream),Dairy,Liquid,glass,200,89.0,3.4,5.0,6.5
Oats (Rolled / Raw),Grains,Raw,cup,40,389.0,16.9,66.3,6.9
Oats Porridge (Cooked),Grains,Cooked,bowl,200,71.0,2.5,12.0,1.5
Potato (Boiled),Vegetables,Cooked,medium,130,87.0,1.9,20.1,0.1
Banana,Fruits,Raw,piece,120,89.0,1.1,22.8,0.3
Curd / Yogurt (Plain),Dairy,Cooked,bowl,150,61.0,3.5,4.7,3.3
Peanut Butter,Spreads,Raw,tbsp,16,588.0,25.0,20.0,50.0
Egg (Boiled),Protein,Cooked,piece,50,155.0,13.0,1.1,11.0
Egg White (Boiled),Protein,Cooked,piece,33,52.0,10.9,0.7,0.2
Chicken Breast (Cooked),Meat,Cooked,serving,100,165.0,31.0,0.0,3.6
Chana / Chickpeas (Boiled),Pulses,Cooked,cup,164,164.0,8.9,27.4,2.6
Apple,Fruits,Raw,medium,150,52.0,0.3,13.8,0.2
Almonds,Nuts,Raw,piece,1.2,579.0,21.2,21.6,49.9
Brown Bread,Bakery,Raw,slice,30,247.0,8.5,46.0,3.4
White Bread,Bakery,Raw,slice,25,265.0,9.0,49.0,3.2
Idli (Steamed),South Indian,Cooked,piece,40,140.0,4.0,28.0,0.5
Dosa (Plain),South Indian,Cooked,piece,80,168.0,3.9,29.0,3.7
Poha (Cooked),Breakfast,Cooked,bowl,150,130.0,2.4,23.0,3.2
Upma (Cooked),Breakfast,Cooked,bowl,150,150.0,3.5,25.0,4.0
Rajma / Kidney Beans (Cooked),Pulses,Cooked,bowl,150,127.0,8.7,22.8,0.5
Fish Curry,Seafood,Cooked,serving,150,140.0,16.0,3.0,7.0
Cucumber,Vegetables,Raw,medium,100,15.0,0.7,3.6,0.1
Tomato,Vegetables,Raw,medium,100,18.0,0.9,3.9,0.2
Moong Dal Khichdi (Cooked),Mixed,Cooked,bowl,200,120.0,4.2,21.0,2.1
"""

class NutritionDatabase:
    """Manager for loading and querying nutritional data."""

    def __init__(self, csv_path: str = DEFAULT_CSV_PATH):
        self.csv_path = csv_path
        self.df: pd.DataFrame = self._load_data()

    def _load_data(self) -> pd.DataFrame:
        candidate_paths = [
            self.csv_path,
            os.path.join(os.getcwd(), "nutrition_data.csv"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nutrition_data.csv"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "nutrition_data.csv"),
            "/var/task/nutrition_data.csv",
        ]
        for p in candidate_paths:
            if os.path.exists(p):
                df = pd.read_csv(p)
                df.columns = [c.strip().lower() for c in df.columns]
                return df

        # Fail-safe embedded fallback
        df = pd.read_csv(io.StringIO(EMBEDDED_NUTRITION_CSV))
        df.columns = [c.strip().lower() for c in df.columns]
        return df

    def get_all_foods(self) -> List[str]:
        """Returns all canonical food names in the database."""
        return self.df["food_name"].tolist()

    def match_food(self, query: str) -> Optional[pd.Series]:
        """
        Matches a user food query to a row in the verified database.
        Returns the Pandas Series row if matched, else None.
        """
        if not query:
            return None
        cleaned = query.strip().lower()

        # 1. Direct alias dictionary lookup
        if cleaned in FOOD_ALIASES:
            canonical = FOOD_ALIASES[cleaned]
            match = self.df[self.df["food_name"].str.lower() == canonical.lower()]
            if not match.empty:
                return match.iloc[0]

        # 2. Exact match in dataset
        match = self.df[self.df["food_name"].str.lower() == cleaned]
        if not match.empty:
            return match.iloc[0]

        # 3. Partial / contains match in dataset
        match = self.df[self.df["food_name"].str.lower().str.contains(re.escape(cleaned), regex=True)]
        if not match.empty:
            return match.iloc[0]

        # 4. Inverted contains match (e.g. query has "cooked rice" and food_name is "Rice (Cooked)")
        for _, row in self.df.iterrows():
            canonical_lower = row["food_name"].lower()
            # Split words
            words = [w for w in re.split(r"[\s\(\)/,]+", canonical_lower) if len(w) > 2]
            if any(w in cleaned for w in words):
                return row

        return None

    def calculate_item_weight_g(self, row: Optional[pd.Series], quantity: float, unit: str) -> float:
        """
        Calculates the weight in grams for a given food item and unit.
        """
        clean_unit = unit.strip().lower() if unit else "g"

        # If already grams / kg
        if clean_unit in ["g", "gram", "grams", "gm", "gms"]:
            return float(quantity)
        if clean_unit in ["kg", "kilogram", "kilograms"]:
            return float(quantity) * 1000.0
        if clean_unit in ["ml", "milliliter"]:
            return float(quantity)

        # Check item-specific serving weight from DB if available
        if row is not None:
            db_unit = str(row.get("serving_unit", "")).strip().lower()
            db_weight = float(row.get("serving_weight_g", 100.0))
            if clean_unit in [db_unit, db_unit + "s", "piece", "pieces", "no", "nos", "slice", "slices"]:
                return float(quantity) * db_weight

        # Generic unit fallback
        if clean_unit in GENERIC_UNIT_WEIGHTS:
            return float(quantity) * GENERIC_UNIT_WEIGHTS[clean_unit]

        # If unknown unit, assume 100g per unit
        return float(quantity) * 100.0


# Singleton instance
_db_instance: Optional[NutritionDatabase] = None


def get_nutrition_db() -> NutritionDatabase:
    """Returns the singleton NutritionDatabase instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = NutritionDatabase()
    return _db_instance


def calculate_meal_nutrition(
    items: List[Dict[str, Any]],
    db: Optional[NutritionDatabase] = None
) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
    """
    Computes nutritional breakdown for a list of meal items.
    
    Each item dict should have:
    - food_name: str
    - quantity: float or int
    - unit: str
    Optional:
    - calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g (if AI estimated)
    
    Returns:
    (processed_items, meal_totals)
    """
    if db is None:
        db = get_nutrition_db()

    processed_items = []
    total_calories = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0
    total_weight = 0.0

    for item in items:
        name = str(item.get("food_name", "")).strip()
        try:
            qty = float(item.get("quantity", 1))
        except (ValueError, TypeError):
            qty = 1.0
        unit = str(item.get("unit", "serving")).strip()

        matched_row = db.match_food(name)
        weight_g = db.calculate_item_weight_g(matched_row, qty, unit)

        if matched_row is not None:
            source = "Verified Database"
            canonical_name = matched_row["food_name"]
            c_100 = float(matched_row["calories_per_100g"])
            p_100 = float(matched_row["protein_per_100g"])
            cb_100 = float(matched_row["carbs_per_100g"])
            f_100 = float(matched_row["fat_per_100g"])
            state = matched_row.get("state", "Standard")
        else:
            source = "AI-estimated"
            canonical_name = name.title()
            c_100 = float(item.get("calories_per_100g", 150.0))
            p_100 = float(item.get("protein_per_100g", 5.0))
            cb_100 = float(item.get("carbs_per_100g", 20.0))
            f_100 = float(item.get("fat_per_100g", 3.0))
            state = "Estimated"

        # Scale by weight
        factor = weight_g / 100.0
        item_calories = round(c_100 * factor, 1)
        item_protein = round(p_100 * factor, 1)
        item_carbs = round(cb_100 * factor, 1)
        item_fat = round(f_100 * factor, 1)

        total_calories += item_calories
        total_protein += item_protein
        total_carbs += item_carbs
        total_fat += item_fat
        total_weight += weight_g

        processed_items.append({
            "original_query": name,
            "display_name": canonical_name,
            "quantity": qty,
            "unit": unit,
            "weight_g": round(weight_g, 1),
            "state": state,
            "calories": item_calories,
            "protein": item_protein,
            "carbohydrates": item_carbs,
            "fat": item_fat,
            "source": source,
        })

    totals = {
        "calories": round(total_calories, 1),
        "protein": round(total_protein, 1),
        "carbohydrates": round(total_carbs, 1),
        "fat": round(total_fat, 1),
        "weight_g": round(total_weight, 1),
    }

    return processed_items, totals


def parse_natural_language_fallback(text: str) -> List[Dict[str, Any]]:
    """
    Offline rule-based parser for meal descriptions when Gemini is unreachable or offline.
    Handles phrases like: '2 rotis, 150g cooked rice, 100g dal and 1 banana'.
    """
    if not text:
        return []

    # Clean text
    clean_text = text.replace("&", ",").replace(" and ", ",")
    parts = [p.strip() for p in clean_text.split(",") if p.strip()]

    items = []
    # Regex pattern: (number optional decimals) (optional unit like g/grams/cup/piece/bowl) (food description)
    # or (number) (food)
    pattern = re.compile(
        r"^([\d\.]+)?\s*(g|grams|gm|gms|kg|ml|cup|cups|bowl|bowls|katori|tbsp|tsp|piece|pieces|slice|slices|glass)?\s*(.*)$",
        re.IGNORECASE
    )

    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        match = pattern.match(part)
        if match:
            qty_str, unit_str, food_name = match.groups()
            qty = float(qty_str) if qty_str else 1.0
            unit = unit_str.lower() if unit_str else "piece"
            food = food_name.strip()
            
            # If food name is empty, part might just be food without number (e.g. "rice")
            if not food:
                food = part
                qty = 1.0
                unit = "serving"
            
            items.append({
                "food_name": food,
                "quantity": qty,
                "unit": unit
            })
        else:
            items.append({
                "food_name": part,
                "quantity": 1.0,
                "unit": "serving"
            })

    return items
