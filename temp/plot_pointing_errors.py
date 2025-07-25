#!/usr/bin/env python3
"""
Plot telescope pointing offsets from a CSV file.

Usage:
    python plot_offsets.py <csv_path> <mode>

Arguments:
    csv_path : str
        Path to the CSV file containing the data.
    mode : str
        Plot mode:
            - "del-az" : plot only Del-Az values
            - "del-el" : plot only Del-El values
            - "both"   : plot both Del-Az and Del-El values

The CSV file is expected to have at least these columns:
    - Az [deg]: azimuth values in degrees
    - Del-Az [amin]: azimuth offsets in arcmin (penultimate column)
    - Del-El [amin]: elevation offsets in arcmin (last column)

Example:
    python plot_offsets.py puntamento_del_az-el.csv both
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Plot telescope pointing offsets from a CSV file.")
    parser.add_argument("csv_path", type=str, help="Path to the CSV file.")
    parser.add_argument("mode", type=str, choices=["del-az", "del-el", "both"],
                        help='Plot mode: "del-az", "del-el" or "both".')
    args = parser.parse_args()

    csv_path = args.csv_path
    mode = args.mode.lower()

    # Load CSV file
    df = pd.read_csv(csv_path)

    # Replace commas with dots and convert to float for numeric columns
    for col in ["Az [deg]", "Del-Az [amin]", "Del-El [amin]"]:
        df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

    # Sort by Az while preserving the corresponding offsets
    df_sorted = df.sort_values(by="Az [deg]").reset_index(drop=True)

    # Plotting
    plt.figure(figsize=(10, 6))
    if mode in ["del-az", "both"]:
        plt.plot(df_sorted["Az [deg]"], df_sorted["Del-Az [amin]"],
                 label="Del-Az (arcmin)", marker="o")
    if mode in ["del-el", "both"]:
        plt.plot(df_sorted["Az [deg]"], df_sorted["Del-El [amin]"],
                 label="Del-El (arcmin)", marker="o")

    plt.xlabel("Azimuth (degrees)")
    plt.ylabel("Offset (arcmin)")
    plt.title("Telescope Pointing Offsets")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
