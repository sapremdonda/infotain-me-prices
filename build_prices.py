"""Builds prices.json, the daily fuel price file Infotain Me reads.

Format (version 1):
  { "version": 1, "date": "YYYY-MM-DD",
    "places": [ { "state": "...", "city": "...", "aliases": [...],
                  "petrol": 94.49, "diesel": 90.17, "cng": 79.59 } ] }

Prices are rupees per litre (per kg for CNG); null means not sold there. If fetching or checking
fails, the script exits with an error and yesterday's file stays published.
"""
import datetime
import json
import sys
from zoneinfo import ZoneInfo

import source  # The price source: fetch() returns (date, list of place dicts in the format above).

MIN_PLACES = 4
FUELS = ("petrol", "diesel", "cng")


def clean(place):
    state = str(place.get("state", "")).strip()
    city = str(place.get("city", "")).strip()
    if not state or not city:
        return None
    out = {"state": state, "city": city}
    if place.get("aliases"):
        out["aliases"] = sorted({a.strip() for a in place["aliases"] if a and a.strip()})
    has_price = False
    for fuel in FUELS:
        value = place.get(fuel)
        try:
            value = round(float(value), 2) if value not in (None, "") else None
        except (TypeError, ValueError):
            value = None
        # Anything outside this range is a parsing mistake, not a price.
        if value is not None and not 30 <= value <= 250:
            value = None
        out[fuel] = value
        has_price = has_price or value is not None
    return out if has_price else None


def main():
    day, raw = source.fetch()
    today = datetime.datetime.now(ZoneInfo("Asia/Kolkata")).date()
    if (today - day).days > 7:
        sys.exit(f"Newest prices are from {day}; keeping yesterday's file.")
    places = [p for p in (clean(p) for p in raw) if p]
    unique = {(p["state"].lower(), p["city"].lower()): p for p in places}
    places = sorted(unique.values(), key=lambda p: (p["state"], p["city"]))
    if len(places) < MIN_PLACES:
        sys.exit(f"Only {len(places)} places with prices; keeping yesterday's file.")
    with open("prices.json", "w", encoding="utf-8") as f:
        json.dump({"version": 1, "date": day.isoformat(), "places": places}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"Wrote {len(places)} places for {day}.")


if __name__ == "__main__":
    main()
