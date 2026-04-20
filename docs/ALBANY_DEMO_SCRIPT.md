# Ghost Air — Albany Case Study: Demo Script & Visual Design

---

## 🎯 Opening Hook (First 10 Seconds)

**On screen (large text, dark background):**

> **June 8, 2023**
> **Albany, NY — AQI 166 (Unhealthy)**
> **Burlington, VT — AQI 11 (Good)**
> **130 miles apart. Zero monitors in between.**

**Voice over (calm, measured — NOT dramatic):**

> "On June 8th, 2023, two EPA stations 130 miles apart reported completely different realities. Albany recorded unhealthy air. Burlington recorded clean air. Between them — the entire Adirondack region — there was no monitor at all. No one in that zone received a warning."

**Why this works:**
- Specific date, specific places, specific numbers
- No overclaiming — just stating what the data shows
- The gap speaks for itself
- Judge understands the problem in 8 seconds

---

## 🗺️ Map Visual Design (The Hero Slide)

### What the judge sees:

```
┌─────────────────────────────────────────────────┐
│                                                   │
│            ● Burlington, VT                       │
│              AQI: 11 (Good)                       │
│              [GREEN dot]                          │
│                                                   │
│         ╔═══════════════════════╗                 │
│         ║   ADIRONDACK REGION   ║                 │
│         ║                       ║                 │
│         ║   NO EPA MONITORS     ║                 │
│         ║   ~130 MILES          ║                 │
│         ║   [GRAY ZONE]         ║                 │
│         ╚═══════════════════════╝                 │
│                                                   │
│            ● Albany, NY                            │
│              AQI: 166 (Unhealthy)                 │
│              [RED dot]                            │
│                                                   │
└─────────────────────────────────────────────────┘
```

### Design specs for your dev:

1. **Base map:** Northeast US (NY, VT, NH, MA, CT) — muted/dark style (Mapbox dark or similar)
2. **Station dots:**
   - Albany = **RED circle** with pulsing animation, labeled "AQI 166"
   - Burlington = **GREEN circle**, labeled "AQI 11"
3. **The gap zone:** Semi-transparent **gray/orange overlay** covering the area between the two stations. Label: "No EPA Monitor — 130 miles"
4. **Dashed line** connecting the two stations showing the distance
5. **Optional wind arrow:** SW→NE arrow showing smoke transport direction (from NOAA data)
6. **No clutter.** No other stations visible initially. Just these two and the gap.

### Animation sequence (for demo video):

| Step | What appears | Duration |
|------|-------------|----------|
| 1 | Dark map of Northeast US | 1s |
| 2 | Albany dot appears RED + "AQI 166 — Unhealthy" | 2s |
| 3 | Burlington dot appears GREEN + "AQI 11 — Good" | 2s |
| 4 | Dashed line + distance label "130 miles" | 1s |
| 5 | Gray zone fills in between + "No EPA Monitor" | 2s |
| 6 | Wind arrow appears (SW→NE) | 1s |

**Total: ~9 seconds.** This IS your first 10 seconds.

---

## 📋 Full Demo Script (3 Minutes)

### 0:00–0:10 — THE HOOK (map animation above)

**Voice:**
> "On June 8th, 2023 — during the worst wildfire smoke event in US history — Albany, New York recorded an AQI of 166. Burlington, Vermont, 130 miles north, recorded 11. The entire Adirondack region between them had no air quality monitor. No one there received a warning."

---

### 0:10–0:30 — THE FINDING (zoom out to show more blind spots)

**On screen:** Map zooms out. 2–3 more blind spot pairs appear.

**Voice:**
> "This wasn't an isolated case. Using only official EPA data from summer 2023, we identified 24 locations where one station recorded dangerous air while a neighboring station — 30 to 150 miles away — reported safe conditions. The zones between them had zero monitoring."

**On screen:** Quick table:
| Location Pair | AQI Gap | Distance | Date |
|---|---|---|---|
| Albany → Burlington | 166 vs 11 | 130 mi | June 8 |
| Berkshire, MA → Burlington | 163 vs 11 | 140 mi | June 8 |
| New Haven → Miller Park, NH | 172 vs 31 | 120 mi | June 8 |

---

### 0:30–0:50 — THE EXPLANATION

**On screen:** Albany case study with wind overlay.

**Voice:**
> "Here's why this happens. On June 8th, Canadian wildfire smoke was moving across the Northeast. Albany sat directly in the smoke plume. Burlington was north of it. But between them — 130 miles of the Adirondack Mountains — there's no EPA station to tell you which side of the line you're on."

> "This isn't a sensor error. Both stations are official EPA monitors reporting accurately. The problem is spatial — the monitoring network simply doesn't cover the gap."

---

### 0:50–1:10 — THE REFRAMING

**On screen:** Simple graphic showing EPA station density.

**Voice:**
> "The US has roughly 1,300 PM2.5 monitors covering 3.8 million square miles. That's one monitor per 2,900 square miles. When air quality changes rapidly across distance — as it does during wildfire smoke events — these gaps become blind spots."

> "We're not saying EPA is wrong. We're saying the network wasn't designed for events like this. And people in the gaps don't get warnings."

---

### 1:10–1:40 — THE ZERVE WORKFLOW

**On screen:** Zerve interface showing the pipeline.

**Voice:**
> "We built this on Zerve. We asked the agent to pull EPA's full PM2.5 dataset for summer 2023 — 215,000 daily records across 991 stations. Then we had it calculate distances between every station pair, flag mismatches where one station reported dangerous air while a neighbor reported safe conditions, and cross-reference with NOAA weather data."

> "The entire pipeline — data ingestion, spatial analysis, mismatch detection — was built and iterated using Zerve's autonomous workflow."

---

### 1:40–2:15 — LIVE APP DEMO

**On screen:** The deployed app.

**Voice:**
> "Here's what we deployed."

**Action:** Enter a normal zip code (e.g., 10001 — Manhattan).

> "Manhattan — well-monitored. Official AQI matches nearby stations. No blind spot."

**Action:** Enter a blind spot zip code (e.g., 12842 — Indian Lake, Adirondacks).

> "Indian Lake, New York. Heart of the Adirondacks. The nearest EPA monitor is 65 miles away. On June 8th, our system flags this as a high-risk blind spot. Official AQI from the nearest station said 'Good.' But stations on either side of this location disagreed by over 150 points."

**On screen:** API response:
```json
{
  "location": "Indian Lake, NY 12842",
  "nearest_epa_station": "Albany, 65 miles south",
  "nearest_station_aqi": 166,
  "alternate_station": "Burlington, VT — 70 miles north",
  "alternate_station_aqi": 11,
  "blind_spot": true,
  "risk_level": "HIGH",
  "explanation": "Located between two stations with 155-point AQI disagreement. No local monitoring.",
  "recommendation": "Limit outdoor activity. Monitor conditions closely."
}
```

---

### 2:15–2:45 — THE "SO WHAT"

**Voice:**
> "This matters for anyone making decisions based on official AQI. A school district in the Adirondacks checking AirNow on June 8th could have seen 'Good' air quality — depending on which station they were nearest to — while the actual conditions in their area were potentially unhealthy."

> "Our system identifies these coverage gaps and flags when neighboring stations disagree significantly — giving decision-makers a more complete picture."

> "This applies to school districts, outdoor event organizers, local health departments — anyone who relies on official air quality data to make safety decisions."

---

### 2:45–3:00 — CLOSE

**On screen:** The map with all 24 blind spots highlighted.

**Voice:**
> "24 blind spots. Summer 2023. Official EPA data only. Monitoring coverage gaps mean localized air quality conditions are not always captured by the nearest station. Ghost Air finds the gaps."

**On screen (final frame):**

> **Ghost Air**
> Detecting Air Quality Blind Spots Before Official Alerts
> Built on Zerve

---

## ✅ Claim Language Reminders

| ✅ Say | ❌ Don't say |
|--------|-------------|
| "Monitoring coverage gaps" | "EPA missed this" |
| "Stations disagreed by 155 points" | "The real AQI was 166" |
| "No monitor existed in between" | "People were breathing toxic air" |
| "Conditions were not captured" | "EPA failed to warn people" |
| "Decision-makers get a more complete picture" | "Our system is more accurate than EPA" |

---

## 📐 Technical Notes for Dev

### Map implementation options (simplest first):
1. **Folium** (Python) — free, works in Jupyter/Zerve, generates interactive HTML maps
2. **Plotly Mapbox** — free tier, good for demo screenshots
3. **Deck.gl** — if building a React app, best visual quality

### For the demo video:
- Screen record the app, don't do a live demo (too risky)
- Record voice separately, overlay in editing
- Keep transitions simple — cuts, not animations
- Dark background for all slides/text

### Key data points to have ready:
- Albany station ID and exact coordinates
- Burlington station ID and exact coordinates
- Indian Lake, NY zip code (12842) — center of the blind spot
- NOAA wind data for June 8, 2023 (Albany region)
- Population of Hamilton County, NY (Adirondacks) — ~4,500 people
- Population of Essex County, NY — ~37,000 people
- Total estimated population in the blind spot zone: ~40,000–50,000
