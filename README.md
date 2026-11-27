# Infotain Me fuel prices

One small file, [`prices.json`](prices.json), with today's retail fuel prices, updated every
morning by a scheduled GitHub Actions job. The [Infotain Me](https://github.com/sapremdonda) app
downloads the whole file, so no one learns which city you look at.

**Source:** official retail selling prices for Delhi, Mumbai, Chennai and Kolkata, from the daily
table published by PPAC (Petroleum Planning & Analysis Cell, Ministry of Petroleum and Natural Gas).
More cities can be added without an app update.

## Format (version 1)

```json
{ "version": 1, "date": "2026-11-27",
  "places": [ { "state": "Delhi", "city": "Delhi", "aliases": ["New Delhi"],
                "petrol": 102.12, "diesel": 95.2, "cng": null } ] }
```

Rupees per litre (per kg for CNG); `null` means not available. If the source can't be read or looks
wrong, the job fails and yesterday's file stays up.

Run by hand: Actions → Daily fuel prices → Run workflow.
