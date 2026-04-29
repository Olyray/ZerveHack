# Ghost Air — Environmental Intelligence

> **ZerveHack 2026** | Built on [Zerve AI](https://zerve.ai) | EPA Air Quality Blind Spot Detection

---

## The Finding That Started Everything

**Albany, NY: AQI 166. Burlington, VT: AQI 11. 130 miles between them. Zero monitoring.**

On June 8, 2023, Albany recorded an Unhealthy air quality index of 166 — a level that triggers health advisories and keeps kids indoors. Burlington, Vermont, 130 miles to the north, recorded an AQI of 11 — essentially pristine air. Between them, the entire Adirondack region had not a single active EPA monitoring station. Nobody in that region received a warning.

This wasn't a fluke. After analysing 215,732 daily EPA air quality records across 991 monitoring stations for summer 2023, Ghost Air identified **24 confirmed blind spots** — station pairs where one station reported Unhealthy air (AQI ≥ 150) while a neighbour 30–150 miles away reported Good air (AQI ≤ 50) on the same day, with zero monitoring in between.

---

## Live Deployments

| Link                                                                                             | Description                                           |
| ------------------------------------------------------------------------------------------------ | ----------------------------------------------------- |
| 🗂️ [Zerve Project Workspace](https://app.zerve.ai/notebook/616aefa1-13b7-4b73-968f-601302e9aea2) | Full analysis notebook — runs end-to-end on Zerve     |
| ⚡ [Public API](https://ghostair.hub.zerve.cloud/)                                               | `GET /ghostair/risk?zip=XXXXX` — live risk endpoint   |
| 🌫️ [Interactive App](https://ghostairfrontend.hub.zerve.cloud/)                                  | Streamlit app with map, ZIP lookup, Albany case study |

---

## What Ghost Air Does

Ghost Air is a three-part system built entirely on Zerve:

### 1. Analysis Notebook

A nine-cell Zerve notebook that:

- Loads and validates 215,732 EPA daily records
- Maps all 991 monitoring stations across the US
- Identifies 24 blind spot pairs using a station-mismatch algorithm (same day, AQI gap ≥ 100, distance 30–150 miles)
- Deep-dives the Albany case study with visualisations
- Ranks the 10 most isolated stations in the US by distance to their nearest neighbour

### 2. Live API

```
GET /ghostair/risk?zip=12842      → {"risk_level": "HIGH", "blind_spot": true, ...}
GET /ghostair/risk?zip=10001      → {"risk_level": "LOW",  "blind_spot": false, ...}
GET /ghostair/risk?lat=43.5&lon=-73.5
GET /ghostair/health
```

The API resolves any US ZIP code to coordinates, finds the nearest EPA station, cross-references the confirmed blind spot database, and returns a risk assessment with explanation.

### 3. Interactive Streamlit App

- **Station coverage map** — 991 green dots (normal coverage) + oversized red dots (blind spot stations)
- **ZIP risk checker** — enter any US ZIP code, get an instant risk assessment
- **Albany case study button** — one click shows the headline finding as a side-by-side AQI comparison

---

## How to Use the App

**Check your own location:**

1. Open the [live app](https://ghostairfrontend.hub.zerve.cloud/)
2. Enter a US ZIP code in the search box and click **Check Risk**
3. See whether your area falls in a known monitoring blind spot

**Try the demo cases:**
| ZIP | Location | Expected Result |
|-----|----------|-----------------|
| `12842` | Indian Lake, NY (Adirondacks) | HIGH risk — blind spot confirmed |
| `10001` | Manhattan, NYC | LOW risk — dense monitoring network |
| Albany button | Albany, NY — June 8, 2023 | AQI 166 vs AQI 11, 130 miles apart |

---

## The Data

All data is sourced from the US EPA Air Quality System (AQS) — public domain.

| File                     | Records      | Description                                          |
| ------------------------ | ------------ | ---------------------------------------------------- |
| `epa_daily_aqi.csv`      | 215,732 rows | Daily PM2.5/AQI readings, summer 2023                |
| `epa_monitors.csv`       | 991 stations | Station locations with lat/lon                       |
| `station_mismatches.csv` | 24 pairs     | Confirmed blind spots with full coordinates          |
| `epa_coverage_gaps.csv`  | 991 rows     | Each station ranked by distance to nearest neighbour |

---

## How It Was Built

Everything was built and deployed on Zerve — no external infrastructure.

```
EPA AQS Data
    ↓
ghost_air_prototype.py     ← data download + AQI conversion
find_blind_spots.py        ← station-pair mismatch detection algorithm
    ↓
Zerve Analysis Notebook    ← 9-cell DAG: load → analyse → visualise → export
    ↓
deployment/api_handler.py  ← FastAPI, deployed as live endpoint on Zerve
deployment/streamlit_app.py← Streamlit app, deployed as interactive app on Zerve
```

The Zerve notebook exports named variables (`epa_df`, `monitors_df`, `mismatches_df`, `albany_data`, etc.) that are consumed directly by the API and Streamlit deployments via `from zerve import variable()` — no data re-loading, no pipeline duplication.

---

## Key Finding Summary

- **24 confirmed blind spots** identified across the continental US, summer 2023
- **Albany↔Burlington** is the most dramatic: AQI gap of 155 points, 130 miles, zero monitoring between them
- **991 EPA stations** cover a continent — gaps are inevitable, and they are not randomly distributed
- The most isolated station in the dataset is **over 150 miles** from its nearest monitoring neighbour

---

## Repository Structure

```
/
├── ghost_air_prototype.py       # Data pipeline and AQI conversion
├── find_blind_spots.py          # Blind spot detection algorithm
├── notebooks/
│   └── 01_blind_spot_analysis.ipynb   # 9-cell Zerve analysis notebook
├── deployment/
│   ├── api_handler.py           # FastAPI endpoint
│   └── streamlit_app.py         # Streamlit interactive app
├── data/
│   ├── epa_daily_aqi.csv
│   ├── epa_monitors.csv
│   ├── station_mismatches.csv
│   └── epa_coverage_gaps.csv
└── docs/
    ├── FINDINGS_SUMMARY.md
    ├── ALBANY_DEMO_SCRIPT.md
    ├── FRONTEND_SPEC.md
    └── BACKEND_FRONTEND_HANDOFF.md
```

---

_Data source: US EPA Air Quality System (AQS), PM2.5 daily summary, summer 2023. Built for [ZerveHack 2026](https://zervehack.devpost.com/)._
