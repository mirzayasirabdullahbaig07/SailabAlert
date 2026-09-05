"""
utils.py — Helper functions for historical timeseries generation,
Plotly chart styling, and Folium map rendering for SailabAlert.
"""

import pandas as pd
import numpy as np
import folium
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------------------------------------------------------
# City Registry & Coordinates
# ---------------------------------------------------------------------------
CITIES = {
    "Karachi": {
        "lat": 24.8607,
        "lon": 67.0011,
        "province": "Sindh",
        "context": "Coastal flooding, urban flash floods",
        "base_rain": 25.0,
        "base_river": 1.5,
        "slope": 5.0,
    },
    "Lahore": {
        "lat": 31.5204,
        "lon": 74.3587,
        "province": "Punjab",
        "context": "Ravi river flooding, urban drainage",
        "base_rain": 55.0,
        "base_river": 3.8,
        "slope": 4.0,
    },
    "Peshawar": {
        "lat": 34.0151,
        "lon": 71.5249,
        "province": "Khyber Pakhtunkhwa",
        "context": "Kabul river surges & hillside flash runoff",
        "base_rain": 45.0,
        "base_river": 3.2,
        "slope": 22.0,
    },
    "Multan": {
        "lat": 30.1575,
        "lon": 71.5249,
        "province": "Punjab",
        "context": "Chenab & Sutlej river overflow corridor",
        "base_rain": 30.0,
        "base_river": 4.2,
        "slope": 3.0,
    },
    "Sialkot": {
        "lat": 32.4945,
        "lon": 74.5229,
        "province": "Punjab",
        "context": "Chenab tributary flash waters & catchment zone",
        "base_rain": 70.0,
        "base_river": 4.8,
        "slope": 8.0,
    },
    "Sukkur": {
        "lat": 27.7052,
        "lon": 68.8574,
        "province": "Sindh",
        "context": "Indus river barrage & major flood artery",
        "base_rain": 20.0,
        "base_river": 6.8,
        "slope": 2.0,
    },
}

RISK_COLOR_MAP = {
    "Low": "#0F5132",
    "Medium": "#D97706",
    "High": "#DC2626",
}


def generate_historical_city_data(seed: int = 101) -> pd.DataFrame:
    """
    Generates 12 months of monthly synthetic data (Sep 2025 – Aug 2026)
    for all 6 monitored cities, reflecting seasonal monsoon peaks (Jul-Aug).
    """
    rng = np.random.default_rng(seed)
    
    # 12 monthly periods leading up to local timestamp (Sep 2025 to Aug 2026)
    dates = pd.date_range(end="2026-08-31", periods=12, freq="ME")
    
    records = []
    
    for city_name, meta in CITIES.items():
        base_r = meta["base_rain"]
        base_riv = meta["base_river"]
        
        for dt in dates:
            month = dt.month
            # Monsoon amplification in July & August
            if month in [7, 8]:
                monsoon_factor = 2.8
            elif month in [6, 9]:
                monsoon_factor = 1.6
            else:
                monsoon_factor = 0.6
                
            rainfall = max(2.0, (base_r * monsoon_factor) + rng.normal(0, 15))
            river_level = max(0.8, (base_riv * (0.8 + 0.4 * monsoon_factor)) + rng.normal(0, 0.6))
            soil_moisture = min(95.0, max(15.0, 25.0 + (rainfall * 0.35) + rng.normal(0, 5)))
            
            # Risk labeling based on thresholds
            if rainfall > 110 or river_level > 6.5 or (rainfall > 70 and river_level > 4.5):
                risk = "High"
            elif rainfall > 50 or river_level > 3.5 or soil_moisture > 65:
                risk = "Medium"
            else:
                risk = "Low"
                
            records.append({
                "city": city_name,
                "date": dt,
                "month_str": dt.strftime("%b %Y"),
                "rainfall_mm": round(float(rainfall), 1),
                "river_level_m": round(float(river_level), 2),
                "soil_moisture_pct": round(float(soil_moisture), 1),
                "risk_label": risk,
            })
            
    return pd.DataFrame(records)


def render_city_trend_chart(df_city: pd.DataFrame, city_name: str) -> go.Figure:
    """
    Constructs an editorial dual-axis Plotly line chart displaying
    12-month precipitation and river gauge stages.
    """
    fig = make_subplots(
        specs=[[{"secondary_y": True}]],
    )

    # Rainfall line (warm terracotta / rust tone)
    fig.add_trace(
        go.Scatter(
            x=df_city["month_str"],
            y=df_city["rainfall_mm"],
            name="Precipitation (mm)",
            mode="lines+markers",
            line=dict(color="#B5651D", width=2.6),
            marker=dict(size=6, color="#B5651D"),
            hovertemplate="%{x}<br>Rainfall: %{y} mm<extra></extra>",
        ),
        secondary_y=False,
    )

    # River level line (slate deep water tone)
    fig.add_trace(
        go.Scatter(
            x=df_city["month_str"],
            y=df_city["river_level_m"],
            name="River Gauge (m)",
            mode="lines+markers",
            line=dict(color="#1A3A5C", width=2.4, dash="dash"),
            marker=dict(size=6, color="#1A3A5C"),
            hovertemplate="%{x}<br>River Gauge: %{y} m<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title=dict(
            text=f"12-Month Hydrological Observations — {city_name}",
            font=dict(family="Playfair Display, Georgia, serif", size=18, color="#1A1714"),
            x=0.0,
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FAF8F5",
        font=dict(family="Inter, sans-serif", size=11, color="#55504A"),
        margin=dict(l=40, r=40, t=50, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
        hovermode="x unified",
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#EFE9DD",
        linecolor="#D9D4C8",
        tickfont=dict(family="Inter, sans-serif", size=10, color="#6C665F"),
    )

    fig.update_yaxes(
        title_text="Rainfall (mm)",
        title_font=dict(family="Inter, sans-serif", size=11, color="#B5651D"),
        showgrid=True,
        gridcolor="#EFE9DD",
        linecolor="#D9D4C8",
        secondary_y=False,
    )

    fig.update_yaxes(
        title_text="River Gauge (m)",
        title_font=dict(family="Inter, sans-serif", size=11, color="#1A3A5C"),
        showgrid=False,
        linecolor="#D9D4C8",
        secondary_y=True,
    )

    return fig


def build_pakistan_risk_map(latest_df: pd.DataFrame) -> folium.Map:
    """
    Builds a Folium map centered on Pakistan, marking the 6 pinned cities
    with colors representing their current risk status.
    """
    # Pakistan geographic centroid
    m = folium.Map(
        location=[30.3753, 69.3451],
        zoom_start=5.2,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    for _, row in latest_df.iterrows():
        c_name = row["city"]
        meta = CITIES[c_name]
        risk = row["risk_label"]
        color = RISK_COLOR_MAP.get(risk, "#6C665F")
        
        popup_html = f"""
        <div style="font-family: 'Inter', sans-serif; font-size: 12px; line-height: 1.5; min-width: 170px;">
            <div style="font-weight: 700; font-size: 13px; color: #1A1714; border-bottom: 1px solid #D9D4C8; padding-bottom: 4px; margin-bottom: 6px;">
                {c_name} ({meta['province']})
            </div>
            <div style="margin-bottom: 3px;">
                <strong>Current Risk:</strong> 
                <span style="color: {color}; font-weight: 700;">{risk}</span>
            </div>
            <div style="color: #6C665F; margin-bottom: 2px;">
                Rainfall: <strong>{row['rainfall_mm']} mm</strong>
            </div>
            <div style="color: #6C665F; margin-bottom: 6px;">
                River Level: <strong>{row['river_level_m']} m</strong>
            </div>
            <div style="font-size: 10px; color: #8C8275; font-style: italic;">
                {meta['context']}
            </div>
        </div>
        """
        
        folium.CircleMarker(
            location=[meta["lat"], meta["lon"]],
            radius=9,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            weight=2,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{c_name}: {risk} Risk",
        ).add_to(m)

    return m
