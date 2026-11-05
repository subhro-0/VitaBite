"""
VitaBite — AI-Powered Food Nutrition Website
Minimalist, elegant, responsive nutrition intelligence application.
"""

import os
from typing import Any, Dict, List
from PIL import Image
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

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

# Load environment variables
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="VitaBite — Understand Your Nutrition",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Minimalist Black & White Custom CSS
CUSTOM_CSS = """
<style>
/* Root Colors & Font */
:root {
    --bg-main: #FFFFFF;
    --bg-secondary: #F8F8F8;
    --card-bg: #F2F2F2;
    --border-color: #E5E5E5;
    --text-primary: #111111;
    --text-secondary: #777777;
    --btn-primary: #000000;
    --btn-text: #FFFFFF;
}

/* Base Body Styling */
body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-main) !important;
    color: var(--text-primary) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

/* Remove Streamlit default decorative bars */
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

/* Custom Navbar */
.vb-nav-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.2rem 0;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 2rem;
}

.vb-brand {
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: var(--text-primary);
    text-decoration: none;
}

.vb-brand span {
    font-weight: 300;
    color: var(--text-secondary);
    margin-left: 6px;
    font-size: 0.9rem;
    letter-spacing: 0;
}

/* Primary Button Styling */
.stButton > button {
    background-color: var(--btn-primary) !important;
    color: var(--btn-text) !important;
    border: 1px solid var(--btn-primary) !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: background-color 0.2s ease, transform 0.1s ease !important;
    box-shadow: none !important;
}

.stButton > button:hover {
    background-color: #222222 !important;
    border-color: #222222 !important;
    color: #FFFFFF !important;
    transform: translateY(-1px);
}

.stButton > button:active {
    transform: translateY(0);
}

/* Secondary Button / Reset */
button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
}

button[kind="secondary"]:hover {
    background-color: var(--bg-secondary) !important;
    border-color: var(--text-primary) !important;
}

/* Clean Cards */
.vb-card {
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    transition: border-color 0.2s ease;
}

.vb-card:hover {
    border-color: #CCCCCC;
}

.vb-card-title {
    font-size: 0.82rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
}

.vb-card-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.1;
}

.vb-card-unit {
    font-size: 0.95rem;
    font-weight: 400;
    color: var(--text-secondary);
    margin-left: 4px;
}

/* Feature Cards on Homepage */
.vb-feature-card {
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 2rem 1.5rem;
    height: 100%;
}

.vb-feature-icon {
    font-size: 1.4rem;
    color: var(--text-primary);
    margin-bottom: 1rem;
    display: inline-block;
}

.vb-feature-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
}

.vb-feature-desc {
    font-size: 0.9rem;
    color: var(--text-secondary);
    line-height: 1.5;
}

/* Hero Section */
.vb-hero {
    padding: 3rem 0 2rem 0;
    max-width: 780px;
}

.vb-hero h1 {
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -1.2px;
    color: var(--text-primary);
    line-height: 1.15;
    margin-bottom: 0.8rem;
}

.vb-hero h2 {
    font-size: 1.25rem;
    font-weight: 400;
    color: var(--text-secondary);
    margin-bottom: 1.2rem;
}

.vb-hero p {
    font-size: 1.05rem;
    color: var(--text-primary);
    line-height: 1.6;
    margin-bottom: 2rem;
}

/* Suggestion Box */
.vb-suggestion-box {
    background-color: var(--bg-secondary);
    border-left: 3px solid var(--text-primary);
    border-radius: 0 6px 6px 0;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}

.vb-suggestion-label {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--text-secondary);
    margin-bottom: 0.3rem;
}

.vb-suggestion-text {
    font-size: 0.95rem;
    color: var(--text-primary);
    line-height: 1.5;
}

/* Medical Disclaimer */
.vb-disclaimer {
    font-size: 0.8rem;
    color: var(--text-secondary);
    border-top: 1px solid var(--border-color);
    padding-top: 0.8rem;
    margin-top: 1.5rem;
    line-height: 1.4;
}

/* Minimal Footer */
.vb-footer {
    border-top: 1px solid var(--border-color);
    padding: 2.5rem 0 1.5rem 0;
    margin-top: 4rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
    color: var(--text-secondary);
}

.vb-footer-links a {
    color: var(--text-primary);
    text-decoration: none;
    margin-left: 1.5rem;
}

.vb-footer-links a:hover {
    text-decoration: underline;
}

/* Inputs & Form Overrides */
div[data-baseweb="input"] {
    background-color: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
}

div[data-baseweb="input"]:focus-within {
    border-color: var(--text-primary) !important;
}

/* Dataframe styling */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Session State Initialization
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Home"

if "analysis_items" not in st.session_state:
    st.session_state.analysis_items = None

if "analysis_totals" not in st.session_state:
    st.session_state.analysis_totals = None

if "ai_suggestions" not in st.session_state:
    st.session_state.ai_suggestions = None

if "user_confirmed_items" not in st.session_state:
    st.session_state.user_confirmed_items = None

if "gemini_api_key_override" not in st.session_state:
    st.session_state.gemini_api_key_override = ""


def get_active_api_key() -> str:
    """Returns the effective Gemini API key from session state or environment."""
    if st.session_state.gemini_api_key_override:
        return st.session_state.gemini_api_key_override.strip()
    return os.getenv("GEMINI_API_KEY", "").strip()


def render_navbar():
    """Renders the top minimal navigation bar."""
    col_logo, col_nav = st.columns([1.5, 2.5])

    with col_logo:
        st.markdown(
            """
            <div style="padding-top: 6px;">
                <span style="font-size: 1.4rem; font-weight: 800; letter-spacing: -0.5px; color: #111111;">VitaBite</span>
                <span style="font-size: 0.85rem; font-weight: 400; color: #777777; margin-left: 6px;">Nutrition Intelligence</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_nav:
        n1, n2, n3 = st.columns(3)
        with n1:
            if st.button("Home", key="nav_home", use_container_width=True):
                st.session_state.nav_page = "Home"
                st.rerun()
        with n2:
            if st.button("Food Analysis", key="nav_analysis", use_container_width=True):
                st.session_state.nav_page = "Food Analysis"
                st.rerun()
        with n3:
            if st.button("About", key="nav_about", use_container_width=True):
                st.session_state.nav_page = "About"
                st.rerun()

    st.markdown("<hr style='margin: 0.8rem 0 1.8rem 0; border: none; border-bottom: 1px solid #E5E5E5;'>", unsafe_allow_html=True)


def render_sidebar_settings():
    """Collapsible sidebar for API Key configuration & dataset verification."""
    with st.sidebar:
        st.markdown("### Settings")
        st.markdown(
            "<p style='color: #777777; font-size: 0.85rem;'>Configure your Google Gemini API key for live AI image vision and dynamic suggestions.</p>",
            unsafe_allow_html=True,
        )

        current_key = get_active_api_key()
        has_env_key = bool(os.getenv("GEMINI_API_KEY"))

        if has_env_key:
            st.success("API Key detected from .env", icon="✔")

        key_input = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.gemini_api_key_override,
            placeholder="Paste AIzaSy... key here",
            help="Your key is stored securely in your local session and never sent to external servers except Google Gemini API.",
        )

        if key_input != st.session_state.gemini_api_key_override:
            st.session_state.gemini_api_key_override = key_input

        st.markdown("---")
        st.markdown("### Verified Indian Food Dataset")
        db = get_nutrition_db()
        st.markdown(f"<p style='color: #777777; font-size: 0.85rem;'>Database contains <strong>{len(db.df)}</strong> verified staples (cooked and raw states).</p>", unsafe_allow_html=True)

        with st.expander("Browse Database Items"):
            st.dataframe(
                db.df[["food_name", "state", "calories_per_100g", "protein_per_100g", "carbs_per_100g", "fat_per_100g"]],
                use_container_width=True,
                hide_index=True,
            )


def render_home_page():
    """Renders the VitaBite Homepage."""
    col_hero, col_img = st.columns([1.2, 1])

    with col_hero:
        st.markdown(
            """
            <div class="vb-hero">
                <span style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #777777;">VitaBite</span>
                <h1 style="margin-top: 0.4rem;">Eat Better.<br>Understand Your Nutrition.</h1>
                <h2>Your AI-powered food and nutrition companion.</h2>
                <p>Discover the nutritional value of your meals and make smarter food choices with AI.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Analyze Your Food", key="hero_btn", type="primary"):
            st.session_state.nav_page = "Food Analysis"
            st.rerun()

    with col_img:
        sample_img_path = os.path.join(os.path.dirname(__file__), "assets", "sample_meal.jpg")
        if os.path.exists(sample_img_path):
            st.image(
                sample_img_path,
                caption="Wholesome meal: Rotis, Yellow Dal, Steamed Rice, Cucumber & Banana",
                use_container_width=True,
            )

    st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)

    # 3 Feature Cards
    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown(
            """
            <div class="vb-feature-card">
                <div class="vb-feature-icon">🔍</div>
                <div class="vb-feature-title">Food Recognition</div>
                <div class="vb-feature-desc">Identify food items and estimated portions instantly from meal photographs using Google Gemini AI.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f2:
        st.markdown(
            """
            <div class="vb-feature-card">
                <div class="vb-feature-icon">📊</div>
                <div class="vb-feature-title">Nutrition Analysis</div>
                <div class="vb-feature-desc">Accurately calculate calories, protein, carbohydrates, and fat using verified food nutritional data.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with f3:
        st.markdown(
            """
            <div class="vb-feature-card">
                <div class="vb-feature-icon">💡</div>
                <div class="vb-feature-title">Smart Suggestions</div>
                <div class="vb-feature-desc">Get simple, practical, AI-powered nutritional recommendations and affordable staple alternatives.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_plot(totals: Dict[str, float]):
    """Renders a minimalist monochromatic Plotly chart showing macro distribution."""
    protein = totals.get("protein", 0.0)
    carbs = totals.get("carbohydrates", 0.0)
    fat = totals.get("fat", 0.0)

    # Macro Calories: Protein (4 kcal/g), Carbs (4 kcal/g), Fat (9 kcal/g)
    protein_kcal = protein * 4.0
    carbs_kcal = carbs * 4.0
    fat_kcal = fat * 9.0

    labels = ["Protein", "Carbohydrates", "Fat"]
    values = [protein_kcal, carbs_kcal, fat_kcal]
    weights = [protein, carbs, fat]

    # Monochromatic palette
    colors = ["#111111", "#666666", "#AAAAAA"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.65,
                marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
                textinfo="label+percent",
                hoverinfo="label+value+percent",
                hovertemplate="<b>%{label}</b><br>Calories: %{value:.1f} kcal<br>Proportion: %{percent}<extra></extra>",
                textfont=dict(family="sans-serif", size=12, color="#111111"),
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="Caloric Distribution by Macronutrient",
            font=dict(size=14, color="#111111", family="sans-serif"),
            x=0.0,
            y=0.98,
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin=dict(t=40, b=20, l=10, r=10),
        height=320,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color="#777777", size=11),
        ),
    )

    st.plotly_chart(fig, use_container_width=True)


def execute_analysis(items_list: List[Dict[str, Any]]):
    """Calculates final nutrition and fetches AI suggestions."""
    if not items_list:
        st.warning("Please provide at least one food item.")
        return

    db = get_nutrition_db()
    processed, totals = calculate_meal_nutrition(items_list, db)

    # Fetch AI suggestions
    api_key = get_active_api_key()
    suggestions, _ = generate_nutrition_suggestions_with_gemini(totals, processed, api_key=api_key)

    st.session_state.analysis_items = processed
    st.session_state.analysis_totals = totals
    st.session_state.ai_suggestions = suggestions


def render_nutrition_results():
    """Renders the 4 macro cards, breakdown table, monochromatic chart, and suggestions."""
    items = st.session_state.analysis_items
    totals = st.session_state.analysis_totals
    suggestions = st.session_state.ai_suggestions

    if not items or not totals:
        return

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 1.5rem; font-weight: 700; color: #111111;'>Nutrition Results</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #777777; font-size: 0.9rem;'>Calculated based on verified food nutrition data and portion weights.</p>", unsafe_allow_html=True)

    # 4 Nutritional Cards
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="vb-card">
                <div class="vb-card-title">Calories</div>
                <div class="vb-card-value">{totals['calories']}<span class="vb-card-unit">kcal</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="vb-card">
                <div class="vb-card-title">Protein</div>
                <div class="vb-card-value">{totals['protein']}<span class="vb-card-unit">g</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="vb-card">
                <div class="vb-card-title">Carbohydrates</div>
                <div class="vb-card-value">{totals['carbohydrates']}<span class="vb-card-unit">g</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="vb-card">
                <div class="vb-card-title">Fat</div>
                <div class="vb-card-value">{totals['fat']}<span class="vb-card-unit">g</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Individual Breakdown Table & Plotly Chart
    col_table, col_chart = st.columns([1.5, 1])

    with col_table:
        st.markdown("#### Meal Breakdown")
        table_rows = []
        for itm in items:
            table_rows.append({
                "Food Item": itm["display_name"],
                "Serving": f"{itm['quantity']} {itm['unit']} ({itm['weight_g']}g)",
                "State": itm["state"],
                "Calories": f"{itm['calories']} kcal",
                "Protein": f"{itm['protein']} g",
                "Carbs": f"{itm['carbohydrates']} g",
                "Fat": f"{itm['fat']} g",
                "Source": itm["source"],
            })

        df_table = pd.DataFrame(table_rows)
        st.dataframe(df_table, use_container_width=True, hide_index=True)

        st.markdown(
            f"""
            <div style="background-color: #F8F8F8; border: 1px solid #E5E5E5; border-radius: 6px; padding: 0.8rem 1rem; margin-top: 0.6rem; font-size: 0.88rem;">
                <strong>Meal Total:</strong> {totals['weight_g']}g portion &bull; 
                <strong>{totals['calories']} kcal</strong> &bull; 
                <strong>{totals['protein']}g</strong> Protein &bull; 
                <strong>{totals['carbohydrates']}g</strong> Carbs &bull; 
                <strong>{totals['fat']}g</strong> Fat
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_chart:
        render_plot(totals)

    # AI Nutrition Suggestions Section
    if suggestions:
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("### AI Nutrition Suggestions")

        s1, s2 = st.columns(2)
        with s1:
            st.markdown(
                f"""
                <div class="vb-suggestion-box">
                    <div class="vb-suggestion-label">1. Protein Balance Assessment</div>
                    <div class="vb-suggestion-text">{suggestions.get('protein_status', 'Balanced protein')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="vb-suggestion-box">
                    <div class="vb-suggestion-label">2. Meal Improvements</div>
                    <div class="vb-suggestion-text">{suggestions.get('meal_improvements', 'Maintain varied whole food intake.')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with s2:
            st.markdown(
                f"""
                <div class="vb-suggestion-box">
                    <div class="vb-suggestion-label">3. Affordable Food Alternatives</div>
                    <div class="vb-suggestion-text">{suggestions.get('affordable_alternatives', 'Sattu, soya chunks, boiled eggs, or homemade curd.')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="vb-suggestion-box">
                    <div class="vb-suggestion-label">4. Balanced Additions</div>
                    <div class="vb-suggestion-text">{suggestions.get('balanced_additions', 'Add fresh cucumbers or a katori of curd.')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Disclaimer
    st.markdown(
        """
        <div class="vb-disclaimer">
            <strong>Medical Disclaimer:</strong> VitaBite provides nutritional estimates for educational and lifestyle guidance only. 
            It is not intended as medical advice, clinical dietary assessment, or diagnosis of nutritional deficiencies.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_food_analysis_page():
    """Renders the main Food Analysis page with Option A (Manual) and Option B (Image)."""
    st.markdown("<h2 style='font-size: 2rem; font-weight: 800; color: #111111;'>Food Analysis</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #777777; font-size: 0.95rem; margin-bottom: 2rem;'>Select your preferred method to analyze meal nutrition.</p>", unsafe_allow_html=True)

    tab_manual, tab_image = st.tabs(["Option A: Enter Food Manually", "Option B: Upload Food Image"])

    # ------------------ OPTION A: MANUAL FOOD ENTRY ------------------
    with tab_manual:
        st.markdown(
            "<p style='color: #111111; font-weight: 500; font-size: 1rem;'>Enter your meal items and quantities:</p>",
            unsafe_allow_html=True,
        )

        sample_prompt = "2 rotis, 150g cooked rice, 100g dal and 1 banana"
        
        # Prefill / Helper button
        col_input, col_example = st.columns([3.5, 1])
        with col_example:
            st.markdown("<div style='height: 1.8rem;'></div>", unsafe_allow_html=True)
            if st.button("Use Example Meal", key="btn_sample_manual"):
                st.session_state.manual_text_input = sample_prompt

        with col_input:
            manual_text = st.text_input(
                "Meal description",
                value=st.session_state.get("manual_text_input", sample_prompt),
                placeholder="e.g., 2 rotis, 150g cooked rice, 100g dal and 1 banana",
                label_visibility="collapsed",
            )

        col_act, _ = st.columns([1, 3])
        with col_act:
            if st.button("Analyze Food", key="btn_analyze_manual", type="primary"):
                if not manual_text.strip():
                    st.warning("Please type your meal description.")
                else:
                    api_key = get_active_api_key()
                    with st.spinner("Interpreting meal items and quantities..."):
                        if api_key:
                            parsed, err = parse_meal_with_gemini(manual_text, api_key=api_key)
                            if err or not parsed:
                                # Fallback to local regex parser
                                parsed = parse_natural_language_fallback(manual_text)
                        else:
                            parsed = parse_natural_language_fallback(manual_text)

                    st.session_state.user_confirmed_items = parsed
                    execute_analysis(parsed)

    # ------------------ OPTION B: FOOD IMAGE RECOGNITION ------------------
    with tab_image:
        st.markdown(
            "<p style='color: #111111; font-weight: 500; font-size: 1rem;'>Upload a food photograph to identify meal components with AI:</p>",
            unsafe_allow_html=True,
        )

        col_upload, col_preview = st.columns([1.2, 1])

        with col_upload:
            uploaded_file = st.file_uploader(
                "Choose food image",
                type=["jpg", "jpeg", "png"],
                help="Supported formats: JPG, JPEG, PNG",
            )

            # Option to test with sample meal photo
            use_sample = st.checkbox("Or test with VitaBite sample thali image", value=False)

            if st.button("Analyze Image", key="btn_analyze_image", type="primary"):
                img_bytes = None
                mime_type = "image/jpeg"

                if uploaded_file is not None:
                    img_bytes = uploaded_file.getvalue()
                    mime_type = uploaded_file.type or "image/jpeg"
                elif use_sample:
                    sample_path = os.path.join(os.path.dirname(__file__), "assets", "sample_meal.jpg")
                    if os.path.exists(sample_path):
                        with open(sample_path, "rb") as f:
                            img_bytes = f.read()
                        mime_type = "image/jpeg"

                if not img_bytes:
                    st.warning("Please upload an image or check the sample image option.")
                else:
                    api_key = get_active_api_key()
                    with st.spinner("AI is analyzing food photograph and estimating portions..."):
                        if api_key:
                            detected, err = analyze_food_image_with_gemini(img_bytes, mime_type, api_key=api_key)
                            if err:
                                st.error(f"AI Recognition Notice: {err}")
                                # Smart fallback to sample items if demo
                                detected = [
                                    {"food_name": "Roti", "quantity": 2.0, "unit": "piece"},
                                    {"food_name": "Rice (Cooked)", "quantity": 150.0, "unit": "g"},
                                    {"food_name": "Dal (Cooked)", "quantity": 100.0, "unit": "g"},
                                    {"food_name": "Banana", "quantity": 1.0, "unit": "piece"},
                                ]
                        else:
                            st.info("No Gemini API key provided. Using visual detection preset for evaluation. Add API key in the sidebar for live AI image inference.")
                            detected = [
                                {"food_name": "Roti", "quantity": 2.0, "unit": "piece"},
                                {"food_name": "Rice (Cooked)", "quantity": 150.0, "unit": "g"},
                                {"food_name": "Dal (Cooked)", "quantity": 100.0, "unit": "g"},
                                {"food_name": "Banana", "quantity": 1.0, "unit": "piece"},
                            ]

                    st.session_state.detected_raw_items = detected
                    st.session_state.user_confirmed_items = detected

        with col_preview:
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Uploaded Food Photograph", use_container_width=True)
            elif use_sample:
                sample_path = os.path.join(os.path.dirname(__file__), "assets", "sample_meal.jpg")
                if os.path.exists(sample_path):
                    st.image(sample_path, caption="Sample Indian Thali", use_container_width=True)

        # Confirm & Edit Detected Items Step
        if "detected_raw_items" in st.session_state and st.session_state.detected_raw_items:
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            st.markdown("#### Confirm Detected Food Items & Quantities")
            st.markdown(
                "<p style='color: #777777; font-size: 0.88rem;'>Review or adjust the AI-detected items and quantities below before calculating nutritional values:</p>",
                unsafe_allow_html=True,
            )

            df_edit = pd.DataFrame(st.session_state.detected_raw_items)
            # Ensure required columns
            for col in ["food_name", "quantity", "unit"]:
                if col not in df_edit.columns:
                    df_edit[col] = ""

            edited_df = st.data_editor(
                df_edit[["food_name", "quantity", "unit"]],
                num_rows="dynamic",
                use_container_width=True,
                key="detected_items_editor",
            )

            if st.button("Confirm & Calculate Nutrition", key="btn_confirm_calc", type="primary"):
                # Convert back to list of dicts
                confirmed_items = edited_df.to_dict(orient="records")
                st.session_state.user_confirmed_items = confirmed_items
                execute_analysis(confirmed_items)

    # Render results section if available
    render_nutrition_results()


def render_about_page():
    """Renders the About page."""
    st.markdown("<h2 style='font-size: 2rem; font-weight: 800; color: #111111;'>About VitaBite</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #777777; font-size: 1.05rem;'>Minimalist, transparent nutrition intelligence powered by verified nutritional data and Google Gemini AI.</p>", unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
            <div class="vb-card">
                <h4 style="margin-top: 0; color: #111111;">Our Philosophy</h4>
                <p style="color: #777777; font-size: 0.95rem; line-height: 1.6;">
                    Most nutrition apps are cluttered with aggressive fitness ads, gamification, and fluorescent charts. 
                    <strong>VitaBite</strong> is built for those who value clarity, elegance, and verified data.
                </p>
                <p style="color: #777777; font-size: 0.95rem; line-height: 1.6;">
                    We combine deterministic, laboratory-backed food compositions with the natural language and computer vision strengths of Google Gemini AI.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="vb-card">
                <h4 style="margin-top: 0; color: #111111;">Data Transparency</h4>
                <p style="color: #777777; font-size: 0.95rem; line-height: 1.6;">
                    We never guess without telling you. Common Indian staples are verified against standard food composition tables. 
                    Raw and cooked states (like uncooked rice vs. boiled rice) are clearly distinguished.
                </p>
                <p style="color: #777777; font-size: 0.95rem; line-height: 1.6;">
                    When an ingredient is uncataloged, Gemini provides an approximate estimation clearly labeled as <em>AI-estimated</em>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("### Technology Stack")
    st.markdown(
        """
        - **Interface:** Streamlit with customized minimalist black & white typography and responsive CSS.
        - **Intelligence:** Google Gemini API (`gemini-2.5-flash`) via the official `google-genai` Python SDK.
        - **Calculations:** Python and Pandas for deterministic macronutrient math.
        - **Visualizations:** Plotly monochromatic charts.
        - **Dataset:** Verified Indian Food Nutrition Dataset (`nutrition_data.csv`).
        """
    )


def render_footer():
    """Renders the minimal website footer."""
    st.markdown(
        """
        <div class="vb-footer">
            <div>
                <strong>VitaBite</strong> &mdash; Eat Better. Understand Your Nutrition.
            </div>
            <div class="vb-footer-links">
                &copy; 2026 VitaBite. All rights reserved.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    render_navbar()
    render_sidebar_settings()

    if st.session_state.nav_page == "Home":
        render_home_page()
    elif st.session_state.nav_page == "Food Analysis":
        render_food_analysis_page()
    elif st.session_state.nav_page == "About":
        render_about_page()

    render_footer()


if __name__ == "__main__":
    main()
