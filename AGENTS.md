# PROJECT: SailabAlert — Flood & Landslide Early Warning System

## What this is

SailabAlert is a disaster early-warning web app for Pakistan. It predicts
flood and landslide risk using rainfall, river water level, soil saturation,
and terrain slope data, then gives AI-generated safety recommendations. This
is being built as a standout CV project for a scholarship application.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit (Python) |
| ML | scikit-learn — Random Forest Classifier for risk prediction |
| AI Agent | Groq API (console.groq.com, OpenAI-compatible endpoint) — `qwen/qwen3.8-27b` (with fallback to `openai/gpt-oss-120b`) — natural-language risk explanations and safety advice |
| Visualization | Plotly and Folium — maps and charts |
| Data | Synthetic dataset (rainfall mm, river level meters, soil moisture %, slope angle degrees) mapped to risk labels (Low / Medium / High) |

Real government datasets (PMD, WAPDA, NASA POWER, SRTM) are noted as future-scope data sources only.

---

## Project Structure

```
SailabAlert/
├── app.py            # Main Streamlit app with sidebar navigation
├── model.py          # Trains/loads the Random Forest model; generates
│                     #   synthetic training data if no dataset exists
├── agent.py          # Handles Groq API calls; takes risk data as input,
│                     #   returns a plain-language safety recommendation
├── utils.py          # Helper functions for data processing and map rendering
└── requirements.txt
```

---

## This Week's Build Plan (step by step, not all at once)

1. **Basic Streamlit app + ML model** — synthetic data, Random Forest classifier
2. **Dashboard UI** — color-coded risk level, Folium map, historical trends chart (Plotly)
3. **Groq API agent** — safety recommendations in natural language (`llama-3.3-70b-versatile` via console.groq.com)
4. **Polish** — multilingual toggle (English / Urdu), alert simulation, styling

---

## Rules to Follow

1. **API key safety** — read `GROQ_API_KEY` from an environment variable. Never hardcode it.
2. **Keep functions small** — one responsibility per function, split across files as listed above.
3. **Synthetic data only** — use sample data for testing; reference real datasets (PMD, WAPDA, NASA POWER, SRTM) only as a "future data sources" note.
4. **Professional styling** — no harsh neon or glowing colors. Use calm, professional tones suited for a scholarship application demo.
