#!/usr/bin/env python3
"""
Compute approximate atmospheric refraction for radio/millimeter wavelengths (~100 GHz).

Usage:
    python refraction_standalone.py --freq 100 --elev 30 --pressure 640 --temp -60 --humidity 0.2

Arguments:
    --freq      Observing frequency in GHz (default: 100)
    --elev      Geometric elevation in degrees
    --pressure  Atmospheric pressure in hPa
    --temp      Temperature in Celsius
    --humidity  Relative humidity (0-1)
"""

import argparse
import numpy as np

def refractivity(P_hPa, T_K, RH):
    """
    Compute refractivity N = (n-1)*1e6 using a simplified Liebe model.
    P_hPa : pressure in hPa
    T_K : temperature in Kelvin
    RH : relative humidity (0-1)
    """
    # Partial pressure of water vapor (approximation using RH and Tetens formula)
    T_C = T_K - 273.15
    es = 6.112 * np.exp((17.67 * T_C) / (T_C + 243.5))  # hPa
    e = RH * es

    # Smith–Weintraub / Liebe coefficients for radio frequencies
    N_dry = 77.6 * (P_hPa / T_K)
    N_wet = 3.73e5 * (e / T_K**2)
    return N_dry + N_wet

def refraction_angle(elev_deg, P_hPa, T_C, RH):
    """
    Approximate refraction angle in arcsec for given elevation, pressure, temperature and RH.
    """
    T_K = T_C + 273.15
    N = refractivity(P_hPa, T_K, RH)
    elev_rad = np.radians(elev_deg)

    # Simple plane-parallel approximation: R ≈ N * 1e-6 * tan(Z)
    Z = np.pi/2 - elev_rad  # zenith distance
    R_rad = N * 1e-6 * np.tan(Z)
    return np.degrees(R_rad) * 3600.0  # arcsec

def main():
    parser = argparse.ArgumentParser(description="Approximate atmospheric refraction at 100 GHz.")
    parser.add_argument("--freq", type=float, default=100.0, help="Frequency in GHz (default: 100).")
    parser.add_argument("--elev", type=float, required=True, help="Elevation in degrees.")
    parser.add_argument("--pressure", type=float, required=True, help="Pressure in hPa.")
    parser.add_argument("--temp", type=float, required=True, help="Temperature in Celsius.")
    parser.add_argument("--humidity", type=float, required=True, help="Relative humidity (0-1).")
    args = parser.parse_args()

    R_arcsec = refraction_angle(args.elev, args.pressure, args.temp, args.humidity)
    print(f"Refraction at {args.elev}° elev, {args.freq} GHz = {R_arcsec:.1f} arcsec")

if __name__ == "__main__":
    main()
