"""Automated verification script for VitaBite core functionality."""

import unittest
from utils.nutrition import (
    get_nutrition_db,
    calculate_meal_nutrition,
    parse_natural_language_fallback,
    FOOD_ALIASES,
)
from utils.gemini import generate_rule_based_suggestions


class TestVitaBiteCore(unittest.TestCase):
    def setUp(self):
        self.db = get_nutrition_db()

    def test_database_loaded(self):
        self.assertGreater(len(self.db.df), 20)
        required_foods = [
            "Rice (Cooked)", "Roti / Chapati", "Dal / Lentils (Cooked)",
            "Sattu (Roasted Gram Flour)", "Paneer (Raw)", "Soya Chunks (Boiled)",
            "Milk (Cow / Toned)", "Oats (Rolled / Raw)", "Potato (Boiled)",
            "Banana", "Curd / Yogurt (Plain)", "Peanut Butter"
        ]
        db_foods = self.db.get_all_foods()
        for f in required_foods:
            self.assertIn(f, db_foods, f"Missing required food: {f}")

    def test_raw_vs_cooked_distinction(self):
        cooked_rice = self.db.match_food("Rice (Cooked)")
        raw_rice = self.db.match_food("Rice (Raw)")
        self.assertIsNotNone(cooked_rice)
        self.assertIsNotNone(raw_rice)
        self.assertNotEqual(cooked_rice["calories_per_100g"], raw_rice["calories_per_100g"])
        self.assertEqual(cooked_rice["state"], "Cooked")
        self.assertEqual(raw_rice["state"], "Raw")

    def test_alias_matching(self):
        test_cases = [
            ("2 rotis", "Roti / Chapati"),
            ("chapati", "Roti / Chapati"),
            ("cooked rice", "Rice (Cooked)"),
            ("dal", "Dal / Lentils (Cooked)"),
            ("dahi", "Curd / Yogurt (Plain)"),
            ("soya chunks", "Soya Chunks (Boiled)"),
            ("boiled egg", "Egg (Boiled)"),
        ]
        for query, expected_name in test_cases:
            match = self.db.match_food(query)
            self.assertIsNotNone(match, f"Failed to match query: {query}")
            self.assertEqual(match["food_name"], expected_name)

    def test_fallback_natural_language_parser(self):
        text = "2 rotis, 150g cooked rice, 100g dal and 1 banana"
        items = parse_natural_language_fallback(text)
        self.assertEqual(len(items), 4)
        
        # Check roti
        self.assertEqual(items[0]["quantity"], 2.0)
        self.assertIn("roti", items[0]["food_name"].lower())

        # Check rice
        self.assertEqual(items[1]["quantity"], 150.0)
        self.assertEqual(items[1]["unit"], "g")

        # Check dal
        self.assertEqual(items[2]["quantity"], 100.0)
        self.assertEqual(items[2]["unit"], "g")

        # Check banana
        self.assertEqual(items[3]["quantity"], 1.0)

    def test_meal_nutrition_calculation(self):
        items = [
            {"food_name": "Roti", "quantity": 2, "unit": "piece"},
            {"food_name": "cooked rice", "quantity": 150, "unit": "g"},
            {"food_name": "dal", "quantity": 100, "unit": "g"},
            {"food_name": "banana", "quantity": 1, "unit": "piece"},
        ]
        proc, totals = calculate_meal_nutrition(items, self.db)
        
        # Verify calories are computed accurately
        # 2 rotis (70g) ~ 184.8 kcal
        # 150g cooked rice ~ 195 kcal
        # 100g cooked dal ~ 116 kcal
        # 1 banana (120g) ~ 106.8 kcal
        # Total ~ 602.6 kcal
        self.assertAlmostEqual(totals["calories"], 602.6, places=1)
        self.assertGreater(totals["protein"], 15.0)
        self.assertGreater(totals["carbohydrates"], 100.0)
        self.assertGreater(totals["fat"], 3.0)

        # Check all sources are verified database
        for item in proc:
            self.assertEqual(item["source"], "Verified Database")

    def test_ai_fallback_suggestions(self):
        totals = {"calories": 602.6, "protein": 18.7, "carbohydrates": 127.2, "fat": 4.6}
        items = [{"food_name": "Roti", "quantity": 2, "unit": "piece"}]
        suggestions = generate_rule_based_suggestions(totals, items)
        
        self.assertIn("protein_status", suggestions)
        self.assertIn("meal_improvements", suggestions)
        self.assertIn("affordable_alternatives", suggestions)
        self.assertIn("balanced_additions", suggestions)
        self.assertIn("sattu", suggestions["affordable_alternatives"].lower())


if __name__ == "__main__":
    unittest.main()
