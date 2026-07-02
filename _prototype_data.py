#!/usr/bin/env python3
"""Generate a richer dataset (with hour-by-hour curves) for the prototype UI.
Reuses the engine in build.py. Writes rich.json next to this script, which
_prototype_page.py then reads. Part of the committed build so the scheduled
GitHub Action can regenerate the prototype page too.
"""
import sys, json, math, datetime, os
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import build as B

OUT = os.path.join(ROOT, "rich.json")


def pooled_of(per):
    p = {}
    for model, members in per.items():
        for memid, byday in members.items():
            p[(model, memid)] = byday
    return p


def hourly(pooled, date, sc):
    tot = len(pooled)
    rows = []
    for h in range(B.TH["hour_start"], B.TH["hour_end"] + 1):
        inb = []
        for byday in pooled.values():
            for (hr, m, g, dd) in byday.get(date, []):
                if hr == h and B.good(m, g, dd, sc):
                    inb.append((m, g, dd))
        frac = round(100 * len(inb) / tot) if tot else 0
        if inb:
            ms = sorted(x[0] for x in inb); gs = sorted(x[1] for x in inb)
            xs = sum(math.cos(math.radians(x[2])) for x in inb)
            ys = sum(math.sin(math.radians(x[2])) for x in inb)
            rows.append([h, frac, round(ms[len(ms) // 2]), round(gs[len(gs) // 2]),
                         B.comp(math.degrees(math.atan2(ys, xs)) % 360)])
        else:
            rows.append([h, frac])
    return rows


def det_pull(lat, lon):
    """Single deterministic hourly forecast (UKMO seamless) — the XCWeather-style
    table: wind, gust, direction, temp, rain, weather-code per hour."""
    url = ("https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s"
           "&hourly=wind_speed_10m,wind_gusts_10m,wind_direction_10m,temperature_2m,precipitation,weather_code"
           "&wind_speed_unit=mph&timezone=Europe/London&forecast_days=8&models=ukmo_seamless" % (lat, lon))
    try:
        d = B.get(url)
    except Exception:
        return {}
    if isinstance(d, dict) and d.get("error"):
        return {}
    H = d.get("hourly", {})
    t = H.get("time", [])
    ws, wg = H.get("wind_speed_10m", []), H.get("wind_gusts_10m", [])
    wd, tp = H.get("wind_direction_10m", []), H.get("temperature_2m", [])
    pr, wc = H.get("precipitation", []), H.get("weather_code", [])
    m = {}
    for i, ts in enumerate(t):
        hr = int(ts[11:13])
        if not (B.TH["hour_start"] <= hr <= B.TH["hour_end"]):
            continue
        def g(a):
            return a[i] if i < len(a) and a[i] is not None else None
        m.setdefault(ts[:10], []).append([
            hr,
            round(g(ws)) if g(ws) is not None else None,
            round(g(wg)) if g(wg) is not None else None,
            int(round(g(wd))) if g(wd) is not None else None,
            round(g(tp)) if g(tp) is not None else None,
            round(g(pr), 1) if g(pr) is not None else 0,
            int(g(wc)) if g(wc) is not None else 0,
        ])
    return m


def main():
    gen = datetime.datetime.now()
    today = gen.date()
    out = {"g": gen.strftime("%a %-d %b, %H:%M"), "th": B.TH, "sites": [], "best": None, "outlook": []}
    allbest = []
    for s in B.SITES:
        sea = B.seaward(s["lat"], s["lon"])
        sm = B.sea_mean(sea)
        per = B.pull(s["lat"], s["lon"])
        detmap = det_pull(s["lat"], s["lon"])
        dates = sorted({d for m in B.DECIDE if m in per for d in per[m]})
        days = []
        for dt in dates:
            rec = B.day_record(per, dt, sea, today)
            m = rec["models"]
            row = {"dd": rec["dd"], "wd": rec["wd"], "ld": rec["lead"], "v": rec["verdict"],
                   "pk": rec["peak"],
                   "xc": m.get("gfs_seamless", {"hours": 0, "go": False}),
                   "met": m.get("ukmo_seamless", {"hours": 0, "go": False}),
                   "ec": m.get("ecmwf_ifs025", {"hours": 0, "go": False})}
            if 0 <= rec["lead"] <= B.TH["firm_days"]:
                row["det"] = detmap.get(dt)
            days.append(row)
        out["sites"].append({"n": s["name"], "lat": round(s["lat"], 5), "lon": round(s["lon"], 5),
                             "sea": round(sm) if sm is not None else None,
                             "sc": B.comp(sm) if sm is not None else "?",
                             "seaarc": [round(b) for b in sea], "d": days})
        for d in days:
            allbest.append((s["name"], d))

    def hrs(d):
        return d["xc"]["hours"] + d["met"]["hours"]
    rank = {"go": 2, "split": 1, "no": 0}
    firm = sorted([(n, d) for n, d in allbest if 0 <= d["ld"] <= B.TH["firm_days"] and d["v"] == "go"],
                  key=lambda x: -hrs(x[1]))
    pick = firm[0] if firm else None
    if not pick:
        sp = sorted([(n, d) for n, d in allbest if 0 <= d["ld"] <= B.TH["firm_days"] and d["v"] == "split"],
                    key=lambda x: -hrs(x[1]))
        pick = sp[0] if sp else None
    if pick:
        n, d = pick
        pk = d["pk"] or {}
        out["best"] = {"s": n, "wd": d["wd"], "dd": d["dd"], "v": d["v"],
                       "h": pk.get("hour"), "mph": pk.get("mph"), "gust": pk.get("gust"), "frm": pk.get("from")}
    from collections import defaultdict
    byday = defaultdict(list)
    for n, d in allbest:
        if B.TH["firm_days"] < d["ld"] <= B.TH["outlook_days"] - 1:
            byday[d["ld"]].append((n, d))
    for ld in sorted(byday):
        n, d = max(byday[ld], key=lambda x: (rank[x[1]["v"]], hrs(x[1])))
        out["outlook"].append({"wd": d["wd"], "dd": d["dd"], "s": n, "v": d["v"]})
    json.dump(out, open(OUT, "w"), separators=(",", ":"))
    print("wrote", OUT, "| sites", len(out["sites"]), "| best", out["best"])


if __name__ == "__main__":
    main()
