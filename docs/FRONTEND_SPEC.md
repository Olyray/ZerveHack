# Ghost Air — Frontend Specification

## Dev Summary

Build a one-screen demo frontend for Ghost Air. Prioritize clarity over completeness. The user should be able to enter a ZIP code or click the Albany case study and instantly see official AQI vs local validated risk, blind-spot status, a recommendation, and a simple map showing the monitoring gap.

---

## Goal

Show that a location can have materially higher air-quality risk than the nearest official reading suggests.

---

## Tech Stack

> ⚠️ **UPDATE:** We are building with **Streamlit** (not React). Use this spec for **design intent and layout guidance** — adapt the layouts to Streamlit components (`st.columns`, `pydeck`/`folium` for maps, `st.metric` for stats).

- **Framework:** Streamlit (Python-only, deploys natively on Zerve)
- **Map:** pydeck or folium (both integrate with Streamlit)
- **Styling:** Clean, minimal — civic tech feel, not startup hype
- **Deployment:** Zerve native deployment (no external hosting needed)

---

## Layout (One Screen)

### Desktop: Two-Column

| Left Column | Right Column |
|-------------|--------------|
| Hero banner | Map panel |
| Input panel | AQI comparison block |
| Results card | 48-hour forecast |
| Explanation panel | |

### Mobile: Stacked

1. Hero banner
2. Input panel
3. Results card
4. AQI comparison block
5. Map panel
6. Explanation panel
7. 48-hour forecast

---

## Section-by-Section Spec

### Section 1: Hero Banner

```
Ghost Air
Detecting air quality blind spots before official alerts
```

Subtitle (smaller):

```
Check whether a location may sit in a monitoring gap where official air-quality readings understate local risk.
```

### Section 2: Input Panel

| Element | Details |
|---------|---------|
| ZIP code input | Text field, numeric |
| City/state autofill | Optional — nice to have, not required |
| "Check Risk" button | Primary action |
| "Try Albany Case Study" button | Secondary action — **required for demo** |

**Must-have interactions:**
- Enter ZIP code → click Check Risk → results update
- Click "Try Albany Case Study" → results + map update to Albany case

### Section 3: Results Card

Display these fields only:

| Field | Example Value |
|-------|---------------|
| **Location** | Albany, NY |
| **Nearest official station** | Burlington, VT |
| **Distance to station** | 130 miles |
| **Official AQI** | 11 |
| **Validated / observed AQI** | 166 |
| **Blind Spot Status** | YES |
| **Risk Level** | HIGH |
| **Recommendation** | Limit outdoor activity. Sensitive groups should remain indoors. |

### Section 4: Visual Comparison Block (Critical — "Aha" Moment)

Side-by-side display:

```
┌──────────────────┬──────────────────┐
│ Official Reading │ Local Risk Signal│
│                  │                  │
│      11          │      166         │
│   [GREEN badge]  │   [RED badge]    │
└──────────────────┴──────────────────┘
```

- Green badge/background for official reading (lower)
- Red badge/background for validated reading (higher)
- This is the single most important visual in the entire app

### Section 5: Map Panel

**Minimum viable behavior:**
- Center on queried location
- Show official station as a marker (labeled with its AQI)
- Show affected location as a marker (labeled with validated AQI)
- Draw a line between them
- Label the distance
- Optional: wind direction arrow overlay

**For the hackathon demo:**
- One highlighted case (Albany → Burlington) is sufficient
- Clickable blind spot markers if time allows

### Section 6: Explanation Panel

Short text block. Example:

```
Official monitoring did not reflect the same level of risk in this area.
Independent analysis of station spacing, observed conditions, and weather
patterns suggests a coverage gap.
```

**Do not overclaim. Keep it factual and restrained.**

### Section 7: 48-Hour Forecast

Small card, not a chart.

```
Today:      HIGH      [red]
Tomorrow:   MODERATE  [orange]
Day After:  LOW       [green]
```

Keep this secondary. If forecast data is weak, simplify further.

---

## Data Contract (API → Frontend)

The backend returns this JSON for each lookup:

```json
{
  "location": "Albany, NY 12207",
  "nearest_station": "Burlington, VT",
  "distance_miles": 130,
  "official_aqi": 11,
  "validated_aqi": 166,
  "blind_spot": true,
  "risk_level": "HIGH",
  "recommendation": "Limit outdoor activity. Sensitive groups should remain indoors.",
  "explanation": "Monitoring coverage gap with materially different observed conditions across distance.",
  "forecast_48h": {
    "today": "HIGH",
    "tomorrow": "MODERATE",
    "day_after": "LOW"
  },
  "map": {
    "location_lat": 42.6526,
    "location_lng": -73.7562,
    "station_lat": 44.4759,
    "station_lng": -73.2121
  }
}
```

### Hardcoded Case Studies (for demo reliability)

If the API isn't ready or for guaranteed demo stability, hardcode these 3 cases in the frontend:

**Case 1 — Albany, NY (Primary demo case)**
- ZIP: 12207
- Location: Albany, NY
- Nearest station: Burlington, VT
- Distance: 130 miles
- Official AQI: 11 | Validated AQI: 166
- Blind spot: YES | Risk: HIGH
- Date: June 8, 2023

**Case 2 — Berkshire County, MA**
- ZIP: 01201
- Location: Pittsfield, MA
- Nearest station: Burlington, VT
- Distance: 140 miles
- Official AQI: 11 | Validated AQI: 163
- Blind spot: YES | Risk: HIGH
- Date: June 8, 2023

**Case 3 — New Haven, CT → Miller State Park, NH**
- ZIP: 06510
- Location: New Haven, CT
- Nearest station: Miller State Park, NH
- Distance: 120 miles
- Official AQI: 31 | Validated AQI: 172
- Blind spot: YES | Risk: HIGH
- Date: June 8, 2023

---

## Design Guidance

### Style
- Clean, analytical, public-interest feel
- Off-white or very light background
- Dark text
- AQI color coding: green / yellow / orange / red
- No neon, no gamer-style UI, no gradients

### Tone
Should feel like:
- ✅ Civic tech
- ✅ Environmental intelligence
- ✅ Decision support

Should NOT feel like:
- ❌ Startup hype
- ❌ "AI magic"
- ❌ Marketing landing page

---

## What NOT to Build

- ❌ Login / auth / user accounts
- ❌ Dashboards with many charts
- ❌ Long methodology text
- ❌ Multiple filters or advanced search
- ❌ Fancy design system
- ❌ Loading animations beyond a simple spinner

---

## If Time Is Tight

Even a static case-study page plus ZIP lookup is enough. The demo video only needs to show:

1. User clicks "Try Albany Case Study"
2. Results card appears with dramatic AQI mismatch
3. Map shows the two stations and the gap
4. Comparison block shows green 11 vs red 166

That's a winning demo moment in under 10 seconds.

---

## Estimated Build Time

| Task | Hours |
|------|-------|
| Project setup (React + Leaflet) | 1–2h |
| Input panel + results card | 2–3h |
| AQI comparison block | 1h |
| Map panel with markers + line | 2–3h |
| Hardcoded case studies | 1h |
| API integration (when backend ready) | 1–2h |
| Styling + responsive layout | 2–3h |
| Testing + polish | 1–2h |
| **Total** | **~12–16 hours (1.5–2 days)** |

---

## File to Share With Frontend Dev

Send them this file:
`C:\Users\Owner\PyCharmMiscProject\ghost_air_output\FRONTEND_SPEC.md`

Plus the backend API spec from:
`C:\Users\Owner\PyCharmMiscProject\ghost_air_output\BACKEND_FRONTEND_HANDOFF.md`
