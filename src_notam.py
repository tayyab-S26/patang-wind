#!/usr/bin/env python3
"""Our kite-flying permissions, as published in the UK NOTAMs.

Flying above 60 m needs CAA permission, and once granted it is published as a
NOTAM: Q-code QWCLW ("captive balloon or kite flying"), a centre point, a radius,
a height and the hours. notaminfo.com plots every UK NOTAM on its National Flight
Planning Map, and the page carries each one as a `notam(...)` call with its fields.

We keep ONLY kite/balloon warnings (QWCL..) whose centre is within NEAR_KM of one
of our beaches; airfield, airspace, drone and survey notices are dropped. One
request per build (the site asks crawlers for 10 s between requests; we make one).
Example of the shape (a Manchester group's, 11 Oct 2026):
  H6751/26 QWCLW 5315N00020E002
  KITE FLYING WI 1NM RADIUS OF 531455N 0001951E (CHAPEL ST LEONARDS). MAX HGT 3000FT AGL.
"""
import datetime, json, math, re, urllib.request

URL = "https://notaminfo.com/nationalmap"
UA = {"User-Agent": "Mozilla/5.0 (patang-wind-planner; hobby; one request per 4h)"}
NEAR_KM = 3.0
CALL = re.compile(r"\nnotam\((.*?)\);(?=\n)", re.S)
WHEN = re.compile(r"(\d{1,2} \w{3} \d{4} \d{2}:\d{2}) GMT")


def _km(a, b, c, d):
    return 6371 * 2 * math.asin(math.sqrt(math.sin(math.radians(c - a) / 2) ** 2 +
                                          math.cos(math.radians(a)) * math.cos(math.radians(c)) *
                                          math.sin(math.radians(d - b) / 2) ** 2))


def _gmt(s):
    return datetime.datetime.strptime(s, "%d %b %Y %H:%M").replace(tzinfo=datetime.timezone.utc)


def parse(html):
    """Every NOTAM on the page as a dict (only the fields we use)."""
    out = []
    for m in CALL.finditer(html):
        try:
            a = json.loads("[" + m.group(1) + "]")
        except Exception:
            continue
        if len(a) < 10:
            continue
        times = WHEN.findall(a[9])
        out.append({"lat": a[1], "lon": a[2], "ref": a[5], "title": a[6].strip(), "q": a[7],
                    "text": re.sub(r"\s*<br>\s*", " ", a[8]).strip(),
                    "when": re.sub(r"\s*<br>\s*", " | ", a[9]).strip(),
                    "from": _gmt(times[0]).isoformat() if times else None,
                    "to": _gmt(times[1]).isoformat() if len(times) > 1 else None})
    return out


def pull(sites, now=None):
    """([{beach, km, ref, text, when, from, to}], meta). Never raises."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    try:
        with urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=60) as r:
            html = r.read().decode("utf-8", "replace")
    except Exception as e:
        return [], {"error": "%s: %s" % (type(e).__name__, e)}
    allnot = parse(html)
    stamp = re.search(r"extracted at\s*([^<\n]+)", html)
    mine = []
    for n in allnot:
        q = n["q"].split("/")
        if len(q) < 2 or not q[1].startswith("QWCL"):          # kite / captive balloon only
            continue
        if n["to"] and n["to"] < now.isoformat():
            continue
        best = min(((_km(s["lat"], s["lon"], n["lat"], n["lon"]), s["name"]) for s in sites), default=None)
        if best and best[0] <= NEAR_KM:
            mine.append(dict(n, beach=best[1], km=round(best[0], 1)))
    meta = {"notams": len(allnot), "kite": sum(1 for n in allnot if "/QWCL" in n["q"]),
            "ours": len(mine), "extracted": stamp.group(1).strip() if stamp else None}
    if not allnot:
        meta["error"] = "page held no NOTAMs (layout changed or blocked)"
    return mine, meta


if __name__ == "__main__":
    import os
    cfg = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")))
    mine, meta = pull(cfg["sites"])
    print(meta)
    for n in mine:
        print(n["beach"], n["km"], "km |", n["ref"], "|", n["text"][:90], "|", n["when"][:80])
