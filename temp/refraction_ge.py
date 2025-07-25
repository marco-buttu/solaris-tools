import numpy as np # Import numpy for mathematical functions like tan and pi
import argparse # Import the argparse module for command-line argument parsing

def celsius_to_kelvin(temp_celsius):
    """
    Converts temperature from Celsius to Kelvin.
    """
    return temp_celsius + 273.15

def saturation_vapor_pressure(temp_celsius):
    """
    Calculates saturation vapor pressure (e_s) in hPa.
    Formula based on Recommendation ITU-R P.453.
    """
    return 6.112 * np.exp((17.67 * temp_celsius) / (temp_celsius + 243.5))

def water_vapor_pressure(relative_humidity_percent, temp_celsius):
    """
    Calculates water vapor pressure (e) in hPa.
    """
    e_s = saturation_vapor_pressure(temp_celsius)
    return (relative_humidity_percent / 100.0) * e_s

def calculate_refractivity_N(pressure_hPa, temperature_celsius, relative_humidity_percent):
    """
    Calculates the air refractivity (N) in N-units.
    Formula based on Recommendation ITU-R P.453-12.
    N = (n-1) * 10^6
    where:
    P = total air pressure in hPa
    T = temperature in Kelvin
    e = partial water vapor pressure in hPa
    """
    T_kelvin = celsius_to_kelvin(temperature_celsius)
    e = water_vapor_pressure(relative_humidity_percent, temperature_celsius)

    # Check to prevent division by zero or invalid temperature values
    if T_kelvin <= 0:
        raise ValueError("Temperature must be greater than 0 Kelvin.")

    N = (77.6 / T_kelvin) * (pressure_hPa + (4810 * e / T_kelvin))
    return N

def calculate_refraction_angle_arcmin(elevation_deg, pressure_hPa, temperature_celsius, relative_humidity_percent):
    """
    Calculates the atmospheric refraction angle in arcminutes.

    Parameters:
    elevation_deg (float): Apparent elevation angle of the signal in degrees (relative to the horizon).
                           Valid values are typically > 0 degrees.
    pressure_hPa (float): Atmospheric pressure at the surface in hPa (hectopascals or mbar).
    temperature_celsius (float): Air temperature at the surface in degrees Celsius.
    relative_humidity_percent (float): Relative humidity in percentage (0-100%).

    Returns:
    float: The refraction angle in arcminutes. The object will appear higher by this value.
           Returns None if the elevation angle is too low or invalid.
    """
    if elevation_deg <= 0:
        print("Warning: This formula is valid for elevation angles > 0 degrees. Returning None.")
        return None

    # Calculate surface refractivity (N_s)
    N_s = calculate_refractivity_N(pressure_hPa, temperature_celsius, relative_humidity_percent)

    # Convert elevation angle from degrees to radians for trigonometric functions
    elevation_radians = np.deg2rad(elevation_deg)

    # Approximate formula for refraction angle (tau in milliradians).
    # This formula is common for moderate elevation angles (e.g., > 1-2 degrees)
    # and is based on a simplified atmospheric model. For very low angles (<1-2 deg),
    # refraction is more complex and would require more advanced models
    # (e.g., integration of profiles).
    # tau [mrad] = (N_s / 1000) * (1 / tan(elevation_radians))
    if np.tan(elevation_radians) == 0: # Avoid division by zero for 0 elevation
        print("Error: Zero elevation angle, cannot calculate refraction with this formula.")
        return None

    refraction_mrad = (N_s / 1000.0) / np.tan(elevation_radians)

    # Convert refraction angle from milliradians to arcminutes
    # 1 milliradian = 0.001 radians
    # 1 radian = 180/pi degrees
    # 1 degree = 60 arcminutes
    # So, 1 mrad = 0.001 * (180/pi) * 60 arcminutes = 3.43774677 arcminutes
    refraction_arcmin = refraction_mrad * (180 / np.pi) * (60 / 1000)

    return refraction_arcmin

# --- Main execution block for command-line arguments ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''
        This script calculates the atmospheric refraction angle for radio waves (e.g., at 100 GHz),
        which causes celestial objects (like satellites) to appear higher in the sky than their
        true geometric position. The calculation is based on the apparent elevation angle,
        atmospheric pressure, temperature, and relative humidity at the observation point.

        The script uses standard formulas from ITU-R P.453 for refractivity and a common
        approximation for the refraction angle (suitable for elevation angles generally > 1-2 degrees).

        Usage Examples:
        1. Calculate refraction for a 5-degree elevation with default atmospheric conditions:
           python calculate_refraction.py --elevation 5.0

        2. Calculate refraction with specific parameters:
           python calculate_refraction.py --elevation 10.0 --pressure 1015.0 --temperature 22.5 --humidity 75.0

        3. Get help message and see default values:
           python calculate_refraction.py --help
        ''',
        formatter_class=argparse.RawTextHelpFormatter # Use RawTextHelpFormatter to preserve newlines in description
    )

    parser.add_argument(
        '--elevation',
        type=float,
        required=True, # This parameter is mandatory
        help='Apparent elevation angle in degrees (e.g., 5.0).'
    )
    parser.add_argument(
        '--pressure',
        type=float,
        default=1013.25, # Standard atmospheric pressure at sea level
        help='Atmospheric pressure in hPa (hectopascals or mbar).'
    )
    parser.add_argument(
        '--temperature',
        type=float,
        default=15.0, # Standard atmospheric temperature
        help='Air temperature in degrees Celsius.'
    )
    parser.add_argument(
        '--humidity',
        type=float,
        default=70.0, # Typical relative humidity in percentage (0-100)
        help='Relative humidity in percentage (0-100).'
    )

    args = parser.parse_args() # Parse the arguments provided by the user

    print("--- Atmospheric Refraction Angle Calculation (100 GHz band) ---")
    print(f"Provided Parameters:")
    print(f"  Elevation: {args.elevation} degrees")
    print(f"  Pressure: {args.pressure} hPa")
    print(f"  Temperature: {args.temperature} °C")
    print(f"  Relative Humidity: {args.humidity} %")

    try:
        refraction_angle = calculate_refraction_angle_arcmin(
            args.elevation,
            args.pressure,
            args.temperature,
            args.humidity
        )

        if refraction_angle is not None:
            print(f"\nEstimated Refraction Angle: {refraction_angle:.3f} arcminutes")
            print("\nNote: Refraction makes the object appear higher than its true position.")
            print("For very low elevation angles (e.g., < 1-2 degrees), this formula is an approximation.")
            print("For precise calculations at low angles, more complex models or ray-tracing may be needed.")
    except ValueError as e:
        print(f"\nError in parameters: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
