#!/usr/bin/env python3

"""
Plot ideal and real scan trajectories (azimuth and/or elevation) for telescope scans
along the Sun. You can visualize only azimuths, only elevations, or both, for both the
ideal and the real trajectory.

A descriptive box in the bottom left displays the main parameters and the maximum error.

Parameters:
    -d / --duration               : Scan duration in seconds (default: 15.0)
    -l / --length                 : Scan length in degrees (default: 1.5)
    -p / --place / --location     : Observing location: 'concordia' or 'testa_grigia'
                                    (default: concordia)
    -s / --shift / --delay        : Delay in seconds between the ideal and real scan
                                    (default: 1.0)
    -n / --interpolation_points   : Number of intermediate interpolation (control)
                                    points (default: 0)
    -t / --observation_time       : Observation start time UTC,
                                    format: YYYY-MM-DDTHH:MM:SS
                                    (default: 2025-12-21T02:00:00)
    -i / --num_samples            : Number of samples per trajectory (default: 100)
    --plot                        : Which quantity to plot: 'azimuth', 'elevation',
                                    or 'both' (default: both)
    --save-plot                   : If set, saves the plot to the given filename
                                    (png, pdf, etc.)

Example usage:
    python plot_trajectories.py \
        --plot azimuth --duration 20 --length 2.0 \
        --location concordia --delay 2.0 --interpolation_points \
"""

import argparse
import matplotlib.pyplot as plt
import numpy as np
from astropy.time import Time
from astropy.coordinates import EarthLocation, NonRotationTransformationWarning
import astropy.units as u
import warnings

from pointing.altaz_scan_error import compute_ideal_trajectory, compute_real_trajectory

warnings.filterwarnings("ignore", category=NonRotationTransformationWarning)


def parse_args():
    """Parse and return command-line arguments for the script."""
    parser = argparse.ArgumentParser(
        description="Plot ideal and real scan trajectories: "
        "azimuth, elevation, or both."
    )
    parser.add_argument(
        "-d",
        "--duration",
        type=float,
        default=15.0,
        help="Scan duration in seconds (default: 15.0)",
    )
    parser.add_argument(
        "-l",
        "--length",
        type=float,
        default=1.5,
        help="Scan length in degrees (default: 1.5)",
    )
    parser.add_argument(
        "-p",
        "--place",
        "--location",
        dest="location",
        type=str,
        choices=["concordia", "testa_grigia"],
        default="concordia",
        help="Observing location: 'concordia' or 'testa_grigia' (default: concordia)",
    )
    parser.add_argument(
        "-s",
        "--shift",
        "--delay",
        dest="delay",
        type=float,
        default=1.0,
        help="Delay in seconds between the ideal and real scan (default: 1.0)",
    )
    parser.add_argument(
        "-n",
        "--interpolation_points",
        type=int,
        default=0,
        help="Number of intermediate interpolation (control) points (default: 0)",
    )
    parser.add_argument(
        "-t",
        "--observation_time",
        type=str,
        default="2025-12-21T02:00:00",
        help="Observation time in UTC, format: YYYY-MM-DDTHH:MM:SS "
        "(default: 2025-12-21T02:00:00)",
    )
    parser.add_argument(
        "-i",
        "--num_samples",
        type=int,
        default=100,
        help="Number of points in each trajectory (default: 100)",
    )
    parser.add_argument(
        "--plot",
        choices=["azimuth", "elevation", "both"],
        default="both",
        help="Which quantity to plot: 'azimuth', 'elevation', or 'both' "
        "(default: both)",
    )
    parser.add_argument(
        "--save-plot",
        type=str,
        default=None,
        help="If set, saves the plot to the given filename (png, pdf, etc.)",
    )
    return parser.parse_args()


def get_location(location_name):
    """Return EarthLocation for the selected location name."""
    if location_name == "concordia":
        return EarthLocation(lat=-75.1 * u.deg, lon=123.35 * u.deg, height=3233 * u.m)
    elif location_name == "testa_grigia":
        return EarthLocation(lat=45.8309 * u.deg, lon=7.7864 * u.deg, height=3315 * u.m)
    else:
        raise ValueError(f"Unknown location: {location_name}")


def compute_max_error(ideal_altaz, real_altaz):
    """
    Compute the maximum angular separation (in arcseconds) between the two trajectories.
    """
    # Calculate angular separation for each point
    separation = ideal_altaz.separation(real_altaz)
    max_err = np.max(separation).to(u.arcsec)
    return max_err.value


def plot_trajectories(ideal_altaz, real_altaz, mode="both", params=None):
    """
    Plot azimuth and/or elevation (ideal and real) as a function of time.
    X axis shows time both as seconds from start and as UTC time (secondary axis).
    A descriptive box at the bottom left shows scan parameters and max error.
    """
    times = ideal_altaz.obstime
    t0 = times[0]
    seconds = (times - t0).sec
    timestamps = [t.datetime.strftime("%H:%M:%S") for t in times]
    fig, ax1 = plt.subplots(figsize=(10, 6))

    if mode == "azimuth":
        ax1.plot(seconds, ideal_altaz.az.deg, label="Ideal Azimuth", color="tab:blue")
        ax1.plot(seconds, real_altaz.az.deg, label="Real Azimuth", color="tab:orange")
        ylabel = "Azimuth [deg]"
        title = "Azimuth vs Time"
    elif mode == "elevation":
        ax1.plot(
            seconds, ideal_altaz.alt.deg, label="Ideal Elevation", color="tab:green"
        )
        ax1.plot(seconds, real_altaz.alt.deg, label="Real Elevation", color="tab:red")
        ylabel = "Elevation [deg]"
        title = "Elevation vs Time"
    else:
        ax1.plot(seconds, ideal_altaz.az.deg, label="Ideal Azimuth", color="tab:blue")
        ax1.plot(seconds, real_altaz.az.deg, label="Real Azimuth", color="tab:orange")
        ax1.plot(
            seconds, ideal_altaz.alt.deg, label="Ideal Elevation", color="tab:green"
        )
        ax1.plot(seconds, real_altaz.alt.deg, label="Real Elevation", color="tab:red")
        ylabel = "Angle [deg]"
        title = "Azimuth/Elevation vs Time"

    ax1.set_xlabel("Time [s from start]")
    ax1.set_ylabel(ylabel)
    ax1.set_title(title)
    ax1.legend()
    ax1.grid(True)

    # Secondary x-axis with UTC time
    def tick_format(x, pos):
        idx = int(np.clip(np.round(x), 0, len(timestamps) - 1))
        return timestamps[idx]

    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())
    tick_locs = np.linspace(seconds[0], seconds[-1], min(8, len(seconds)))
    ax2.set_xticks(tick_locs)
    ax2.set_xticklabels([tick_format(x, None) for x in tick_locs])
    ax2.set_xlabel("Time [UTC]")
    fig.tight_layout()

    # Add description box with scan parameters and max error
    if params is not None:
        # Prepare the description text
        description = (
            f"Location: {params['location']}, Time: "
            f"{params['observation_time']}\n"
            f"Scan duration: {params['duration']} s, Scan length: "
            f"{params['length']} deg\n"
            f"Interpolation points: {params['interpolation_points']}, "
            f"Delay: {params['delay']}, "
            f"Max error: {params['max_error']:.2f} arcsec"
        )
        plt.gcf().text(
            0.02,
            0.03,
            description,
            fontsize=9,
            va="bottom",
            ha="left",
            bbox=dict(facecolor="white", edgecolor="black", alpha=0.9),
        )


def main():
    """Main function. Parse arguments, compute trajectories, and show plot."""
    args = parse_args()
    location = get_location(args.location)
    obs_time = Time(args.observation_time)
    # Compute both ideal and real trajectories
    ideal = compute_ideal_trajectory(
        location, obs_time, args.duration, args.length, args.num_samples
    )
    real = compute_real_trajectory(
        location,
        obs_time,
        args.duration,
        args.length,
        args.delay,
        args.interpolation_points,
        args.num_samples,
    )
    max_error = compute_max_error(ideal, real)
    params = {
        "location": args.location,
        "observation_time": obs_time.isot,
        "duration": args.duration,
        "length": args.length,
        "delay": args.delay,
        "interpolation_points": args.interpolation_points,
        "max_error": max_error,
    }
    plot_trajectories(ideal, real, mode=args.plot, params=params)
    if args.save_plot:
        plt.savefig(args.save_plot)
        print(f"Plot saved as {args.save_plot}")
    plt.show()


if __name__ == "__main__":
    main()
