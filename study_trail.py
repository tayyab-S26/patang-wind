#!/usr/bin/env python3
"""How far ahead can we trust a GO?  (Tayyab's method, run backwards.)

His observation: watch the call for one day as the runs come in (Wednesday 6pm,
midnight, Thursday 6am...) and the way it moves tells you whether it will hold.
We can replay that for the last two years instead of waiting for it to happen:

  the forecast as it stood 5, 4, 3, 2, 1 days before each day (Open-Meteo's
  archive of earlier runs: GFS = XCWeather's model, UKMO = the Met Office model)
                         versus
  what the wind actually did (ERA5 reanalysis, the standard record of past
  weather on a ~30 km grid).

Same rule as the board: a full day = 9+ good hours between 8am and 8pm, good =
11-18 mph mean, gust <= 26, blowing offshore for that beach.

Output: study/trail_study.json and a printed summary.
"""
import collections, datetime, json, math, os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(ROOT, "config.json")))
TH = CFG["thresholds"]
START, END = sys.argv[1] if len(sys.argv) > 1 else "2024-10-01", sys.argv[2] if len(sys.argv) > 2 else "2026-10-08"
LEADS = [0, 1, 2, 3, 4, 5]
MODELS = {"gfs_seamless": "XC", "ukmo_seamless": "Met"}
UA = {"User-Agent": "patang-wind-planner/1.0 (hobby study)"}


def get(url, tries=6):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(30 * (i + 1)); continue
            raise
        except Exception:
            time.sleep(5 * (i + 1))
    raise RuntimeError("gave up: " + url[:120])


def angd(a, b):
    return abs((a - b + 180) % 360 - 180)


def good(w, g, d, face):
    return (w is not None and g is not None and d is not None and TH["mean_min"] <= w <= TH["mean_max"]
            and g <= TH["gust_max"] and angd((d + 180) % 360, face) <= TH["offshore_arc"])


def day_hours(times, ws, gs, ds, face):
    """{date: good hours} counting only days with all 13 flying hours present."""
    tot, have = collections.Counter(), collections.Counter()
    for i, t in enumerate(times):
        h = int(t[11:13])
        if not (TH["hour_start"] <= h <= TH["hour_end"]):
            continue
        if ws[i] is None or gs[i] is None or ds[i] is None:
            continue
        have[t[:10]] += 1
        tot[t[:10]] += good(ws[i], gs[i], ds[i], face)
    return {d: tot[d] for d in have if have[d] >= 13}


def pull(site):
    face = site["face_deg"]
    out = {"truth": {}, "fc": {}}
    a = get("https://archive-api.open-meteo.com/v1/archive?latitude=%s&longitude=%s&hourly=wind_speed_10m,wind_gusts_10m,"
            "wind_direction_10m&wind_speed_unit=mph&timezone=Europe/London&start_date=%s&end_date=%s&models=era5"
            % (site["lat"], site["lon"], START, END))["hourly"]
    out["truth"] = day_hours(a["time"], a["wind_speed_10m"], a["wind_gusts_10m"], a["wind_direction_10m"], face)
    for m, lab in MODELS.items():
        vs = []
        for L in LEADS:
            sfx = "" if L == 0 else "_previous_day%d" % L
            vs += ["wind_speed_10m" + sfx, "wind_gusts_10m" + sfx, "wind_direction_10m" + sfx]
        time.sleep(4)
        h = get("https://previous-runs-api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s&hourly=%s&wind_speed_unit=mph"
                "&timezone=Europe/London&start_date=%s&end_date=%s&models=%s"
                % (site["lat"], site["lon"], ",".join(vs), START, END, m))["hourly"]
        for L in LEADS:
            sfx = "" if L == 0 else "_previous_day%d" % L
            out["fc"]["%s%d" % (lab, L)] = day_hours(h["time"], h["wind_speed_10m" + sfx], h["wind_gusts_10m" + sfx],
                                                     h["wind_direction_10m" + sfx], face)
    return out


def main():
    os.makedirs(os.path.join(ROOT, "study"), exist_ok=True)
    cache = os.path.join(ROOT, "study", "trail_raw.json")
    raw = json.load(open(cache)) if os.path.exists(cache) else {}
    for s in CFG["sites"]:
        if s["name"] in raw:
            continue
        print("pulling", s["name"], flush=True)
        raw[s["name"]] = pull(s)
        json.dump(raw, open(cache, "w"))
        time.sleep(6)
    full = TH["full_day_hours"]
    rows = []                      # one per beach-day with truth and every lead's call
    for b, r in raw.items():
        for d, th in r["truth"].items():
            row = {"b": b, "d": d, "act": th >= full, "act_h": th}
            for k, v in r["fc"].items():
                if d in v:
                    row[k] = v[d] >= full
                    row[k + "h"] = v[d]
            rows.append(row)
    json.dump(rows, open(os.path.join(ROOT, "study", "trail_rows.json"), "w"))
    report(rows)


def pct(a, b):
    return "%3d%% (%d/%d)" % (round(100 * a / b), a, b) if b else "   - (0)"


def report(rows):
    print("\nbeach-days with actual + forecasts:", len(rows))
    # 1. how often does a full day actually happen, by beach and month
    print("\n1) Actual full days (ERA5), share of days")
    by = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        k = (r["b"], int(r["d"][5:7]))
        by[k][0] += r["act"]; by[k][1] += 1
    months = [10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    print("%-15s" % "" + "".join("%5s" % datetime.date(2000, m, 1).strftime("%b") for m in months))
    for b in CFG["sites"]:
        n = b["name"]
        print("%-15s" % n + "".join("%4d%%" % round(100 * by[(n, m)][0] / by[(n, m)][1]) if by[(n, m)][1] else "    -" for m in months))
    # 2. a GO at each lead: how often did it happen
    print("\n2) When the forecast said FULL DAY this many days ahead, how often it actually was")
    for lab in ("XC", "Met", "both"):
        line = []
        for L in LEADS[::-1]:
            if lab == "both":
                sel = [r for r in rows if r.get("XC%d" % L) and r.get("Met%d" % L)]
            else:
                sel = [r for r in rows if r.get("%s%d" % (lab, L))]
            line.append("%dd %s" % (L, pct(sum(r["act"] for r in sel), len(sel))))
        print("%-5s " % lab + "  ".join(line))
    # 3. his method: the trail. Both apps say GO two days out; what did the earlier runs say?
    print("\n3) Both apps GO two days ahead, split by how the call got there (the trail)")
    def both(r, L):
        return bool(r.get("XC%d" % L)) and bool(r.get("Met%d" % L))
    groups = collections.defaultdict(list)
    for r in rows:
        if not both(r, 2) or "XC4" not in r or "Met4" not in r:
            continue
        held = both(r, 3) and both(r, 4)
        new = not both(r, 3) and not both(r, 4)
        groups["held 4,3,2 days out" if held else "new at 2 days out" if new else "wobbled (on at 4 or 3, not both)"].append(r)
    for g, sel in groups.items():
        print("  %-36s actual full day %s" % (g, pct(sum(r["act"] for r in sel), len(sel))))
    print("\n4) Both apps GO two days ahead: did it survive to 1 day and the day itself (the apps' own call)?")
    sel = [r for r in rows if both(r, 2) and "XC1" in r and "XC0" in r]
    print("  still GO 1 day out: %s   still GO on the day: %s   actual: %s"
          % (pct(sum(both(r, 1) for r in sel), len(sel)), pct(sum(both(r, 0) for r in sel), len(sel)),
             pct(sum(r["act"] for r in sel), len(sel))))
    for keep in (True, False):
        s2 = [r for r in sel if both(r, 1) == keep]
        print("    %-26s actual full day %s" % ("held at 1 day out:" if keep else "dropped at 1 day out:", pct(sum(r["act"] for r in s2), len(s2))))
    # 5. near-misses: good hours forecast 2 days ahead vs actual
    print("\n5) Forecast good hours two days ahead (lower of the two apps) vs actual full day")
    bands = [(0, 0), (1, 4), (5, 8), (9, 10), (11, 13)]
    for lo, hi in bands:
        s2 = [r for r in rows if "XC2h" in r and "Met2h" in r and lo <= min(r["XC2h"], r["Met2h"]) <= hi]
        print("  %2d-%-2d good hours: actual full day %s" % (lo, hi, pct(sum(r["act"] for r in s2), len(s2))))


if __name__ == "__main__":
    main()
