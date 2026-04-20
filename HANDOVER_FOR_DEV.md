# Ghost Air — Single Source of Truth for Dev

> **You have 2–3 days to build this. Everything you need is in this document and this folder.**

---

## The Project in 30 Seconds

Ghost Air detects **air quality monitoring blind spots** — places where EPA stations are too far apart to give accurate readings. Using EPA's own data from summer 2023, we found **24 locations** where one station said "Unhealthy" (AQI ≥150) while another station 30–150 miles away said "Good" (AQI ≤50) — with **zero monitoring in between**.

**Headline finding:** On June 8, 2023, Albany NY recorded AQI 166 (Unhealthy). Burlington VT, 130 miles north, recorded AQI 11 (Good). The entire Adirondack region between them had no air quality monitoring. Nobody got a warning.

**Your job:** Turn this validated analysis into a **deployed API + Streamlit app on Zerve.**

---

## Hackathon Context

| | |
|---|---|
| **Competition** | Zerve AI Hackathon — $10,000 in prizes |
| **Deadline** | April 29, 2026 @ 2:00 PM EDT |
| **Platform** | Everything runs on Zerve (no AWS, Vercel, or external hosting) |
| **Deliverables** | Public Zerve project (runs without errors) + 3-min demo video + 300-word summary + social post |
| **Bonus** | Deployed API + app get **priority consideration** from judges |

### Judging Weights

| Criteria | Weight | What We Have |
|----------|--------|-------------|
| Analytical Depth | 35% | 24 blind spots from 14,483 station pairs — strong |
| End-to-End Workflow | 30% | Need full pipeline on Zerve: data → analysis → API + app |
| Storytelling & Clarity | 20% | Albany case study — judge gets it in 10 seconds |
| Creativity & Ambition | 15% | Not another dashboard — we find where monitoring *fails* |

---

## What's in This Folder

### Data Files (upload to Zerve)

| File | Size | What It Is |
|------|------|-----------|
| `epa_daily_aqi.csv` | 18 MB | 215,732 daily PM2.5/AQI records from 991 EPA stations, summer 2023. **Core dataset.** |
| `epa_monitors.csv` | 56 KB | 991 EPA station locations with lat/lon. **Needed for the map.** |
| `station_mismatches.csv` | 3 KB | The 24 confirmed blind spots. **Powers the app.** |
| `epa_coverage_gaps.csv` | 73 KB | Stations ranked by isolation. Nice to have, not critical for v1. |

### Python Files (reusable code)

| File | What It Does |
|------|-------------|
| `ghost_air_prototype.py` | Full pipeline: EPA data download, PM2.5→AQI conversion, station mapping, coverage gap analysis. **Reuse these functions directly.** |
| `find_blind_spots.py` | Station-pair mismatch detection — the core analysis that found the 24 blind spots. |

**Key functions in `ghost_air_prototype.py`:**
- `pm25_to_aqi()` — PM2.5 to AQI conversion (EPA breakpoints)
- `apply_epa_correction()` — PurpleAir correction factor
- `aqi_category()` — AQI label lookup
- `find_blind_spots()` — Main blind spot detection
- `analyze_coverage_gaps()` — Station isolation ranking

### Reference Documents

| File | What It Is | When to Read |
|------|-----------|-------------|
| `FINDINGS_SUMMARY.md` | The validated findings: 24 blind spots, top 3 examples, June 7–8 wildfire event details. | **Read this** — understand the story to build the right UI |
| `FRONTEND_SPEC.md` | UI design reference: section-by-section layout, interactions, color codes. Build with **Streamlit** (ignore any React mentions). | Reference while building the app |
| `BACKEND_FRONTEND_HANDOFF.md` | API↔UI contract: why frontend matters, screen wireframes, what the API returns. | Reference alongside FRONTEND_SPEC |
| `ALBANY_DEMO_SCRIPT.md` | 3-minute demo video script with timestamps. | Read last — only for recording the demo |

### Files to Ignore

| File | Why |
|------|-----|
| `ghost_air_report.md` | Outdated 1 KB summary. Everything useful is in FINDINGS_SUMMARY.md. |
| `daily_88101_2023.zip` | Raw EPA download. Already processed into the CSVs. |
| `DEV_ONBOARDING.md` | Earlier draft. This document supersedes it. |

---

## What You're Building

### 1. Analysis Notebook (Zerve)
Port the prototype logic into a clean Zerve notebook:
- Load the 3 CSV files
- Show station count, date range, AQI distribution
- Reproduce blind spot detection methodology (logic is in `find_blind_spots.py`)
- Highlight Albany→Burlington case study with visualizations
- **Must run without errors end-to-end** — submission requirement

### 2. API Endpoint

**Endpoint:** `GET /ghostair/risk?lat=43.5&lon=-73.5` (or `?zip=12842`)

```json
{
  "location": "Adirondack Region, NY",
  "nearest_station": "Albany, NY",
  "nearest_station_distance_miles": 65,
  "official_aqi": 42,
  "predicted_aqi": 138,
  "blind_spot": true,
  "risk_level": "HIGH",
  "recommendation": "Limit outdoor activity. Sensitive groups should remain indoors.",
  "explanation": "This location is 65 miles from the nearest EPA monitor..."
}
```

**Logic:**
1. Find nearest EPA station to input coordinates
2. If distance > 30 miles → flag as potential blind spot
3. Check `station_mismatches.csv` for historical mismatches with neighbors
4. Return risk assessment

Deploy as a Zerve API endpoint.

### 3. Streamlit App

- **Map:** US map with green dots (EPA stations) and red zones (blind spots) — use `pydeck` or `folium`
- **ZIP code input** + "Check Risk" button
- **"Try Albany Case Study" button** — pre-fills the Albany example (**required for demo**)
- **Results card:** Official AQI vs predicted AQI, blind spot status, risk level, recommendation
- **AQI comparison:** Side-by-side — green badge (official: 11) vs red badge (local risk: 166). **This is the "aha moment."**

Deploy on Zerve.

---

## 3-Day Schedule

| Day | What | Hours |
|-----|------|-------|
| **Day 1** | Read this doc + FINDINGS_SUMMARY.md (1h). Set up Zerve, upload CSVs (30min). Build analysis notebook (2–3h). Start API (2h). | ~6h |
| **Day 2** | Finish API (1h). Build Streamlit app — map, ZIP input, results card, Albany button (4–5h). Test end-to-end (1h). | ~6h |
| **Day 3** | Polish. Optional: add NOAA wind or Census data. Record demo video (`ALBANY_DEMO_SCRIPT.md`). Write 300-word summary. Submit. | ~4h |

---

## Technical Guardrails

- **Zerve Native Only:** No external hosting. Deploy both API and Streamlit app through Zerve.
- **Hardcode Case Studies:** Hardcode Albany, Berkshire, and New Haven as fail-safes in the frontend for a perfect demo every time.
- **Variable Binding:** Use Zerve's `variable()` function to pull data from notebooks into the app for fast load times.
- **Frontend = Streamlit:** Ignore any React/Leaflet references in FRONTEND_SPEC.md. Use Streamlit + pydeck/folium.

---

## API Keys Needed

| Service | Cost | Turnaround |
|---------|------|------------|
| PurpleAir API | Free | ~24 hours (sign up NOW if using) |
| Census Bureau | Free | Instant |
| EPA / NOAA | Free | No key needed — public data |
| Zerve | Free tier | Instant |

> PurpleAir is **optional**. The EPA-only analysis is already strong enough without it.

---

## Verification Tests

When the app is working, these should pass:

| Input | Expected Result |
|-------|----------------|
| ZIP `12842` (Indian Lake, Adirondacks) | **HIGH** risk, blind spot = YES |
| ZIP `10001` (Manhattan, NYC) | **LOW** risk, blind spot = NO |
| Click "Try Albany Case Study" | Albany AQI 166 vs Burlington AQI 11, 130 miles, full comparison |

---

## Optional Enhancements (If Time Permits)

| Enhancement | Effort | Value |
|-------------|--------|-------|
| NOAA wind data overlay | 2h | Shows smoke direction — adds credibility |
| Census population in blind spots | 30min | "125,000 people had no warning" — adds impact |
| PurpleAir validation | 2h+ | Independent sensor confirmation |
| 48-hour forecast | 2–3h | Transforms retrospective analysis into proactive tool |

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| PurpleAir API key delayed | EPA-only analysis is already compelling. Proceed without it. |
| No PurpleAir sensors in blind spots | Frame as "neither EPA NOR independent monitoring" — even more dramatic. |
| NOAA wind data hard to parse | Just state wind direction from weather report for June 7–8. |
| Zerve deployment issues | Build locally first, deploy to Zerve last. |
| Demo runs over 3 minutes | Script is timed in ALBANY_DEMO_SCRIPT.md. Practice twice. |

---

## 300-Word Summary Template

> **What question did we ask?**
> Are there locations in the US where air quality poses a health risk that official EPA monitoring does not capture — due to gaps in station coverage?
>
> **What did we find?**
> Using EPA PM2.5 data from summer 2023, we analyzed 14,483 station pairs across 991 monitors and identified 24 instances where one station recorded "Unhealthy" air (AQI ≥150) while a neighboring station 30–150 miles away recorded "Good" air (AQI ≤50) on the same day — with no monitoring in between. The most dramatic: Albany NY recorded AQI 166 while Burlington VT, 130 miles north, recorded AQI 11 during the June 2023 Canadian wildfire smoke event. The entire Adirondack region between them had zero air quality monitoring.
>
> **Why does it matter?**
> Air quality alerts depend on monitor proximity. When the nearest station is 50+ miles away, localized pollution events go undetected. Schools, health departments, and event organizers make decisions based on official AQI — and in these cases, official readings did not reflect conditions in the gap zones.
>
> **What did we build?**
> A deployed API and interactive app on Zerve. Input a location and receive: official AQI, predicted AQI, blind spot status, risk level, and recommended actions. The full pipeline — data ingestion, cross-source analysis, spatial modeling, and deployment — was built using Zerve's autonomous agent workflow.

---

## Safe Claim Language

| ✅ Use | ❌ Avoid |
|--------|----------|
| "Monitoring coverage gaps mean localized conditions are not always captured" | "EPA missed this" / "EPA failed" |
| "Independent sensors detected elevated readings" | "The real AQI was X" |
| "Official readings did not reflect conditions in the gap zone" | "People were breathing toxic air unknowingly" |

---

## The One Thing That Matters Most

**Lead with the finding, not the technology.**

The first thing a judge sees must be:
> "Albany: AQI 166. Burlington: AQI 11. 130 miles between them. Zero monitoring."

Everything else supports that moment.
