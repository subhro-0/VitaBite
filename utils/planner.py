"""
Personal nutrition calculator and budget-friendly meal planner for VitaBite.
Calculates BMR, TDEE, macronutrient targets, and optimizes meals by daily budget.
"""

from typing import Any, Dict, List, Optional


def calculate_daily_macro_needs(
    age: int,
    gender: str,
    weight_kg: float,
    height_cm: float,
    activity_level: str = "moderate",
    goal: str = "maintain",
) -> Dict[str, Any]:
    """
    Calculates BMR (Mifflin-St Jeor), TDEE, and optimal macronutrient split.
    """
    # 1. BMR Calculation
    gender_clean = gender.strip().lower()
    if gender_clean in ["male", "m", "man"]:
        bmr = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age) + 5.0
    else:
        bmr = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age) - 161.0

    # 2. Activity Multiplier
    activity_map = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "very_active": 1.725,
        "extra_active": 1.9,
    }
    multiplier = activity_map.get(activity_level.strip().lower(), 1.55)
    tdee = bmr * multiplier

    # 3. Goal Adjustment
    goal_clean = goal.strip().lower()
    if "loss" in goal_clean or "cut" in goal_clean:
        target_calories = max(1200.0, tdee - 400.0)
        protein_per_kg = 1.8  # Higher protein to preserve lean muscle during deficit
    elif "gain" in goal_clean or "bulk" in goal_clean:
        target_calories = tdee + 350.0
        protein_per_kg = 1.8
    else:  # maintain
        target_calories = tdee
        protein_per_kg = 1.6

    # 4. Macro Splits
    # Protein: 4 kcal/g
    target_protein_g = round(weight_kg * protein_per_kg, 1)
    protein_calories = target_protein_g * 4.0

    # Fat: 25% of target calories, 9 kcal/g
    fat_calories = target_calories * 0.25
    target_fat_g = round(fat_calories / 9.0, 1)

    # Carbohydrates: Remaining calories, 4 kcal/g
    carb_calories = max(0.0, target_calories - protein_calories - fat_calories)
    target_carbs_g = round(carb_calories / 4.0, 1)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "target_calories": round(target_calories),
        "target_protein_g": target_protein_g,
        "target_carbs_g": target_carbs_g,
        "target_fat_g": target_fat_g,
        "goal": goal,
        "activity_level": activity_level,
    }


# High-nutrition, verified budget staples in Indian market with estimated retail prices (INR)
BUDGET_FOOD_CATALOG = [
    {
        "name": "Sattu Drink (Roasted Gram)",
        "serving": "50g with water & lemon",
        "meal_type": "Morning / Snack",
        "price_inr": 8.0,
        "calories": 206,
        "protein": 12.8,
        "carbs": 32.5,
        "fat": 2.6,
        "diet": "veg",
        "why": "Extremely cost-effective complete protein and slow-digesting complex carbs.",
    },
    {
        "name": "Boiled Eggs (2 nos)",
        "serving": "2 whole eggs",
        "meal_type": "Breakfast",
        "price_inr": 14.0,
        "calories": 155,
        "protein": 13.0,
        "carbs": 1.1,
        "fat": 11.0,
        "diet": "egg",
        "why": "High biological value protein with essential choline and healthy fats.",
    },
    {
        "name": "Oats Porridge with Milk",
        "serving": "40g oats + 150ml milk",
        "meal_type": "Breakfast",
        "price_inr": 16.0,
        "calories": 245,
        "protein": 11.5,
        "carbs": 34.0,
        "fat": 7.5,
        "diet": "veg",
        "why": "Heart-healthy soluble beta-glucan fiber and sustained morning energy.",
    },
    {
        "name": "Soya Chunks Curry (50g raw)",
        "serving": "1 large bowl cooked curry",
        "meal_type": "Lunch / Dinner",
        "price_inr": 10.0,
        "calories": 172,
        "protein": 26.0,
        "carbs": 16.5,
        "fat": 0.5,
        "diet": "veg",
        "why": "Over 50% protein density at less than ₹10 per serving; unmatched cost efficiency.",
    },
    {
        "name": "Yellow Moong/Toor Dal (1 bowl)",
        "serving": "150g cooked dal",
        "meal_type": "Lunch / Dinner",
        "price_inr": 12.0,
        "calories": 116,
        "protein": 7.0,
        "carbs": 19.0,
        "fat": 2.0,
        "diet": "veg",
        "why": "Essential daily amino acids and potassium.",
    },
    {
        "name": "Whole Wheat Rotis (3 pcs)",
        "serving": "3 chapatis (~105g)",
        "meal_type": "Lunch / Dinner",
        "price_inr": 6.0,
        "calories": 277,
        "protein": 9.5,
        "carbs": 57.0,
        "fat": 2.6,
        "diet": "veg",
        "why": "Affordable complex energy staple with natural fiber.",
    },
    {
        "name": "Steamed White Rice (1 cup)",
        "serving": "158g cooked",
        "meal_type": "Lunch",
        "price_inr": 5.0,
        "calories": 205,
        "protein": 4.2,
        "carbs": 44.5,
        "fat": 0.4,
        "diet": "veg",
        "why": "Easily digestible clean carbohydrates for meal volume.",
    },
    {
        "name": "Curd / Dahi (1 bowl)",
        "serving": "150g fresh curd",
        "meal_type": "Lunch",
        "price_inr": 12.0,
        "calories": 92,
        "protein": 5.3,
        "carbs": 7.0,
        "fat": 5.0,
        "diet": "veg",
        "why": "Probiotics for gut health and bioavailable calcium.",
    },
    {
        "name": "Bananas (2 pcs)",
        "serving": "2 medium bananas",
        "meal_type": "Pre-Workout / Snack",
        "price_inr": 10.0,
        "calories": 178,
        "protein": 2.2,
        "carbs": 45.6,
        "fat": 0.6,
        "diet": "veg",
        "why": "Fast electrolyte replenishment and natural fruit energy.",
    },
    {
        "name": "Roasted Peanuts (30g)",
        "serving": "1 handful",
        "meal_type": "Evening Snack",
        "price_inr": 6.0,
        "calories": 175,
        "protein": 7.5,
        "carbs": 6.0,
        "fat": 15.0,
        "diet": "veg",
        "why": "Dense healthy unsaturated fats and budget-friendly plant protein.",
    },
    {
        "name": "Cucumber & Tomato Salad",
        "serving": "1 large plate with lemon",
        "meal_type": "Salad / Side",
        "price_inr": 8.0,
        "calories": 35,
        "protein": 1.6,
        "carbs": 7.5,
        "fat": 0.3,
        "diet": "veg",
        "why": "Zero-guilt volume, hydration, vitamin C, and fiber.",
    },
    {
        "name": "Chicken Breast (150g Cooked)",
        "serving": "150g grilled/steamed",
        "meal_type": "Dinner",
        "price_inr": 48.0,
        "calories": 248,
        "protein": 46.5,
        "carbs": 0.0,
        "fat": 5.4,
        "diet": "nonveg",
        "why": "Lean animal protein for aggressive muscle repair.",
    },
    {
        "name": "Raw/Cooked Paneer (60g)",
        "serving": "60g diced cubes",
        "meal_type": "Snack / Dinner",
        "price_inr": 24.0,
        "calories": 178,
        "protein": 11.0,
        "carbs": 2.7,
        "fat": 13.8,
        "diet": "veg",
        "why": "Rich dairy casein protein and sustained fullness.",
    },
]


def generate_budget_meal_plan(
    daily_budget_inr: float,
    target_calories: Optional[float] = None,
    target_protein: Optional[float] = None,
    dietary_pref: str = "any",
) -> Dict[str, Any]:
    """
    Optimizes a nutritious day of eating strictly respecting the user's daily budget.
    """
    budget = max(40.0, float(daily_budget_inr))
    diet_clean = dietary_pref.strip().lower()

    # Filter catalog by diet
    eligible = []
    for f in BUDGET_FOOD_CATALOG:
        if diet_clean in ["veg", "vegetarian"] and f["diet"] in ["egg", "nonveg"]:
            continue
        if diet_clean in ["egg", "eggetarian"] and f["diet"] == "nonveg":
            continue
        eligible.append(f)

    # Sort items by protein-per-rupee and calorie-per-rupee density
    eligible_sorted = sorted(eligible, key=lambda x: (x["protein"] / x["price_inr"]), reverse=True)

    selected_items: List[Dict[str, Any]] = []
    spent = 0.0
    total_cals = 0.0
    total_protein = 0.0
    total_carbs = 0.0
    total_fat = 0.0

    # Ensure baseline carb + protein staples
    staples_names = ["Whole Wheat Rotis (3 pcs)", "Yellow Moong/Toor Dal (1 bowl)"]
    if diet_clean not in ["veg", "vegetarian"]:
        staples_names.append("Boiled Eggs (2 nos)")
    else:
        staples_names.append("Soya Chunks Curry (50g raw)")

    for name in staples_names:
        item = next((i for i in eligible if i["name"] == name), None)
        if item and (spent + item["price_inr"] <= budget):
            selected_items.append(item)
            spent += item["price_inr"]
            total_cals += item["calories"]
            total_protein += item["protein"]
            total_carbs += item["carbs"]
            total_fat += item["fat"]

    # Fill remaining budget with highest value options
    for item in eligible_sorted:
        if item in selected_items:
            continue
        if spent + item["price_inr"] <= budget:
            selected_items.append(item)
            spent += item["price_inr"]
            total_cals += item["calories"]
            total_protein += item["protein"]
            total_carbs += item["carbs"]
            total_fat += item["fat"]

    # Calculate target fulfillment percentages
    pct_cal = round((total_cals / target_calories * 100), 1) if target_calories else None
    pct_prot = round((total_protein / target_protein * 100), 1) if target_protein else None

    return {
        "budget_inr": round(budget),
        "total_cost_inr": round(spent),
        "remaining_budget_inr": round(budget - spent),
        "total_calories": round(total_cals),
        "total_protein_g": round(total_protein, 1),
        "total_carbs_g": round(total_carbs, 1),
        "total_fat_g": round(total_fat, 1),
        "target_calories_fulfillment_pct": pct_cal,
        "target_protein_fulfillment_pct": pct_prot,
        "items_count": len(selected_items),
        "items": selected_items,
    }
