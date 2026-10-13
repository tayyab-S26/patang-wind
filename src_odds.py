#!/usr/bin/env python3
"""Odds of a flyable day, from the weather centres' ensembles.

Permission has to be applied for two days ahead, so a single forecast is not
enough: we need to know how LIKELY the weekend is. Each centre runs its model
18-51 times from slightly different starts; the share of those runs that give a
full offshore day is the odds. Four free ensembles (Open-Meteo ensemble API, one
request per beach):
  GFS (the model behind XCWeather) 31 runs, ECMWF 51, Met Office 18, ICON 40.

odds for a beach-day = the average of the four centres' shares (each centre one
vote, so the 51-run one does not drown the 18-run one); lo / hi = the most
pessimistic and most optimistic centre, which is how far they disagree.

Same rule as the board: 9+ good hours of 8am-8pm, good = 11-18 mph, gust <= 26,
offshore for that beach. `p6` is the softer question: 6+ good hours.
"""
import datetime, json, os, re, time, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(ROOT, "config.json")))
TH = CFG["thresholds"]
MODELS = {"ncep_gefs025": "GFS", "ecmwf_ifs025_ensemble": "ECMWF", "ukmo_global_ensemble_20km": "Met Office",
          "icon_seamless_eps": "ICON"}
ASK = "gfs025,ecmwf_ifs025,ukmo_global_ensemble_20km,icon_seamless"
KEY = re.compile(r"^(wind_speed_10m|wind_gusts_10m|wind_direction_10m)(?:_member(\d+))?_(.+)$")
OUT = os.path.join(ROOT, "docs", "odds.json")


def _get(url, tries=5):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "patang-wind-planner/1.0"}), timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500:
                raise
            time.sleep(20 * (i + 1))
        except Exception:
            time.sleep(5 * (i + 1))
    raise RuntimeError("ensemble service did not answer")


def angd(a, b):
    return abs((a - b + 180) % 360 - 180)


def beach(site, dates):
    """{date: {'p','p6','lo','hi','by':{centre: pct},'n': members}} for one beach."""
    H = _get("https://ensemble-api.open-meteo.com/v1/ensemble?latitude=%s&longitude=%s&hourly=wind_speed_10m,"
             "wind_gusts_10m,wind_direction_10m&wind_speed_unit=mph&timezone=Europe/London&forecast_days=9&models=%s"
             % (site["lat"], site["lon"], ASK))["hourly"]
    times = H["time"]
    mem = {}                                   # (model, member) -> {var: series}
    for k, v in H.items():
        m = KEY.match(k)
        if m and m.group(3) in MODELS:
            mem.setdefault((m.group(3), m.group(2) or "00"), {})[m.group(1)] = v
    out = {}
    for d in dates:
        idx = [i for i, t in enumerate(times) if t[:10] == d and TH["hour_start"] <= int(t[11:13]) <= TH["hour_end"]]
        by, by6, n = {}, {}, 0
        for model in MODELS:
            full = six = cnt = 0
            for (mo, _), s in mem.items():
                if mo != model:
                    continue
                ws, wg, wd = s.get("wind_speed_10m"), s.get("wind_gusts_10m"), s.get("wind_direction_10m")
                if not ws or not wd:
                    continue
                good = have = 0
                for i in idx:
                    w, dr = ws[i], wd[i]
                    g = wg[i] if wg else None
                    if w is None or dr is None:
                        continue
                    have += 1
                    if (TH["mean_min"] <= w <= TH["mean_max"] and (g is None or g <= TH["gust_max"])
                            and angd((dr + 180) % 360, site["face_deg"]) <= TH["offshore_arc"]):
                        good += 1
                if have >= 10:
                    cnt += 1
                    full += good >= TH["full_day_hours"]
                    six += good >= 6
            if cnt >= 5:
                by[MODELS[model]] = round(100 * full / cnt)
                by6[MODELS[model]] = round(100 * six / cnt)
                n += cnt
        if by:
            out[d] = {"p": round(sum(by.values()) / len(by)), "p6": round(sum(by6.values()) / len(by6)),
                      "lo": min(by.values()), "hi": max(by.values()), "by": by, "n": n}
    return out


def pull(sites, dates):
    """Writes docs/odds.json and returns it. On failure the last good file is kept
    (its own `asof` says how old it is) and the error is recorded beside it."""
    old = json.load(open(OUT)) if os.path.exists(OUT) else {}
    res = {"asof": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "dates": dates, "b": {}}
    try:
        for s in sites:
            res["b"][s["name"]] = beach(s, dates)
            time.sleep(4)
    except Exception as e:
        if old.get("b"):
            old["error"] = "%s: %s" % (type(e).__name__, e)
            json.dump(old, open(OUT, "w"), separators=(",", ":"))
            return old
        res["error"] = "%s: %s" % (type(e).__name__, e)
    json.dump(res, open(OUT, "w"), separators=(",", ":"))
    return res


def weekend_dates(today=None):
    """The coming Saturday and Sunday (today counts if it is one of them)."""
    today = today or datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1))).date()
    out = []
    for i in range(0, 8):
        d = today + datetime.timedelta(days=i)
        if d.weekday() in (5, 6):
            out.append(d.isoformat())
        if len(out) == 2 or (out and d.weekday() == 6):
            break
    return out


if __name__ == "__main__":
    ds = weekend_dates()
    r = pull(CFG["sites"], ds)
    print(r.get("asof"), r.get("error") or "", ds)
    for b, v in r["b"].items():
        print("  %-15s" % b + "  ".join("%s: %3d%% (%d-%d) 6h+ %d%% %s" % (d[5:], v[d]["p"], v[d]["lo"], v[d]["hi"], v[d]["p6"], v[d]["by"]) for d in ds if d in v))
