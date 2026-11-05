# VitaBite — AI-Powered Food Nutrition Website

VitaBite is a functional, responsive, and minimalist AI-powered food nutrition website built with **Python**, **Streamlit**, the official **Google Gemini API**, **Pandas**, and **Plotly**.

Designed with a clean, monochrome aesthetic (black, white, and greys), VitaBite provides instant nutrition calculations based on verified food composition tables combined with AI image recognition and dietary recommendations.

---

## Key Features

- **Minimalist Aesthetic:** Clean black-and-white visual identity, light-grey cards, rounded corners, subtle transitions, and monochromatic data visualizations.
- **Manual Food Analysis (Option A):** Natural language parsing of complex meals (e.g., *"2 rotis, 150g cooked rice, 100g dal and 1 banana"*).
- **Food Image Recognition (Option B):** Upload meal photographs (JPG, JPEG, PNG) to detect foods and estimate portions with Google Gemini Vision.
- **Human-in-the-Loop Confirmation:** Interactive table allowing users to review, confirm, or edit detected food items and portion sizes before final nutritional calculations.
- **Deterministic Nutritional Math:**
  - 4 Key Metric Cards: Calories (kcal), Protein (g), Carbohydrates (g), and Fat (g).
  - Verified Indian Food Composition database (`nutrition_data.csv`) distinguishing raw vs. cooked states (e.g., cooked rice vs. raw rice).
  - Clear attribution labeling: *Verified Database* vs. *AI-estimated*.
  - Monochromatic Plotly donut chart depicting macronutrient caloric contributions.
- **Practical AI Nutrition Guidance:** Short, actionable recommendations on protein balance, affordable substitutes (sattu, soya chunks, boiled eggs, curd), and simple balancing additions.

---

## Project Structure

```
VitaBite/
│
├── app.py                     # Main Streamlit web application & UI
├── nutrition_data.csv         # Verified Indian food nutrition dataset
├── requirements.txt           # Python dependencies
├── .env.example               # Template for API credentials
├── .gitignore                 # Excluded environments and caches
├── README.md                  # Documentation and running guide
├── assets/
│   └── sample_meal.jpg        # Natural Indian meal photo for 1-click evaluation
└── utils/
    ├── __init__.py
    ├── nutrition.py           # Database matching, unit conversions, and calculations
    └── gemini.py              # Gemini 2.5 Flash API client & suggestions
```

---

## Setup & Running Instructions

### 1. Prerequisites
- Python 3.10+ installed.

### 2. Clone / Open Directory
```bash
cd VitaBite
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Google Gemini API Key
Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).

Copy the template:
```bash
cp .env.example .env
```
Open `.env` and set your key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Alternatively, you can also paste your Gemini API key directly into the sidebar in the VitaBite web application).*

### 5. Launch the Website
```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## Verified Nutrition Database

VitaBite includes verified nutritional values per 100g for key Indian staples:
- **Grains:** Roti / Chapati, Cooked Rice, Raw Rice, Oats, Oats Porridge, Brown Bread, White Bread
- **Pulses & Legumes:** Cooked Dal, Raw Dal, Rajma, Chana / Chickpeas, Moong Dal Khichdi
- **Dairy & Proteins:** Paneer (raw & cooked), Soya Chunks (raw & boiled), Milk (cow & full cream), Curd / Yogurt, Boiled Eggs, Egg Whites, Chicken Breast, Fish
- **Healthy Fats & Snacks:** Sattu, Peanut Butter, Almonds, Poha, Upma, Idli, Dosa
- **Vegetables & Fruits:** Boiled Potato, Banana, Apple, Cucumber, Tomato

---

## Medical Disclaimer

VitaBite provides nutritional estimates for educational and lifestyle guidance only. It is not intended as medical advice, clinical dietary assessment, or diagnosis of nutritional deficiencies.
