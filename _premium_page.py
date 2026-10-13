#!/usr/bin/env python3
"""Premium look, as a PROTOTYPE: writes docs/preview.html only.

It takes the live page generator (_prototype_page.py), swaps the stylesheet and a
few markup strings, and runs it. The data, the verdict logic and every interaction
are the live ones, so what is judged here is the look alone. Once approved the
changes get folded into _prototype_page.py and this file goes.

Design: "kite paper on a sea sky". Deep indigo ink and one indigo band for the
call that matters; the patang's own paper colours (rani pink, saffron, parrot
green) carry meaning, never decoration: green = go, saffron = maybe, pink = you
are here. Bricolage Grotesque for the voice, Hanken Grotesk for the numbers.
"""
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(ROOT, "_prototype_page.py")).read()

CSS = r"""
:root{--ink:#0f1b3d;--ink2:#4a5878;--ink3:#8592ad;--sky:#eef3fa;--paper:#fff;--line:#dbe3ef;--mist:#f3f6fb;
--indigo:#22308f;--indigo2:#3a4bc0;--rani:#e0245e;--saffron:#f5a300;--parrot:#12a150;--parrot-d:#0b7a3b;
--disp:"Bricolage Grotesque","Hanken Grotesk",system-ui,sans-serif;--body:"Hanken Grotesk",system-ui,-apple-system,sans-serif}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--sky);color:var(--ink);font:15px/1.5 var(--body);font-variant-numeric:tabular-nums}
button{font-family:inherit}
:focus-visible{outline:2px solid var(--rani);outline-offset:2px}
.wrap{max-width:780px;margin:0 auto;padding:18px 14px 64px}

/* top bar */
.bar{display:flex;align-items:center;gap:18px;flex-wrap:wrap;margin-bottom:16px}
.brand{display:flex;align-items:center;gap:10px}
.brand svg{width:26px;height:32px;flex:none}
h1{font:700 24px/1 var(--disp);letter-spacing:-.02em;margin:0}
.nav{display:flex;background:var(--paper);border:1px solid var(--line);border-radius:999px;padding:3px;gap:2px}
.nb{border:0;background:transparent;border-radius:999px;padding:7px 16px;font-size:14px;font-weight:600;color:var(--ink2);cursor:pointer}
.nb.on{background:var(--indigo);color:#fff}
.upd{margin-left:auto;text-align:right;font-size:12.5px;color:var(--ink2);line-height:1.35}
.upd span{display:block;font-size:11px;color:var(--ink3)}
.sec{display:none}.sec.on{display:block}

/* the call that matters */
.hero{position:relative;overflow:hidden;display:grid;grid-template-columns:1fr auto;gap:8px 28px;align-items:center;
  background:linear-gradient(118deg,#1a2577 0%,#2a3aa6 52%,#4a5fd6 100%);color:#fff;border-radius:18px;padding:22px 150px 22px 26px;margin-bottom:12px}
.hero::after{content:"";position:absolute;inset:auto 0 0 0;height:5px;background:var(--parrot)}
.hero.v-mid::after{background:var(--saffron)}
.hverd{font:800 44px/0.98 var(--disp);letter-spacing:-.03em}
.hsite{font:600 19px/1.2 var(--disp);margin-top:8px;opacity:.96}
.hmeta{font-size:14.5px;line-height:1.45;margin-top:6px;color:#d7dcf7;max-width:46ch}
.hmeters{min-width:230px;font-size:12.5px;color:#d7dcf7}
.hm{display:grid;grid-template-columns:86px 1fr 34px;align-items:center;gap:8px;margin:7px 0}
.hm .trk{position:relative;height:8px;border-radius:5px;background:rgba(255,255,255,.2)}
.hm .trk i{position:absolute;inset:0 auto 0 0;border-radius:5px;background:#fff}
.hm .trk u{position:absolute;top:-4px;bottom:-4px;left:69.2%;width:2px;background:var(--saffron)}
.hm b{color:#fff;font-weight:700;text-align:right}
.hmk{font-size:11.5px;color:#b9c1ee;margin-top:2px}
.kite{position:absolute;right:26px;top:50%;width:104px;height:150px;margin-top:-78px;transform-origin:50% 40%;transform:rotate(14deg);animation:sway 5.5s ease-in-out infinite}
@keyframes sway{0%,100%{transform:rotate(11deg) translateY(0)}50%{transform:rotate(18deg) translateY(-5px)}}
@media (prefers-reduced-motion:reduce){.kite{animation:none}}

/* permission line */
.permbar{display:block;background:var(--paper);border:1px solid var(--line);border-left:4px solid var(--indigo);border-radius:10px;padding:9px 14px;margin:0 0 12px;font-size:13.5px;color:var(--ink2)}
.permbar b{color:var(--ink)}
.permbar a{color:var(--indigo);font-weight:600;text-underline-offset:2px}
.permbar .pi{margin-top:5px;color:var(--ink)}
.permbar .none{color:var(--ink2)}
.nbadge{display:inline-block;margin-left:7px;font-size:10.5px;font-weight:700;color:#fff;background:var(--indigo);border-radius:4px;padding:1px 6px;vertical-align:2px}

/* the board: one sheet, ten rows */
.board{background:var(--paper);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.dayhead{display:flex;align-items:flex-end;gap:10px;padding:12px 14px 8px;border-bottom:1px solid var(--line);background:var(--mist)}
.dayhead .cname{min-width:96px}
.strip7{display:flex;gap:3px;margin-left:auto}
.dh{width:32px;display:flex;flex-direction:column;align-items:center;line-height:1.15}
.dh b{font-size:10.5px;font-weight:600;color:var(--ink3)}
.dh span{font-size:10px;color:var(--ink3)}
.dh.we b,.dh.we span{color:var(--ink)}
.dh.td b{color:var(--rani)}
.dhchev{width:10px;flex:none}
.card{border-bottom:1px solid var(--line);background:var(--paper)}
.card:last-child{border-bottom:0}
.chead{display:flex;align-items:center;gap:10px;padding:9px 14px;cursor:pointer;position:relative}
.chead:hover{background:#f8fafd}
.cname{font:600 15.5px/1.2 var(--disp);letter-spacing:-.01em;min-width:96px}
.csea{font:400 12px/1.3 var(--body);color:var(--ink3);display:block;margin-top:1px}
.dc{position:relative;width:32px;height:32px;border-radius:7px;display:flex;flex-direction:column;align-items:center;justify-content:center;cursor:pointer;background:var(--mist);color:var(--ink3)}
.dc .lab{font-size:10.5px;font-weight:700;line-height:1;letter-spacing:.01em}
.dc .bars{display:none}
.dc.v-hi{background:var(--parrot);color:#fff}
.dc.v-mid{background:#ffefc2;color:#7a4f00}
.dc.perm{box-shadow:inset 0 0 0 2px var(--indigo)}
.dc:hover{filter:brightness(.96)}
.chev{width:0;height:0;border-left:5px solid transparent;border-right:5px solid transparent;border-top:6px solid var(--ink3);transition:transform .15s;flex:none}
.card.open .chev{transform:rotate(180deg)}
.panel{display:none;padding:4px 14px 16px;border-top:1px solid var(--line);background:#fcfdff}
.card.open .panel{display:block}
.widehint{display:none}
.colR{display:none}

/* detail */
.verdict{font-size:14.5px;margin:12px 0;line-height:1.5;color:var(--ink)}
.blk{margin:14px 0}
.blkh{font-size:12.5px;font-weight:600;color:var(--ink2);margin-bottom:7px}
.chips{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:10px}
.chip{border:1px solid var(--line);border-radius:8px;padding:5px 9px;font-size:12px;font-weight:500;cursor:pointer;color:var(--ink2);background:var(--paper)}
.chip:hover{border-color:var(--ink3)}
.chip.on{border-color:var(--indigo);color:#fff;background:var(--indigo);font-weight:600}
.wsum{font-size:14px;margin-top:8px;color:var(--ink)}
.muted{color:var(--ink3);font-size:13.5px}
.conf div{display:flex;align-items:center;gap:8px;margin:4px 0;font-size:13px;color:var(--ink2)}
.note{font-size:13.5px;color:var(--ink2);line-height:1.55;background:var(--mist);border-radius:10px;padding:11px 13px}
.strip{display:flex;align-items:flex-end;gap:3px;height:52px}
.sb{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px}
.sbar{width:100%;max-width:18px;border-radius:3px 3px 0 0;min-height:2px}
.sl{font-size:10px;color:var(--ink3)}
.xcw{overflow-x:auto;margin:8px 0 8px;border-radius:12px;border:1px solid var(--line);background:var(--paper)}
.xcday{background:var(--mist);padding:8px 10px 8px 14px;font:700 18px/1.2 var(--disp);letter-spacing:-.01em;color:var(--ink);display:flex;align-items:center;gap:7px;border-bottom:1px solid var(--line)}
.xcday small{font:500 11px var(--body);color:var(--ink3)}
.srcsw{margin-left:auto;display:flex;background:var(--paper);border:1px solid var(--line);border-radius:999px;padding:2px;gap:2px}
.srcsw button{border:0;background:transparent;border-radius:999px;color:var(--ink2);font:600 12.5px var(--body);padding:5px 12px;cursor:pointer}
.srcsw button.on{background:var(--indigo);color:#fff}
.xcw table{border-collapse:collapse;width:100%;font-size:15.5px;font-weight:500;background:var(--paper);color:#10203f}
.xcw td{padding:0 6px;height:38px;text-align:center;white-space:nowrap;border-top:2px solid #fff}
.xcw td.tm{background:#e6ecf5;color:var(--ink);text-align:left;padding-left:12px;width:78px;font-weight:600}
.xcw td.ar{width:50px}
.xcw td.ar span{display:inline-block;color:var(--indigo);font-weight:900;font-size:24px;line-height:1}
.xcw td.to{color:#a9b4c8;font-size:12px;width:26px;padding:0;font-weight:400}
.xcw td.rn{color:var(--ink2);font-weight:400}
.xcw td.rn.wetc{background:#e3f4fb;color:var(--ink)}
.xcw td.ic{font-size:20px;width:46px}
.xcw tr.gd td.tm{box-shadow:inset 5px 0 0 var(--parrot);color:var(--parrot-d);font-weight:700}
.xcw tr.gd td.ar span{color:var(--parrot)}
.xcw tr.off td.tm{background:#d3dbe8;color:var(--ink2)}
.xckey{font-size:12px;color:var(--ink3);margin:0 0 10px;line-height:1.5}
details{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:4px 16px;margin:12px 0;font-size:14px}
summary{cursor:pointer;font-weight:600;color:var(--ink);padding:8px 0}
details p{margin:8px 0;color:var(--ink2);line-height:1.6;max-width:72ch}
#livewrap{height:80vh;min-height:520px;border-radius:14px;overflow:hidden;border:1px solid var(--line);background:#dfe7f2}
.maplegend{font-size:12.5px;color:var(--ink3);margin-top:8px;line-height:1.5}
.foot{color:var(--ink3);font-size:12.5px;margin-top:22px;line-height:1.65;max-width:110ch}
.foot a{color:var(--ink2)}
.foot b{color:var(--ink2)}

@media (min-width:1100px){
  .wrap{max-width:none;padding:18px 32px 64px}
  .cols{display:grid;grid-template-columns:minmax(800px,1.15fr) minmax(0,1fr);gap:18px;align-items:start}
  .colL,.colR{min-width:0}
  .colL details{margin-top:14px}
  .colR{display:block;position:sticky;top:14px;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:14px 16px 16px;max-height:calc(100vh - 28px);overflow:auto}
  .sidehd{font:700 22px/1.15 var(--disp);letter-spacing:-.02em}
  .sidehd span{display:block;font:400 13px/1.4 var(--body);letter-spacing:0;color:var(--ink3);margin-top:2px}
  #side .verdict{margin:8px 0}
  #side .blk{margin:8px 0}
  #side .blkh{display:none}
  #side .chips{margin-bottom:8px}
  #side .chip{padding:4px 7px;font-size:11.5px}
  #side .wsum{margin:0 0 6px}
  #side .xcw{margin:6px 0 8px}
  #side .xcw td{height:31px}
  #side .xcw table{font-size:14.5px}
  .strip7{flex:1;margin-left:14px;gap:4px}
  .chead>div:first-child,.dayhead>.cname{width:158px;min-width:158px;flex:none}
  .dh{flex:1;width:auto;min-width:36px}
  .dh b{font-size:11.5px}.dh span{font-size:11px}
  .dc{flex:1;width:auto;min-width:36px;height:46px;justify-content:flex-end;padding:0 0 5px}
  .dc .lab{position:absolute;top:5px;left:0;right:0;text-align:center;font-size:11px}
  .dc .bars{display:flex;align-items:flex-end;gap:3px;height:20px}
  .dc .bars i{display:block;width:7px;border-radius:2px 2px 0 0;background:#c3cddd;min-height:2px}
  .dc .bars i.f{background:var(--ink2)}
  .dc.v-hi .bars i{background:rgba(255,255,255,.55)}
  .dc.v-hi .bars i.f{background:#fff}
  .dc.v-mid .bars i{background:#e3cf95}
  .dc.v-mid .bars i.f{background:#c98500}
  .dc.out{opacity:.6}
  .card.sel .chead{background:#f6f8fd}
  .card.sel .chead::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--rani)}
  .chev,.dhchev{display:none}
  .widehint{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--ink3);font-weight:400;line-height:1.25}
  .widehint i{display:inline-block;width:6px;border-radius:2px 2px 0 0;background:var(--ink2);vertical-align:bottom}
  #livewrap{height:calc(100vh - 170px);min-height:560px}
}
@media (min-width:1600px){#side .chips{flex-wrap:nowrap}#side .chip{flex:1;text-align:center;white-space:nowrap;padding:4px 3px}}
@media (max-width:700px){
  .hero{grid-template-columns:1fr;padding:18px 96px 20px 18px}
  .hverd{font-size:34px}
  .hmeters{min-width:0;margin-top:6px}
  .kite{width:70px;height:101px;right:14px;top:16px;margin-top:0}
  .upd{margin-left:0;text-align:left;width:100%}
}
@media (max-width:430px){
  .chead{gap:7px;padding:10px 10px}
  .dayhead{gap:7px;padding:10px 10px 7px}
  .cname{min-width:78px;font-size:14px}
  .strip7{gap:2px}
  .dc{width:26px;height:26px;border-radius:6px}
  .dc .lab{font-size:9px}
  .dh{width:26px}.dh b{font-size:9px}.dh span{font-size:9px}
  .xcw table{font-size:13.5px}.xcw td{height:33px;padding:0 3px}.xcw td.tm{width:56px;padding-left:7px}
  .xcw td.ar{width:32px}.xcw td.ar span{font-size:19px}.xcw td.ic{width:30px;font-size:17px}
}
"""

KITE = ('<svg class="kite" viewBox="0 0 104 150" aria-hidden="true">'
        '<path d="M52 62 C40 96 60 118 30 150" fill="none" stroke="#ffffff" stroke-opacity=".55" stroke-width="1.2"/>'
        '<path d="M52 4 L52 54 L12 54 Z" fill="#e0245e"/><path d="M52 4 L92 54 L52 54 Z" fill="#f5a300"/>'
        '<path d="M12 54 L52 54 L52 112 Z" fill="#f5a300"/><path d="M92 54 L52 54 L52 112 Z" fill="#e0245e"/>'
        '<path d="M52 4 L52 112" stroke="#0f1b3d" stroke-opacity=".5" stroke-width="1.4"/>'
        '<path d="M12 54 Q52 34 92 54" fill="none" stroke="#0f1b3d" stroke-opacity=".5" stroke-width="1.4"/>'
        '<path d="M52 112 L44 128 L60 128 Z" fill="#12a150"/></svg>')
MARK = ('<svg viewBox="0 0 26 32" aria-hidden="true"><path d="M13 1 L13 14 L3 14 Z" fill="#e0245e"/><path d="M13 1 L23 14 L13 14 Z" fill="#f5a300"/>'
        '<path d="M3 14 L13 14 L13 28 Z" fill="#f5a300"/><path d="M23 14 L13 14 L13 28 Z" fill="#e0245e"/><path d="M13 28 L10.5 32 L15.5 32 Z" fill="#12a150"/></svg>')


def swap(a, b, count=1):
    global src
    assert src.count(a) == count, (src.count(a), a[:80])
    src = src.replace(a, b)


def swap_line(prefix, new):
    """Replace the one source line that starts with `prefix`."""
    global src
    lines = src.split("\n")
    hit = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hit) == 1, (len(hit), prefix[:60])
    lines[hit[0]] = new
    src = "\n".join(lines)


# stylesheet
i, j = src.index('CSS = """'), src.index('"""\n\nJS = r')
src = src[:i] + "CSS = r'''" + CSS + "'''\n\nJS = r" + src[j + len('"""\n\nJS = r'):]

# hero: the verdict first, in words
swap_line("html+='<div class=\"heads\"><div class=\"hero\">", r'''var FULLD={Mon:'Monday',Tue:'Tuesday',Wed:'Wednesday',Thu:'Thursday',Fri:'Friday',Sat:'Saturday',Sun:'Sunday'},FULLM={Jan:'January',Feb:'February',Mar:'March',Apr:'April',May:'May',Jun:'June',Jul:'July',Aug:'August',Sep:'September',Oct:'October',Nov:'November',Dec:'December'};
var bday=null;D.sites.forEach(function(s){if(s.n===b.s)s.d.forEach(function(d){if(d.dd===b.dd)bday=d;});});
var bxc=bday&&bday.xc?bday.xc.hours:0,bmet=bday&&bday.met?bday.met.hours:0;
var hverd=(b.v==='go'?'Go on ':b.v==='wet'?'Wet on ':'Maybe ')+(FULLD[b.wd]||b.wd);
var hwhy=b.v==='go'?'Both apps call a full day.':b.v==='wet'?'Both apps like the wind, but it rains.':'Only '+((bday&&which(bday)[0])==='Met'?'the Met Office calls':'XCWeather calls')+' a full day.';
function meter(lbl,h){return '<div class="hm"><span>'+lbl+'</span><span class="trk"><i style="width:'+Math.min(100,Math.round(h/13*100))+'%"></i><u></u></span><b>'+h+' h</b></div>';}
html+='<div class="heads"><div class="hero '+(b.v==='go'?'v-hi':'v-mid')+'"><div><div class="hverd">'+hverd+'</div><div class="hsite">'+b.s+', '+b.dd.split(' ')[0]+' '+(FULLM[b.dd.split(' ')[1]]||'')+'</div><div class="hmeta">'+b.mph+' mph gusting '+b.gust+', from the '+b.frm+' and out to sea. '+hwhy+'</div></div><div class="hmeters">'+meter('XCWeather',bxc)+meter('Met Office',bmet)+'<div class="hmk">Good hours between 8am and 8pm. The mark is 9, a full day.</div></div>''' + KITE.replace("'", "\\'") + r'''</div>';''')

# permission line, plain words
swap_line("html+='<div class=\"permbar\"><b>Kite permission (NOTAM)</b>",
          r'''html+='<div class="permbar"><b>Kite permission</b> '+(NM.error?'<span class="none">could not be checked this time ('+NM.error+').</span>':NT.length?(NT.length===1?'is published for one of our beaches.':'is published for '+NT.length+' of our beaches.'):'<span class="none">none published for our beaches yet.</span>')+' <a href="https://notaminfo.com/nationalmap" target="_blank" rel="noopener">Open the NOTAM map</a>' ''')
swap("""return '<div class="pi">✈ <b>'+n.beach+'</b> · '+n.ref+' · '+ntDate(n.from)+' → '+ntDate(n.to)+(ntFt(n.text)?' · max '+ntFt(n.text):'')+'</div>';""",
     """return '<div class="pi"><b>'+n.beach+'</b>, '+n.ref+', '+ntDate(n.from)+' to '+ntDate(n.to)+(ntFt(n.text)?', up to '+ntFt(n.text):'')+'</div>';""")
swap("<summary>How to read this — tap to open</summary>", "<summary>How to read this</summary>")

# the board: one sheet; weekend and today marked in the header; bars for each app's good hours
swap("""html+='<div class="cols"><div class="colL"><div class="dayhead"><div class="cname"><span class="widehint">small numbers = good hours<br>XC · Met Office (9+ = full day)</span></div><div class="strip7">'+dhCols.map(function(d){return '<div class="dh"><b>'+(d.ld===0?'Today':d.wd)+'</b><span>'+d.dd.split(' ')[0]+'</span></div>';}).join('')""",
     """html+='<div class="cols"><div class="colL"><div class="board"><div class="dayhead"><div class="cname"><span class="widehint"><span><i style="height:14px"></i> <i style="height:9px"></i></span><span>good hours:<br>XCWeather, Met Office</span></span></div><div class="strip7">'+dhCols.map(function(d){return '<div class="dh'+((d.wd==='Sat'||d.wd==='Sun')?' we':'')+(d.ld===0?' td':'')+'"><b>'+(d.ld===0?'Today':d.wd)+'</b><span>'+d.dd.split(' ')[0]+'</span></div>';}).join('')""")
swap("""cells+='<div class="dc'+(d.ld>7?' out':'')+(pd[dIso(d)]?' perm':'')+'" style="'+STY[k]+';font-size:12px;font-weight:700" onclick="pwOpen(event,'+i+','+d.ld+')" title="'+d.wd+' '+d.dd+'">'+cellTxt(d)+'<small>'+(d.xc?d.xc.hours:0)+'·'+(d.met?d.met.hours:0)+'</small></div>';""",
     """var xh=d.xc?d.xc.hours:0,mh=d.met?d.met.hours:0,lab=d.v==='no'?'':cellTxt(d).replace('?','');cells+='<div class="dc v-'+k+(d.ld>7?' out':'')+(pd[dIso(d)]?' perm':'')+'" onclick="pwOpen(event,'+i+','+d.ld+')" title="'+d.wd+' '+d.dd+': XCWeather '+xh+' good hours, Met Office '+mh+'">'+'<span class="lab">'+lab+'</span><span class="bars"><i class="'+(xh>=9?'f':'')+'" style="height:'+Math.round(xh/13*100)+'%"></i><i class="'+(mh>=9?'f':'')+'" style="height:'+Math.round(mh/13*100)+'%"></i></span></div>';""")
swap("""html+='</div><div class="colR" id="side"></div></div>';""", """html+='</div></div><div class="colR" id="side"></div></div>';""")

# detail pane, plain words
swap("""'<div class="sidehd">'+s.n+'<span>faces '+s.fc+' · offshore wind comes from the '+s.off_from+'</span></div>'""",
     """'<div class="sidehd">'+s.n+'<span>Faces '+s.fc+'. A wind from the '+s.off_from+' blows out to sea.</span></div>'""")
swap("""'<div class="permbar" style="margin:6px 0 4px">✈ <b>Permission '+n.ref+'</b> · '+ntDate(n.from)+' → '+ntDate(n.to)+(ntFt(n.text)?' · max '+ntFt(n.text):'')+'<div class="pi" style="font-size:12px;color:#4a5a72">'+n.text+'</div></div>'""",
     """'<div class="permbar" style="margin:8px 0 4px"><b>Permission '+n.ref+'</b>, '+ntDate(n.from)+' to '+ntDate(n.to)+(ntFt(n.text)?', up to '+ntFt(n.text):'')+'<div class="pi" style="font-size:12.5px;color:#4a5878">'+n.text+'</div></div>'""")
swap("""sum='<div class="wsum">Fly-window <b>'+hl(a)+'–'+hl(b+1)+'</b> · '+(pk.mph||'?')+' mph, gust '+(pk.gust||'?')+' · wind '+(pk.from||'?')+' — the green rows'+rsuf+'</div>';""",
     """sum='<div class="wsum">Good from <b>'+hl(a)+'m to '+hl(b+1)+'m</b>, '+(pk.mph||'?')+' mph gusting '+(pk.gust||'?')+', wind from the '+(pk.from||'?')+'.'+(rt?' <b'+(day.v==='wet'?' style="color:#a36a00"':'')+'>'+rt.charAt(0).toUpperCase()+rt.slice(1)+'.</b>':'')+'</div>';""")
swap("""sum='<div class="wsum muted">No offshore in-band window this day — too light or wrong direction.</div>';""",
     """sum='<div class="wsum muted">No good hours on this day: too light, too strong, or blowing the wrong way.</div>';""")
swap("#2f7d3f':'#a9a090')+'\">'+(go?'✓ full day':'✗ only '+h+'h')", "#0b7a3b':'#8592ad')+'\">'+(go?'Full day, '+h+' h':'Only '+h+' h')")
swap("""var col=d.v==='go'?"#2f7d3f":(d.v==='wet'||d.v==='split')?"#c98f12":"#b9afa0";""", """var col=d.v==='go'?"#12a150":(d.v==='wet'||d.v==='split')?"#f5a300":"#c3cddd";""")

# softer versions of the XCWeather bands, same steps
swap("return v<9?'#a9f3fb':v<13?'#c9f7fc':v<19?'#a6f79e':v<25?'#fbfb86':v<32?'#fbc9a0':v<39?'#f9a08c':'#f47c7c';",
     "return v<9?'#bfeaf5':v<13?'#d6f2f8':v<19?'#b2ecb0':v<25?'#f6f29a':v<32?'#f8cfa6':v<39?'#f4a994':'#ee8585';")
swap("return t<5?'#cfe8f5':t<10?'#d9e6a8':t<16?'#d9cf5c':t<19?'#e0b85a':t<22?'#dba24c':t<26?'#d98e45':'#d7743c';",
     "return t<5?'#d6e9f5':t<10?'#e3ecb8':t<16?'#e6dd82':t<19?'#ebc97c':t<22?'#e8b56c':t<26?'#e5a062':'#e08656';")

# page head: brand, tabs, updated
swap("""'<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>'""",
     """'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600..800&family=Hanken+Grotesk:wght@400;500;600;700&display=swap">'""")
swap("""'<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'""", "''")
swap("""'<div class="top"><h1>Patang Wind</h1></div>'""", """'<header class="bar"><div class="brand">""" + MARK + """<h1>Patang Wind</h1></div>'
        '<div class="nav"><button class="nb on" data-s="forecast">Forecast</button><button class="nb" data-s="live">Wind map</button></div>'
        '<div class="upd">Updated ' + data["g"] + ('<span>' + data["src"].replace(" | ", ". ") + '</span>' if data.get("src") else '') + '</div></header>'""")
swap("""'<p class="sub">UK beach game planner · updated ' + data["g"] + '</p>'""", "''")
swap("""+ ('<p class="sub" style="opacity:.7;font-size:11px">' + data["src"] + '</p>' if data.get("src") else '') +""", "")
swap("""'<div class="nav"><button class="nb on" data-s="forecast">Forecast</button><button class="nb" data-s="live">Wind map</button></div>'
        '<div id="sec-forecast\"""", """'<div id="sec-forecast\"""")
swap('"docs", "prototype.html"', '"docs", "preview.html"', count=2)
swap('print("wrote docs/prototype.html |"', 'print("wrote docs/preview.html |"')

exec(compile(src, "_premium_page(generated)", "exec"))
