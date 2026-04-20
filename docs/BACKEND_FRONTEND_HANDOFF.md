# Ghost Air — Developer Handoff Package

---

## What to Share With Your Backend Dev

Send them these files:

### Must-Read (in this order)
| # | File | Path | Why |
|---|------|------|-----|
| 1 | **Implementation Plan** | `ghost_air_output/IMPLEMENTATION_PLAN.md` | Full picture: what we're building, why, judging criteria, day-by-day plan |
| 2 | **Dev Handoff** | `ghost_air_output/DEV_HANDOFF.md` | Technical build plan: API spec, data sources, tasks, API keys needed |
| 3 | **Findings Summary** | `ghost_air_output/FINDINGS_SUMMARY.md` | The validated findings — what the data already proved |

### Code to Reuse
| File | Path | What's Inside |
|------|------|---------------|
| **Prototype** | `ghost_air_prototype.py` | EPA data download, PM2.5→AQI conversion, station mapping, coverage gap analysis |
| **Blind Spot Finder** | `find_blind_spots.py` | Station-pair mismatch detection, the core analysis that found 24 blind spots |

### Data (Already Downloaded)
| File | Path | Contents |
|------|------|----------|
| Raw EPA data | `ghost_air_output/daily_88101_2023.zip` | Summer 2023 PM2.5 daily data (8.5 MB) |
| Processed AQI | `ghost_air_output/epa_daily_aqi.csv` | 215,732 daily AQI records |
| Station locations | `ghost_air_output/epa_monitors.csv` | 991 EPA stations with lat/lon |
| Coverage gaps | `ghost_air_output/epa_coverage_gaps.csv` | Stations ranked by isolation |
| Blind spots | `ghost_air_output/station_mismatches.csv` | 24 confirmed mismatches |

### Reference (for demo/video)
| File | Path | Purpose |
|------|------|---------|
| Demo script | `ghost_air_output/ALBANY_DEMO_SCRIPT.md` | Exact 3-min video script with timestamps |

---

## Do You Need a Frontend? YES.

You need a simple frontend. Here's why and what it should be:

### Why Frontend Matters
- **Judges give priority to deployed apps** — the hackathon brief says "Deployed projects will receive priority consideration"
- **The demo video needs a visual** — you can't demo an API call in a terminal and expect to win
- **The map IS the story** — the blind spot only makes sense when you SEE the gap on a map

### What the Frontend Should Be (Keep It Simple)

**Option A — Streamlit (Recommended for speed)**
- Fastest to build on Zerve
- Python-only (your backend dev can build it too)
- Built-in map support via `st.map()` or `pydeck`
- Deploy directly on Zerve
- **Build time: 3–5 hours**

**Option B — Gradio**
- Also Python-only
- Good for input/output interfaces
- Less flexible for maps
- **Build time: 3–5 hours**

**Option C — Separate React/HTML frontend**
- Better looking but slower to build
- Needs a frontend dev
- Overkill for a hackathon
- **Build time: 1–2 days**

### 👉 Recommendation: Go with Streamlit. One dev can build both backend + frontend.

---

## Frontend Spec (What It Must Show)

### Screen 1: The Map (Landing Page)
```
┌─────────────────────────────────────────────┐
│  GHOST AIR — Air Quality Blind Spot Detector │
├─────────────────────────────────────────────┤
│                                             │
│         [ US MAP ]                          │
│                                             │
│    🟢 = EPA stations (green dots)           │
│    🔴 = Blind spot zones (red shading)      │
│    ⚠️ = Mismatch locations (warning icons)  │
│                                             │
│  Click a red zone to see details            │
│                                             │
├─────────────────────────────────────────────┤
│  Enter zip code or coordinates: [________]  │
│                          [Check Risk]       │
└─────────────────────────────────────────────┘
```

### Screen 2: Risk Result (After zip code input)
```
┌─────────────────────────────────────────────┐
│  📍 Adirondack Region, NY 12842             │
├─────────────────────────────────────────────┤
│                                             │
│  Official AQI:    42  (Good) 🟢             │
│  Predicted AQI:   138 (Unhealthy for        │
│                        Sensitive Groups) 🟠  │
│  Blind Spot:      YES ⚠️                    │
│  Risk Level:      HIGH 🔴                   │
│                                             │
│  Nearest EPA Station: Albany, NY — 65 mi    │
│                                             │
│  Explanation:                               │
│  "This location is 65 miles from the        │
│   nearest EPA monitor. During the June 2023 │
│   wildfire event, stations on either side   │
│   showed dramatically different readings    │
│   with no monitoring in between."           │
│                                             │
│  Recommendation:                            │
│  "Limit outdoor activity. Sensitive groups  │
│   should remain indoors."                   │
│                                             │
│  48-Hour Forecast:                          │
│  Tomorrow:    AQI ~95  (Moderate) 🟡        │
│  Day After:   AQI ~52  (Moderate) 🟡        │
│                                             │
└─────────────────────────────────────────────┘
```

### Screen 3: Case Study View (When clicking a blind spot on map)
```
┌─────────────────────────────────────────────┐
│  BLIND SPOT: Albany, NY ↔ Burlington, VT    │
├─────────────────────────────────────────────┤
│                                             │
│  [ ZOOMED MAP showing both stations ]       │
│  [ Red shading between them ]               │
│  [ Wind direction arrow overlay ]           │
│                                             │
│  Station A: Albany, NY                      │
│    AQI: 166 (Unhealthy) 🔴                  │
│                                             │
│  Station B: Burlington, VT                  │
│    AQI: 11 (Good) 🟢                        │
│                                             │
│  Distance: 130 miles                        │
│  Date: June 8, 2023                         │
│  Event: Canadian wildfire smoke             │
│  Monitoring between: NONE                   │
│                                             │
│  Wind: SW at 15 mph — carrying smoke        │
│  northward through the Adirondack region    │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Backend API (What the Dev Builds)

### Endpoint 1: Risk Check
```
GET /risk?lat=43.5&lon=-73.5
GET /risk?zip=12842
```

**Response:**
```json
{
  "location": "Adirondack Region, NY",
  "nearest_epa_station": "Albany, NY",
  "nearest_epa_distance_miles": 65,
  "official_aqi": 42,
  "predicted_aqi": 138,
  "blind_spot": true,
  "risk_level": "HIGH",
  "recommendation": "Limit outdoor activity. Sensitive groups should remain indoors.",
  "explanation": "This location is 65 miles from the nearest EPA monitor. During pollution events, conditions here may differ significantly from official readings.",
  "forecast_48h": {
    "tomorrow": {"predicted_aqi": 95, "risk": "MODERATE"},
    "day_after": {"predicted_aqi": 52, "risk": "LOW"}
  }
}
```

### Endpoint 2: Blind Spots List
```
GET /blindspots
```

**Response:**
```json
{
  "count": 24,
  "blind_spots": [
    {
      "station_a": "Albany, NY",
      "station_a_aqi": 166,
      "station_b": "Burlington, VT",
      "station_b_aqi": 11,
      "distance_miles": 130,
      "date": "2023-06-08",
      "event": "Canadian wildfire smoke"
    }
  ]
}
```

### Endpoint 3: Station Map Data
```
GET /stations
```
Returns all 991 EPA station locations for map rendering.

---

## Tech Stack Summary

| Layer | Technology | Why |
|-------|-----------|-----|
| **Platform** | Zerve | Required by hackathon |
| **Backend** | Python on Zerve | Data pipeline + API |
| **Frontend** | Streamlit on Zerve | Fastest to deploy, Python-only |
| **Map** | Pydeck or Folium (via Streamlit) | Interactive map with layers |
| **Data** | EPA + NOAA + PurpleAir (optional) + Census | Multi-source fusion |
| **Deployment** | Zerve API + Zerve App | Both required for max score |

---

## What to Tell Your Backend Dev (Copy-Paste This)

> **Hey — here's the Ghost Air project for the Zerve hackathon.**
>
> **What it is:** We detect air quality monitoring blind spots — places where air is dangerous but no EPA monitor exists nearby. We already validated the concept: 24 confirmed blind spots from summer 2023, strongest being Albany NY (AQI 166) vs Burlington VT (AQI 11), 130 miles apart with zero monitoring between them.
>
> **What's done:** Prototype scripts + all data + findings. See the files below.
>
> **What you need to build:**
> 1. Port the analysis pipeline to Zerve
> 2. Add NOAA wind data for the top 3 blind spots
> 3. Add Census population data for blind spot zones
> 4. Build a REST API with 3 endpoints (risk check, blind spots list, stations)
> 5. Build a Streamlit frontend with a map + zip code lookup + case study view
> 6. Deploy both on Zerve
>
> **Files to read first:**
> - `ghost_air_output/IMPLEMENTATION_PLAN.md` — full plan
> - `ghost_air_output/DEV_HANDOFF.md` — technical details
> - `ghost_air_output/FINDINGS_SUMMARY.md` — what we found
>
> **Code to reuse:**
> - `ghost_air_prototype.py` — data pipeline
> - `find_blind_spots.py` — blind spot detection
>
> **Data (already downloaded):**
> - `ghost_air_output/` folder — all CSVs + raw EPA zip
>
> **API keys needed:**
> - PurpleAir: https://develop.purpleair.com/ (free, ~24h approval) — sign up NOW
> - Census: https://api.census.gov/data/key_signup.html (free, instant)
> - EPA + NOAA: no key needed (public data)
>
> **Timeline: 3 days.**
> - Day 1: Data enrichment (NOAA wind + PurpleAir + Census) + port to Zerve
> - Day 2: API + Streamlit app
> - Day 3: Demo video + summary + submit
>
> **The most important thing:** The finding is already validated. Don't rebuild the analysis — build the product around it.

---

## API Keys — Sign Up Immediately

| Service | URL | Cost | Wait Time |
|---------|-----|------|-----------|
| **PurpleAir** (do this FIRST) | https://develop.purpleair.com/ | Free | ~24 hours |
| **Census Bureau** | https://api.census.gov/data/key_signup.html | Free | Instant |
| **Zerve** | https://www.zerve.ai/ | Free tier | Instant |
| EPA / NOAA | No signup needed | Free | N/A |
