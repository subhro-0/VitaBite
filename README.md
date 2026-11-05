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

## Deploying Directly on Vercel (via GitHub)

VitaBite is fully configured for **1-click deployment on Vercel**:

### 1. Push code to your GitHub Repository:
```bash
git init
git add .
git commit -m "VitaBite Vercel Ready"
git branch -M main
git remote add origin https://github.com/<your-username>/VitaBite.git
git push -u origin main
```

### 2. Deploy on Vercel:
1. Go to **[vercel.com](https://vercel.com)** and click **"Add New Project"**.
2. Select and import your **`VitaBite`** repository from GitHub.
3. Keep the default settings (Vercel automatically detects `vercel.json` and Python backend in `api/index.py`).
4. Under **Environment Variables**, add:
   - **Name:** `GEMINI_API_KEY`
   - **Value:** `your_gemini_api_key_here`
5. Click **Deploy**.

Vercel will build and launch your application with a public `https://vitabite-*.vercel.app` URL!

---

## Running Locally

### Option 1: Fast Full-Stack App (Vercel Simulation)
```bash
uvicorn api.index:app --reload --port 8000
```
Open `public/index.html` or visit `http://localhost:8000`.

### Option 2: Streamlit Interface
```bash
streamlit run app.py
```
Open `http://localhost:8501`.

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
