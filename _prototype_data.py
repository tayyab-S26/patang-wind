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
    out = {"g": gen.strftime("%a %-d %b, %H:%M"), "src": B.truesrc.stamp(), "th": B.TH, "sites": [], "best": None, "outlook": []}
    allbest = []
    for s in B.SITES:
        face = B.face_for(s)
        per = B.truesrc.overlay(B.pull(s["lat"], s["lon"]), s["name"])
        rainper = B.rain_pull(s["lat"], s["lon"])
        detmap = det_pull(s["lat"], s["lon"])
        metmap = {}
        if B.truesrc.enabled():
            # the hour-by-hour table shows XCWeather's own numbers (NOAA GFS 0.25),
            # 5am-9pm; an hour NOAA's run does not hold keeps the old row
            xc = B.truesrc.load().get("gfs", {}).get(s["name"], {})
            for dt, xrows in xc.items():
                old = {r[0]: r for r in detmap.get(dt, [])}
                new = {}
                for r in xrows:
                    ex = r[6] if len(r) > 6 and isinstance(r[6], dict) else {}
                    rain = r[4] or 0
                    cc = ex.get("cc")
                    code = 80 if rain >= 1 else 61 if rain >= 0.2 else 3 if cc is None or cc >= 85 else 2 if cc >= 25 else 0
                    new[r[0]] = [r[0], round(r[1]), round(r[2]), int(r[3]),
                                 None if ex.get("t") is None else round(ex["t"]), round(rain, 1), code]
                for h, r in old.items():
                    new.setdefault(h, r)
                detmap[dt] = [new[h] for h in sorted(new)]
            # the same table in the Met Office's own numbers (their site forecast)
            def mo_code(sym, rain):
                if sym is None or sym < 0:
                    return 61 if (rain or 0) >= 0.2 else 2
                return (0 if sym <= 1 else 2 if sym <= 3 else 45 if sym <= 6 else 3 if sym <= 8 else
                        61 if sym <= 12 else 80 if sym <= 15 else 71 if sym <= 27 else 95)
            for dt, mrows in B.truesrc.load().get("met", {}).get(s["name"], {}).items():
                metmap[dt] = [[r[0], round(r[1]), round(r[2]), None if r[3] is None else int(r[3]),
                               None if r[6].get("t") is None else round(r[6]["t"]),
                               round(r[4] or 0, 1), mo_code(r[6].get("sym"), r[4])]
                              for r in mrows if r[1] is not None and r[2] is not None]
        dates = sorted({d for m in B.DECIDE if m in per for d in per[m]})
        days = []
        for dt in dates:
            rec = B.day_record(per, dt, face, today, rainper)
            m = rec["models"]
            w = rec["wet"]
            row = {"dd": rec["dd"], "wd": rec["wd"], "ld": rec["lead"], "v": rec["verdict"],
                   "pk": rec["peak"],
                   # wet: true / false / null (null = no rain forecast this far out)
                   "wet": {"w": w["wet"], "h": w["hours"], "sp": w["span"]},
                   "xc": m.get("gfs_seamless", {"hours": 0, "go": False}),
                   "met": m.get("ukmo_seamless", {"hours": 0, "go": False}),
                   "ec": m.get("ecmwf_ifs025", {"hours": 0, "go": False})}
            if 0 <= rec["lead"] <= (B.TH["outlook_days"] - 1 if B.truesrc.enabled() else B.TH["firm_days"]):
                row["det"] = detmap.get(dt)
                if metmap.get(dt):
                    row["detm"] = metmap[dt]
            days.append(row)
        out["sites"].append({"n": s["name"], "lat": round(s["lat"], 5), "lon": round(s["lon"], 5),
                             "face": round(face) if face is not None else None,
                             "fc": B.comp(face) if face is not None else "?",
                             "off_from": B.comp((face + 180) % 360) if face is not None else "?",
                             "d": days})
        for d in days:
            allbest.append((s["name"], d))

    def hrs(d):
        return d["xc"]["hours"] + d["met"]["hours"]
    rank = {"go": 3, "wet": 2, "split": 1, "no": 0}
    # dry-and-agreed first, then agreed-but-wet, then a model split
    pick = None
    for want in ("go", "wet", "split"):
        cand = sorted([(n, d) for n, d in allbest
                       if 0 <= d["ld"] <= B.TH["firm_days"] and d["v"] == want],
                      key=lambda x: -hrs(x[1]))
        if cand:
            pick = cand[0]
            break
    if pick:
        n, d = pick
        pk = d["pk"] or {}
        out["best"] = {"s": n, "wd": d["wd"], "dd": d["dd"], "v": d["v"], "wet": d["wet"],
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
