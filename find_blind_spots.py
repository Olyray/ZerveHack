"""
Ghost Air — Deep Blind Spot Analysis
Focus: June 7, 2023 (Canadian wildfire smoke) and other major events.
Strategy: Find pairs of EPA stations where one recorded very high AQI and a distant
neighbor recorded low AQI on the same day — the area between them is the blind spot.
"""
import pandas as pd
import numpy as np
from geopy.distance import geodesic

epa = pd.read_csv('ghost_air_output/epa_daily_aqi.csv')
monitors = pd.read_csv('ghost_air_output/epa_monitors.csv')

print("="*70)
print("GHOST AIR — Deep Blind Spot Analysis")
print("="*70)

# ============================================================
# APPROACH 1: Adjacent Station Mismatch
# Find station pairs 30-100 miles apart where AQI diverges dramatically
# The area between them = unmonitored blind spot
# ============================================================
print("\n--- APPROACH 1: Adjacent Station Mismatches ---")
print("Finding station pairs where one shows danger, the other shows safe...\n")

# Build station pair distances (only pairs 30-100 miles apart)
coords = list(zip(monitors['lat'], monitors['lon']))
n = len(coords)

# Focus on key event dates
key_dates = ['2023-06-07', '2023-06-08', '2023-06-28', '2023-06-29',
             '2023-08-19', '2023-08-20', '2023-08-28']

# Also find ALL dates with widespread high AQI
daily_high = epa[epa['aqi'] >= 150].groupby('date').size()
widespread_dates = daily_high[daily_high >= 10].index.tolist()
print(f"Dates with 10+ stations reporting AQI >= 150: {len(widespread_dates)}")
for d in widespread_dates[:10]:
    count = daily_high[d]
    print(f"  {d}: {count} stations")

all_dates = list(set(key_dates + widespread_dates[:20]))

# For efficiency, precompute distances for nearby pairs
print("\nComputing station pair distances (this takes a moment)...")
nearby_pairs = []
for i in range(n):
    for j in range(i+1, n):
        dist = geodesic(coords[i], coords[j]).miles
        if 30 <= dist <= 150:
            nearby_pairs.append((i, j, dist))

print(f"Found {len(nearby_pairs)} station pairs 30-150 miles apart")

# For each key date, find pairs with dramatic AQI mismatch
print("\n--- Searching for dramatic mismatches ---\n")
blind_spots = []

for date in sorted(all_dates):
    day_data = epa[epa['date'] == date]
    if len(day_data) == 0:
        continue

    # Create lookup: (lat, lon) -> aqi for this day
    aqi_lookup = {}
    for _, row in day_data.iterrows():
        key = (round(row['lat'], 4), round(row['lon'], 4))
        if key not in aqi_lookup or row['aqi'] > aqi_lookup[key]['aqi']:
            aqi_lookup[key] = {'aqi': row['aqi'], 'site_name': row['site_name'],
                              'state': row['state'], 'county': row['county'],
                              'pm25': row['pm25_mean']}

    for i, j, dist in nearby_pairs:
        key_i = (round(monitors.iloc[i]['lat'], 4), round(monitors.iloc[i]['lon'], 4))
        key_j = (round(monitors.iloc[j]['lat'], 4), round(monitors.iloc[j]['lon'], 4))

        if key_i not in aqi_lookup or key_j not in aqi_lookup:
            continue

        aqi_i = aqi_lookup[key_i]['aqi']
        aqi_j = aqi_lookup[key_j]['aqi']

        # One station >= 150 (Unhealthy), other <= 50 (Good)
        if (aqi_i >= 150 and aqi_j <= 50) or (aqi_j >= 150 and aqi_i <= 50):
            high_idx = i if aqi_i > aqi_j else j
            low_idx = j if aqi_i > aqi_j else i
            high_key = key_i if aqi_i > aqi_j else key_j
            low_key = key_j if aqi_i > aqi_j else key_i

            blind_spots.append({
                'date': date,
                'high_station': aqi_lookup[high_key]['site_name'],
                'high_state': aqi_lookup[high_key]['state'],
                'high_county': aqi_lookup[high_key]['county'],
                'high_aqi': aqi_lookup[high_key]['aqi'],
                'high_lat': monitors.iloc[high_idx]['lat'],
                'high_lon': monitors.iloc[high_idx]['lon'],
                'low_station': aqi_lookup[low_key]['site_name'],
                'low_state': aqi_lookup[low_key]['state'],
                'low_county': aqi_lookup[low_key]['county'],
                'low_aqi': aqi_lookup[low_key]['aqi'],
                'low_lat': monitors.iloc[low_idx]['lat'],
                'low_lon': monitors.iloc[low_idx]['lon'],
                'distance_miles': round(dist, 1),
                'aqi_gap': abs(aqi_lookup[high_key]['aqi'] - aqi_lookup[low_key]['aqi']),
            })

blind_df = pd.DataFrame(blind_spots)
if len(blind_df) > 0:
    blind_df = blind_df.sort_values('aqi_gap', ascending=False)
    blind_df.to_csv('ghost_air_output/station_mismatches.csv', index=False)

    print(f"FOUND {len(blind_df)} dramatic mismatches (AQI >= 150 vs <= 50)")
    print(f"\nTop 15 most dramatic blind spots:\n")
    for _, row in blind_df.head(15).iterrows():
        print(f"  📅 {row['date']}")
        print(f"  🔴 {row['high_station']} ({row['high_state']}, {row['high_county']}): AQI {row['high_aqi']:.0f}")
        print(f"  🟢 {row['low_station']} ({row['low_state']}, {row['low_county']}): AQI {row['low_aqi']:.0f}")
        print(f"  📏 Distance: {row['distance_miles']} miles | AQI Gap: {row['aqi_gap']:.0f}")
        mid_lat = (row['high_lat'] + row['low_lat']) / 2
        mid_lon = (row['high_lon'] + row['low_lon']) / 2
        print(f"  📍 Blind spot center: ({mid_lat:.4f}, {mid_lon:.4f})")
        print(f"  ⚠️  The {row['distance_miles']:.0f}-mile zone between these stations had NO monitoring.")
        print()

    # Summary by date
    print("\n--- Mismatches by Date ---")
    for date, group in blind_df.groupby('date'):
        print(f"  {date}: {len(group)} mismatches, max gap: {group['aqi_gap'].max():.0f}")
else:
    print("No dramatic mismatches found with current thresholds.")

# ============================================================
# APPROACH 2: Smoke Plume Edge Detection
# During June 7 event, find the geographic boundary where AQI drops
# The transition zone = where people were likely exposed but unmonitored
# ============================================================
print("\n\n--- APPROACH 2: June 7, 2023 Smoke Boundary Analysis ---")
june7 = epa[epa['date'] == '2023-06-07'].copy()
print(f"Stations reporting on June 7: {len(june7)}")
print(f"Stations with AQI >= 100: {len(june7[june7['aqi'] >= 100])}")
print(f"Stations with AQI >= 150: {len(june7[june7['aqi'] >= 150])}")
print(f"Stations with AQI >= 200: {len(june7[june7['aqi'] >= 200])}")

# Show geographic spread
print("\nAQI by state on June 7:")
state_summary = june7.groupby('state').agg(
    mean_aqi=('aqi', 'mean'),
    max_aqi=('aqi', 'max'),
    stations=('aqi', 'count')
).sort_values('max_aqi', ascending=False)
for state, row in state_summary.head(15).iterrows():
    print(f"  {state}: avg AQI {row['mean_aqi']:.0f}, max {row['max_aqi']:.0f} ({row['stations']:.0f} stations)")
