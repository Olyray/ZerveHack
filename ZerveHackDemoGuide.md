ZerveHack
Project Name: Ghost Air: Dev Onboarding & 2-Day Build Plan
Project Title: Ghost Air — Environmental Intelligence
Deadline: April 29, 2026 @ 2:00 PM EDT
Objective: Deploy a live API + Streamlit App on Zerve.
The 12 Essential Project Files
Discard all other files. Send only these to your Zerve workspace.

1. Data (4 Files — Upload to Zerve)
   epa_daily_aqi.csv (18 MB): Core dataset; 215,732 cleaned records.
   epa_monitors.csv (56 KB): 991 station locations for mapping.
   station_mismatches.csv (3 KB): The 24 confirmed "blind spot" pairs.
   epa_coverage_gaps.csv (73 KB): Stations ranked by isolation.
2. Python Code (2 Files — Reusable Logic)
   ghost_air_prototype.py: PM2.5 to AQI conversion and mapping functions.
   find_blind_spots.py: The core logic used to detect the 24 mismatches.
3. Documentation (6 Files — Reference)
   HANDOVER_FOR_DEV.md: Read First. Single source of truth for build specs and API schema.
   FINDINGS_SUMMARY.md: Explains the story (e.g., Albany vs. Burlington) to inform the UI.
   FRONTEND_SPEC.md: UI layout reference (Build with Streamlit, ignore React notes).
   BACKEND_FRONTEND_HANDOFF.md: API↔UI contract and wireframes.
   ALBANY_DEMO_SCRIPT.md: Storyboard for the 3-minute demo video.
   README.md: Landing page for the Zerve project.

The 2-Day Implementation Roadmap
Day 1: Analysis & API
Morning: Set up Zerve project; upload CSVs; build analysis notebook to reproduce Albany case study visuals.
Afternoon: Build FastAPI endpoint GET /ghostair/risk?lat=XX&lon=YY returning JSON with blind spot status and risk level.
Day 2: App & Submission
Morning: Build Streamlit app. Features: Map with AQI dots, ZIP lookup, and "Try Albany Case Study" fail-safe button.
Afternoon: End-to-end testing, record 3-minute demo video, and submit the Public Zerve project link.

Verification Tests
Input
Expected Output
ZIP 12842 (Indian Lake)
HIGH Risk, Blind Spot = YES
ZIP 10001 (Manhattan)
LOW Risk, Blind Spot = NO
Albany Button
AQI 166 (Albany) vs. AQI 11 (Burlington)

Non-Negotiable Rules
Zerve Only: No AWS, Vercel, or external hosting.
Streamlit Only: Disregard any "React" mentions in legacy docs.
No Dead Weight: I already deleted daily_88101_2023.zip and daily_88101_2023.csv. They are raw, unprocessed files already accounted for in epa_daily_aqi.csv.
Zero-Error Project: The Zerve project must run end-to-end for the judges.
Dev Note: "Start with HANDOVER_FOR_DEV.md. It is the blueprint for everything. We have 10 days to the deadline, but we are aiming for a 2-day build cycle

Ghost Air: Environmental Intelligence — Final Project Structure
📂 Zerve Workspace Organization

/Ghost Air: Environmental Intelligence
├── 📁 data/ # Core Datasets
│ ├── epa_daily_aqi.csv # 215,732 daily records (Summer 2023)
│ ├── epa_monitors.csv # 991 EPA station locations
│ ├── station_mismatches.csv # 24 confirmed blind spot pairs
│ └── epa_coverage_gaps.csv # Station isolation rankings
│
├── 📁 docs/ # Strategic Blueprints
│ ├── FINDINGS_SUMMARY.md # Case studies & "The Story" (Albany vs. Burlington)
│ ├── FRONTEND_SPEC.md # Streamlit UI & map requirements
│ ├── BACKEND_FRONTEND_HANDOFF.md # API JSON schema & wireframes
│ └── ALBANY_DEMO_SCRIPT.md # 3-minute video storyboard
│
├── 📁 notebooks/ # Analysis & Pipelines (Empty)
│ └── 01_blind_spot_analysis.ipynb # [Dev to create] Reproducible pipeline
│
├── 📁 deployment/ # Production Apps (Empty)
│ ├── streamlit_app.py # [Dev to create] Interactive frontend
│ └── api_handler.py # [Dev to create] FastAPI endpoint
│
├── README.md # Master Onboarding Guide
├── HANDOVER_FOR_DEV.md # SINGLE SOURCE OF TRUTH (Root)
├── ghost_air_prototype.py # Reusable PM2.5/AQI functions
├── find_blind_spots.py # Reusable mismatch detection logic
└── requirements.txt # Project dependencies (Streamlit, Pandas, etc.)

Final Actions for Success
Folder Creation: Manually create the data/, docs/, notebooks/, and deployment/ folders in your Zerve project.
File Organization: \* Move the 4 CSVs into data/.
Move the 4 MD files listed above into docs/.
Keep the README.md, HANDOVER_FOR_DEV.md, and the 2 Python logic files at the root.
