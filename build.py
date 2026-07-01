#!/usr/bin/env python3
"""Patang Wind — UK beach game planner.

Pulls ensemble wind forecasts from Open-Meteo (free, no key) for each beach,
scores each day against a fighter-kite flying window (steady wind + gust band,
inside flying hours, blowing OFFSHORE / out to sea), and writes a static page
to docs/ that GitHub Pages serves. Runs unattended from a GitHub Action.
"""
import urllib.request, json, datetime, re, math, os, html
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(ROOT, "config.json")))
TH = CFG["thresholds"]
MODELS = CFG.get("models", ["gfs025", "ecmwf_ifs025"])
SITES = CFG["sites"]
UA = {"User-Agent": "patang-wind-planner/1.0 (hobby; github pages)"}
COMP = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def get(url, timeout=120):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return json.load(r)


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
    """Return the compass bearing toward open sea, or None.

    Samples elevation in a 16-point ring at 3 km and 6 km. Open-Meteo's DEM
    returns exactly 0.0 over sea (land is non-zero, even negative for fens),
    so a bearing counts as sea only if both ring samples are exactly 0.0.
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
        return None
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
    if not sea:
        return None
    x = sum(math.cos(math.radians(b)) for b in sea)
    y = sum(math.sin(math.radians(b)) for b in sea)
    return math.degrees(math.atan2(y, x)) % 360


def pull(lat, lon):
    """Pull every ensemble member's hourly wind for the flying hours, per model."""
    per = {}
    for model in MODELS:
        url = ("https://ensemble-api.open-meteo.com/v1/ensemble?latitude=%s&longitude=%s"
               "&hourly=wind_speed_10m,wind_gusts_10m,wind_direction_10m"
               "&wind_speed_unit=mph&timezone=Europe/London&forecast_days=%d&models=%s"
               % (lat, lon, TH["outlook_days"], model))
        try:
            d = get(url)
        except Exception:
            continue
        if isinstance(d, dict) and d.get("error"):
            continue
        H = d.get("hourly", {})
        times = H.get("time", [])
        mv = defaultdict(dict)
        for k, arr in H.items():
            if k == "time":
                continue
            mm = re.match(r"(wind_speed_10m|wind_gusts_10m|wind_direction_10m)(?:_member(\d+))?$", k)
            if not mm:
                continue
            mv[mm.group(2) or "00"][mm.group(1)] = arr
        members = {}
        for memid, vd in mv.items():
            ws, wg, wd = vd.get("wind_speed_10m"), vd.get("wind_gusts_10m"), vd.get("wind_direction_10m")
            if not ws:
                continue
            byday = defaultdict(list)
            for i, t in enumerate(times):
                hr = int(t[11:13])
                if TH["hour_start"] <= hr <= TH["hour_end"]:
                    byday[t[:10]].append((hr, ws[i], wg[i] if wg else None, wd[i] if wd else None))
            members[memid] = byday
        per[model] = members
    return per


def good(m, g, dd, sc):
    if m is None or g is None:
        return False
    if not (TH["mean_min"] <= m <= TH["mean_max"]):
        return False
    if not (TH["gust_min"] <= g <= TH["gust_max"]):
        return False
    if sc is not None and dd is not None and angdiff((dd + 180) % 360, sc) > TH["offshore_arc"]:
        return False
    return True


def day_prob(members, date, sc):
    """Fraction of members flyable for a FULL day — a contiguous run of good
    hours >= full_day_hours (offshore + in band), because it's only worth
    taking the day off if it's flyable across 8am-8pm, not just a few hours."""
    tot = len(members)
    if not tot:
        return 0, None
    fly = 0
    hourhits = defaultdict(list)
    for memid, byday in members.items():
        good_hours = []
        for hr, m, g, dd in sorted(byday.get(date, [])):
            if good(m, g, dd, sc):
                good_hours.append(hr)
                hourhits[hr].append((m, g, dd))
        if len(good_hours) >= TH["full_day_hours"]:
            fly += 1
    prob = round(100 * fly / tot)
    peak = None
    if hourhits:
        ph = max(hourhits.items(), key=lambda x: len(x[1]))
        ms = sorted(v[0] for v in ph[1])
        gss = sorted(v[1] for v in ph[1])
        xs = sum(math.cos(math.radians(v[2])) for v in ph[1])
        ys = sum(math.sin(math.radians(v[2])) for v in ph[1])
        peak = {"hour": ph[0], "mph": round(ms[len(ms) // 2]),
                "gust": round(gss[len(gss) // 2]), "from": comp(math.degrees(math.atan2(ys, xs)) % 360)}
    return prob, peak


def build():
    gen = datetime.datetime.now()
    today = gen.date()
    out = {"generated": gen.strftime("%a %-d %b %Y, %H:%M"), "criteria": TH,
           "sites": [], "best_pick": None, "outlook": []}
    allbest = []
    for s in SITES:
        sc = seaward(s["lat"], s["lon"])
        per = pull(s["lat"], s["lon"])
        pooled = {}
        for model, members in per.items():
            for memid, byday in members.items():
                pooled[(model, memid)] = byday
        dates = sorted({d for byday in pooled.values() for d in byday})
        days = []
        for dt in dates:
            prob, peak = day_prob(pooled, dt, sc)
            models = {m: day_prob(per[m], dt, sc)[0] for m in per}
            wd = datetime.date.fromisoformat(dt)
            days.append({"date": dt, "wd": wd.strftime("%a"), "dd": wd.strftime("%-d %b"),
                         "prob": prob, "models": models, "peak": peak, "lead": (wd - today).days})
        out["sites"].append({"name": s["name"],
                             "sea": round(sc) if sc is not None else None,
                             "sea_c": comp(sc) if sc is not None else "?", "days": days})
        for d in days:
            allbest.append((d["prob"], s["name"], d))
    firm = sorted([(p, n, d) for p, n, d in allbest if 1 <= d["lead"] <= TH["firm_days"]], key=lambda x: -x[0])
    if firm:
        p, n, d = firm[0]
        out["best_pick"] = {"site": n, "wd": d["wd"], "dd": d["dd"], "prob": p, "peak": d["peak"]}
    byday = defaultdict(list)
    for p, n, d in allbest:
        if TH["firm_days"] < d["lead"] <= TH["outlook_days"] - 1:
            byday[d["date"]].append((p, n, d))
    for dt in sorted(byday):
        p, n, d = max(byday[dt], key=lambda x: x[0])
        out["outlook"].append({"wd": d["wd"], "dd": d["dd"], "site": n, "prob": p})
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "docs", "board.json"), "w"), indent=0)
    open(os.path.join(ROOT, "docs", "index.html"), "w").write(render(out))
    print("wrote docs/index.html + docs/board.json |", len(out["sites"]), "sites | best:", out["best_pick"])


def bucket(p):
    return "hi" if p >= 60 else ("mid" if p >= 35 else "lo")


def render(out):
    th = out["criteria"]
    firm_days = th["firm_days"]
    cols = [d for d in out["sites"][0]["days"] if 1 <= d["lead"] <= firm_days] if out["sites"] else []
    head = "".join(f'<th>{c["wd"]}<span>{c["dd"]}</span></th>' for c in c0(cols))
    rows = []
    for s in out["sites"]:
        cells = []
        by_lead = {d["lead"]: d for d in s["days"]}
        for c in cols:
            d = by_lead.get(c["lead"])
            cells.append(cell(d, c))
        sea = f'<span class="sea">sea {s["sea_c"]}</span>' if s["sea"] is not None else ""
        rows.append(f'<tr><th class="site">{html.escape(s["name"])}{sea}</th>{"".join(cells)}</tr>')
    bp = out["best_pick"]
    if bp and bp["peak"]:
        pk = bp["peak"]
        hero = (f'<div class="hero"><div><div class="lbl">best window this week</div>'
                f'<div class="hsite">{html.escape(bp["site"])}</div>'
                f'<div class="hmeta">{bp["wd"]} {bp["dd"]} &middot; {fmt_hour(pk["hour"])} &middot; '
                f'{pk["mph"]} mph, gust {pk["gust"]} &middot; wind {pk["from"]} (offshore)</div></div>'
                f'<div class="hnum"><span>{bp["prob"]}%</span><small>{"likely" if bp["prob"] >= 60 else "possible" if bp["prob"] >= 35 else "long shot"}</small></div></div>')
    else:
        hero = '<div class="hero none">No flying window in the band this week. Try the outlook below.</div>'
    outlook = "".join(
        f'<div class="ochip"><span>{o["wd"]} {o["dd"]}</span> {html.escape(o["site"])} {o["prob"]}%</div>'
        for o in out["outlook"])
    crit = (f'{th["mean_min"]}–{th["mean_max"]} mph &middot; gust {th["gust_min"]}–{th["gust_max"]} '
            f'&middot; {th["hour_start"]:02d}:00–{th["hour_end"]:02d}:00 &middot; offshore only')
    return PAGE.format(generated=out["generated"], crit=crit, hero=hero, head=head,
                       rows="".join(rows), outlook=outlook)


def c0(cols):
    return cols


def cell(d, c):
    if d is None:
        return '<td class="cell lo"><span class="pct">&ndash;</span></td>'
    p = d["prob"]
    b = bucket(p)
    peak = d["peak"]
    label = c["wd"] + " " + c["dd"]
    if p == 0 and not peak:
        title = f"{label} · 0%"
        return f'<td class="cell lo" title="{html.escape(title)}"><span class="pct">&ndash;</span></td>'
    sub = ""
    if b != "lo" and peak:
        sub = f'<span class="sub">{fmt_hour(peak["hour"])} {peak["from"]}</span>'
    title = f"{label} · {p}%"
    if peak:
        title += f' · {fmt_hour(peak["hour"])} · {peak["mph"]} mph, gust {peak["gust"]}, from {peak["from"]}'
    ms = d.get("models") or {}
    if ms:
        title += " · " + ", ".join(f"{k.split('_')[0]} {v}%" for k, v in ms.items())
    return f'<td class="cell {b}" title="{html.escape(title)}"><span class="pct">{p}%</span>{sub}</td>'


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
.hnum span{{font-size:42px;font-weight:600;color:var(--hi)}}
.hnum small{{display:block;font-size:11px;color:var(--mut);margin-top:2px}}
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
<span><span class="dot" style="background:var(--hi-bg);border:1px solid var(--hi)"></span>likely &ge;60%</span>
<span><span class="dot" style="background:var(--mid-bg);border:1px solid var(--mid)"></span>possible 35–59%</span>
<span><span class="dot" style="background:var(--lo-bg);border:1px solid var(--line)"></span>low &lt;35%</span>
<span>tap a cell for the detail</span>
</div>
<p class="olbl">10–14 day outlook &middot; rough, low confidence</p>
<div class="outlook">{outlook}</div>
<p class="foot">Probability = share of {n} ensemble forecast runs (GFS + ECMWF, via
<a href="https://open-meteo.com">Open-Meteo</a>) flyable offshore for most of 8am–8pm — a full day.
Gust forecasts are the least certain part — treat the number as a ranking, not a promise.
Summer winds are light; the board greens up Oct–Apr. Auto-updates ~4&times;/day.</p>
</div></body></html>""".replace("{n}", "the")


if __name__ == "__main__":
    build()
