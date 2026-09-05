"""
model.py — Synthetic data generation and Random Forest risk classifier for SailabAlert.

Features used for prediction:
    rainfall_mm       : Rainfall in millimetres
    river_level_m     : River water level in metres
    soil_moisture_pct : Soil moisture as a percentage
    slope_deg         : Terrain slope angle in degrees

Risk labels:
    0 → Low
    1 → Medium
    2 → High

Future data sources (real-world, not yet integrated):
    PMD   — Pakistan Meteorological Department (rainfall, forecasts)
    WAPDA — River gauge and flow data
    NASA POWER / SRTM — Soil moisture and elevation/slope datasets
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL_PATH = "sailabalert_rf_model.joblib"

FEATURE_COLS = [
    "rainfall_mm",
    "river_level_m",
    "soil_moisture_pct",
    "slope_deg",
]

LABEL_MAP = {0: "Low", 1: "Medium", 2: "High"}
LABEL_COLOURS = {"Low": "#2e7d32", "Medium": "#f57c00", "High": "#c62828"}


# ---------------------------------------------------------------------------
# Synthetic data
# ---------------------------------------------------------------------------

def _score_risk(rainfall: float, river_level: float,
                soil_moisture: float, slope: float) -> int:
    """
    Rule-based scorer that converts environmental readings into a risk label.

    Scoring rationale:
    - Rainfall and river level are the primary flood drivers.
    - High soil moisture amplifies runoff and landslide susceptibility.
    - Steep slopes sharply raise landslide probability.

    Returns:
        0 (Low), 1 (Medium), or 2 (High)
    """
    score = 0

    # Rainfall (mm)
    if rainfall > 150:
        score += 3
    elif rainfall > 75:
        score += 2
    elif rainfall > 30:
        score += 1

    # River level (m)
    if river_level > 7:
        score += 3
    elif river_level > 4:
        score += 2
    elif river_level > 2:
        score += 1

    # Soil moisture (%) — amplifier for both flood runoff and landslides
    if soil_moisture > 75:
        score += 2
    elif soil_moisture > 50:
        score += 1

    # Slope (degrees) — landslide susceptibility driver
    if slope > 35:
        score += 2
    elif slope > 20:
        score += 1

    if score >= 6:
        return 2  # High
    elif score >= 3:
        return 1  # Medium
    else:
        return 0  # Low


def generate_synthetic_data(n_samples: int = 2000, random_state: int = 42) -> pd.DataFrame:
    """
    Generate a synthetic dataset of environmental sensor readings with risk labels.

    Parameter ranges are representative of monsoon-season conditions in Pakistan:
        rainfall_mm       : 0 – 250 mm  (low drizzle to extreme monsoon event)
        river_level_m     : 0 – 12 m    (low water to severe flood stage)
        soil_moisture_pct : 10 – 95 %   (dry soil to near-saturated)
        slope_deg         : 0 – 60°     (flat plains to steep hill slopes)

    Returns:
        pd.DataFrame with columns: rainfall_mm, river_level_m,
        soil_moisture_pct, slope_deg, risk_label (int), risk_label_str (str)
    """
    rng = np.random.default_rng(random_state)

    rainfall     = rng.uniform(0,   250, n_samples)
    river_level  = rng.uniform(0,    12, n_samples)
    soil_moisture = rng.uniform(10,  95, n_samples)
    slope        = rng.uniform(0,    60, n_samples)

    labels = np.array([
        _score_risk(r, rl, sm, sl)
        for r, rl, sm, sl in zip(rainfall, river_level, soil_moisture, slope)
    ])

    df = pd.DataFrame({
        "rainfall_mm":       rainfall.round(1),
        "river_level_m":     river_level.round(2),
        "soil_moisture_pct": soil_moisture.round(1),
        "slope_deg":         slope.round(1),
        "risk_label":        labels,
        "risk_label_str":    [LABEL_MAP[lbl] for lbl in labels],
    })

    return df


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def train_model(
    df: pd.DataFrame,
    random_state: int = 42,
) -> tuple[RandomForestClassifier, str]:
    """
    Train a Random Forest Classifier on the provided DataFrame.

    Returns:
        (trained_model, classification_report_str)
    """
    X = df[FEATURE_COLS]
    y = df["risk_label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=random_state,
        stratify=y,
    )

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=2,
        class_weight="balanced",   # guards against class imbalance
        random_state=random_state,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    report = classification_report(
        y_test,
        clf.predict(X_test),
        target_names=["Low", "Medium", "High"],
    )

    return clf, report


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def save_model(model: RandomForestClassifier, path: str = MODEL_PATH) -> None:
    """Persist the trained model to disk with joblib."""
    joblib.dump(model, path)


def load_model(path: str = MODEL_PATH) -> RandomForestClassifier:
    """Load a persisted model from disk."""
    return joblib.load(path)


def load_or_train_model(
    model_path: str = MODEL_PATH,
    n_samples: int = 2000,
    verbose: bool = True,
) -> RandomForestClassifier:
    """
    Load the model from disk if it exists; otherwise generate synthetic data,
    train a new model, save it, and return it.

    Args:
        model_path : Path to the saved model file.
        n_samples  : Number of synthetic samples to generate if training.
        verbose    : Print progress messages if True.

    Returns:
        Trained RandomForestClassifier
    """
    if os.path.exists(model_path):
        if verbose:
            print(f"[model] Loading existing model from '{model_path}'")
        return load_model(model_path)

    if verbose:
        print("[model] No saved model found — generating synthetic data and training...")

    df = generate_synthetic_data(n_samples=n_samples)
    model, report = train_model(df)

    if verbose:
        print("[model] Training complete.\n")
        print(report)

    save_model(model, model_path)

    if verbose:
        print(f"[model] Model saved to '{model_path}'")

    return model


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def predict_risk(
    model: RandomForestClassifier,
    rainfall_mm: float,
    river_level_m: float,
    soil_moisture_pct: float,
    slope_deg: float,
) -> tuple[str, int, dict[str, float]]:
    """
    Predict risk level for a single set of environmental readings.

    Args:
        model             : Trained RandomForestClassifier.
        rainfall_mm       : Rainfall in mm.
        river_level_m     : River water level in metres.
        soil_moisture_pct : Soil moisture percentage.
        slope_deg         : Terrain slope in degrees.

    Returns:
        label_str     : "Low", "Medium", or "High"
        label_int     : 0, 1, or 2
        probabilities : {"Low": float, "Medium": float, "High": float}
    """
    X = pd.DataFrame([{
        "rainfall_mm":       rainfall_mm,
        "river_level_m":     river_level_m,
        "soil_moisture_pct": soil_moisture_pct,
        "slope_deg":         slope_deg,
    }])

    label_int = int(model.predict(X)[0])
    proba = model.predict_proba(X)[0]
    probabilities = {LABEL_MAP[i]: round(float(p), 3) for i, p in enumerate(proba)}

    return LABEL_MAP[label_int], label_int, probabilities


# ---------------------------------------------------------------------------
# CLI entry point — trains and runs a quick sanity check
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    model = load_or_train_model(verbose=True)

    print("\n[model] Sanity check — sample predictions:")
    test_cases = [
        (10,  1.0, 20, 5,   "Low expected"),
        (90,  4.5, 60, 22,  "Medium expected"),
        (200, 9.5, 88, 45,  "High expected"),
    ]
    for rainfall, river, soil, slope, note in test_cases:
        label, _, proba = predict_risk(model, rainfall, river, soil, slope)
        print(
            f"  rainfall={rainfall:>4}mm  river={river}m  "
            f"soil={soil}%  slope={slope}deg  =>  {label:<6}  ({note})"
        )
        print(f"    probabilities: {proba}")
