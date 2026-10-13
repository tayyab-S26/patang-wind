#!/usr/bin/env python3
"""Rebuild everything the site serves, in one command.

Runs the engine (docs/index.html + docs/board.json) then the rich prototype
(docs/prototype.html). This is the single entry point the scheduled GitHub
Action calls every few hours, and what you run locally to refresh by hand:

    python build_all.py
"""
import subprocess, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
# The XC and Met Office columns read NOAA GRIB and Met Office NetCDF files
# (src_gfs025 / src_metoffice). The scheduled runner starts bare, so install
# their readers here: the workflow file itself can't be edited from this repo's
# token. If this fails the build still runs, and the page footer says which
# column fell back to the Open-Meteo stand-in.
if os.environ.get("GITHUB_ACTIONS"):
    subprocess.call([sys.executable, "-m", "pip", "install", "-q", "h5py", "numpy", "eccodes"])
for script in ["build.py", "_prototype_data.py", "_prototype_page.py"]:
    print("== running", script)
    subprocess.check_call([sys.executable, os.path.join(ROOT, script)])
# measured wind from the Met Office stations near each beach (kept only 48 h at source,
# so every build banks what is new). Needs MO_OBS_KEY; without it this step says so and moves on.
try:
    import json, src_obs
    print("== observations:", src_obs.collect(json.load(open(os.path.join(ROOT, "config.json")))["sites"]))
except Exception as e:
    print("== observations skipped:", e)
print("== done: docs/index.html, docs/board.json, docs/prototype.html")
