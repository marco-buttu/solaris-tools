"""
Fit offset models for azimuth and elevation pointing corrections from telescope data.

The script performs a polynomial fit (with outlier rejection via z-score)
on azimuth and elevation offsets and saves the models for later use.

It supports:
- Reading from a TSV file with metadata lines starting with '#'
- Fitting offset_az vs azimuth and offset_el vs elevation
- Saving fitted models to disk
- Predicting new values using saved models
- Optional plotting
- Saving results (coefficients and R²) to a text file

Usage examples:
---------------
# Fit models and show plots
python fit_offset_models.py ../templates/offsets_example.tsv --plot

# Fit models of degree 3 and save results
python fit_offset_models.py ../templates/offsets_example.tsv --degree 3 \
       --output results.txt

# Predict offset_az at 125 degrees azimuth
python fit_offset_models.py ../templates/offsets_example.tsv --predict_az 125

# Predict offset_el at 40 degrees elevation
python fit_offset_models.py ../templates/offsets_example.tsv --predict_el 40
"""

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial import Polynomial
from sklearn.metrics import r2_score
from scipy.stats import zscore
import joblib


def fit_with_zscore(x, y, degree=3, z=3.0):
    """Perform polynomial fit with outlier removal based on z-score."""
    # Ensure inputs are float arrays
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    # Compute z-scores; handle the case where std is zero or NaN
    y_std = y.std()
    if y_std == 0 or np.isnan(y_std):
        mask = np.ones_like(y, dtype=bool)  # keep all points
    else:
        zscores = np.abs((y - y.mean()) / y_std)
        mask = zscores < z  # keep points within threshold

    # Filter out outliers
    x_clean = x[mask]
    y_clean = y[mask]

    # Fit a polynomial model to the filtered data
    p_clean = Polynomial.fit(x_clean, y_clean, deg=degree).convert()
    y_pred = p_clean(x_clean)

    # Compute R² score of the fitted model
    r2 = r2_score(y_clean, y_pred)
    return p_clean, x_clean, y_clean, r2


def load_data(filepath):
    """Load TSV file ignoring commented metadata lines.
    Force numeric types for required columns.
    """
    df = pd.read_csv(filepath, sep="\t", comment="#")
    # Force numeric types; convert non-numeric values to NaN
    for col in ["azimuth", "elevation", "offset_az", "offset_el"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    # Drop rows with missing essential values for fitting
    df = df.dropna(subset=["azimuth", "elevation", "offset_az", "offset_el"])
    return df


def plot_fit(x_raw, y_raw, x_clean, y_clean, model, xlabel, ylabel, title):
    """Plot model vs data."""
    x_plot = np.linspace(min(x_clean), max(x_clean), 200)
    plt.scatter(x_raw, y_raw, color="gray", label="Raw data")
    plt.scatter(x_clean, y_clean, color="blue", label="Filtered data")
    plt.plot(x_plot, model(x_plot), color="red", label="Fit")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)


def save_model(model, filename):
    joblib.dump(model, filename)


def save_summary(filename, model_az, r2_az, model_el, r2_el):
    """Save model summary to text file."""
    with open(filename, "w") as f:
        f.write("Model: offset_az = f(azimuth)\n")
        f.write(str(model_az) + "\n")
        f.write(f"R² = {r2_az:.4f}\n\n")
        f.write("Model: offset_el = f(elevation)\n")
        f.write(str(model_el) + "\n")
        f.write(f"R² = {r2_el:.4f}\n")


def load_model(filename):
    return joblib.load(filename)


def main():
    # Main CLI entry point
    parser = argparse.ArgumentParser(
        description="Fit and save telescope pointing offset models."
    )
    parser.add_argument("tsv_file", help="Path to the input TSV file")
    parser.add_argument(
        "--degree", type=int, default=2, help="Polynomial degree (default: 2)"
    )
    parser.add_argument("--plot", action="store_true", help="Show plots")
    parser.add_argument(
        "--output", default="fit_results.txt", help="Output text file for summary"
    )
    parser.add_argument(
        "--predict_az", type=float, help="Predict offset_az for a given azimuth"
    )
    parser.add_argument(
        "--predict_el", type=float, help="Predict offset_el for a given elevation"
    )
    args = parser.parse_args()

    # Prediction mode
    if args.predict_az or args.predict_el:
        if args.predict_az:
            model = load_model("model_offset_az.joblib")
            print(f"Predicted offset_az: {model(args.predict_az):.4f} arcsec")
        if args.predict_el:
            model = load_model("model_offset_el.joblib")
            print(f"Predicted offset_el: {model(args.predict_el):.4f} arcsec")
        return

    # Fit mode
    df = load_data(args.tsv_file)

    model_az, x_az, y_az, r2_az = fit_with_zscore(
        df["azimuth"], df["offset_az"], degree=args.degree
    )
    print("\nModel: offset_az = f(azimuth)")
    print(model_az)
    print(f"R² = {r2_az:.4f}")
    save_model(model_az, "model_offset_az.joblib")

    model_el, x_el, y_el, r2_el = fit_with_zscore(
        df["elevation"], df["offset_el"], degree=args.degree
    )
    print("\nModel: offset_el = f(elevation)")
    print(model_el)
    print(f"R² = {r2_el:.4f}")
    save_model(model_el, "model_offset_el.joblib")

    save_summary(args.output, model_az, r2_az, model_el, r2_el)
    print(f"\nSummary saved to: {args.output}")

    if args.plot:
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        plot_fit(
            df["azimuth"],
            df["offset_az"],
            x_az,
            y_az,
            model_az,
            "Azimuth (deg)",
            "Offset Az (arcsec)",
            "offset_az vs azimuth",
        )
        plt.subplot(1, 2, 2)
        plot_fit(
            df["elevation"],
            df["offset_el"],
            x_el,
            y_el,
            model_el,
            "Elevation (deg)",
            "Offset El (arcsec)",
            "offset_el vs elevation",
        )
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()
