#!/usr/bin/env python3
"""The trail study again, judged against MEASURED wind instead of ERA5.

study_trail.py used ERA5 (a 30 km reconstruction) as "what happened"; even the
same-day forecast only matched it 30% of the time, so ERA5 was the weak link.
Here "what happened" = the nearest real weather station (NOAA Integrated
Surface Database, hourly METAR/SYNOP: wind direction, mean speed, reported
gust). Coverage Oct 2024 -> 24 Aug 2025 (the archive stops there).

Forecasts come from study/trail_raw.json (written by study_trail.py).
Control first: if the forecast made ON the day does not match the station, the
station is not a fair judge for that beach and its rows are left out.
"""
import collections, csv, datetime, io, json, os, time, urllib.request
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(ROOT, "config.json")))
TH = CFG["thresholds"]
LON = ZoneInfo("Europe/London")
MS = 2.236936
# nearest station with hourly wind through Aug 2025, distance from the beach pin
STATION = {"Sheerness": ("03693099999", "Shoeburyness, 13 km"), "Leysdown": ("03693099999", "Shoeburyness, 20 km"),
           "Whitstable": ("03797035047", "Manston, 25 km"), "Deal": ("03796099999", "Langdon Bay, 8 km, 117 m up"),
           "Cooden": ("03882099999", "Herstmonceux, 11 km inland"), "Seaford": ("03876099999", "Shoreham, 29 km"),
           "Portland": ("03857099999", "Isle of Portland, 1 km, 52 m up"), "Salthouse": ("03488099999", "Weybourne, 2 km")}


def angd(a, b):
    return abs((a - b + 180) % 360 - 180)


def good(w, g, d, face):
    return (w is not None and d is not None and TH["mean_min"] <= w <= TH["mean_max"]
            and (g if g is not None else w) <= TH["gust_max"] and angd((d + 180) % 360, face) <= TH["offshore_arc"])


def station_hours(sid):
    """{local datetime hour: (mph, gust mph or None, dir)}; the observation nearest each whole hour."""
    cache = os.path.join(ROOT, "study", "st_%s.json" % sid)
    if os.path.exists(cache):
        return {k: tuple(v) for k, v in json.load(open(cache)).items()}
    best = {}
    for y in (2024, 2025):
        url = "https://noaa-global-hourly-pds.s3.amazonaws.com/%d/%s.csv" % (y, sid)
        raw = urllib.request.urlopen(url, timeout=180).read().decode("utf-8", "replace")
        for r in csv.DictReader(io.StringIO(raw)):
            w = (r.get("WND") or "").split(",")
            if len(w) < 5 or w[0] == "999" or w[3] == "9999" or w[1] not in "0145" or w[4] not in "0145":
                continue
            t = datetime.datetime.fromisoformat(r["DATE"]).replace(tzinfo=datetime.timezone.utc)
            hr = (t + datetime.timedelta(minutes=30)).replace(minute=0, second=0)
            off = abs((t - hr).total_seconds())
            g = None
            oc = (r.get("OC1") or "").split(",")
            if len(oc) >= 2 and oc[0] not in ("", "9999"):
                g = int(oc[0]) / 10 * MS
            k = hr.astimezone(LON).strftime("%Y-%m-%dT%H")
            if k not in best or off < best[k][0]:
                best[k] = (off, int(w[3]) / 10 * MS, g, int(w[0]) if w[2] != "C" else None)
        time.sleep(1)
    out = {k: (v[1], v[2], v[3]) for k, v in best.items()}
    json.dump(out, open(cache, "w"))
    return out


def day_good(obs, face):
    tot, have = collections.Counter(), collections.Counter()
    for k, (w, g, d) in obs.items():
        h = int(k[11:13])
        if TH["hour_start"] <= h <= TH["hour_end"]:
            have[k[:10]] += 1
            tot[k[:10]] += good(w, g, d, face)
    return {d: tot[d] for d in have if have[d] >= 11}        # allow 2 missing reports


def pct(a, b):
    return "%3d%% (%d/%d)" % (round(100 * a / b), a, b) if b else "   - (0)"


def main():
    raw = json.load(open(os.path.join(ROOT, "study", "trail_raw.json")))
    full = TH["full_day_hours"]
    face = {s["name"]: s["face_deg"] for s in CFG["sites"]}
    rows = []
    for b, (sid, where) in STATION.items():
        print("station for", b, "=", where, flush=True)
        act = day_good(station_hours(sid), face[b])
        for d, h in act.items():
            row = {"b": b, "d": d, "act": h >= full, "act_h": h}
            for k, v in raw[b]["fc"].items():
                if d in v:
                    row[k] = v[d] >= full
                    row[k + "h"] = v[d]
            rows.append(row)
    json.dump(rows, open(os.path.join(ROOT, "study", "station_rows.json"), "w"))

    print("\nCONTROL: the forecast made on the day vs the station (does the judge see what the apps see?)")
    for b in STATION:
        s = [r for r in rows if r["b"] == b and "XC0" in r]
        fc = [r for r in s if r["XC0"]]
        ac = [r for r in s if r["act"]]
        print("  %-11s days %3d | XC said full day %3d, station agreed %s | station full days %3d, XC had said so %s"
              % (b, len(s), len(fc), pct(sum(r["act"] for r in fc), len(fc)), len(ac), pct(sum(r["XC0"] for r in ac), len(ac))))
    LEADS = [5, 4, 3, 2, 1, 0]
    print("\nWhen the forecast said FULL DAY this many days ahead, how often the station measured one")
    for lab in ("XC", "Met", "both"):
        parts = []
        for L in LEADS:
            sel = [r for r in rows if (r.get("XC%d" % L) and r.get("Met%d" % L)) if lab == "both"] if lab == "both" else [r for r in rows if r.get("%s%d" % (lab, L))]
            parts.append("%dd %s" % (L, pct(sum(r["act"] for r in sel), len(sel))))
        print("  %-5s" % lab + "  ".join(parts))
    print("\nXC's good hours two days ahead vs what the station measured")
    for lo, hi in [(0, 0), (1, 4), (5, 8), (9, 10), (11, 13)]:
        s = [r for r in rows if "XC2h" in r and lo <= r["XC2h"] <= hi]
        print("  %2d-%-2d good hours: full day measured %s   avg measured good hours %.1f"
              % (lo, hi, pct(sum(r["act"] for r in s), len(s)), sum(r["act_h"] for r in s) / len(s) if s else 0))
    print("\nThe trail (XC): full day 2 days ahead, by what the 3- and 4-day runs had said")
    g = collections.defaultdict(list)
    for r in rows:
        if r.get("XC2") and "XC3" in r and "XC4" in r:
            k = "held from 4 days out" if (r["XC3"] and r["XC4"]) else "appeared at 2 days out" if not (r["XC3"] or r["XC4"]) else "on and off"
            g[k].append(r)
    for k, s in g.items():
        print("  %-24s full day measured %s" % (k, pct(sum(r["act"] for r in s), len(s))))
    s = [r for r in rows if r.get("XC2") and "XC1" in r]
    for keep in (True, False):
        s2 = [r for r in s if r["XC1"] == keep]
        print("  2 days out, then %-12s 1 day out: full day measured %s" % ("still GO" if keep else "dropped", pct(sum(r["act"] for r in s2), len(s2))))


if __name__ == "__main__":
    main()
