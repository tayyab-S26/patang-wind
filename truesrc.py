#!/usr/bin/env python3
"""The numbers the apps themselves show, laid over the Open-Meteo stand-ins.

The board's two decision columns are named after the apps the group checks on
the day. Until Oct 2026 both were Open-Meteo models that only resemble them:
  XC column   gfs_seamless  = GFS on a 13 km grid; XCWeather uses the 0.25 deg grid
  Met column  ukmo_seamless = one raw UKMO model; the Met Office site shows its blend
Checked against the apps on 11-12 Oct 2026 (Sheerness): src_gfs025 matches
XCWeather to 2 decimals, src_metoffice matches the Met Office site to ~0.4 mph.

overlay() swaps those hours in under the SAME model keys, so nothing downstream
changes. An hour the true source does not hold (earlier today, before the model
run started) keeps the Open-Meteo value rather than going missing.

On when config.json has "true_sources": true, or PATANG_TRUE=1 in the environment.
"""
import json, os, time

ROOT = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(ROOT, "config.json")))
CACHE = os.path.join(ROOT, "truesrc_cache.json")       # gitignored, shared by the build steps
MAP = {"gfs_seamless": "gfs", "ukmo_seamless": "met"}
_T = None


def enabled():
    env = os.environ.get("PATANG_TRUE")
    if env is not None:
        return env == "1"
    return bool(CFG.get("true_sources"))


def load():
    """{'gfs': {beach: {date: rows}}, 'met': {...}, 'meta': {...}}; pulled once
    per build (build.py and _prototype_data.py are separate processes)."""
    global _T
    if _T is not None:
        return _T
    if os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < 1800:
        _T = json.load(open(CACHE))
        return _T
    th, sites = CFG["thresholds"], CFG["sites"]
    kw = dict(days=th["outlook_days"], hour_start=th["hour_start"], hour_end=th["hour_end"])
    out = {"meta": {}}
    for key, modname in (("gfs", "src_gfs025"), ("met", "src_metoffice")):
        try:
            data, meta = __import__(modname).pull(sites, **kw)
        except Exception as e:           # say so on the page; never pass silently
            data, meta = {}, {"error": "%s: %s" % (type(e).__name__, e)}
        out[key] = data
        out["meta"][key] = meta
    json.dump(out, open(CACHE, "w"))
    _T = out
    return out


def overlay(per, site_name):
    """per = {model: {date: [(hr, mph, gust, dir), ...]}} from build.pull()."""
    if not enabled():
        return per
    T = load()
    for model, key in MAP.items():
        true = T.get(key, {}).get(site_name)
        if not true or model not in per:
            continue
        merged = {}
        for date in set(per[model]) | set(true):
            hours = {r[0]: tuple(r[:4]) for r in per[model].get(date, [])}
            for r in true.get(date, []):
                if r[1] is not None and r[2] is not None:
                    hours[r[0]] = (r[0], r[1], r[2], r[3])
            merged[date] = [hours[h] for h in sorted(hours)]
        per[model] = merged
    return per


def stamp():
    """One line for the page footer: which run / blend the columns came from."""
    if not enabled():
        return ""
    m = load()["meta"]
    g, mo = m.get("gfs", {}), m.get("met", {})
    bits = []
    bits.append("XC column: NOAA GFS 0.25 deg, run %s" % g["run"] if g.get("run")
                else "XC column: NOAA unavailable, Open-Meteo stand-in")
    bits.append("Met column: Met Office blend %s" % mo["blend_newest"] if mo.get("blend_newest")
                else "Met column: Met Office open data unavailable, Open-Meteo stand-in")
    return " | ".join(bits)
