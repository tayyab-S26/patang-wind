#!/usr/bin/env python3
"""The Met Office's own site forecast, free, no account.

What the Met Office app shows is NOT a raw model. It is IMPROVER: a blend of
several models and ensembles, corrected for coast and hills, re-issued through
the day. Open-Meteo's `ukmo_seamless` is one raw model (UKMO global 10 km), so
it is not the number a Met Office user sees.

The blend itself is published as open data on AWS (bucket
`met-office-uk-spot-percentiles`, CC BY-SA 4.0, kept 30 days): one small NetCDF
per valid time and parameter, holding 15 percentiles for ~8,700 UK spots. We
take the newest blend for every hour we need and read the spot nearest each
beach. Hourly for ~5.5 days, then 3-hourly out to ~15 days (interpolated to the
hour, flagged `interp`).

Rows match src_gfs025: (hr, mph, gust_mph, dir_from, rain_mm, interp, extra)
where mph / gust / rain are the MEDIAN (p50) and extra carries the spread:
{'lo': p10 mph, 'hi': p90 mph, 'gust_hi': p90 gust, 'rain_hi': p90 rain mm}.
"""
import datetime, io, math, os, re, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo

BUCKET = "https://met-office-uk-spot-percentiles.s3.eu-west-2.amazonaws.com/"
UA = {"User-Agent": "patang-wind-planner/1.0 (hobby; github pages)"}
LON = ZoneInfo("Europe/London")
UTC = datetime.timezone.utc
MS_MPH = 2.236936
P_SPEED, P_DIR = "wind_speed_at_10m", "wind_direction_at_10m"
P_GUST1, P_GUST3 = "wind_gust_at_10m_max-PT01H", "wind_gust_at_10m_max-PT03H"
P_RAIN1, P_RAIN3 = "precipitation_accumulation-PT01H", "precipitation_accumulation-PT03H"
PARAMS = (P_SPEED, P_DIR, P_GUST1, P_GUST3, P_RAIN1, P_RAIN3)
KEY_RE = re.compile(r"/(\d{8}T\d{4}Z)-B(\d{8}T\d{4}Z)-([A-Za-z0-9_\-]+)\.nc$")
CACHE = os.environ.get("PATANG_MO_CACHE")       # optional folder, dev only


def _get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None


def _list(prefix):
    """Every key under a prefix (S3 pages at 1,000)."""
    keys, token = [], None
    while True:
        u = BUCKET + "?list-type=2&prefix=" + urllib.request.quote(prefix, safe="")
        if token:
            u += "&continuation-token=" + urllib.request.quote(token, safe="")
        b = _get(u)
        if b is None:
            return None
        t = b.decode()
        keys += re.findall(r"<Key>([^<]+)</Key>", t)
        m = re.search(r"<NextContinuationToken>([^<]+)</NextContinuationToken>", t)
        if not m:
            return keys
        token = m.group(1)


def newest_keys(now=None):
    """{(param, valid_utc): key} keeping the newest blend for each. Lists today
    and yesterday: the far end of the forecast is only re-issued a few times a
    day, so today's folder alone stops short in the small hours."""
    now = now or datetime.datetime.now(UTC)
    prefixes = []
    for back in (0, 1):
        d = now - datetime.timedelta(days=back)
        prefixes += [f"uk-spot-percentiles/{d:%Y/%m/%d}/T{h:02d}" for h in range(24)]
    with ThreadPoolExecutor(max_workers=12) as ex:
        lists = list(ex.map(_list, prefixes))
    if all(l is None for l in lists):
        return None
    best = {}
    for l in lists:
        for k in l or []:
            m = KEY_RE.search(k)
            if not m or m.group(3) not in PARAMS:
                continue
            valid, blend, param = m.groups()
            cur = best.get((param, valid))
            if cur is None or blend > cur[0]:
                best[(param, valid)] = (blend, k)
    return best


def _read(key, want_ids):
    """{site_id: value or [15 percentiles]} for the spots we want."""
    import h5py, numpy as np
    raw = None
    path = os.path.join(CACHE, key.rsplit("/", 1)[-1]) if CACHE else None
    if path and os.path.exists(path):
        raw = open(path, "rb").read()
    if raw is None:
        raw = _get(BUCKET + key)
        if raw is None:
            return None
        if path:
            open(path, "wb").write(raw)
    try:
        f = h5py.File(io.BytesIO(raw), "r")
    except Exception:
        return None
    ids = [b"".join(r).decode().strip() for r in f["met_office_site_id"][...]]
    pos = {s: i for i, s in enumerate(ids)}
    skip = {"latitude", "longitude", "altitude", "met_office_site_id", "wmo_id", "percentile",
            "spot_index", "blend_time", "forecast_period", "forecast_reference_time", "time",
            "height", "string8", "bnds", "forecast_period_bnds", "time_bnds"}
    var = [n for n in f if n not in skip and getattr(f[n], "ndim", 0) >= 1][0]
    d = f[var][...]
    out = {}
    for s in want_ids:
        i = pos.get(s)
        if i is None:
            continue
        out[s] = float(d[i]) if d.ndim == 1 else [float(x) for x in d[:, i]]
    if "percentile" in f:
        out["_pct"] = [float(x) for x in f["percentile"][...]]
    return out


def nearest_sites(sites, key):
    """Nearest Met Office spot to each beach: {beach: (site_id, km, altitude_m)}."""
    import h5py
    raw = _get(BUCKET + key)
    f = h5py.File(io.BytesIO(raw), "r")
    lat, lon, alt = f["latitude"][...], f["longitude"][...], f["altitude"][...]
    ids = [b"".join(r).decode().strip() for r in f["met_office_site_id"][...]]
    out = {}
    for s in sites:
        if s.get("mo_site"):
            i = ids.index(s["mo_site"])
        else:
            c = math.cos(math.radians(s["lat"]))
            i = min(range(len(ids)), key=lambda j: (lat[j] - s["lat"]) ** 2 + ((lon[j] - s["lon"]) * c) ** 2)
        km = 111.2 * math.hypot(float(lat[i]) - s["lat"],
                                (float(lon[i]) - s["lon"]) * math.cos(math.radians(s["lat"])))
        out[s["name"]] = (ids[i], round(km, 1), round(float(alt[i])))
    return out


def _pct(vals, pcts, p):
    return vals[pcts.index(float(p))]


def pull(sites, days=14, hour_start=8, hour_end=20, now=None):
    """({beach: {date: [row, ...]}}, meta). Empty dicts if the bucket is down."""
    now = now or datetime.datetime.now(UTC)
    best = newest_keys(now)
    if not best:
        return {}, {}
    t0 = now.replace(minute=0, second=0, microsecond=0)
    t1 = (now.astimezone(LON).replace(hour=0, minute=0, second=0, microsecond=0)
          + datetime.timedelta(days=days)).astimezone(UTC)
    fmt = "%Y%m%dT%H%MZ"
    # from local midnight: a full day is counted over all of 8am-8pm, hours gone included
    day0 = now.astimezone(LON).replace(hour=0, minute=0, second=0, microsecond=0).astimezone(UTC)
    speed_vt = sorted(v for (p, v) in best if p == P_SPEED
                      and day0 <= datetime.datetime.strptime(v, fmt).replace(tzinfo=UTC) <= t1)
    if not speed_vt:
        return {}, {}
    # only the valid times that can touch a flying hour (3-hourly steps reach 2 h either side)
    def useful(v):
        loc = datetime.datetime.strptime(v, fmt).replace(tzinfo=UTC).astimezone(LON)
        return hour_start - 3 <= loc.hour <= hour_end + 3
    vts = [v for v in speed_vt if useful(v)]
    jobs = []
    for v in vts:
        jobs.append((P_SPEED, v))
        if (P_DIR, v) in best:
            jobs.append((P_DIR, v))
        g = P_GUST1 if (P_GUST1, v) in best else P_GUST3
        if (g, v) in best:
            jobs.append((g, v))
        r = P_RAIN1 if (P_RAIN1, v) in best else P_RAIN3
        if (r, v) in best:
            jobs.append((r, v))
    near = nearest_sites(sites, best[(P_SPEED, vts[0])][1])
    want = sorted({v[0] for v in near.values()})
    with ThreadPoolExecutor(max_workers=16) as ex:
        got = list(ex.map(lambda j: _read(best[j][1], want), jobs))
    data = {j: g for j, g in zip(jobs, got) if g}
    blends = sorted(best[j][0] for j in data)

    out = {}
    for s in sites:
        sid = near[s["name"]][0]
        steps = {}
        for v in vts:
            sp = data.get((P_SPEED, v), {})
            if sid not in sp:
                continue
            pc = sp["_pct"]
            row = {"sp": _pct(sp[sid], pc, 50), "lo": _pct(sp[sid], pc, 10), "hi": _pct(sp[sid], pc, 90),
                   "dir": data.get((P_DIR, v), {}).get(sid), "gust": None, "gust_hi": None,
                   "rain": None, "rain_hi": None}
            # an hourly max / total is stamped with the END of its hour; the Met
            # Office site shows it against the hour it STARTS (checked 11 Oct 2026)
            nxt = (datetime.datetime.strptime(v, fmt) + datetime.timedelta(hours=1)).strftime(fmt)
            for p, div in ((P_GUST1, 1), (P_GUST3, 1)):
                g = data.get((p, nxt if p == P_GUST1 and (p, nxt) in data else v), {})
                if sid in g:
                    row["gust"], row["gust_hi"] = _pct(g[sid], g["_pct"], 50), _pct(g[sid], g["_pct"], 90)
                    break
            for p, div in ((P_RAIN1, 1), (P_RAIN3, 3)):
                r = data.get((p, nxt if p == P_RAIN1 and (p, nxt) in data else v), {})
                if sid in r:      # metres over the period -> mm per hour
                    row["rain"] = _pct(r[sid], r["_pct"], 50) * 1000 / div
                    row["rain_hi"] = _pct(r[sid], r["_pct"], 90) * 1000 / div
                    break
            steps[datetime.datetime.strptime(v, fmt).replace(tzinfo=UTC)] = row
        ts = sorted(steps)
        byday = {}
        for k, t in enumerate(ts):
            fill = [(t, 0.0)]
            gap = (ts[k + 1] - t).total_seconds() / 3600 if k + 1 < len(ts) else 0
            if gap in (2, 3):
                fill += [(t, n / gap) for n in range(1, int(gap))]
            for base, frac in fill:
                a = steps[base]
                b = steps[ts[k + 1]] if frac else a
                lin = lambda x, y: None if x is None or y is None else x + (y - x) * frac
                d = None
                if a["dir"] is not None and b["dir"] is not None:
                    x = (1 - frac) * math.sin(math.radians(a["dir"])) + frac * math.sin(math.radians(b["dir"]))
                    y = (1 - frac) * math.cos(math.radians(a["dir"])) + frac * math.cos(math.radians(b["dir"]))
                    d = round(math.degrees(math.atan2(x, y)) % 360)
                # a period max / total belongs to the step that CLOSES the period
                per = b if frac else a
                loc = (base + datetime.timedelta(hours=gap * frac)).astimezone(LON)
                if not (hour_start <= loc.hour <= hour_end):
                    continue
                mph = lambda x: None if x is None else round(x * MS_MPH, 1)
                byday.setdefault(loc.strftime("%Y-%m-%d"), []).append(
                    (loc.hour, mph(lin(a["sp"], b["sp"])), mph(per["gust"]), d,
                     None if per["rain"] is None else round(per["rain"], 2), bool(frac) or gap >= 2,
                     {"lo": mph(lin(a["lo"], b["lo"])), "hi": mph(lin(a["hi"], b["hi"])),
                      "gust_hi": mph(per["gust_hi"]),
                      "rain_hi": None if per["rain_hi"] is None else round(per["rain_hi"], 2)}))
        out[s["name"]] = byday
    meta = {"blend_newest": blends[-1] if blends else None, "blend_oldest": blends[0] if blends else None,
            "files": len(data), "asked": len(jobs), "valid_times": len(vts),
            "sites": {n: {"id": v[0], "km": v[1], "alt_m": v[2]} for n, v in near.items()}}
    return out, meta


if __name__ == "__main__":
    import json
    cfg = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")))
    t0 = time.time()
    data, meta = pull(cfg["sites"])
    print("in", round(time.time() - t0, 1), "s |", {k: v for k, v in meta.items() if k != "sites"})
    for n, bd in data.items():
        ds = sorted(bd)
        print(f"  {n:15s} {meta['sites'][n]} days {len(ds)} {ds[0]}..{ds[-1]} hours/day {[len(bd[d]) for d in ds]}")
