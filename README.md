# Patang Wind

A planning board for flying patang (fighter kites) at UK beaches. It checks the
wind 5–14 days ahead across a list of beaches and shows the probability of a good
flying day — steady wind in band, gusts in band, blowing **offshore** (out to
sea), inside flying hours — so you can pick a site and a day before you commit.

- **Data:** free ensemble forecasts from [Open-Meteo](https://open-meteo.com)
  (GFS / GEFS + ECMWF ENS), ~82 forecast runs per beach. No API key, no cost.
- **Probability** = the share of those runs that produce a real flying window
  that day. It's a ranking, not a promise — gust forecasts are the weak link.
- **Offshore detection** is automatic: the build samples the coastline around
  each pin and works out which way the sea is.

## How it runs

`build.py` pulls the forecasts, scores each day, and writes a static page to
`docs/`. A GitHub Action (`.github/workflows/update.yml`) runs it ~4×/day and
commits the result. GitHub Pages serves `docs/` as the live page. Nothing to
keep running; no server.

## Setup (one time)

1. Create a new GitHub repo and push this folder to it.
2. Repo **Settings → Pages → Build and deployment → Source: Deploy from a
   branch → Branch: `main` / folder: `/docs`** → Save.
3. Repo **Settings → Actions → General → Workflow permissions → Read and write
   permissions** → Save.
4. **Actions** tab → "update board" → **Run workflow** (or wait for the next
   scheduled run). The page appears at `https://<user>.github.io/<repo>/`.

## Change the beaches or thresholds

Everything lives in `config.json`:

- Add/remove a beach: edit the `sites` list (`name`, `lat`, `lon`). Get
  `lat,lon` from Google Maps: long-press the spot → copy the coordinates.
- Tune the flying window: `mean_min/max`, `gust_min/max` (mph), `hour_start/end`,
  `offshore_arc` (degrees either side of straight-out-to-sea that still counts
  as offshore).

## Run locally

```
python build.py
open docs/index.html
```
