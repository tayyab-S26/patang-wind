#!/usr/bin/env python3
"""Measured wind near each beach: the Met Office's own stations, hour by hour.

Met Office Weather DataHub, Land Observations (free plan, 360 calls a day):
hourly wind speed, gust and direction from ~150 UK stations, last 48 hours only.
So every build fetches the stations near our beaches and APPENDS anything new to
docs/obs/YYYY-MM.jsonl; that file is the record the forecast trail gets scored
against (study: forecast vs what was measured).

Key: env MO_OBS_KEY, else ~/.patang_metoffice_obs_key. No key = skip quietly.
Direction arrives as a 16-point compass word; stored as degrees (centre of the point).
"""
import datetime, json, math, os, time, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
API = "https://data.hub.api.metoffice.gov.uk/observation-land/1/"
COMP = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
MS_MPH = 2.236936
B32 = "0123456789bcdefghjkmnpqrstuvwxyz"


def geohash_latlon(g):
    lat, lon, even = [-90.0, 90.0], [-180.0, 180.0], True
    for ch in g:
        v = B32.index(ch)
        for bit in (16, 8, 4, 2, 1):
            r = lon if even else lat
            mid = (r[0] + r[1]) / 2
            r[0 if v & bit else 1] = mid
            even = not even
    return (lat[0] + lat[1]) / 2, (lon[0] + lon[1]) / 2


def km(a, b, c, d):
    return 6371 * 2 * math.asin(math.sqrt(math.sin(math.radians(c - a) / 2) ** 2 +
                                          math.cos(math.radians(a)) * math.cos(math.radians(c)) *
                                          math.sin(math.radians(d - b) / 2) ** 2))


def _key():
    k = os.environ.get("MO_OBS_KEY")
    if k:
        return k.strip()
    p = os.path.expanduser("~/.patang_metoffice_obs_key")
    return open(p).read().strip() if os.path.exists(p) else None


def _get(path, key):
    req = urllib.request.Request(API + path, headers={"apikey": key, "accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def stations(sites, key):
    """{beach: {'geohash','area','km'}}; cached in config-like file, the nearest never moves."""
    cache = os.path.join(ROOT, "docs", "obs", "stations.json")
    have = json.load(open(cache)) if os.path.exists(cache) else {}
    for s in sites:
        if s["name"] in have:
            continue
        best = None
        for x in _get("nearest?lat=%.2f&lon=%.2f&max=5" % (s["lat"], s["lon"]), key):
            la, lo = geohash_latlon(x["geohash"])
            d = km(s["lat"], s["lon"], la, lo)
            if best is None or d < best["km"]:
                best = {"geohash": x["geohash"], "area": x.get("area"), "km": round(d, 1),
                        "lat": round(la, 4), "lon": round(lo, 4)}
        have[s["name"]] = best
        time.sleep(0.3)
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    json.dump(have, open(cache, "w"), indent=1)
    return have


def collect(sites):
    """Append new hourly observations; returns a small summary dict. Never raises."""
    key = _key()
    if not key:
        return {"skipped": "no observations key"}
    try:
        st = stations(sites, key)
        odir = os.path.join(ROOT, "docs", "obs")
        seen = set()
        for f in sorted(os.listdir(odir))[-2:] if os.path.isdir(odir) else []:
            if f.endswith(".jsonl"):
                for line in open(os.path.join(odir, f)):
                    r = json.loads(line)
                    seen.add((r["g"], r["t"]))
        added = 0
        for g in sorted({v["geohash"] for v in st.values() if v}):
            for o in _get(g, key):
                t = o.get("datetime")
                if not t or (g, t) in seen or o.get("wind_speed") is None:
                    continue
                d = o.get("wind_direction")
                row = {"g": g, "t": t, "w": round(o["wind_speed"] * MS_MPH, 1),
                       "gu": None if o.get("wind_gust") is None else round(o["wind_gust"] * MS_MPH, 1),
                       "d": COMP.index(d) * 22.5 if d in COMP else None}
                with open(os.path.join(odir, t[:7] + ".jsonl"), "a") as f:
                    f.write(json.dumps(row, separators=(",", ":")) + "\n")
                seen.add((g, t)); added += 1
            time.sleep(0.3)
        return {"added": added, "stations": len({v["geohash"] for v in st.values() if v})}
    except Exception as e:
        return {"error": "%s: %s" % (type(e).__name__, e)}


if __name__ == "__main__":
    cfg = json.load(open(os.path.join(ROOT, "config.json")))
    print(collect(cfg["sites"]))
    for b, v in json.load(open(os.path.join(ROOT, "docs", "obs", "stations.json"))).items():
        print("  %-15s %s %-28s %5.1f km  (%s, %s)" % (b, v["geohash"], v["area"], v["km"], v["lat"], v["lon"]))
