"""
agent.py — Groq API Agent for SailabAlert.

Generates concise, plain-language disaster safety recommendations using
Groq's currently active chat completion models (e.g., qwen/qwen3.8-27b).
"""

import os
from groq import Groq

# Active supported chat model on Groq console
PRIMARY_MODEL = "qwen/qwen3.8-27b"
FALLBACK_MODEL = "openai/gpt-oss-120b"


def get_safety_recommendation(
    risk_label: str,
    confidence: float,
    rainfall: float,
    river_level: float,
    soil_moisture: float,
    slope: float,
) -> str:
    """
    Calls the Groq API via the official Python SDK to generate an authoritative
    2-3 sentence public safety advisory.

    Parameters:
        risk_label    : 'Low', 'Medium', or 'High'
        confidence    : Model confidence percentage (e.g., 94.2)
        rainfall      : Precipitation in mm
        river_level   : River water level in metres
        soil_moisture : Soil saturation percentage
        slope         : Terrain slope in degrees

    Returns:
        A concise 2-3 sentence plain-language safety advisory.
    """
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return (
            "GROQ_API_KEY environment variable is not configured. "
            "Please configure your API key to activate live Groq safety advisories. "
            "In general, follow local disaster management guidance and maintain distance from active water channels."
        )

    client = Groq(api_key=api_key)

    system_prompt = (
        "You are an expert disaster response advisor for the Pakistan National Disaster Management Authority (NDMA). "
        "Your task is to provide clear, calm, and actionable safety recommendations based on hydrological and geological risk data. "
        "Keep your response strictly to 2-3 concise sentences. "
        "Focus on immediate, practical public safety actions (e.g. evacuation advisories, staying away from riverbanks, landslide precautions for steep terrain). "
        "Do not use markdown bullets, thinking tags, or preamble. Deliver only the advisory statement."
    )

    user_prompt = (
        f"Hazard Assessment Data:\n"
        f"- Risk Level: {risk_label} ({confidence}% confidence)\n"
        f"- Rainfall Accumulation: {rainfall} mm\n"
        f"- River Gauge Level: {river_level} meters\n"
        f"- Soil Saturation: {soil_moisture}%\n"
        f"- Terrain Slope Angle: {slope} degrees\n\n"
        f"Provide a 2 to 3 sentence authoritative public safety recommendation tailored specifically to these hazard conditions in Pakistan."
    )

    for model_id in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            completion = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=220,
            )
            raw_content = completion.choices[0].message.content.strip()
            # Clean any internal reasoning tags if present
            if "</think>" in raw_content:
                raw_content = raw_content.split("</think>")[-1].strip()
            return raw_content
        except Exception:
            continue

    return (
        f"Advisory generation currently unavailable. For {risk_label} risk conditions, "
        f"follow provincial emergency instructions and monitor PMD/NDMA early-warning bulletins."
    )
