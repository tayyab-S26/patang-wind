#!/usr/bin/env python3
"""Generate the main page (docs/prototype.html) from
the rich dataset. Self-contained (own warm theme, no external deps). Separate
from the live index.html so both can be compared at different links.
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
RICH = os.path.join(ROOT, "rich.json")
data = json.load(open(RICH))

CSS = r'''
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

/* the weekend: odds, because permission is asked two days ahead */
.wk{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:10px 16px 8px;margin:0 0 12px;display:grid;grid-template-columns:1fr;gap:6px 28px}
.wkh{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.wkh b{font:700 17px/1.2 var(--disp);letter-spacing:-.01em}
.wkap{font-size:12.5px;font-weight:600;color:var(--indigo);background:#e9edfb;border-radius:999px;padding:2px 10px}
.wkap.late{color:var(--ink2);background:var(--mist)}
.wkv{font-size:13.5px;font-weight:600;margin:2px 0 4px;color:var(--ink2)}
.wkv.hi{color:var(--parrot-d)}.wkv.mid{color:#a36a00}
.wkr{display:grid;grid-template-columns:104px minmax(60px,1fr) 40px auto;align-items:center;gap:2px 10px;margin:4px 0}
.wkn{font-weight:600;font-size:14px}
.wkt{height:9px;border-radius:5px;background:var(--mist);overflow:hidden}
.wkt i{display:block;height:100%;border-radius:5px;background:var(--ink3)}
.wkt i.hi{background:var(--parrot)}.wkt i.mid{background:var(--saffron)}
.wkr b{text-align:right;font-size:15px}
.wks{font-size:12px;color:var(--ink3);white-space:nowrap}
.wkf{grid-column:1/-1;font-size:11.5px;color:var(--ink3);border-top:1px solid var(--line);padding-top:7px}
@media (min-width:700px){.wk{grid-template-columns:1fr 1fr}}
@media (max-width:520px){.wkr{grid-template-columns:96px 1fr 40px}.wks{grid-column:1/-1}}

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
  .widehint{font-size:11.5px;color:var(--ink2)}
  .widehint .lg{display:flex;align-items:flex-end;gap:2px;height:14px}
  .widehint i{display:block;width:6px;border-radius:2px 2px 0 0;background:var(--ink2)}
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
'''

JS = r'''
const COMP=["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"];
function comp(d){return COMP[Math.round((d%360)/22.5)%16];}
function hl(h){var ap=h<12?"a":"p";var x=h%12||12;return x+ap;}
function vcls(v){return v==='go'?'hi':(v==='split'||v==='wet')?'mid':'lo';}
function which(d){var y=[];if(d.xc&&d.xc.go)y.push('XC');if(d.met&&d.met.go)y.push('Met');return y;}
function cellTxt(d){if(d.v==='go')return 'GO';if(d.v==='wet')return '☔';if(d.v==='split')return (which(d)[0]||'?')+'?';return '–';}
function mkTxt(d){return d.v==='go'?'✓':d.v==='wet'?'☔':d.v==='split'?'?':'–';}
function dscore(d){return (d.v==='go'?200:d.v==='wet'?150:d.v==='split'?100:0)+((d.xc?d.xc.hours:0)+(d.met?d.met.hours:0));}
/* Rain in plain words. w===null means no model reaches this day — say so, never
   render it as 'dry', or a day we cannot judge reads as one we've cleared. */
function rainTxt(d){var w=d&&d.wet;if(!w)return '';
  if(w.w===null||w.w===undefined)return 'no rain forecast this far out';
  if(!w.w)return 'dry enough';
  return 'rain'+(w.sp?' '+hl(w.sp[0])+'–'+hl(w.sp[1]+1):'')+' · '+w.h+' wet hrs';}
var STY={hi:"background:#e7f3e3;color:#2f7d3f",mid:"background:#fbeed4;color:#9a6b12",lo:"background:#f4efe6;color:#8a8170"};
var root=document.getElementById("pwroot");
var WIDE=window.matchMedia("(min-width:1100px)").matches,MAXLD=WIDE?13:7;
var b=D.best,html="";
var hbadge={go:'GO',wet:'WET',split:'MAYBE'}[b.v]||'MAYBE';
var hnote={go:'XC + Met Office agree',wet:'wind agreed — but '+rainTxt(b),split:'one model only — coin-flip'}[b.v]||'';
var FULLD={Mon:'Monday',Tue:'Tuesday',Wed:'Wednesday',Thu:'Thursday',Fri:'Friday',Sat:'Saturday',Sun:'Sunday'},FULLM={Jan:'January',Feb:'February',Mar:'March',Apr:'April',May:'May',Jun:'June',Jul:'July',Aug:'August',Sep:'September',Oct:'October',Nov:'November',Dec:'December'};
var bday=null;D.sites.forEach(function(s){if(s.n===b.s)s.d.forEach(function(d){if(d.dd===b.dd)bday=d;});});
var bxc=bday&&bday.xc?bday.xc.hours:0,bmet=bday&&bday.met?bday.met.hours:0;
var hverd=(b.v==='go'?'Go on ':b.v==='wet'?'Wet on ':'Maybe ')+(FULLD[b.wd]||b.wd);
var hwhy=b.v==='go'?'Both apps call a full day.':b.v==='wet'?'Both apps like the wind, but it rains.':'Only '+((bday&&which(bday)[0])==='Met'?'the Met Office calls':'XCWeather calls')+' a full day.';
function meter(lbl,h){return '<div class="hm"><span>'+lbl+'</span><span class="trk"><i style="width:'+Math.min(100,Math.round(h/13*100))+'%"></i><u></u></span><b>'+h+' h</b></div>';}
html+='<div class="heads"><div class="hero '+(b.v==='go'?'v-hi':'v-mid')+'"><div><div class="hverd">'+hverd+'</div><div class="hsite">'+b.s+', '+b.dd.split(' ')[0]+' '+(FULLM[b.dd.split(' ')[1]]||'')+'</div><div class="hmeta">'+b.mph+' mph gusting '+b.gust+', from the '+b.frm+' and out to sea. '+hwhy+'</div></div><div class="hmeters">'+meter('XCWeather',bxc)+meter('Met Office',bmet)+'<div class="hmk">Good hours between 8am and 8pm. The mark is 9, a full day.</div></div><svg class="kite" viewBox="0 0 104 150" aria-hidden="true"><path d="M52 62 C40 96 60 118 30 150" fill="none" stroke="#ffffff" stroke-opacity=".55" stroke-width="1.2"/><path d="M52 4 L52 54 L12 54 Z" fill="#e0245e"/><path d="M52 4 L92 54 L52 54 Z" fill="#f5a300"/><path d="M12 54 L52 54 L52 112 Z" fill="#f5a300"/><path d="M92 54 L52 54 L52 112 Z" fill="#e0245e"/><path d="M52 4 L52 112" stroke="#0f1b3d" stroke-opacity=".5" stroke-width="1.4"/><path d="M12 54 Q52 34 92 54" fill="none" stroke="#0f1b3d" stroke-opacity=".5" stroke-width="1.4"/><path d="M52 112 L44 128 L60 128 Z" fill="#12a150"/></svg></div>';
function dIso(d){var y=new Date().getFullYear(),m={Jan:1,Feb:2,Mar:3,Apr:4,May:5,Jun:6,Jul:7,Aug:8,Sep:9,Oct:10,Nov:11,Dec:12}[d.dd.split(' ')[1]],dd=+d.dd.split(' ')[0];if(new Date().getMonth()===11&&m===1)y++;return y+'-'+(m<10?'0':'')+m+'-'+(dd<10?'0':'')+dd;}
var NT=(D.notam&&D.notam.items)||[],NM=(D.notam&&D.notam.meta)||{};
function ntDate(iso){var d=new Date(iso);return d.toLocaleString('en-GB',{weekday:'short',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit',timeZone:'Europe/London'});}
function ntFt(t){var m=t.match(/MAX HGT ([0-9]+FT[^.]*)/);return m?m[1].toLowerCase():'';}
function ntDays(n){var out={};if(!n.from||!n.to)return out;var a=new Date(n.from),b=new Date(n.to);for(var t=new Date(a);t<=b;t=new Date(t.getTime()+3600e3*6)){out[t.toLocaleDateString('en-CA',{timeZone:'Europe/London'})]=1;}out[b.toLocaleDateString('en-CA',{timeZone:'Europe/London'})]=1;return out;}
function siteNt(name){return NT.filter(function(n){return n.beach===name;});}
html+='<div class="permbar"><b>Kite permission</b> '+(NM.error?'<span class="none">could not be checked this time ('+NM.error+').</span>':NT.length?(NT.length===1?'is published for one of our beaches.':'is published for '+NT.length+' of our beaches.'):'<span class="none">none published for our beaches yet.</span>')+' <a href="https://notaminfo.com/nationalmap" target="_blank" rel="noopener">Open the NOTAM map</a>' 
  +NT.map(function(n){return '<div class="pi"><b>'+n.beach+'</b>, '+n.ref+', '+ntDate(n.from)+' to '+ntDate(n.to)+(ntFt(n.text)?', up to '+ntFt(n.text):'')+'</div>';}).join('')+'</div>';
var WK=D.weekend||{days:[]};
function wkWord(p){return p>=50?'Worth applying':p>=30?'A coin flip':p>=10?'A long shot':'No real chance';}
function wkCls(p){return p>=50?'hi':p>=30?'mid':'lo';}
html+='<div class="wk">'+(WK.days.length?WK.days.map(function(d){
  var top=d.rows.filter(function(r){return r.p>=3||r.p6>=10;}).slice(0,2),best=d.rows[0]||{p:0};
  var ap=d.apply_in>0?'Apply by '+d.apply:d.apply_in===0?'Apply today':'Past the two-day deadline';
  return '<div class="wkd"><div class="wkh"><b>'+d.name+'</b><span class="wkap'+(d.apply_in<0?' late':'')+'">'+ap+'</span></div>'
    +'<div class="wkv '+wkCls(best.p)+'">'+(top.length?wkWord(best.p)+' at '+best.b:'No beach has a real chance')+'</div>'
    +top.map(function(r){return '<div class="wkr" title="'+Object.keys(r.by).map(function(k){return k+' '+r.by[k]+'%';}).join(', ')+'"><span class="wkn">'+r.b+'</span><span class="wkt"><i class="'+wkCls(r.p)+'" style="width:'+Math.max(2,r.p)+'%"></i></span><b>'+r.p+'%</b><span class="wks">centres '+r.lo+' to '+r.hi+'%, 6 hours+ '+r.p6+'%</span></div>';}).join('')
    +'</div>';}).join('')+'<div class="wkf">Odds of a full offshore day (9+ good hours) from 140 runs of four weather centres. "Centres" is how far they disagree; "6 hours+" is the odds of a shorter session'+(WK.asof?', worked out '+new Date(WK.asof).toLocaleString('en-GB',{weekday:'short',hour:'2-digit',minute:'2-digit',timeZone:'Europe/London'}):'')+'.'+(WK.error?' The latest update failed, so these are the previous figures.':'')+'</div>'
  :'<div class="wkf">Weekend odds could not be worked out this time'+(WK.error?' ('+WK.error+')':'')+'.</div>')+'</div>';
html+='<details><summary>How to read this</summary>'
+'<p><b>GO (green)</b> means the two apps you check on the day — <b>XCWeather</b> and the <b>Met Office</b> — <b>both</b> forecast a full offshore day. <b>maybe (amber)</b> means they split: one says go, one says no — the cell shows which one. Grey means neither.</p>'
+'<p><b>☔ wet (amber)</b> means the wind call stands — both apps agree — but one of them forecasts '+D.th.wet_mm+'mm+ of rain for '+D.th.wet_hours+'+ of the flying hours, so it&#39;s not a day to drive to. Rain past about day 8 comes from XC (GFS) alone; the Met Office model doesn&#39;t reach that far.</p>'
+'<p><b>A good day</b> = wind 11–18 mph, gusts up to 26, blowing <b>offshore</b> (out to sea so kites fly over water), for <b>at least 9 hours</b> between 8am and 8pm — a full day, because it&#39;s only worth leaving work for a full day, not a lucky couple of hours.</p>'
+'<p><b>Plan early, commit late.</b> A third model (ECMWF) rides along silently — tap any day to see all three. Summer winds are light; this fills with green from October to spring.</p></details></div>';
var dhCols=D.sites[0].d.filter(function(d){return d.ld>=0&&d.ld<=MAXLD;});
html+='<div class="cols"><div class="colL"><div class="board"><div class="dayhead"><div class="cname"><span class="widehint"><span class="lg"><i style="height:14px"></i><i style="height:9px"></i></span><span>Bars: good hours from<br>XCWeather and Met Office</span></span></div><div class="strip7">'+dhCols.map(function(d){return '<div class="dh'+((d.wd==='Sat'||d.wd==='Sun')?' we':'')+(d.ld===0?' td':'')+'"><b>'+(d.ld===0?'Today':d.wd)+'</b><span>'+d.dd.split(' ')[0]+'</span></div>';}).join('')+'</div><div class="dhchev"></div></div>';
D.sites.forEach(function(s,i){
  var firm=s.d.filter(function(d){return d.ld>=0&&d.ld<=MAXLD;}),cells="",pd={};
  siteNt(s.n).forEach(function(n){var x=ntDays(n);for(var k in x)pd[k]=1;});
  firm.forEach(function(d){var k=vcls(d.v);var xh=d.xc?d.xc.hours:0,mh=d.met?d.met.hours:0,lab=d.v==='no'?'':cellTxt(d).replace('?','');cells+='<div class="dc v-'+k+(d.ld>7?' out':'')+(pd[dIso(d)]?' perm':'')+'" onclick="pwOpen(event,'+i+','+d.ld+')" title="'+d.wd+' '+d.dd+': XCWeather '+xh+' good hours, Met Office '+mh+'">'+'<span class="lab">'+lab+'</span><span class="bars"><i class="'+(xh>=9?'f':'')+'" style="height:'+Math.round(xh/13*100)+'%"></i><i class="'+(mh>=9?'f':'')+'" style="height:'+Math.round(mh/13*100)+'%"></i></span></div>';});
  html+='<div class="card" id="card'+i+'"><div class="chead" onclick="pwTog('+i+')"><div><div class="cname">'+s.n+(siteNt(s.n).length?'<span class="nbadge">NOTAM</span>':'')+'</div><span class="csea">faces '+s.fc+'</span></div><div class="strip7">'+cells+'</div><span class="chev"></span></div><div class="panel" id="panel'+i+'"></div></div>';
});
html+='</div></div><div class="colR" id="side"></div></div>';
root.innerHTML=html;
if(WIDE){var cl=root.querySelector('.colL');cl.insertBefore(root.querySelector('.hero'),cl.firstChild);cl.insertBefore(root.querySelector('.permbar'),cl.children[1]);cl.insertBefore(root.querySelector('.wk'),cl.children[2]);cl.appendChild(root.querySelector('details'));}
function bestFirm(s){var f=s.d.filter(function(d){return d.ld>=0&&d.ld<=7;});return f.reduce(function(a,d){return dscore(d)>dscore(a)?d:a;},f[0]);}
function windColor(v){if(v==null)return '#eee';return v<9?'#bfeaf5':v<13?'#d6f2f8':v<19?'#b2ecb0':v<25?'#f6f29a':v<32?'#f8cfa6':v<39?'#f4a994':'#ee8585';}
function tempColor(t){if(t==null)return '#f3efe6';return t<5?'#d6e9f5':t<10?'#e3ecb8':t<16?'#e6dd82':t<19?'#ebc97c':t<22?'#e8b56c':t<26?'#e5a062':'#e08656';}
function wIcon(c){c=c||0;if(c===0)return '☀';if(c<=2)return '⛅';if(c===3)return '☁';if(c>=45&&c<=48)return '🌫';if(c>=51&&c<=67)return '🌦';if(c>=71&&c<=77)return '🌨';if(c>=80&&c<=82)return '🌧';if(c>=95)return '⛈';return '☁';}
function angd(a,b){return Math.abs(((a-b+180)%360)-180);}
function goodHr(s,w,g,dr){if(w==null||g==null||w<D.th.mean_min||w>D.th.mean_max||g>D.th.gust_max)return false;if(s.face==null||dr==null)return true;return angd((dr+180)%360,s.face)<=D.th.offshore_arc;}
var SRC='xc',CURI=null,CURLD=null;
window.pwSrc=function(v){SRC=v;if(CURI!==null)pwDay(CURI,CURLD);};
function winBlock(s,day){
  if(!day){return '<div class="muted">No forecast for this day.</div>';}
  var rows="",gh=[],DET=(SRC==='met'?day.detm:day.det);
  (DET||[]).forEach(function(r){
    var h=r[0],w=r[1],g=r[2],dr=r[3],tp=r[4],rn=r[5],wc=r[6],gd=goodHr(s,w,g,dr);
    var inw=h>=D.th.hour_start&&h<=D.th.hour_end;
    if(gd&&inw)gh.push(h);
    rows+='<tr class="'+(gd?'gd':'')+(inw?'':' off')+'"><td class="tm">'+(h<10?'0'+h:h)+':00</td>'
      +'<td class="ar"><span style="transform:rotate('+((dr+180)%360)+'deg)">↑</span></td>'
      +'<td style="background:'+windColor(w)+'">'+(w==null?'–':w+' mph')+'</td>'
      +'<td class="to">to</td>'
      +'<td style="background:'+windColor(g)+'">'+(g==null?'–':g+' mph')+'</td>'
      +'<td style="background:'+tempColor(tp)+'">'+(tp==null?'–':tp+' °C')+'</td>'
      +'<td class="rn'+(rn>0?' wetc':'')+'">'+(rn>0?rn:'0')+' mm</td><td class="ic">'+wIcon(wc)+'</td></tr>';
  });
  var tog='<span class="srcsw"><button class="'+(SRC==='xc'?'on':'')+'" onclick="pwSrc(\'xc\')">XCWeather</button><button class="'+(SRC==='met'?'on':'')+'" onclick="pwSrc(\'met\')">Met Office</button></span>';
  var tbl=!DET?'<div class="xcw"><div class="xcday">'+day.wd+' '+day.dd+tog+'</div></div><div class="muted" style="margin:8px 0">No '+(SRC==='met'?'Met Office':'XCWeather')+' hour-by-hour numbers for this day.</div>':'<div class="xcw"><div class="xcday">'+day.wd+' '+day.dd+' <small>BST</small>'+tog+'</div><table>'+rows+'</table></div><div class="xckey">Green bar on the time = a good hour (11–18 mph, gust up to 26, blowing offshore). Darker grey times are outside 8am–8pm, shown but not counted in the verdict. Arrow shows where the wind is going.</div>';
  var pk=day.pk||{},sum;
  var rt=rainTxt(day),rsuf=rt?' · <b'+(day.v==='wet'?' style="color:#9a6b12"':'')+'>'+rt+'</b>':'';
  if(!DET){sum='';}
  else if(gh.length){var a=Math.min.apply(null,gh),b=Math.max.apply(null,gh);sum='<div class="wsum">Good from <b>'+hl(a)+'m to '+hl(b+1)+'m</b>, '+(pk.mph||'?')+' mph gusting '+(pk.gust||'?')+', wind from the '+(pk.from||'?')+'.'+(rt?' <b'+(day.v==='wet'?' style="color:#a36a00"':'')+'>'+rt.charAt(0).toUpperCase()+rt.slice(1)+'.</b>':'')+'</div>';}
  else{sum='<div class="wsum muted">No good hours on this day: too light, too strong, or blowing the wrong way.</div>';}
  function mrow(lbl,rd,silent){var go=rd&&rd.go,h=rd?rd.hours:0;
    return '<div><span style="min-width:88px">'+lbl+(silent?' <span style="color:#a9a090">·watching</span>':'')+'</span>'
      +'<b style="color:'+(go?'#0b7a3b':'#8592ad')+'">'+(go?'Full day, '+h+' h':'Only '+h+' h')+'</b></div>';}
  var msg=day.v==='go'?'Both your apps agree — the trustworthy call.'
         :day.v==='wet'?('Both your apps agree on the wind — but it rains: '+rainTxt(day)+'. Your call whether the group minds.')
         :day.v==='split'?('Your two apps disagree — a coin-flip, your judgement call.')
         :'Neither app gives a full offshore day.';
  if((day.v==='go'||day.v==='wet')&&day.ec&&!day.ec.go)msg+=' ECMWF is the lone holdout — logged.';
  var conf='<div class="blk"><div class="blkh" style="display:block">the two apps you check — plus a silent watcher</div><div class="conf">'
   +mrow('XC (GFS)',day.xc,false)+mrow('Met Office',day.met,false)+mrow('ECMWF',day.ec,true)
   +'<div style="color:#8a8170;margin-top:6px">'+msg+'</div></div></div>';
  return sum+tbl+conf;
}
function panelHTML(i){
  var s=D.sites[i],sel=bestFirm(s);
  var fg=s.d.filter(function(d){return d.ld>=0&&d.ld<=7&&d.v==='go';});
  var wt=s.d.filter(function(d){return d.ld>=0&&d.ld<=7&&d.v==='wet';});
  var mb=s.d.filter(function(d){return d.ld>=0&&d.ld<=7&&d.v==='split';});
  var verdict=fg.length?('Both apps agree on <b>'+fg[0].wd+' '+fg[0].dd+'</b>'+(fg.length>1?', also '+fg.slice(1).map(function(d){return d.wd;}).join(', '):'')+' — go.')
    :wt.length?('Both apps agree on the wind for <b>'+wt[0].wd+' '+wt[0].dd+'</b>, but it rains ('+rainTxt(wt[0])+') — your call.')
    :mb.length?('No day both apps agree this week. Closest: <b>'+mb[0].wd+' '+mb[0].dd+'</b> — only '+(which(mb[0])[0]||'one')+' likes it, your call.')
    :'No offshore full-day here in the next 7 days — the lightest stretch of summer.';
  var note='<div class="blk"><div class="blkh" style="display:block">why this beach, this wind</div><div class="note">This beach faces the open sea to the <b>'+s.fc+'</b>. You need wind blowing that way (out to sea), i.e. <b>from the '+s.off_from+'</b> side — that keeps cut kites over open water, off the beach. Grey days are usually windy but blowing along the shore or onshore.</div></div>';
  CURI=i;CURLD=sel.ld;
  var chips='<div class="blk"><div class="blkh">pick a day</div><div class="chips" id="chips'+i+'">'+s.d.filter(function(d){return d.ld>=0&&d.ld<=MAXLD;}).map(function(d){return '<div class="chip'+(d.ld===sel.ld?' on':'')+'" onclick="pwDay('+i+','+d.ld+')">'+(d.ld===0?'Today':d.wd)+' '+cellTxt(d)+'</div>';}).join('')+'</div><div id="win'+i+'">'+winBlock(s,sel)+'</div></div>';
  var bars="";
  s.d.filter(function(d){return d.ld>=1;}).forEach(function(d){
    var hp=(d.v==='go'?40:d.v==='wet'?32:d.v==='split'?24:5)+2,firm=d.ld<=7;
    var col=d.v==='go'?"#12a150":(d.v==='wet'||d.v==='split')?"#f5a300":"#c3cddd";
    var lab={go:'both agree',wet:'agreed but wet',split:'split',no:'no window'}[d.v];
    bars+='<div class="sb" title="'+d.wd+' '+d.dd+': '+lab+'"><div class="sbar" style="height:'+hp+'px;background:'+col+';opacity:'+(firm?.9:.4)+'"></div><div class="sl">'+d.wd[0]+'</div></div>';
  });
  var strip='<div class="blk"><div class="blkh" style="display:block">next two weeks — solid = firm, faded = rough outlook</div><div class="strip">'+bars+'</div></div>';
  return '<div class="verdict">'+verdict+'</div>'+chips+note+strip;
}
function showSide(i,ld){var s=D.sites[i],pn=siteNt(s.n).map(function(n){return '<div class="permbar" style="margin:8px 0 4px"><b>Permission '+n.ref+'</b>, '+ntDate(n.from)+' to '+ntDate(n.to)+(ntFt(n.text)?', up to '+ntFt(n.text):'')+'<div class="pi" style="font-size:12.5px;color:#4a5878">'+n.text+'</div></div>';}).join('');document.getElementById("side").innerHTML='<div class="sidehd">'+s.n+'<span>Faces '+s.fc+'. A wind from the '+s.off_from+' blows out to sea.</span></div>'+pn+panelHTML(i);document.querySelectorAll(".card").forEach(function(c,k){c.classList.toggle("sel",k===i);});if(ld!=null)pwDay(i,ld);}
window.pwTog=function(i){if(WIDE){showSide(i,null);return;}var c=document.getElementById("card"+i),open=c.classList.contains("open");if(!open){if(!document.getElementById("panel"+i).innerHTML){document.getElementById("panel"+i).innerHTML=panelHTML(i);}c.classList.add("open");}else{c.classList.remove("open");}};
window.pwOpen=function(e,i,ld){e.stopPropagation();if(WIDE){showSide(i,ld);return;}var c=document.getElementById("card"+i);if(!document.getElementById("panel"+i).innerHTML){document.getElementById("panel"+i).innerHTML=panelHTML(i);}c.classList.add("open");pwDay(i,ld);};
window.pwDay=function(i,ld){CURI=i;CURLD=ld;var s=D.sites[i],day=s.d.filter(function(d){return d.ld===ld;})[0],w=document.getElementById("win"+i);if(w)w.innerHTML=winBlock(s,day);var ch=document.getElementById("chips"+i);if(ch){ch.querySelectorAll(".chip").forEach(function(x){x.classList.remove("on");});var idx=s.d.filter(function(d){return d.ld>=0&&d.ld<=MAXLD;}).findIndex(function(d){return d.ld===ld;});if(idx>=0)ch.children[idx].classList.add("on");}};
function median(a){a=a.slice().sort(function(x,y){return x-y;});return a.length?a[Math.floor(a.length/2)]:null;}
function circMean(arr){var x=0,y=0,n=0;arr.forEach(function(d){if(d!=null){x+=Math.cos(d*Math.PI/180);y+=Math.sin(d*Math.PI/180);n++;}});return n?(Math.atan2(y,x)*180/Math.PI+360)%360:null;}
function dayByLd(s,ld){return s.d.filter(function(d){return d.ld===ld;})[0];}
function genDir(day){return (day&&day.det)?circMean(day.det.map(function(r){return r[3];})):null;}
function genSpd(day){return (day&&day.det)?median(day.det.map(function(r){return r[1];}).filter(function(v){return v!=null;})):null;}
function winSum(s,day){if(!day||!day.det)return '';var gh=day.det.filter(function(r){return goodHr(s,r[1],r[2],r[3]);});if(!gh.length)return 'no offshore window';var hs=gh.map(function(r){return r[0];}),pk=day.pk||{};return hl(Math.min.apply(null,hs))+'–'+hl(Math.max.apply(null,hs)+1)+' · '+(pk.mph||genSpd(day))+' mph, gust '+(pk.gust||'?');}
var MAP=null,MARKERS=[],MAPLD=null;
function bestFirmLd(){var best=0,bp=-1;D.sites.forEach(function(s){s.d.forEach(function(d){if(d.ld>=0&&d.ld<=7){var sc=dscore(d);if(sc>bp){bp=sc;best=d.ld;}}});});return best;}
function buildMapDays(){document.getElementById('mapdays').innerHTML=D.sites[0].d.filter(function(d){return d.ld>=0&&d.ld<=7;}).map(function(d){return '<div class="chip'+(d.ld===MAPLD?' on':'')+'" onclick="pwMapDay('+d.ld+')">'+(d.ld===0?'Today':d.wd)+' '+d.dd+'</div>';}).join('');}
function mkHTML(d,deg){return '<div class="mk mk-'+vcls(d.v)+'"><span class="mka" style="transform:rotate('+deg+'deg)">↑</span><span class="mkp">'+mkTxt(d)+'</span></div>';}
function drawMarkers(){MARKERS.forEach(function(m){MAP.removeLayer(m);});MARKERS=[];D.sites.forEach(function(s,i){var day=dayByLd(s,MAPLD);if(!day)return;var dir=genDir(day),toward=dir==null?0:(dir+180)%360;var icon=L.divIcon({className:'mkwrap',html:mkHTML(day,toward),iconSize:[40,40],iconAnchor:[20,20]});var mk=L.marker([s.lat,s.lon],{icon:icon}).addTo(MAP);var lab=day.v==='go'?'GO — both agree':day.v==='wet'?('☔ wet — '+rainTxt(day)):day.v==='split'?('maybe — '+(which(day)[0]||'one')+' only'):'no fly window';mk.bindPopup('<div class="lpop"><b>'+s.n+'</b><br>'+lab+(day.v==='no'?'':' · '+winSum(s,day))+'<br>faces '+s.fc+' · <a href="#" onclick="pwGoCard('+i+');return false;">hourly →</a></div>');MARKERS.push(mk);});}
window.pwMapDay=function(ld){MAPLD=ld;buildMapDays();if(MAP)drawMarkers();};
function fitMap(){if(MAP)MAP.fitBounds(L.latLngBounds(D.sites.map(function(s){return [s.lat,s.lon];})),{padding:[40,40]});}
function initMap(){if(MAP)return;MAPLD=MAPLD||bestFirmLd();MAP=L.map('lmap',{scrollWheelZoom:true,wheelPxPerZoomLevel:90}).setView([51.6,0.6],7);L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',maxZoom:18}).addTo(MAP);buildMapDays();drawMarkers();fitMap();}
window.pwGoCard=function(i){pwShowSec('forecast');if(WIDE){showSide(i,null);return;}var c=document.getElementById('card'+i);if(!document.getElementById('panel'+i).innerHTML){document.getElementById('panel'+i).innerHTML=panelHTML(i);}c.classList.add('open');c.scrollIntoView({block:'start'});};
var LIVEI=null;
function liveSrc(st){return 'https://embed.windy.com/embed2.html?lat='+st.lat+'&lon='+st.lon+'&detailLat='+st.lat+'&detailLon='+st.lon+'&zoom=8&level=surface&overlay=wind&product=ecmwf&menu=&message=true&marker=true&calendar=now&pressure=&type=map&location=coordinates&detail=true&metricWind=mph&metricTemp=%C2%B0C&radarRange=-1';}
window.pwLive=function(i){LIVEI=i;document.getElementById('livebeaches').innerHTML=D.sites.map(function(st,k){return '<div class="chip'+(k===i?' on':'')+'" onclick="pwLive('+k+')">'+st.n+'</div>';}).join('');document.getElementById('livewrap').innerHTML='<iframe width="100%" height="100%" style="border:0" loading="lazy" src="'+liveSrc(D.sites[i])+'"></iframe>';};
function pwShowSec(name){['forecast','live'].forEach(function(n){document.getElementById('sec-'+n).classList.toggle('on',n===name);});document.querySelectorAll('.nb').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-s')===name);});if(name==='live'&&LIVEI===null){var bi=0;D.sites.forEach(function(st,k){if(D.best&&st.n===D.best.s)bi=k;});pwLive(bi);}}
if(WIDE){var bi=0,bld=null;D.sites.forEach(function(s,k){if(D.best&&s.n===D.best.s){bi=k;s.d.forEach(function(d){if(d.dd===D.best.dd)bld=d.ld;});}});showSide(bi,bld);}
document.querySelectorAll('.nb').forEach(function(b){b.addEventListener('click',function(){pwShowSec(b.getAttribute('data-s'));});});
'''

head = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Patang Wind — beach planner</title>'
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600..800&family=Hanken+Grotesk:wght@400;500;600;700&display=swap">'
        ''
        '<style>' + CSS + '</style></head><body><div class="wrap">'
        '<header class="bar"><div class="brand"><svg viewBox="0 0 26 32" aria-hidden="true"><path d="M13 1 L13 14 L3 14 Z" fill="#e0245e"/><path d="M13 1 L23 14 L13 14 Z" fill="#f5a300"/><path d="M3 14 L13 14 L13 28 Z" fill="#f5a300"/><path d="M23 14 L13 14 L13 28 Z" fill="#e0245e"/><path d="M13 28 L10.5 32 L15.5 32 Z" fill="#12a150"/></svg><h1>Patang Wind</h1></div>'
        '<div class="nav"><button class="nb on" data-s="forecast">Forecast</button><button class="nb" data-s="live">Wind map</button></div>'
        '<div class="upd">Updated ' + data["g"] + ('<span>' + data["src"].replace(" | ", ". ") + '</span>' if data.get("src") else '') + '</div></header>'
        ''
        
        '<div id="sec-forecast" class="sec on"><div id="pwroot"></div></div>'
        '<div id="sec-live" class="sec"><div class="chips" id="livebeaches" style="margin-bottom:10px"></div><div id="livewrap"></div>'
        '<p class="maplegend" style="margin-top:8px">Windy&#39;s own map and forecast. Pick a beach above: the strip at the bottom shows its dates and every hour&#39;s wind, gusts and direction (arrows). Drag the time bar to move the map through the days.</p></div>'
        '<p class="foot">Each day is judged on the two apps you check, using the numbers they show: the '
        '<b>XCWeather</b> column is NOAA&#39;s GFS model on the same 0.25&deg; grid XCWeather draws from, and the '
        '<b>Met Office</b> column is the Met Office&#39;s own blended site forecast (their open data). GREEN only when both '
        'agree it&#39;s a full offshore day (9+ hrs of 8am&ndash;8pm); amber when they split. The hourly table shows '
        'either app&#39;s numbers (switch above it) from 5am to 9pm; only 8am&ndash;8pm counts. An agreed day still '
        'drops to <b>&#9748; wet</b> when either forecasts ' + str(data["th"]["wet_mm"]) + 'mm+ of rain for '
        + str(data["th"]["wet_hours"]) + '+ of the flying hours (rain still comes via <a href="https://open-meteo.com">Open-Meteo</a>). '
        'ECMWF rides along silently so we can later check whose call comes true at each beach. '
        'Gusts are the least certain part — read it as a ranking, not a promise. Updates every 4 hours.</p>'
        '<p class="foot" style="margin-top:8px">Data: Met Office site forecasts &copy; Crown copyright, Met Office, licensed under <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> (from the Met Office open data on AWS). GFS forecasts from NOAA/NCEP. Rain and the ECMWF watcher via <a href="https://open-meteo.com">Open-Meteo</a> (CC BY 4.0). Wind map by <a href="https://www.windy.com">Windy</a>.</p>'
        '</div>')
foot = '<script>\nconst D=' + json.dumps(data, separators=(",", ":")) + ';\n(function(){' + JS + '})();\n</script></body></html>'

open(os.path.join(ROOT, "docs", "prototype.html"), "w").write(head + foot)
print("wrote docs/prototype.html |", os.path.getsize(os.path.join(ROOT, "docs", "prototype.html")), "bytes")
