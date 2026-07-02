#!/usr/bin/env python3
"""Patang Wind — UK beach game planner.

Pulls deterministic wind forecasts from Open-Meteo (free, no key) for each beach
from the two models Tayyab checks on the day — XCWeather's GFS and the Met Office
(UKMO) — plus ECMWF as a silent second opinion. Scores each day against a
fighter-kite flying window (steady wind + gust band, inside flying hours, blowing
OFFSHORE / out to sea). A day is GREEN only when BOTH decision models agree it's a
full offshore day; AMBER when they split (a coin-flip); grey when neither bites.
Writes a static page to docs/ that GitHub Pages serves. Runs from a GitHub Action.
"""
import urllib.request, json, datetime, re, math, os, html, time
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(ROOT, "config.json")))
TH = CFG["thresholds"]
# The two models you actually check on the day drive the verdict; ECMWF rides
# along silently so we can later score whether its dissents come true.
DECIDE = CFG.get("decide_models", ["gfs_seamless", "ukmo_seamless"])
WATCH = CFG.get("watch_models", ["ecmwf_ifs025"])
ALLMODELS = DECIDE + WATCH
MODEL_LABEL = {"gfs_seamless": "XC (GFS)", "ukmo_seamless": "Met Office",
               "ecmwf_ifs025": "ECMWF", "icon_seamless": "ICON", "gem_global": "GEM"}
SITES = CFG["sites"]
UA = {"User-Agent": "patang-wind-planner/1.0 (hobby; github pages)"}
COMP = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def get(url, timeout=120, tries=4):
    """Fetch JSON with retries — the build fires ~24 Open-Meteo calls in a burst
    per run, so a single transient timeout / throttle shouldn't fail the whole
    build."""
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return json.load(r)
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


def comp(d):
    return "?" if d is None else COMP[int((d % 360) / 22.5 + 0.5) % 16]


def angdiff(a, b):
    return abs((a - b + 180) % 360 - 180)


def fmt_hour(h):
    ap = "am" if h < 12 else "pm"
    x = h % 12 or 12
    return f"{x}{ap}"


def offset(lat, lon, bearing, dist_km):
    br = math.radians(bearing)
    return (lat + (dist_km / 111.32) * math.cos(br),
            lon + (dist_km / (111.32 * math.cos(math.radians(lat)))) * math.sin(br))


def seaward(lat, lon):
    """Return the list of compass bearings that point at open sea (or []).

    Samples elevation in a 16-point ring at 3 km and 6 km. Open-Meteo's DEM
    returns exactly 0.0 over sea (land is non-zero, even negative for fens),
    so a bearing counts as sea only if both ring samples are exactly 0.0.

    We keep the full SET of sea bearings rather than averaging them to a single
    heading — headland/estuary beaches (Sheerness, Portland) have sea wrapping
    round a wide, sometimes split arc, and averaging that to one point wrongly
    rejects wind blowing at the edges of the arc (e.g. due-east open water).
    """
    bearings = [i * 22.5 for i in range(16)]
    dists = [3, 6]
    lats, lons, idx = [lat], [lon], {}
    for b in bearings:
        for d in dists:
            la, lo = offset(lat, lon, b, d)
            lats.append(la); lons.append(lo); idx[(b, d)] = len(lats) - 1
    url = ("https://api.open-meteo.com/v1/elevation?latitude=%s&longitude=%s"
           % (",".join(f"{x:.4f}" for x in lats), ",".join(f"{x:.4f}" for x in lons)))
    try:
        el = get(url).get("elevation", [])
    except Exception:
        return []
    sea = []
    for b in bearings:
        ok = True
        for d in dists:
            i = idx[(b, d)]
            v = el[i] if i < len(el) else None
            if v is None or v != 0.0:
                ok = False; break
        if ok:
            sea.append(b)
    return sea


def sea_for(s):
    """Sea-bearing set for a site. Beach geography is static, so prefer the
    cached 'sea_deg' in config.json and only hit the elevation API when it's
    missing — that keeps the scheduled build off a flaky per-run dependency."""
    cached = s.get("sea_deg")
    if cached:
        return list(cached)
    return seaward(s["lat"], s["lon"])


def sea_mean(sea):
    """Circular-mean bearing of a sea-bearing set, for display only."""
    if not sea:
        return None
    x = sum(math.cos(math.radians(b)) for b in sea)
    y = sum(math.sin(math.radians(b)) for b in sea)
    return math.degrees(math.atan2(y, x)) % 360


def offshore(dd, sea):
    """True if wind FROM bearing dd blows OUT toward the sea.

    Tests the downwind heading against every detected sea bearing (not a single
    averaged one), so a wind counts as offshore when it heads into any part of
    the open-water arc within offshore_arc degrees. Unknown direction / no sea
    detected -> not filtered (returns True)."""
    if dd is None or not sea:
        return True
    blow = (dd + 180) % 360
    return any(angdiff(blow, b) <= TH["offshore_arc"] for b in sea)


def pull(lat, lon):
    """Deterministic hourly wind for every model, one API call.

    Open-Meteo suffixes each series with the model id when several models are
    requested (wind_speed_10m_gfs_seamless, ...). Returns
    {model: {date: [(hr, mean, gust, dir), ...]}} for the flying hours only."""
    url = ("https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s"
           "&hourly=wind_speed_10m,wind_gusts_10m,wind_direction_10m"
           "&wind_speed_unit=mph&timezone=Europe/London&forecast_days=%d&models=%s"
           % (lat, lon, TH["outlook_days"], ",".join(ALLMODELS)))
    try:
        d = get(url)
    except Exception:
        return {}
    H = d.get("hourly", {})
    times = H.get("time", [])
    per = {}
    for m in ALLMODELS:
        ws = H.get("wind_speed_10m_" + m)
        wg = H.get("wind_gusts_10m_" + m)
        wd = H.get("wind_direction_10m_" + m)
        if not ws:
            continue
        byday = defaultdict(list)
        for i, t in enumerate(times):
            hr = int(t[11:13])
            if TH["hour_start"] <= hr <= TH["hour_end"]:
                byday[t[:10]].append((hr, ws[i], wg[i] if wg else None, wd[i] if wd else None))
        per[m] = byday
    return per


def good(m, g, dd, sea):
    if m is None or g is None:
        return False
    if not (TH["mean_min"] <= m <= TH["mean_max"]):
        return False
    if not (TH["gust_min"] <= g <= TH["gust_max"]):
        return False
    return offshore(dd, sea)


def day_read(byday, date, sea):
    """One model's deterministic read for a day: how many offshore + in-band
    hours it gives inside the flying window, whether that clears full_day_hours,
    the good-hours span, and a representative peak (median wind/gust/dir)."""
    good_hours, rows = [], []
    for hr, m, g, dd in sorted(byday.get(date, [])):
        if good(m, g, dd, sea):
            good_hours.append(hr)
            rows.append((m, g, dd))
    n = len(good_hours)
    peak = None
    if rows:
        ms = sorted(r[0] for r in rows)
        gs = sorted(r[1] for r in rows)
        xs = sum(math.cos(math.radians(r[2])) for r in rows)
        ys = sum(math.sin(math.radians(r[2])) for r in rows)
        peak = {"hour": good_hours[len(good_hours) // 2], "mph": round(ms[len(ms) // 2]),
                "gust": round(gs[len(gs) // 2]), "from": comp(math.degrees(math.atan2(ys, xs)) % 360)}
    return {"hours": n, "go": n >= TH["full_day_hours"],
            "span": [good_hours[0], good_hours[-1]] if good_hours else None, "peak": peak}


def verdict_of(reads):
    """GREEN when both decision models call a full offshore day; AMBER when they
    split (a genuine coin-flip); grey when neither does."""
    gos = [reads[m]["go"] for m in DECIDE if m in reads]
    if gos and all(gos):
        return "go"
    if any(gos):
        return "split"
    return "no"


def day_record(per, dt, sea, today):
    reads = {m: day_read(per.get(m, {}), dt, sea) for m in ALLMODELS if m in per}
    v = verdict_of(reads)
    wd = datetime.date.fromisoformat(dt)
    # headline peak: the Met Office read on a GO day (highest-res for UK coast),
    # else whichever decision model likes it, else any read.
    order = ["ukmo_seamless", "gfs_seamless"] + [m for m in ALLMODELS]
    peak = None
    for m in order:
        r = reads.get(m)
        if r and r["go"] and r["peak"]:
            peak = r["peak"]; break
    if peak is None:
        for m in order:
            r = reads.get(m)
            if r and r["peak"]:
                peak = r["peak"]; break
    return {"date": dt, "wd": wd.strftime("%a"), "dd": wd.strftime("%-d %b"),
            "lead": (wd - today).days, "verdict": v, "peak": peak,
            "models": {m: {"hours": reads[m]["hours"], "go": reads[m]["go"]} for m in reads},
            "agree": len({reads[m]["go"] for m in DECIDE if m in reads}) == 1}


def build():
    gen = datetime.datetime.now()
    today = gen.date()
    out = {"generated": gen.strftime("%a %-d %b %Y, %H:%M"), "criteria": TH,
           "sites": [], "best_pick": None, "outlook": []}
    allbest = []
    for s in SITES:
        sea = sea_for(s)
        sm = sea_mean(sea)
        per = pull(s["lat"], s["lon"])
        dates = sorted({d for m in DECIDE if m in per for d in per[m]})
        days = [day_record(per, dt, sea, today) for dt in dates]
        out["sites"].append({"name": s["name"],
                             "sea": round(sm) if sm is not None else None,
                             "sea_c": comp(sm) if sm is not None else "?",
                             "sea_arc": [comp(b) for b in sea], "days": days})
        for d in days:
            allbest.append((s["name"], d))
    # best pick this week = a day both models AGREE on (verdict go), most hours first
    def hrs(d):
        return sum(d["models"].get(m, {}).get("hours", 0) for m in DECIDE)
    firm = [(n, d) for n, d in allbest if 0 <= d["lead"] <= TH["firm_days"] and d["verdict"] == "go"]
    firm.sort(key=lambda x: -hrs(x[1]))
    if firm:
        n, d = firm[0]
        out["best_pick"] = {"site": n, "wd": d["wd"], "dd": d["dd"], "peak": d["peak"],
                            "verdict": "go", "models": d["models"]}
    else:  # nothing agreed — surface the best split day so the week isn't blank
        split = [(n, d) for n, d in allbest if 0 <= d["lead"] <= TH["firm_days"] and d["verdict"] == "split"]
        split.sort(key=lambda x: -hrs(x[1]))
        if split:
            n, d = split[0]
            out["best_pick"] = {"site": n, "wd": d["wd"], "dd": d["dd"], "peak": d["peak"],
                                "verdict": "split", "models": d["models"]}
    rank = {"go": 2, "split": 1, "no": 0}
    byday = defaultdict(list)
    for n, d in allbest:
        if TH["firm_days"] < d["lead"] <= TH["outlook_days"] - 1:
            byday[d["date"]].append((n, d))
    for dt in sorted(byday):
        n, d = max(byday[dt], key=lambda x: (rank[x[1]["verdict"]], hrs(x[1])))
        out["outlook"].append({"wd": d["wd"], "dd": d["dd"], "site": n, "verdict": d["verdict"]})
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "docs", "board.json"), "w"), indent=0)
    open(os.path.join(ROOT, "docs", "index.html"), "w").write(render(out))
    print("wrote docs/index.html + docs/board.json |", len(out["sites"]), "sites | best:", out["best_pick"])


VCLASS = {"go": "hi", "split": "mid", "no": "lo"}
VWORD = {"go": "GO", "split": "maybe", "no": "—"}


def short(m):
    return MODEL_LABEL.get(m, m).split()[0]


def render(out):
    th = out["criteria"]
    firm_days = th["firm_days"]
    base = max(out["sites"], key=lambda s: len(s["days"]), default=None) if out["sites"] else None
    cols = [d for d in base["days"] if 0 <= d["lead"] <= firm_days] if base else []
    head = "".join(f'<th>{"Today" if c["lead"] == 0 else c["wd"]}<span>{c["dd"]}</span></th>' for c in cols)
    rows = []
    for s in out["sites"]:
        by_lead = {d["lead"]: d for d in s["days"]}
        cells = "".join(cell(by_lead.get(c["lead"]), c) for c in cols)
        sea = f'<span class="sea">sea {s["sea_c"]}</span>' if s["sea"] is not None else ""
        rows.append(f'<tr><th class="site">{html.escape(s["name"])}{sea}</th>{cells}</tr>')
    bp = out["best_pick"]
    if bp and bp["peak"]:
        pk = bp["peak"]
        go = bp["verdict"] == "go"
        badge = "GO" if go else "MAYBE"
        note = "XC + Met Office both agree" if go else "only one model likes it — a coin-flip"
        hero = (f'<div class="hero"><div><div class="lbl">best window this week</div>'
                f'<div class="hsite">{html.escape(bp["site"])}</div>'
                f'<div class="hmeta">{bp["wd"]} {bp["dd"]} &middot; {fmt_hour(pk["hour"])} &middot; '
                f'{pk["mph"]} mph, gust {pk["gust"]} &middot; wind {pk["from"]} (offshore)</div>'
                f'<div class="hnote">{note}</div></div>'
                f'<div class="hnum {VCLASS[bp["verdict"]]}"><span>{badge}</span></div></div>')
    else:
        hero = '<div class="hero none">No day this week where both models agree. Try the outlook below.</div>'
    outlook = "".join(
        f'<div class="ochip {VCLASS[o["verdict"]]}"><span>{o["wd"]} {o["dd"]}</span> '
        f'{html.escape(o["site"])} {VWORD[o["verdict"]]}</div>'
        for o in out["outlook"])
    crit = (f'{th["mean_min"]}–{th["mean_max"]} mph &middot; gust &le;{th["gust_max"]} '
            f'&middot; offshore &middot; {th["full_day_hours"]}+ hrs of {th["hour_start"]:02d}:00–{th["hour_end"]:02d}:00 '
            f'&middot; <b>XC + Met Office must agree</b>')
    return PAGE.format(generated=out["generated"], crit=crit, hero=hero, head=head,
                       rows="".join(rows), outlook=outlook)


def cell(d, c):
    if d is None:
        return '<td class="cell lo"><span class="pct">&ndash;</span></td>'
    v = d["verdict"]
    b = VCLASS[v]
    peak = d["peak"]
    label = c["wd"] + " " + c["dd"]
    ms = d.get("models") or {}
    tip = {"go": "both agree — GO", "split": "split — coin-flip", "no": "no window"}[v]
    title = f"{label} · {tip}"
    if peak:
        title += f' · {fmt_hour(peak["hour"])} {peak["mph"]} mph, gust {peak["gust"]}, {peak["from"]}'
    if ms:
        title += " · " + ", ".join(
            f'{MODEL_LABEL.get(m, m)} {ms[m]["hours"]}h {"✓" if ms[m]["go"] else "✗"}'
            for m in ALLMODELS if m in ms)
    if v == "no":
        return f'<td class="cell lo" title="{html.escape(title)}"><span class="pct">&ndash;</span></td>'
    if v == "go":
        main, sub = "GO", (f'<span class="sub">{fmt_hour(peak["hour"])} {peak["from"]}</span>' if peak else "")
    else:
        yes = [short(m) for m in DECIDE if ms.get(m, {}).get("go")]
        main = (yes[0] if yes else "?") + "?"
        sub = f'<span class="sub">{fmt_hour(peak["hour"])} {peak["from"]}</span>' if peak else ""
    return f'<td class="cell {b}" title="{html.escape(title)}"><span class="pct">{main}</span>{sub}</td>'


PAGE = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Patang Wind — beach game planner</title>
<style>
:root{{--bg:#fbf8f1;--card:#fff;--ink:#26211a;--mut:#8a8170;--line:#e7ded0;
--hi-bg:#e7f3e3;--hi:#2f7d3f;--mid-bg:#fbeed4;--mid:#9a6b12;--lo-bg:#f4efe6;--accent:#c9a227;}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;-webkit-text-size-adjust:100%}}
.wrap{{max-width:860px;margin:0 auto;padding:22px 16px 60px}}
h1{{font-size:22px;font-weight:600;margin:0}}
.sub1{{color:var(--mut);font-size:13px;margin:2px 0 0}}
.crit{{color:var(--mut);font-size:12.5px;margin:8px 0 18px}}
.hero{{display:flex;align-items:center;gap:18px;background:var(--card);border:2px solid var(--accent);border-radius:14px;padding:16px 18px;margin-bottom:18px}}
.hero.none{{border-color:var(--line);color:var(--mut);font-size:14px;display:block}}
.lbl{{font-size:12px;color:var(--mut);margin-bottom:3px}}
.hsite{{font-size:18px;font-weight:600}}
.hmeta{{font-size:13.5px;color:#5c5446;margin-top:2px}}
.hnum{{margin-left:auto;text-align:right;line-height:1}}
.hnum span{{font-size:34px;font-weight:700;letter-spacing:.5px;color:var(--hi)}}
.hnum.mid span{{color:var(--mid)}}
.hnote{{font-size:12px;color:var(--mut);margin-top:5px}}
.scroll{{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--line);border-radius:12px;background:var(--card)}}
table{{border-collapse:collapse;width:100%;min-width:560px}}
th,td{{padding:7px 4px;text-align:center}}
thead th{{font-size:11px;color:var(--mut);font-weight:500;border-bottom:1px solid var(--line)}}
thead th span{{display:block;font-size:10px;opacity:.8}}
th.site{{text-align:left;font-weight:600;font-size:13px;white-space:nowrap;position:sticky;left:0;background:var(--card);padding-left:12px;border-right:1px solid var(--line)}}
th.site .sea{{display:block;font-weight:400;font-size:11px;color:var(--mut)}}
tbody tr+tr td,tbody tr+tr th{{border-top:1px solid var(--line)}}
.cell{{min-width:70px}}
.pct{{font-size:15px;font-weight:600;font-variant-numeric:tabular-nums}}
.sub{{display:block;font-size:11px;font-weight:400}}
.cell.hi{{background:var(--hi-bg)}}.cell.hi .pct{{color:var(--hi)}}.cell.hi .sub{{color:var(--hi)}}
.cell.mid{{background:var(--mid-bg)}}.cell.mid .pct{{color:var(--mid)}}.cell.mid .sub{{color:var(--mid)}}
.cell.lo{{background:var(--lo-bg)}}.cell.lo .pct{{color:var(--mut)}}
.legend{{display:flex;flex-wrap:wrap;gap:14px;font-size:12.5px;color:var(--mut);margin:12px 2px 0}}
.dot{{display:inline-block;width:11px;height:11px;border-radius:3px;vertical-align:-1px;margin-right:5px}}
.olbl{{font-size:12.5px;color:#5c5446;margin:22px 0 8px}}
.outlook{{display:flex;flex-wrap:wrap;gap:8px}}
.ochip{{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:6px 10px;font-size:12.5px;color:var(--mut)}}
.ochip span{{color:#5c5446}}
.ochip.hi{{background:var(--hi-bg);border-color:var(--hi);color:var(--hi)}}
.ochip.mid{{background:var(--mid-bg);border-color:var(--mid);color:var(--mid)}}
.foot{{color:var(--mut);font-size:12px;margin-top:26px;line-height:1.7}}
.foot a{{color:#5c5446}}
</style></head><body>
<div class="wrap">
<h1>Patang Wind</h1>
<p class="sub1">UK beach game planner &middot; updated {generated}</p>
<p class="crit">good day = {crit}</p>
{hero}
<div class="scroll"><table>
<thead><tr><th class="site">beach</th>{head}</tr></thead>
<tbody>{rows}</tbody>
</table></div>
<div class="legend">
<span><span class="dot" style="background:var(--hi-bg);border:1px solid var(--hi)"></span><b>GO</b> — XC &amp; Met Office both agree</span>
<span><span class="dot" style="background:var(--mid-bg);border:1px solid var(--mid)"></span><b>maybe</b> — they split (coin-flip); cell shows which app</span>
<span><span class="dot" style="background:var(--lo-bg);border:1px solid var(--line)"></span>no offshore full-day</span>
<span>tap a cell for both apps' hours</span>
</div>
<p class="olbl">10–14 day outlook &middot; rough, low confidence</p>
<div class="outlook">{outlook}</div>
<p class="foot">Each day is judged on the two models you check on the day — <b>XCWeather (GFS)</b> and
the <b>Met Office (UKMO)</b>, via <a href="https://open-meteo.com">Open-Meteo</a>. GREEN only when
<b>both</b> agree it's a full offshore day (9+ hrs of 8am–8pm); amber when they split. ECMWF rides
along silently so we can later check whose call comes true at each beach.
Gusts are the least certain part — treat as a ranking, not a promise.
Summer winds are light; the board greens up Oct–Apr. Auto-updates ~4&times;/day.</p>
</div></body></html>""".replace("{n}", "the")


if __name__ == "__main__":
    build()
