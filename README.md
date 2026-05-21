# 🏋️ Gym Tracker

A personal workout tracking web app built with Flask and Google Sheets, accessible from any device via mobile browser.

## Overview

I built this app to solve a real problem: tracking progressive overload during workouts without relying on paper or clunky spreadsheets. The goal was a fast, mobile-first interface that stores data persistently and can be analyzed later.

**Live app:** [https://gym-tracker-160u.onrender.com](https://gym-tracker-160u.onrender.com)

---

## Features

- **Google OAuth login** — secure authentication with your Google account
- **4-day training templates** — load your weekly routine once, reuse every session
- **Per-session weight tracking** — log sets, reps, weight and comments for each exercise
- **Editable history** — fix any weight entry directly from the log view
- **Search & highlight** — filter past workouts by exercise, date or training day
- **Google Sheets as database** — all data stored in a structured spreadsheet for easy analysis
- **Responsive mobile UI** — designed for use during training, one-handed

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 + Flask |
| Auth | Google OAuth 2.0 + PKCE |
| Database | Google Sheets API via gspread |
| Frontend | Vanilla HTML + CSS + JavaScript |
| Hosting | Render (free tier) |
| Version control | Git + GitHub |

---

## Architecture

```
Browser (mobile)
      │
      ▼
Flask (Render)
      │
      ├── Google OAuth 2.0 (authentication)
      │
      └── Google Sheets API
            ├── Templates sheet (workout routines)
            └── Log sheet (training history)
```

The app runs as a server-side Flask application. There is no frontend framework — the UI is pure HTML/CSS/JS served by Jinja2 templates. All state is stored in Google Sheets, which also serves as the data source for future analysis.

---

## Data Model

### `Templates` sheet
Stores the 4 training day templates. Updated when the monthly routine changes.

| dia | seccion | ejercicio | sets | reps |
|-----|---------|-----------|------|------|
| 1 | activacion | Band pull-apart | 3 | 15 |
| 1 | A | Squat | 4 | 8 |

### `Log` sheet
One row per exercise per session. Designed for time-series analysis of progressive overload.

| session_id | fecha | semana | dia | seccion | ejercicio | sets | reps | peso | comentario |
|------------|-------|--------|-----|---------|-----------|------|------|------|------------|
| 1748000000 | 20/05/2025 | 1 | 1 | A | Squat | 4 | 8 | 80 | felt strong |

---

## Key Technical Decisions

**Why Flask over a frontend-only app?**
Credentials for Google Sheets API need to stay server-side. A pure frontend app would expose them to the client.

**Why Google Sheets as a database?**
For a single-user personal project, Sheets provides free persistence, a familiar interface for manual edits, and is directly usable for data analysis (charts, pivot tables, etc.) without any ETL pipeline.

**Why vanilla JS over React?**
Minimal dependencies, faster iteration, no build step. The UI complexity doesn't justify a framework at this scale.

**OAuth + PKCE implementation**
Google's newer OAuth policies require PKCE (Proof Key for Code Exchange) for web apps. Implemented manually using `hashlib` and `secrets` since `google-auth-oauthlib` doesn't handle it automatically in all versions.

**Credentials management in production**
`client_secret.json` is excluded from version control. In production (Render), credentials are injected as an environment variable and written to a temporary file at runtime.

---

## Local Setup

```bash
# Clone the repo
git clone https://github.com/cortemartina/gym-tracker.git
cd gym-tracker

# Install dependencies
pip install -r requirements.txt

# Add your credentials
# Place client_secret.json in the root directory

# Run
python app.py
```

Then open `http://localhost:5000` in your browser.

---

## Future Improvements

- Progress charts (weight over time per exercise)
- REST API + React frontend migration
- Multi-user support with per-user Sheet isolation
- PWA support for offline use

---

## Author

Built by Martina Corte — Biochemistry + Data Analysis background, applying analytical thinking to software projects.
