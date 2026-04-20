# Ghost Air — Air Quality Blind Spot Detector

> **Zerve AI Hackathon** | Deadline: April 29, 2026 @ 2:00 PM EDT | $10,000 in prizes

## What Is This?

Ghost Air detects **air quality monitoring blind spots** — places where EPA stations are too far apart to give accurate readings. Using EPA's own data from summer 2023, we found **24 locations** where one station said "Unhealthy" (AQI ≥150) while another station 30–150 miles away said "Good" (AQI ≤50) — with zero monitoring in between.

**Headline finding:** On June 8, 2023, Albany NY recorded AQI 166 (Unhealthy). Burlington VT, 130 miles north, recorded AQI 11 (Good). The entire Adirondack region between them had no air quality monitoring.

## Start Here

👉 **Read [`HANDOVER_FOR_DEV.md`](HANDOVER_FOR_DEV.md)** — single document with everything you need to build in 2–3 days.

## Folder Contents

### Data (upload to Zerve)
| File | Description |
|------|-------------|
| `epa_daily_aqi.csv` (18 MB) | 215,732 daily PM2.5/AQI records, summer 2023 |
| `epa_monitors.csv` | 991 EPA station locations with lat/lon |
| `station_mismatches.csv` | 24 confirmed blind spots |
| `epa_coverage_gaps.csv` | Stations ranked by isolation |

### Code (reusable)
| File | Description |
|------|-------------|
| `ghost_air_prototype.py` | Full pipeline: data download, AQI conversion, coverage gaps |
| `find_blind_spots.py` | Station-pair mismatch detection (found the 24 blind spots) |

### Docs
| File | Description |
|------|-------------|
| `HANDOVER_FOR_DEV.md` | **Start here.** Complete build guide, API spec, schedule, everything. |
| `FINDINGS_SUMMARY.md` | Validated findings — the 24 blind spots and top 3 examples |
| `FRONTEND_SPEC.md` | UI design reference (build with Streamlit, not React) |
| `BACKEND_FRONTEND_HANDOFF.md` | API↔UI contract and wireframes |
| `ALBANY_DEMO_SCRIPT.md` | 3-min demo video script |

## What to Build

1. **Analysis Notebook** — Zerve notebook reproducing the blind spot detection
2. **API** — `GET /ghostair/risk?zip=12842` → risk assessment JSON
3. **Streamlit App** — Map + ZIP lookup + Albany case study button

**Tech stack:** Streamlit + pydeck/folium. Deploy everything on Zerve (no external hosting).
