"""
app.py — Editorial & Data Journalism Dashboard for SailabAlert.
"""

import datetime
import streamlit as st
from model import load_or_train_model, predict_risk
from agent import get_safety_recommendation
from utils import (
    CITIES,
    generate_historical_city_data,
    render_city_trend_chart,
    build_pakistan_risk_map,
)
from streamlit_folium import st_folium

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SailabAlert — Flood & Landslide Intelligence",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Language State & Translations Dictionary
# ---------------------------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state["lang"] = "English"

TEXTS = {
    "English": {
        "tagline": "FLOOD & LANDSLIDE INTELLIGENCE FOR PAKISTAN",
        "meta": (
            '4 Risk Factors<span class="dot">·</span>'
            'Synthetic Training Dataset<span class="dot">·</span>'
            'Live Groq Analysis Ready<span class="dot">·</span>'
            'Monsoon Season Coverage'
        ),
        "tab_dashboard": "Dashboard",
        "tab_trends": "Historical Trends",
        "card_input_eyebrow": "Environmental & Hydrological Inputs",
        "card_input_desc": "Configure environmental readings to calculate current flood and landslide hazard probabilities.",
        "rainfall_label": "Rainfall Accumulation (mm)",
        "river_label": "River Gauge Level (meters)",
        "soil_label": "Soil Saturation Moisture (%)",
        "slope_label": "Terrain Slope Incline (degrees)",
        "btn_generate": "Generate Risk Assessment",
        "card_threat_eyebrow": "Calculated Threat Index",
        "confidence": "Confidence",
        "gauge_low": "Low Hazard",
        "gauge_mid": "Moderate",
        "gauge_high": "Severe Threat",
        "ai_advisory_eyebrow": "⚡ AI Public Safety Advisory · Groq Intelligence",
        "prob_eyebrow": "Probability Distribution",
        "risk_labels": {
            "Low": "Low Risk",
            "Medium": "Medium Risk",
            "High": "High Risk",
        },
        "metric_precipitation": "Precipitation",
        "metric_river": "Hydraulic Stage",
        "metric_soil": "Soil Saturation",
        "metric_slope": "Terrain Gradient",
        "metric_mm": "mm",
        "metric_meters": "meters",
        "metric_pct": "%",
        "metric_deg": "degrees",
    },
    "اردو": {
        "tagline": "پاکستان کے لیے سیلاب اور لینڈ سلائیڈنگ کی معلومات",
        "meta": (
            '۴ خطرے کے عوامل<span class="dot">·</span>'
            'مصنوعی تربیتی ماڈل<span class="dot">·</span>'
            'لائیو گروک تجزیہ فعال<span class="dot">·</span>'
            'مون سون سیزن مانیٹرنگ'
        ),
        "tab_dashboard": "ڈیش بورڈ",
        "tab_trends": "تاریخی رجحانات",
        "card_input_eyebrow": "ماحولیاتی و ہائیڈرولوجیکل مشاہدات",
        "card_input_desc": "سیلاب اور لینڈ سلائیڈنگ کے ممکنہ خطرے کے تخمینے کے لیے درج ذیل اشاریے منتخب کریں۔",
        "rainfall_label": "بارش کی مقدار (ملی میٹر)",
        "river_label": "دریا کی سطح (میٹر)",
        "soil_label": "زمین میں نمی (فیصد)",
        "slope_label": "زمین کی ڈھلوان (ڈگری)",
        "btn_generate": "خطرے کا اندازہ لگائیں",
        "card_threat_eyebrow": "حساب شدہ خطرے کا انڈیکس",
        "confidence": "اعتماد",
        "gauge_low": "کم خطرہ",
        "gauge_mid": "درمیانہ",
        "gauge_high": "شدید خطرہ",
        "ai_advisory_eyebrow": "⚡ اے آئی عوامی حفاظتی ہدایت نامہ · گروک انٹیلی جنس",
        "prob_eyebrow": "خطرے کا امکانی تناسب",
        "risk_labels": {
            "Low": "کم خطرہ",
            "Medium": "درمیانہ خطرہ",
            "High": "شدید خطرہ",
        },
        "metric_precipitation": "بارش",
        "metric_river": "دریا کا بہاؤ",
        "metric_soil": "مٹی کی نمی",
        "metric_slope": "ڈھلوان",
        "metric_mm": "ملی میٹر",
        "metric_meters": "میٹر",
        "metric_pct": "فیصد",
        "metric_deg": "ڈگری",
    },
}

# ---------------------------------------------------------------------------
# Editorial / Data Journalism Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* Base typography */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Playfair+Display:wght@700;900&family=Inter:wght@400;500;600;700&display=swap');

        .stApp {
            background-color: #F5F1E8;
            color: #2B2825;
            font-family: 'Lora', 'Georgia', serif;
        }

        /* Suppress sidebar */
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }

        /* Main container width */
        .main .block-container {
            max-width: 1120px;
            padding-top: 2.5rem;
            padding-bottom: 4rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        /* Deep Navy River & Storm Gradient Hero Banner (160px visual section) */
        .masthead-hero-banner {
            position: relative;
            background: 
                radial-gradient(ellipse at 50% -20%, rgba(56, 120, 180, 0.45) 0%, rgba(13, 27, 42, 0) 75%),
                linear-gradient(180deg, #09172A 0%, #112239 45%, #182E47 70%, #F5F1E8 100%);
            border-radius: 6px 6px 0 0;
            padding: 2.6rem 2rem 2.2rem 2rem;
            margin-bottom: 0;
            box-shadow: 0 4px 20px rgba(9, 23, 42, 0.16);
            overflow: hidden;
        }

        /* Topographic contour & water wave SVG pattern overlay (12% opacity) */
        .masthead-hero-banner::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='60' viewBox='0 0 120 60'%3E%3Cpath d='M0 25 Q 30 10 60 25 T 120 25 M0 40 Q 30 25 60 40 T 120 40 M0 55 Q 30 40 60 55 T 120 55 M0 10 Q 30 -5 60 10 T 120 10' fill='none' stroke='%23FFFFFF' stroke-width='1.2' opacity='0.13'/%3E%3C/svg%3E");
            background-repeat: repeat;
            pointer-events: none;
            z-index: 1;
        }

        /* Masthead text elements styled for dark gradient banner */
        .masthead-container {
            position: relative;
            z-index: 3;
            text-align: center;
        }

        .masthead-tagline {
            font-family: 'Inter', sans-serif;
            color: #E29555 !important;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.28em;
            text-transform: uppercase;
            margin-bottom: 0.55rem;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
        }

        /* Pure white bold title with high contrast and subtle shadow */
        .masthead-title {
            font-family: 'Playfair Display', 'Georgia', serif;
            font-size: 4.4rem;
            font-weight: 900;
            color: #FFFFFF !important;
            line-height: 1.05;
            letter-spacing: -0.02em;
            margin: 0 auto;
            padding: 0;
            text-shadow: 0 3px 12px rgba(0, 0, 0, 0.65), 0 1px 2px rgba(0, 0, 0, 0.9);
        }

        .masthead-meta {
            font-family: 'Inter', sans-serif;
            font-size: 0.92rem;
            color: #E6EEF5 !important;
            margin-top: 0.85rem;
            letter-spacing: 0.03em;
            text-shadow: 0 1px 4px rgba(0, 0, 0, 0.75);
        }

        .masthead-meta span.dot {
            margin: 0 0.6rem;
            color: #A4B8CC !important;
            font-size: 0.95rem;
        }

        /* Outline SVG Slider Header Styling */
        .slider-label-row {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.88rem;
            font-weight: 600;
            color: #2B2825;
            margin-top: 0.65rem;
            margin-bottom: -0.3rem;
        }

        .slider-svg-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #B5651D;
        }

        /* Threat Gauge CSS */
        .threat-gauge-wrapper {
            margin-top: 1.1rem;
            padding-top: 0.9rem;
            border-top: 1px dashed #E5DFD3;
        }

        .threat-gauge-track {
            position: relative;
            height: 10px;
            border-radius: 5px;
            background: linear-gradient(90deg, #0F5132 0%, #D97706 50%, #DC2626 100%);
            margin-top: 0.7rem;
            margin-bottom: 0.4rem;
        }

        .threat-gauge-pin {
            position: absolute;
            top: -5px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #FFFFFF;
            border: 3px solid #1A1714;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
            transform: translateX(-50%);
            transition: left 0.4s ease;
        }

        .threat-gauge-labels {
            display: flex;
            justify-content: space-between;
            font-family: 'Inter', sans-serif;
            font-size: 0.75rem;
            font-weight: 600;
            color: #8C8275;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }

        /* Newspaper double rule */
        .editorial-double-rule {
            border-top: 3px solid #2B2825;
            border-bottom: 1px solid #2B2825;
            height: 5px;
            margin-top: 0.8rem;
            margin-bottom: 1.8rem;
        }

        /* Horizontal tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2.5rem;
            border-bottom: 1px solid #D9D4C8;
            padding-bottom: 0;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #6C665F;
            background-color: transparent;
            border: none;
            padding: 0.6rem 0.2rem 0.75rem 0.2rem;
        }
        .stTabs [aria-selected="true"] {
            color: #B5651D !important;
            border-bottom: 3px solid #B5651D !important;
        }

        /* Editorial cards */
        .editorial-card {
            background-color: #FFFFFF;
            border: 1px solid #D9D4C8;
            border-radius: 4px;
            padding: 1.35rem 1.6rem;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.02);
            margin-bottom: 1.2rem;
        }

        .editorial-card-eyebrow {
            font-family: 'Inter', sans-serif;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #8C8275;
            margin-bottom: 0.45rem;
        }

        .editorial-metric-num {
            font-family: 'Playfair Display', 'Georgia', serif;
            font-size: 2.5rem;
            font-weight: 800;
            line-height: 1.1;
            margin: 0;
        }

        /* Recommendation Box */
        .recommendation-card {
            background-color: #FFFFFF;
            border: 1px solid #D9D4C8;
            border-left: 4px solid #B5651D;
            border-radius: 4px;
            padding: 1.3rem 1.6rem;
            margin-top: 1.2rem;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
        }

        /* Urgent Simulated Alert Dispatch Banner (High Risk Only) */
        .simulated-alert-card {
            background-color: #FEF7F6;
            border: 1px solid #F1CECA;
            border-left: 5px solid #991B1B;
            border-radius: 4px;
            padding: 1.25rem 1.55rem;
            margin-top: 1.2rem;
            box-shadow: 0 2px 8px rgba(153, 27, 27, 0.04);
        }

        .simulated-alert-header {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #991B1B;
            margin-bottom: 0.45rem;
        }

        .simulated-alert-desc {
            font-family: 'Lora', 'Georgia', serif;
            font-size: 0.92rem;
            line-height: 1.5;
            color: #382725;
            margin: 0 0 0.85rem 0;
        }

        .simulated-alert-log {
            background-color: #FFFFFF;
            border: 1px solid #EAD8D6;
            border-radius: 3px;
            padding: 0.65rem 0.9rem;
            font-family: 'Courier New', monospace;
            font-size: 0.77rem;
            line-height: 1.6;
            color: #554442;
        }

        .recommendation-eyebrow {
            font-family: 'Inter', sans-serif;
            font-size: 0.74rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: #B5651D;
            margin-bottom: 0.45rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .recommendation-body {
            font-family: 'Lora', 'Georgia', serif;
            font-size: 0.98rem;
            line-height: 1.65;
            color: #26231F;
            margin: 0;
        }

        /* Probability meter bar */
        .prob-bar-container {
            background-color: #EFE9DD;
            border-radius: 2px;
            height: 8px;
            width: 100%;
            overflow: hidden;
            margin-top: 0.35rem;
            margin-bottom: 0.8rem;
        }

        .prob-bar-fill {
            height: 100%;
            border-radius: 2px;
            transition: width 0.4s ease;
        }

        /* Footer */
        .editorial-footer {
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            color: #8C8275;
            line-height: 1.55;
            border-top: 1px solid #D9D4C8;
            padding-top: 1.4rem;
            margin-top: 3.2rem;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Language Selector Bar (Top Right)
# ---------------------------------------------------------------------------
col_lang_spacer, col_lang_toggle = st.columns([5.5, 1.5])
with col_lang_toggle:
    selected_lang = st.selectbox(
        "Language / زبان",
        options=["English", "اردو"],
        index=0 if st.session_state["lang"] == "English" else 1,
        key="lang_selector",
        label_visibility="collapsed",
    )
    st.session_state["lang"] = selected_lang

t = TEXTS[st.session_state["lang"]]

# ---------------------------------------------------------------------------
# Centered Masthead
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="masthead-hero-banner">
        <div class="masthead-container">
            <div class="masthead-tagline">{t['tagline']}</div>
            <h1 class="masthead-title" style="color: #FFFFFF !important;">SailabAlert</h1>
            <div class="masthead-meta">
                {t['meta']}
            </div>
        </div>
    </div>
    <div class="editorial-double-rule"></div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Model Loader
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Calibrating classification model...")
def get_model():
    return load_or_train_model(verbose=False)

model = get_model()

# ---------------------------------------------------------------------------
# Color and content mappings
# ---------------------------------------------------------------------------
RISK_PALETTE = {
    "Low": {
        "text": "#0F5132",
        "bg": "#F0F7F3",
        "border": "#0F5132",
        "bar": "#0F5132",
        "summary": "Hydrological and gradient markers remain balanced within normal ranges. Flash flood and slope-failure risks are low under these readings.",
    },
    "Medium": {
        "text": "#B45309",
        "bg": "#FFFBEB",
        "border": "#D97706",
        "bar": "#D97706",
        "summary": "Elevated soil saturation coupled with intermediate river or rain accumulation highlights moderate vulnerability. Close surveillance advised.",
    },
    "High": {
        "text": "#991B1B",
        "bg": "#FEF2F2",
        "border": "#DC2626",
        "bar": "#DC2626",
        "summary": "Critical threshold exceeded. Extreme runoff and steep-gradient landslide hazard are imminent. High alert status recommended.",
    },
}

# ---------------------------------------------------------------------------
# Tabs Navigation
# ---------------------------------------------------------------------------
tab_dashboard, tab_trends = st.tabs([t["tab_dashboard"], t["tab_trends"]])

# ===========================================================================
# TAB: Dashboard
# ===========================================================================
with tab_dashboard:
    col_input, col_spacer, col_output = st.columns([1.05, 0.08, 1.25])

    with col_input:
        st.markdown(
            f"""
            <div class="editorial-card">
                <div class="editorial-card-eyebrow">{t['card_input_eyebrow']}</div>
                <p style="font-size: 0.88rem; color: #55504A; line-height: 1.45; margin-bottom: 1rem;">
                    {t['card_input_desc']}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 1. Rainfall slider with inline SVG raindrop
        st.markdown(
            f"""
            <div class="slider-label-row">
                <span class="slider-svg-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path>
                    </svg>
                </span>
                <span>{t['rainfall_label']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        rainfall = st.slider(
            t["rainfall_label"],
            min_value=0.0,
            max_value=250.0,
            value=45.0,
            step=1.0,
            help="Total recorded rainfall in millimetres (0–250 mm).",
            label_visibility="collapsed",
        )

        # 2. River level slider with inline SVG wave
        st.markdown(
            f"""
            <div class="slider-label-row">
                <span class="slider-svg-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"></path>
                        <path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"></path>
                        <path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"></path>
                    </svg>
                </span>
                <span>{t['river_label']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        river_level = st.slider(
            t["river_label"],
            min_value=0.0,
            max_value=12.0,
            value=3.2,
            step=0.1,
            help="Current river water level above baseline zero in metres.",
            label_visibility="collapsed",
        )

        # 3. Soil moisture slider with inline SVG sprout / plant
        st.markdown(
            f"""
            <div class="slider-label-row">
                <span class="slider-svg-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M7 20h10"></path>
                        <path d="M10 20c0-4.4 3.6-8 8-8"></path>
                        <path d="M14 20c0-6.6-5.4-12-12-12 0 6.6 5.4 12 12 12z"></path>
                    </svg>
                </span>
                <span>{t['soil_label']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        soil_moisture = st.slider(
            t["soil_label"],
            min_value=10.0,
            max_value=95.0,
            value=52.0,
            step=1.0,
            help="Volumetric moisture content of the soil profile.",
            label_visibility="collapsed",
        )

        # 4. Slope incline slider with inline SVG mountain / incline slope
        st.markdown(
            f"""
            <div class="slider-label-row">
                <span class="slider-svg-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="m8 3 4 8 5-5 5 15H2L8 3z"></path>
                    </svg>
                </span>
                <span>{t['slope_label']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        slope_deg = st.slider(
            t["slope_label"],
            min_value=0.0,
            max_value=60.0,
            value=18.0,
            step=0.5,
            help="Topographical gradient in degrees. Values above 25° denote elevated landslide risk.",
            label_visibility="collapsed",
        )

        st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)
        generate_clicked = st.button(t["btn_generate"], type="primary", use_container_width=True)

    with col_output:
        label, _, proba = predict_risk(
            model,
            rainfall_mm=rainfall,
            river_level_m=river_level,
            soil_moisture_pct=soil_moisture,
            slope_deg=slope_deg,
        )

        cfg = RISK_PALETTE[label]
        conf_pct = round(proba[label] * 100, 1)

        # Calculate position for horizontal threat gauge pin (Low=16%, Medium=50%, High=84%)
        gauge_pos_map = {
            "Low": 16.0,
            "Medium": 50.0,
            "High": 84.0,
        }
        # Blend with model probabilities to show fine-grained placement
        base_pos = gauge_pos_map[label]
        if label == "Low":
            pin_pct = round(10 + (proba["Low"] * 0.15 + (1 - proba["Low"]) * 0.20) * 100, 1)
            pin_pct = min(28.0, max(8.0, pin_pct))
        elif label == "Medium":
            pin_pct = round(35.0 + proba["High"] * 30.0 - proba["Low"] * 10.0, 1)
            pin_pct = min(66.0, max(36.0, pin_pct))
        else: # High
            pin_pct = round(72.0 + proba["High"] * 22.0, 1)
            pin_pct = min(94.0, max(72.0, pin_pct))

        # Primary Threat Index Card with Horizontal Gauge Bar
        translated_risk_label = t["risk_labels"][label]

        st.markdown(
            f"""
            <div class="editorial-card" style="border-left: 5px solid {cfg['border']};">
                <div class="editorial-card-eyebrow">{t['card_threat_eyebrow']}</div>
                <div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 0.3rem;">
                    <span class="editorial-metric-num" style="color: {cfg['text']};">{translated_risk_label}</span>
                    <span style="font-family: 'Inter', sans-serif; font-size: 0.95rem; font-weight: 700; color: #6C665F;">
                        {conf_pct}% {t['confidence']}
                    </span>
                </div>
                <p style="font-size: 0.9rem; color: #4A453E; line-height: 1.5; margin-top: 0.75rem; margin-bottom: 0.4rem;">
                    {cfg['summary']}
                </p>
                <div class="threat-gauge-wrapper">
                    <div class="threat-gauge-labels">
                        <span style="color: #0F5132;">{t['gauge_low']}</span>
                        <span style="color: #D97706;">{t['gauge_mid']}</span>
                        <span style="color: #DC2626;">{t['gauge_high']}</span>
                    </div>
                    <div class="threat-gauge-track">
                        <div class="threat-gauge-pin" style="left: {pin_pct}%;"></div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Simulated Alert Banner (Triggered ONLY when Risk is High)
        if label == "High":
            current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S PKT")
            st.markdown(
                f"""
                <div class="simulated-alert-card">
                    <div class="simulated-alert-header">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#991B1B" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>
                        <span>⚠ SIMULATED ALERT DISPATCHED</span>
                    </div>
                    <p class="simulated-alert-desc">
                        In a live deployment, this critical threshold triggers automated emergency SMS and email dispatch 
                        protocols to registered residents and local civil defence authorities within the affected sector.
                    </p>
                    <div class="simulated-alert-log">
                        <div>&bull; SMS transmitted to: <strong>+92-3XX-XXXXXXX</strong> (Provincial Disaster Liaison) [SIMULATED]</div>
                        <div>&bull; Email dispatched to: <strong>district-disaster-management@example.gov.pk</strong> [SIMULATED]</div>
                        <div>&bull; Dispatch Timestamp: <strong>{current_timestamp}</strong></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # AI Safety Advisory Box
        with st.spinner("Consulting Groq safety intelligence engine..."):
            safety_advice = get_safety_recommendation(
                risk_label=label,
                confidence=conf_pct,
                rainfall=rainfall,
                river_level=river_level,
                soil_moisture=soil_moisture,
                slope=slope_deg,
            )

        st.markdown(
            f"""
            <div class="recommendation-card">
                <div class="recommendation-eyebrow">
                    {t['ai_advisory_eyebrow']}
                </div>
                <p class="recommendation-body">
                    {safety_advice}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Probability Breakdown Card
        st.markdown(
            f"""
            <div class="editorial-card" style="margin-top: 1.2rem;">
                <div class="editorial-card-eyebrow">{t['prob_eyebrow']}</div>
            """,
            unsafe_allow_html=True,
        )

        for cat in ["Low", "Medium", "High"]:
            c_pct = int(proba[cat] * 100)
            c_cfg = RISK_PALETTE[cat]
            c_trans_label = t["risk_labels"][cat]
            st.markdown(
                f"""
                <div style="margin-bottom: 0.65rem;">
                    <div style="display: flex; justify-content: space-between; font-family: 'Inter', sans-serif; font-size: 0.84rem;">
                        <span style="font-weight: 600; color: {c_cfg['text']};">{c_trans_label}</span>
                        <span style="color: #6C665F; font-weight: 500;">{c_pct}%</span>
                    </div>
                    <div class="prob-bar-container">
                        <div class="prob-bar-fill" style="width: {c_pct}%; background-color: {c_cfg['bar']};"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # Metric summary grid
        st.markdown(
            f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                <div class="editorial-card" style="padding: 0.85rem 1.1rem; margin-bottom: 0;">
                    <div class="editorial-card-eyebrow" style="margin-bottom: 0.2rem;">{t['metric_precipitation']}</div>
                    <div style="font-family: 'Playfair Display', serif; font-size: 1.35rem; font-weight: 700; color: #1A1714;">
                        {rainfall} <span style="font-size: 0.8rem; font-family: 'Inter', sans-serif; color: #8C8275;">{t['metric_mm']}</span>
                    </div>
                </div>
                <div class="editorial-card" style="padding: 0.85rem 1.1rem; margin-bottom: 0;">
                    <div class="editorial-card-eyebrow" style="margin-bottom: 0.2rem;">{t['metric_river']}</div>
                    <div style="font-family: 'Playfair Display', serif; font-size: 1.35rem; font-weight: 700; color: #1A1714;">
                        {river_level} <span style="font-size: 0.8rem; font-family: 'Inter', sans-serif; color: #8C8275;">{t['metric_meters']}</span>
                    </div>
                </div>
                <div class="editorial-card" style="padding: 0.85rem 1.1rem; margin-bottom: 0;">
                    <div class="editorial-card-eyebrow" style="margin-bottom: 0.2rem;">{t['metric_soil']}</div>
                    <div style="font-family: 'Playfair Display', serif; font-size: 1.35rem; font-weight: 700; color: #1A1714;">
                        {soil_moisture} <span style="font-size: 0.8rem; font-family: 'Inter', sans-serif; color: #8C8275;">{t['metric_pct']}</span>
                    </div>
                </div>
                <div class="editorial-card" style="padding: 0.85rem 1.1rem; margin-bottom: 0;">
                    <div class="editorial-card-eyebrow" style="margin-bottom: 0.2rem;">{t['metric_slope']}</div>
                    <div style="font-family: 'Playfair Display', serif; font-size: 1.35rem; font-weight: 700; color: #1A1714;">
                        {slope_deg} <span style="font-size: 0.8rem; font-family: 'Inter', sans-serif; color: #8C8275;">{t['metric_deg']}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ===========================================================================
# TAB: Historical Trends
# ===========================================================================
with tab_trends:
    # Generate cached or memoized 12-month synthetic timeseries data
    @st.cache_data
    def load_historical_data():
        return generate_historical_city_data()

    df_hist = load_historical_data()

    st.markdown(
        """
        <div class="editorial-card" style="margin-top: 1.2rem;">
            <div class="editorial-card-eyebrow">Archival & Time-Series Observations</div>
            <h3 style="font-family: 'Playfair Display', serif; font-size: 1.7rem; color: #1A1714; margin-top: 0.2rem; margin-bottom: 0.5rem;">
                Historical Hydrological Patterns (Past 12 Months)
            </h3>
            <p style="font-size: 0.9rem; color: #55504A; line-height: 1.5; margin-bottom: 0;">
                Examine retrospective rainfall and river gauge oscillations across key Pakistani flood-corridor stations. 
                Select an urban station below to render its 12-month hydrograph.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # City Selector Dropdown
    selected_city = st.selectbox(
        "Select Monitoring Station / City",
        options=list(CITIES.keys()),
        index=0,
        help="Select a monitored municipal or river-basin station.",
    )

    df_city_selected = df_hist[df_hist["city"] == selected_city].sort_values("date")

    # Plotly Trend Chart Container
    fig_city = render_city_trend_chart(df_city_selected, selected_city)
    st.plotly_chart(fig_city, use_container_width=True)

    # Map Section
    st.markdown(
        """
        <div class="editorial-card" style="margin-top: 1.8rem; margin-bottom: 0.8rem;">
            <div class="editorial-card-eyebrow">Geospatial Hazard Registry</div>
            <h3 style="font-family: 'Playfair Display', serif; font-size: 1.6rem; color: #1A1714; margin-top: 0.2rem; margin-bottom: 0.5rem;">
                Pakistan National River-Basin Surveillance
            </h3>
            <p style="font-size: 0.9rem; color: #55504A; line-height: 1.5; margin-bottom: 0;">
                Color-coded regional telemetry stations indicating most recent risk classification (Green = Low, Amber = Medium, Red = High). Click markers to reveal current readings.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Extract latest month snapshot for each city to render map status
    latest_date = df_hist["date"].max()
    df_latest = df_hist[df_hist["date"] == latest_date]

    map_obj = build_pakistan_risk_map(df_latest)
    st_folium(map_obj, width=None, height=480, returned_objects=[])

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="editorial-footer">
        <strong>SailabAlert Early Warning System</strong> — Disaster risk reduction research for Pakistan.
        <br>
        <em>Data Notice:</em> Current early-warning scoring utilizes synthetic benchmark calibrations. Institutional telemetry pipelines (PMD, WAPDA, NASA POWER, SRTM) represent scheduled integration targets.
    </div>
    """,
    unsafe_allow_html=True,
)
