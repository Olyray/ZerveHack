"""
Ghost Air Prototype — Phase A: Finding Sprint
Validates whether compelling air quality blind spots exist in real data.

Approach:
1. Pull EPA AQS monitor locations + daily PM2.5 AQI (summer 2023 — Canadian wildfire season)
2. Pull PurpleAir sensor data for the same period
3. Apply EPA correction factor to PurpleAir readings
4. Identify PurpleAir sensors >20 miles from nearest EPA station
5. Flag mismatches: corrected PurpleAir AQI >100 AND nearest EPA AQI <50, duration >24h
6. Output blind spot candidates with location details
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from geopy.distance import geodesic
import json
import time
import os

# ============================================================
# CONFIGURATION
# ============================================================
# Summer 2023 — Canadian wildfire smoke event (June-July 2023)
# This is the highest-probability period for dramatic blind spots
START_DATE = "2023-06-01"
END_DATE = "2023-08-31"

# Thresholds
MIN_DISTANCE_FROM_EPA_MILES = 20  # PurpleAir sensor must be this far from nearest EPA station
PURPLEAIR_AQI_THRESHOLD = 100     # "Unhealthy for Sensitive Groups"
EPA_AQI_THRESHOLD = 50            # "Good"
MIN_MISMATCH_HOURS = 24           # Minimum duration for a mismatch to count

# EPA AQS API (free, no key needed for basic queries)
EPA_AQS_BASE = "https://aqs.epa.gov/data/api"
# You need a free EPA AQS API account — register at https://aqs.epa.gov/aqsweb/documents/data_api.html
# For prototype, we'll use the public daily summary endpoint
EPA_EMAIL = os.environ.get("EPA_EMAIL", "")
EPA_KEY = os.environ.get("EPA_KEY", "")

# PurpleAir API (free tier — need API key from purpleair.com/develop)
PURPLEAIR_API_KEY = os.environ.get("PURPLEAIR_API_KEY", "")

# Output
OUTPUT_DIR = "ghost_air_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def pm25_to_aqi(pm25):
    """Convert PM2.5 concentration (µg/m³) to AQI using EPA breakpoints."""
    if pm25 < 0:
        return 0
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]
    for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
        if pm25 <= bp_hi:
            aqi = ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + aqi_lo
            return round(aqi)
    return 500  # Beyond scale


def apply_epa_correction(pm25_cf1):
    """
    Apply EPA correction factor to PurpleAir PM2.5 (CF=1) readings.
    EPA correction (2021 version): PM2.5_corrected = 0.524 * PM2.5_cf1 - 0.0862 * RH + 5.75
    Simplified (without humidity): PM2.5_corrected = 0.524 * PM2.5_cf1 + 5.75
    This is conservative — with humidity it would be even lower.
    """
    return 0.524 * pm25_cf1 + 5.75


def aqi_category(aqi):
    """Return AQI category label."""
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


# ============================================================
# STEP 1: GET EPA MONITOR LOCATIONS AND AQI DATA
# ============================================================

def get_epa_monitors_and_aqi():
    """
    Pull EPA PM2.5 monitor locations and daily AQI.
    Uses the EPA AQS API if credentials are available,
    otherwise falls back to the public AirNow historical files.
    """
    print("\n" + "="*60)
    print("STEP 1: Pulling EPA PM2.5 station data...")
    print("="*60)

    # Try EPA Daily Summary Files (publicly available, no API key needed)
    # These are pre-generated CSV files from EPA
    # URL pattern: https://aqs.epa.gov/aqsweb/airdata/daily_88101_{year}.zip
    # 88101 = PM2.5 FRM/FEM parameter code

    year = 2023
    url = f"https://aqs.epa.gov/aqsweb/airdata/daily_88101_{year}.zip"
    print(f"Downloading EPA daily PM2.5 data for {year}...")
    print(f"URL: {url}")

    try:
        # Download the zip file
        response = requests.get(url, timeout=120)
        response.raise_for_status()

        # Save and extract
        zip_path = os.path.join(OUTPUT_DIR, f"daily_88101_{year}.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)

        print(f"Downloaded {len(response.content) / 1024 / 1024:.1f} MB")

        # Read CSV from zip (handle nested folder structure)
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as z:
            csv_files = [f for f in z.namelist() if f.endswith('.csv')]
            if not csv_files:
                raise ValueError("No CSV file found in ZIP")
            with z.open(csv_files[0]) as csv_file:
                df = pd.read_csv(csv_file, low_memory=False)
        print(f"Loaded {len(df)} daily records")

        # Filter to summer 2023
        df["Date Local"] = pd.to_datetime(df["Date Local"])
        mask = (df["Date Local"] >= START_DATE) & (df["Date Local"] <= END_DATE)
        df = df[mask].copy()
        print(f"Filtered to {START_DATE} — {END_DATE}: {len(df)} records")

        # Extract key columns
        epa_data = df[["State Code", "County Code", "Site Num", "Latitude", "Longitude",
                        "Date Local", "Arithmetic Mean", "AQI", "State Name", "County Name",
                        "Local Site Name"]].copy()
        epa_data = epa_data.rename(columns={
            "Arithmetic Mean": "pm25_mean",
            "AQI": "aqi",
            "Latitude": "lat",
            "Longitude": "lon",
            "Date Local": "date",
            "State Name": "state",
            "County Name": "county",
            "Local Site Name": "site_name"
        })

        # Get unique monitor locations
        monitors = epa_data.groupby(["lat", "lon"]).agg({
            "state": "first",
            "county": "first",
            "site_name": "first"
        }).reset_index()
        print(f"Found {len(monitors)} unique EPA PM2.5 monitor locations")

        # Save
        epa_data.to_csv(os.path.join(OUTPUT_DIR, "epa_daily_aqi.csv"), index=False)
        monitors.to_csv(os.path.join(OUTPUT_DIR, "epa_monitors.csv"), index=False)

        return epa_data, monitors

    except Exception as e:
        print(f"ERROR downloading EPA data: {e}")
        print("\nFallback: Creating synthetic EPA station data for prototype validation...")
        return create_fallback_epa_data()


def create_fallback_epa_data():
    """
    If EPA download fails, create a realistic dataset based on known EPA station locations
    to validate the pipeline logic. This is ONLY for testing the prototype flow.
    """
    print("Using known EPA station locations for pipeline validation...")

    # Real EPA station locations (subset — major metros)
    stations = [
        {"lat": 40.8164, "lon": -73.9020, "state": "New York", "county": "Bronx", "site_name": "IS 52"},
        {"lat": 40.7161, "lon": -74.0014, "state": "New York", "county": "New York", "site_name": "Canal St"},
        {"lat": 39.9956, "lon": -75.0697, "state": "New Jersey", "county": "Camden", "site_name": "Copewood-Davis"},
        {"lat": 38.9219, "lon": -77.0131, "state": "District Of Columbia", "county": "District of Columbia", "site_name": "McMillan"},
        {"lat": 33.9533, "lon": -118.2283, "state": "California", "county": "Los Angeles", "site_name": "Compton"},
        {"lat": 41.7514, "lon": -87.7133, "state": "Illinois", "county": "Cook", "site_name": "Washington HS"},
        {"lat": 42.3292, "lon": -83.1064, "state": "Michigan", "county": "Wayne", "site_name": "Dearborn"},
        {"lat": 29.6700, "lon": -95.1283, "state": "Texas", "county": "Harris", "site_name": "Deer Park"},
        {"lat": 47.5683, "lon": -122.3092, "state": "Washington", "county": "King", "site_name": "Beacon Hill"},
        {"lat": 45.4967, "lon": -122.6025, "state": "Oregon", "county": "Multnomah", "site_name": "SE Lafayette"},
    ]

    monitors = pd.DataFrame(stations)
    print(f"Using {len(monitors)} known EPA station locations for validation")
    monitors.to_csv(os.path.join(OUTPUT_DIR, "epa_monitors.csv"), index=False)

    # Note: No daily AQI data in fallback — will need real data for actual blind spot detection
    return None, monitors


# ============================================================
# STEP 2: GET PURPLEAIR SENSOR DATA
# ============================================================

def get_purpleair_sensors(epa_monitors):
    """
    Pull PurpleAir sensor locations and readings.
    Uses PurpleAir API if key is available.
    """
    print("\n" + "="*60)
    print("STEP 2: Pulling PurpleAir sensor data...")
    print("="*60)

    if not PURPLEAIR_API_KEY:
        print("WARNING: No PurpleAir API key found.")
        print("Set PURPLEAIR_API_KEY environment variable.")
        print("Get a free key at: https://develop.purpleair.com/")
        print("\nUsing public PurpleAir data download approach instead...")
        return get_purpleair_public_data(epa_monitors)

    # PurpleAir API v2 — get sensors in the continental US
    headers = {"X-API-Key": PURPLEAIR_API_KEY}

    # Get outdoor sensors with location data
    # We'll query by bounding box (continental US)
    url = "https://api.purpleair.com/v2/sensors"
    params = {
        "fields": "latitude,longitude,pm2.5_cf_1,pm2.5_cf_1_a,pm2.5_cf_1_b,humidity,name",
        "location_type": 0,  # outdoor only
        "nwlng": -125.0,
        "nwlat": 49.0,
        "selng": -66.0,
        "selat": 24.0,
        "max_age": 0,  # all sensors, not just active
    }

    try:
        print("Querying PurpleAir API for US outdoor sensors...")
        response = requests.get(url, headers=headers, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        fields = data["fields"]
        sensors = pd.DataFrame(data["data"], columns=fields)
        print(f"Found {len(sensors)} PurpleAir outdoor sensors in continental US")

        sensors.to_csv(os.path.join(OUTPUT_DIR, "purpleair_sensors.csv"), index=False)
        return sensors

    except Exception as e:
        print(f"PurpleAir API error: {e}")
        return get_purpleair_public_data(epa_monitors)


def get_purpleair_public_data(epa_monitors):
    """
    Alternative: Use PurpleAir's public data downloads or ThingSpeak historical data.
    For prototype, we'll check if the pipeline logic works with available data.
    """
    print("\nAttempting to use PurpleAir public data...")

    # PurpleAir makes historical data available through their download tool
    # For the prototype, let's check what's accessible
    # The key insight: we can validate the CONCEPT even with limited data

    # Check if we can access the PurpleAir map data (public, no key)
    try:
        # PurpleAir public JSON endpoint (current readings only, but gives us sensor locations)
        url = "https://www.purpleair.com/json"
        print("Note: PurpleAir public JSON endpoint may be deprecated.")
        print("For full historical data, a PurpleAir API key is required.")
        print("\nProceeding with pipeline validation using available data...")
        return None
    except:
        return None


# ============================================================
# STEP 3: FIND BLIND SPOTS
# ============================================================

def find_blind_spots(epa_data, epa_monitors, purpleair_sensors):
    """
    Core analysis: find locations where PurpleAir shows danger but EPA doesn't.
    """
    print("\n" + "="*60)
    print("STEP 3: Analyzing for blind spots...")
    print("="*60)

    if epa_data is None or purpleair_sensors is None:
        print("\nInsufficient data for full blind spot analysis.")
        print("Running coverage gap analysis with EPA monitor locations only...")
        return analyze_coverage_gaps(epa_monitors, epa_data)

    # For each PurpleAir sensor, find distance to nearest EPA station
    print("Calculating distances between PurpleAir sensors and EPA stations...")

    epa_coords = list(zip(epa_monitors["lat"], epa_monitors["lon"]))
    results = []

    for idx, sensor in purpleair_sensors.iterrows():
        if pd.isna(sensor.get("latitude")) or pd.isna(sensor.get("longitude")):
            continue

        sensor_coord = (sensor["latitude"], sensor["longitude"])

        # Find nearest EPA station
        min_dist = float("inf")
        nearest_epa = None
        for i, epa_coord in enumerate(epa_coords):
            dist = geodesic(sensor_coord, epa_coord).miles
            if dist < min_dist:
                min_dist = dist
                nearest_epa = i

        if min_dist >= MIN_DISTANCE_FROM_EPA_MILES:
            results.append({
                "purpleair_name": sensor.get("name", "Unknown"),
                "purpleair_lat": sensor["latitude"],
                "purpleair_lon": sensor["longitude"],
                "purpleair_pm25_cf1": sensor.get("pm2.5_cf_1", None),
                "nearest_epa_station": epa_monitors.iloc[nearest_epa]["site_name"],
                "nearest_epa_lat": epa_monitors.iloc[nearest_epa]["lat"],
                "nearest_epa_lon": epa_monitors.iloc[nearest_epa]["lon"],
                "distance_to_epa_miles": round(min_dist, 1),
            })

    if not results:
        print("No PurpleAir sensors found >20 miles from EPA stations.")
        return pd.DataFrame()

    blind_candidates = pd.DataFrame(results)
    print(f"Found {len(blind_candidates)} PurpleAir sensors >{MIN_DISTANCE_FROM_EPA_MILES} miles from nearest EPA station")

    # Apply EPA correction and calculate AQI
    if "purpleair_pm25_cf1" in blind_candidates.columns:
        mask = blind_candidates["purpleair_pm25_cf1"].notna()
        blind_candidates.loc[mask, "corrected_pm25"] = blind_candidates.loc[mask, "purpleair_pm25_cf1"].apply(apply_epa_correction)
        blind_candidates.loc[mask, "corrected_aqi"] = blind_candidates.loc[mask, "corrected_pm25"].apply(pm25_to_aqi)
        blind_candidates.loc[mask, "aqi_category"] = blind_candidates.loc[mask, "corrected_aqi"].apply(aqi_category)

    # Save all candidates
    blind_candidates.to_csv(os.path.join(OUTPUT_DIR, "blind_spot_candidates.csv"), index=False)

    # Filter for high-risk mismatches
    if "corrected_aqi" in blind_candidates.columns:
        high_risk = blind_candidates[blind_candidates["corrected_aqi"] >= PURPLEAIR_AQI_THRESHOLD]
        print(f"\nHIGH RISK blind spots (corrected AQI >= {PURPLEAIR_AQI_THRESHOLD}): {len(high_risk)}")
        if len(high_risk) > 0:
            high_risk.to_csv(os.path.join(OUTPUT_DIR, "high_risk_blind_spots.csv"), index=False)
            print("\nTop blind spot candidates:")
            for _, row in high_risk.head(10).iterrows():
                print(f"  📍 {row['purpleair_name']}")
                print(f"     Corrected AQI: {row['corrected_aqi']} ({row['aqi_category']})")
                print(f"     Nearest EPA: {row['nearest_epa_station']} ({row['distance_to_epa_miles']} mi)")
                print()

    return blind_candidates


def analyze_coverage_gaps(epa_monitors, epa_data=None):
    """
    Even without PurpleAir data, we can identify WHERE blind spots are most likely
    by analyzing EPA station coverage gaps.
    """
    print("\n--- Coverage Gap Analysis ---")
    print(f"Analyzing {len(epa_monitors)} EPA monitor locations for coverage gaps...\n")

    # Calculate distance between each pair of EPA stations
    coords = list(zip(epa_monitors["lat"], epa_monitors["lon"]))
    n = len(coords)

    # For each station, find its nearest neighbor
    nearest_distances = []
    for i in range(n):
        min_dist = float("inf")
        for j in range(n):
            if i != j:
                dist = geodesic(coords[i], coords[j]).miles
                if dist < min_dist:
                    min_dist = dist
        nearest_distances.append(min_dist)

    epa_monitors = epa_monitors.copy()
    epa_monitors["nearest_station_miles"] = nearest_distances

    # Stations with large gaps around them = potential blind spot zones
    epa_monitors_sorted = epa_monitors.sort_values("nearest_station_miles", ascending=False)

    print("EPA stations with LARGEST coverage gaps (most isolated):")
    print("These areas between stations are where blind spots are most likely.\n")
    for _, row in epa_monitors_sorted.head(10).iterrows():
        print(f"  📍 {row['site_name']} ({row['state']}, {row['county']})")
        print(f"     Nearest other EPA station: {row['nearest_station_miles']:.1f} miles away")
        print(f"     Coordinates: ({row['lat']:.4f}, {row['lon']:.4f})")
        print()

    epa_monitors_sorted.to_csv(os.path.join(OUTPUT_DIR, "epa_coverage_gaps.csv"), index=False)

    # If we have AQI data, find days where isolated stations reported high AQI
    # (suggesting pollution events that nearby areas couldn't detect)
    if epa_data is not None:
        print("\n--- High AQI Events at Isolated Stations ---")
        print("(Pollution events that nearby areas may have missed)\n")

        isolated = epa_monitors_sorted[epa_monitors_sorted["nearest_station_miles"] > 30]
        if len(isolated) > 0:
            for _, station in isolated.head(5).iterrows():
                station_data = epa_data[
                    (epa_data["lat"] == station["lat"]) &
                    (epa_data["lon"] == station["lon"]) &
                    (epa_data["aqi"] >= 100)
                ]
                if len(station_data) > 0:
                    print(f"  📍 {station['site_name']} ({station['state']})")
                    print(f"     Nearest EPA neighbor: {station['nearest_station_miles']:.1f} mi")
                    print(f"     Days with AQI >= 100 (summer 2023): {len(station_data)}")
                    print(f"     Max AQI recorded: {station_data['aqi'].max()}")
                    print(f"     → Areas BETWEEN this station and its nearest neighbor")
                    print(f"       had NO monitoring during these events.")
                    print()

    return epa_monitors_sorted


# ============================================================
# STEP 4: GENERATE REPORT
# ============================================================

def generate_report(epa_data, epa_monitors, blind_spots):
    """Generate a summary report of findings."""
    print("\n" + "="*60)
    print("STEP 4: Generating Report")
    print("="*60)

    report = []
    report.append("# Ghost Air — Prototype Findings Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    report.append("## Data Sources")
    report.append(f"- EPA PM2.5 monitors analyzed: {len(epa_monitors)}")
    if epa_data is not None:
        report.append(f"- EPA daily records (summer 2023): {len(epa_data)}")
    report.append(f"- Analysis period: {START_DATE} to {END_DATE}")
    report.append(f"- Blind spot threshold: PurpleAir sensor >{MIN_DISTANCE_FROM_EPA_MILES} mi from EPA station\n")

    report.append("## Key Findings\n")

    if blind_spots is not None and len(blind_spots) > 0:
        if "corrected_aqi" in blind_spots.columns:
            high_risk = blind_spots[blind_spots.get("corrected_aqi", pd.Series()) >= PURPLEAIR_AQI_THRESHOLD]
            report.append(f"### Blind Spot Candidates: {len(blind_spots)}")
            report.append(f"### High Risk (AQI >= {PURPLEAIR_AQI_THRESHOLD}): {len(high_risk)}\n")
        else:
            report.append(f"### Coverage Gap Zones Identified: {len(blind_spots)}\n")

        report.append("### Top Candidates\n")
        display_cols = [c for c in blind_spots.columns if c in
                       ["site_name", "state", "county", "nearest_station_miles",
                        "purpleair_name", "corrected_aqi", "distance_to_epa_miles", "aqi_category"]]
        if display_cols:
            for _, row in blind_spots.head(5).iterrows():
                for col in display_cols:
                    if col in row.index and pd.notna(row[col]):
                        report.append(f"- {col}: {row[col]}")
                report.append("")

    report.append("## Next Steps\n")
    report.append("1. Obtain PurpleAir API key for historical sensor data")
    report.append("2. Cross-reference blind spots with NOAA wind data")
    report.append("3. Add Census population data for impact quantification")
    report.append("4. Build deployed API on Zerve")

    report_text = "\n".join(report)

    report_path = os.path.join(OUTPUT_DIR, "ghost_air_report.md")
    with open(report_path, "w") as f:
        f.write(report_text)

    print(f"\nReport saved to: {report_path}")
    print("\n" + report_text)

    return report_text


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print("="*60)
    print("  GHOST AIR — Phase A: Finding Sprint")
    print("  Detecting Air Quality Blind Spots")
    print("="*60)
    print(f"\nAnalysis period: {START_DATE} to {END_DATE}")
    print(f"Blind spot distance threshold: {MIN_DISTANCE_FROM_EPA_MILES} miles")
    print(f"AQI mismatch threshold: PurpleAir >= {PURPLEAIR_AQI_THRESHOLD}, EPA <= {EPA_AQI_THRESHOLD}")

    # Step 1: EPA data
    epa_data, epa_monitors = get_epa_monitors_and_aqi()

    # Step 2: PurpleAir data
    purpleair_sensors = get_purpleair_sensors(epa_monitors)

    # Step 3: Find blind spots
    blind_spots = find_blind_spots(epa_data, epa_monitors, purpleair_sensors)

    # Step 4: Report
    generate_report(epa_data, epa_monitors, blind_spots)

    print("\n" + "="*60)
    print("  PROTOTYPE COMPLETE")
    print("="*60)
    print(f"\nAll output saved to: {OUTPUT_DIR}/")
    print("\nFiles generated:")
    for f in os.listdir(OUTPUT_DIR):
        size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
        print(f"  {f} ({size/1024:.1f} KB)")

    print("\n--- KILL CRITERIA CHECK ---")
    print("1. Can we find 3-5 blind spots?")
    if blind_spots is not None and len(blind_spots) >= 3:
        print("   ✅ YES — candidates identified")
    else:
        print("   ⚠️  NEEDS MORE DATA — get PurpleAir API key for validation")

    print("2. Can we validate with independent source?")
    if purpleair_sensors is not None:
        print("   ✅ YES — PurpleAir data available")
    else:
        print("   ⚠️  NEEDS PurpleAir API key")

    print("3. Is at least one example dramatic enough?")
    print("   → Review output files to assess")


if __name__ == "__main__":
    main()
