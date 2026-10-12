#!/usr/bin/env python3
"""NOAA GFS at 0.25 degrees, straight from NOAA — the forecast XCWeather displays.

XCWeather's own FAQ: "The forecast data displayed by XCWeather is from a high
quality numerical weather prediction model run by the United States government
(GFS) and is updated every six hours ... a grid of points at 1/4 degree (~27km)
intervals. XCWeather interpolates this information to give a forecast for each
location."

Open-Meteo's `gfs_seamless` is NOT this: it serves the 0.11 degree (13 km) GFS
surface fields, and its `gfs025` id returns no surface wind at all (measured
2026-10-11: 0 real hours). So the only way to hold the number an XCWeather user
sees is to read the 0.25 degree grid ourselves. NOAA's grib filter cuts each
forecast hour down to our variables and a small box, ~3 KB a file, public domain.

Returns hourly rows in Europe/London time. Hours 0-120 are hourly in the model;
beyond that it is 3-hourly and we interpolate between steps (flagged `interp`).
"""
import datetime, math, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo

UA = {"User-Agent": "patang-wind-planner/1.0 (hobby; github pages)"}
LON = ZoneInfo("Europe/London")
BOX = {"toplat": 53, "bottomlat": 50, "leftlon": -3, "rightlon": 2}   # all eight beaches
BASE = "https://nomads.ncep.noaa.gov/cgi-bin/"
MS_MPH = 2.236936


def _url(day, cyc, fh):
    hourly = fh <= 120
    script = "filter_gfs_0p25_1hr.pl" if hourly else "filter_gfs_0p25.pl"
    return (f"{BASE}{script}?dir=%2Fgfs.{day}%2F{cyc:02d}%2Fatmos"
            f"&file=gfs.t{cyc:02d}z.pgrb2.0p25.f{fh:03d}"
            "&var_UGRD=on&var_VGRD=on&var_GUST=on&var_APCP=on"
            "&lev_10_m_above_ground=on&lev_surface=on&subregion="
            + "".join(f"&{k}={v}" for k, v in BOX.items()))


def _fetch(url, tries=4):
    """Raw GRIB bytes, or None. NOAA answers a missing file with an HTML page at
    HTTP 200/404, so the test is the GRIB magic, never the status code."""
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                b = r.read()
            if b[:4] == b"GRIB":
                return b
            return None
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
        except Exception:
            pass
        time.sleep(1.5 * (i + 1))
    return None


def _decode(raw):
    """{name: (lats, lons, values)} for one forecast hour. `tp` keeps only the
    bucket that does NOT start at hour 0 (GFS also ships a since-run-start total)."""
    import eccodes as ec
    out, pos = {}, 0
    while pos < len(raw):
        g = ec.codes_new_from_message(raw[pos:])
        n = ec.codes_get(g, "totalLength")
        name = ec.codes_get(g, "shortName")
        step = str(ec.codes_get(g, "stepRange"))
        keep = name in ("10u", "10v", "gust")
        if name == "tp" and "-" in step:
            a, b = step.split("-")
            # the 0-N running total is kept only when it IS the bucket (N <= 6)
            if a != "0" or int(b) <= 6:
                keep, name = True, "tp"
                out["tp_span"] = (int(a), int(b))
        if keep:
            ni, nj = ec.codes_get(g, "Ni"), ec.codes_get(g, "Nj")
            la0 = ec.codes_get(g, "latitudeOfFirstGridPointInDegrees")
            la1 = ec.codes_get(g, "latitudeOfLastGridPointInDegrees")
            lo0 = ec.codes_get(g, "longitudeOfFirstGridPointInDegrees")
            v = ec.codes_get_values(g)
            out[name] = {"ni": ni, "nj": nj, "la0": la0, "la1": la1,
                         "lo0": lo0 if lo0 < 180 else lo0 - 360, "v": v}
        ec.codes_release(g)
        pos += n
    return out


def _bilinear(f, lat, lon):
    """Bilinear value of one field at a point on the regular 0.25 degree grid."""
    ni, nj = f["ni"], f["nj"]
    dlat = (f["la1"] - f["la0"]) / (nj - 1)
    x = (lon - f["lo0"]) / 0.25
    y = (lat - f["la0"]) / dlat
    i, j = int(math.floor(x)), int(math.floor(y))
    i, j = min(max(i, 0), ni - 2), min(max(j, 0), nj - 2)
    fx, fy = x - i, y - j
    v = f["v"]
    g = lambda jj, ii: float(v[jj * ni + ii])
    return ((1 - fx) * (1 - fy) * g(j, i) + fx * (1 - fy) * g(j, i + 1)
            + (1 - fx) * fy * g(j + 1, i) + fx * fy * g(j + 1, i + 1))


def latest_cycle(days, now=None):
    """Newest run whose LAST hour we need is already published. A run appears
    hour by hour over ~1.5 h, so picking it by its first file would hand back a
    forecast that stops short while looking complete."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    last = min(384, days * 24 + 24)
    last -= last % 3
    t = now.replace(minute=0, second=0, microsecond=0)
    t -= datetime.timedelta(hours=t.hour % 6)
    for _ in range(6):
        day, cyc = t.strftime("%Y%m%d"), t.hour
        if _fetch(_url(day, cyc, last), tries=1):
            return day, cyc, last
        t -= datetime.timedelta(hours=6)
    return None


def pull(sites, days=14, hour_start=8, hour_end=20):
    """{site_name: {date: [(hr, mph, gust_mph, dir_from, rain_mm, interp), ...]}}
    plus meta {'run': 'YYYYMMDD HHZ', 'hours': n}. Empty dict if NOAA is down."""
    pick = latest_cycle(days)
    if not pick:
        return {}, {}
    day, cyc, last = pick
    run = datetime.datetime.strptime(f"{day}{cyc:02d}", "%Y%m%d%H").replace(tzinfo=datetime.timezone.utc)
    fhs = list(range(0, 121)) + list(range(123, last + 1, 3))
    fhs = [h for h in fhs if h <= last]
    with ThreadPoolExecutor(max_workers=4) as ex:
        raws = list(ex.map(lambda h: _fetch(_url(day, cyc, h)), fhs))
    grids = {h: _decode(r) for h, r in zip(fhs, raws) if r}
    # per site: a value at every model step, then onto local clock hours
    out = {}
    for s in sites:
        steps = {}
        for h in sorted(grids):
            g = grids[h]
            if not all(k in g for k in ("10u", "10v", "gust")):
                continue
            u, v = _bilinear(g["10u"], s["lat"], s["lon"]), _bilinear(g["10v"], s["lat"], s["lon"])
            gust = _bilinear(g["gust"], s["lat"], s["lon"])
            rain = None
            if "tp" in g:
                a, b = g["tp_span"]
                tot = _bilinear(g["tp"], s["lat"], s["lon"])
                prev = grids.get(h - (1 if h <= 120 else 3), {})
                if a == h - (1 if h <= 120 else 3) or "tp" not in prev or prev.get("tp_span", (None,))[0] != a:
                    amt = tot                       # first step of the bucket
                else:
                    amt = tot - _bilinear(prev["tp"], s["lat"], s["lon"])
                rain = max(0.0, amt) / (1 if h <= 120 else 3)   # mm per hour
            steps[h] = (u, v, gust, rain)
        byday = {}
        hs = sorted(steps)
        for k, h in enumerate(hs):
            span = [(h, 0.0)]
            if k + 1 < len(hs) and hs[k + 1] - h == 3:    # includes the 120 -> 123 seam
                span += [(h, 1 / 3), (h, 2 / 3)]          # fill the two missing hours
            for base, frac in span:
                a = steps[base]
                b = steps[hs[k + 1]] if frac and k + 1 < len(hs) else a
                u = a[0] + (b[0] - a[0]) * frac
                v = a[1] + (b[1] - a[1]) * frac
                gust = a[2] + (b[2] - a[2]) * frac
                rain = b[3] if frac else a[3]
                valid = run + datetime.timedelta(hours=base + (3 * frac if frac else 0))
                loc = valid.astimezone(LON)
                if not (hour_start <= loc.hour <= hour_end):
                    continue
                spd = math.hypot(u, v) * MS_MPH
                dirf = (math.degrees(math.atan2(-u, -v))) % 360
                byday.setdefault(loc.strftime("%Y-%m-%d"), []).append(
                    (loc.hour, round(spd, 1), round(gust * MS_MPH, 1), round(dirf),
                     None if rain is None else round(rain, 2), bool(frac) or base > 120))
        out[s["name"]] = byday
    return out, {"run": f"{day} {cyc:02d}Z", "hours": len(grids), "asked": len(fhs)}


if __name__ == "__main__":
    import json
    cfg = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")))
    t0 = time.time()
    data, meta = pull(cfg["sites"])
    print("meta", meta, "in", round(time.time() - t0, 1), "s")
    for n, bd in data.items():
        ds = sorted(bd)
        print(f"  {n:15s} days {len(ds)} {ds[0]}..{ds[-1]} hours/day {sorted({len(bd[d]) for d in ds})}")
