# Bora Setúbal

Everything within 100 km of Setúbal — events, concerts, exhibitions, tours, workshops and recurring markets.
Live site: https://robtheriver72.github.io/borasetubal/

## How it works
- `events.csv` and `markets.csv` are the data (mirrors of the Google Sheets "Freevent Events" and "Freevent Markets").
- `template.html` is the page; `build.py` bakes the CSVs into it and writes `index.html`.
- A daily Claude scheduled task refreshes the sheets, updates the CSVs, runs `python3 build.py`, and pushes.

Rebuild locally: `python3 build.py`
