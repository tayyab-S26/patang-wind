#!/usr/bin/env python3
"""Generate a standalone, interactive prototype page (docs/prototype.html) from
the rich dataset. Self-contained (own warm theme, no external deps). Separate
from the live index.html so both can be compared at different links.
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
RICH = os.path.join(ROOT, "rich.json")
data = json.load(open(RICH))

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#fbf8f1;color:#26211a;font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;-webkit-text-size-adjust:100%;font-variant-numeric:tabular-nums}
.wrap{max-width:760px;margin:0 auto;padding:22px 14px 70px}
.top{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
h1{font-size:22px;font-weight:600;margin:0}
.tag{font-size:11px;color:#9a7b16;background:#f7efd6;border:1px solid #e6d6a6;border-radius:20px;padding:2px 9px}
.sub{color:#8a8170;font-size:13px;margin:3px 0 16px}
.hero{display:flex;align-items:center;gap:16px;background:#fff;border:2px solid #c9a227;border-radius:14px;padding:14px 16px;margin-bottom:10px}
.hlbl{font-size:12px;color:#5c5446}
.hsite{font-size:18px;font-weight:500}
.hmeta{font-size:13px;color:#5c5446;margin-top:1px}
.hnum{margin-left:auto;text-align:right;line-height:1}
.hnum b{font-family:Georgia,'Times New Roman',serif;font-size:40px;font-weight:500;color:#2f7d3f}
.hnum span{display:block;font-size:11px;color:#8a8170}
details{background:#f4efe6;border-radius:10px;padding:6px 14px;margin-bottom:16px;font-size:14px}
summary{cursor:pointer;font-size:13px;color:#5c5446;padding:5px 0}
details p{margin:7px 0;color:#5c5446;line-height:1.6}
.card{border:1px solid #e7ded0;border-radius:12px;margin-bottom:8px;background:#fff;overflow:hidden}
.chead{display:flex;align-items:center;gap:10px;padding:11px 13px;cursor:pointer}
.chead:hover{background:#faf6ec}
.cname{font-weight:600;font-size:14.5px;min-width:96px}
.csea{font-size:11px;color:#8a8170;display:block;font-weight:400}
.strip7{display:flex;gap:3px;margin-left:auto}
.dc{width:32px;height:32px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;cursor:pointer}
.dayhead{display:flex;align-items:center;gap:10px;padding:2px 13px 6px}
.dayhead .cname{min-width:96px}
.dh{width:32px;display:flex;flex-direction:column;align-items:center;line-height:1.12}
.dh b{font-size:10px;font-weight:600;color:#8a8170}
.dh span{font-size:9px;color:#b3a892}
.dhchev{width:10px;flex:none}
.chev{width:0;height:0;border-left:5px solid transparent;border-right:5px solid transparent;border-top:6px solid #b3a892;transition:transform .15s;flex:none}
.card.open .chev{transform:rotate(180deg)}
.panel{display:none;padding:2px 14px 16px;border-top:1px solid #f0e8d9}
.card.open .panel{display:block}
.verdict{font-size:14px;margin:13px 0 14px;line-height:1.55}
.blk{margin:15px 0}
.blkh{font-size:12px;color:#8a8170;margin-bottom:8px;text-transform:uppercase;letter-spacing:.03em}
.chips{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:12px}
.chip{border:1px solid #e7ded0;border-radius:8px;padding:5px 9px;font-size:12px;cursor:pointer;color:#5c5446;background:#faf6ec}
.chip.on{border-color:#c9a227;color:#9a7b16;background:#f7efd6;font-weight:600}
.hours{display:flex;align-items:flex-end;gap:4px;height:70px}
.hb{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:3px}
.hbar{width:100%;max-width:20px;border-radius:3px 3px 0 0}
.hl{font-size:10px;color:#a59c8a}
.wsum{font-size:13.5px;margin-top:10px}
.conf div{display:flex;align-items:center;gap:8px;margin:4px 0;font-size:12.5px;color:#5c5446}
.cftrk{flex:1;height:9px;border-radius:5px;background:#f0e8d9}
.cfbar{height:9px;border-radius:5px;background:#2f7d3f;min-width:2px}
.note{font-size:13px;color:#5c5446;line-height:1.6;background:#f4efe6;border-radius:9px;padding:11px 13px}
.strip{display:flex;align-items:flex-end;gap:3px;height:52px}
.sb{flex:1;display:flex;flex-direction:column;align-items:center;gap:2px}
.sbar{width:100%;max-width:18px;border-radius:2px 2px 0 0;min-height:2px}
.sl{font-size:10px;color:#a59c8a}
.muted{color:#8a8170;font-size:13px}
.foot{color:#8a8170;font-size:12px;margin-top:26px;line-height:1.7}
.foot a{color:#5c5446}
.xcw{overflow-x:auto;margin:8px 0 10px;border-radius:8px;border:1px solid #e3e3e3}
.xcday{background:#f1f1f1;padding:9px 12px;font-size:19px;color:#222;display:flex;align-items:baseline;gap:6px;border-bottom:1px solid #e0e0e0}
.xcday small{font-size:11px;color:#8a8a8a}
.xcday em{margin-left:auto;font-style:normal;font-size:11px;color:#8a8a8a}
.srcsw{margin-left:auto;display:flex;border:1px solid #cfcfcf;border-radius:8px;overflow:hidden}
.srcsw button{border:0;background:#fff;color:#555;font-size:12.5px;padding:5px 11px;cursor:pointer}
.srcsw button.on{background:#26211a;color:#fbf8f1;font-weight:600}
.xcw table{border-collapse:collapse;width:100%;font-size:16px;background:#fff}
.xcw td{padding:0 6px;height:40px;text-align:center;white-space:nowrap;border-top:2px solid #fff}
.xcw td.tm{background:#ececec;color:#333;text-align:left;padding-left:10px;width:78px;font-variant-numeric:tabular-nums}
.xcw td.ar{width:52px}
.xcw td.ar span{display:inline-block;color:#3d2bb3;font-weight:900;font-size:26px;line-height:1}
.xcw td.to{color:#b9b9b9;font-size:12px;width:26px;padding:0}
.xcw td.rn{color:#333}
.xcw td.rn.wetc{background:#e6f9fd}
.xcw td.ic{font-size:21px;width:48px}
.xcw tr.gd td.tm{box-shadow:inset 5px 0 0 #2f7d3f;font-weight:700;color:#1f6a30}
.xcw tr.gd td.ar span{color:#1f8a36}
.xcw tr.off td.tm{background:#d6d6d6}
.xckey{font-size:11.5px;color:#8a8170;margin:-2px 0 10px}
@media (max-width:430px){.xcw table{font-size:14px}.xcw td{height:34px;padding:0 3px}.xcw td.tm{width:58px;padding-left:6px}.xcw td.ar{width:34px}.xcw td.ar span{font-size:20px}.xcw td.ic{width:30px;font-size:17px}}
.nav{display:flex;gap:6px;margin:4px 0 16px}
.nb{border:1px solid #e7ded0;background:#fff;border-radius:9px;padding:7px 15px;font-size:13.5px;color:#5c5446;cursor:pointer}
.nb.on{background:#26211a;color:#fbf8f1;border-color:#26211a}
.sec{display:none}
.sec.on{display:block}
#lmap{height:60vh;min-height:380px;border-radius:12px;border:1px solid #e7ded0}
#livewrap{height:80vh;min-height:520px;border-radius:12px;overflow:hidden;border:1px solid #e7ded0;background:#eaf0f4}
.maplegend{font-size:12px;color:#8a8170;margin-top:8px;line-height:1.5}
.mkwrap{background:transparent;border:0}
.mk{width:40px;height:40px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.3)}
.mk .mka{font-size:13px;line-height:1;color:#fff;opacity:.92}
.mk .mkp{font-size:12px;line-height:1.1;font-weight:700;color:#fff}
.mk-hi{background:#2f7d3f}.mk-mid{background:#cf9518}.mk-lo{background:#a9a090}
.lpop b{font-size:14px}.lpop a{color:#2f7d3f;font-weight:600}
.leaflet-container{font:13px -apple-system,BlinkMacSystemFont,sans-serif}
.colR{display:none}
.dc small{display:none}
.widehint{display:none}
@media (min-width:1100px){
  .wrap{max-width:none;padding:22px 32px 70px}
  .colL .hero{margin-bottom:12px}
  .colL details{margin-top:14px}
  #side .verdict{margin:6px 0 8px}
  #side .blk{margin:8px 0}
  #side .blkh{display:none}
  #side .chips{margin-bottom:8px;gap:4px}
  #side .chip{padding:4px 7px;font-size:11.5px}
  #side .wsum{margin:0 0 6px}
  #side .xcw{margin:6px 0 8px}
  #side .xcw td{height:32px}
  #side .xcw table{font-size:15px}
  #side .xcday{padding:6px 12px;font-size:17px}
  .cols{display:grid;grid-template-columns:minmax(780px,1.15fr) minmax(0,1fr);gap:18px;align-items:start}
  .colL,.colR{min-width:0}
  .colR{display:block;position:sticky;top:14px;background:#fff;border:1px solid #e7ded0;border-radius:12px;padding:12px 16px 16px;max-height:calc(100vh - 28px);overflow:auto}
  .sidehd{font-size:17px;font-weight:600}
  .sidehd span{font-size:12px;color:#8a8170;font-weight:400;margin-left:6px}
  .strip7{flex:1;margin-left:14px;gap:4px}
  .chead>div:first-child,.dayhead>.cname{width:150px;min-width:150px;flex:none}
  .dc{flex:1;width:auto;min-width:36px;height:44px;flex-direction:column;line-height:1.15;font-size:13px}
  .dc small{display:block;font-size:9px;font-weight:500;opacity:.8}
  .dc.out{opacity:.62}
  .dh{flex:1;width:auto;min-width:36px}
  .dh b{font-size:11px}.dh span{font-size:10px}
  #lmap{height:74vh}
  #livewrap{height:calc(100vh - 240px);min-height:560px}
  .card.sel{border-color:#c9a227;box-shadow:0 0 0 1px #c9a227}
  .chev,.dhchev{display:none}
  .widehint{display:block;font-size:10px;color:#a59c8a;font-weight:400}
}
@media (min-width:1600px){#side .chips{flex-wrap:nowrap}#side .chip{flex:1;text-align:center;white-space:nowrap;padding:4px 3px}}
@media (max-width:430px){
  .chead{gap:7px;padding:11px 10px}
  .dayhead{gap:7px;padding:2px 10px 6px}
  .cname{min-width:76px;font-size:13px}
  .csea{font-size:10.5px}
  .strip7{gap:2px}
  .dc{width:26px;height:26px;font-size:10px;border-radius:5px}
  .dh{width:26px}
  .dh b{font-size:9px}
  .dh span{font-size:8px}
}
"""

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
html+='<div class="heads"><div class="hero"><div><div class="hlbl">best full-day this week</div><div class="hsite">'+b.s+'</div><div class="hmeta">'+b.wd+' '+b.dd+' · '+b.mph+' mph, gust '+b.gust+' · wind '+b.frm+' (offshore)</div></div><div class="hnum"><b style="color:'+(b.v==='go'?'#2f7d3f':'#c98f12')+'">'+hbadge+'</b><span>'+hnote+'</span></div></div>';
html+='<details><summary>How to read this — tap to open</summary>'
+'<p><b>GO (green)</b> means the two apps you check on the day — <b>XCWeather</b> and the <b>Met Office</b> — <b>both</b> forecast a full offshore day. <b>maybe (amber)</b> means they split: one says go, one says no — the cell shows which one. Grey means neither.</p>'
+'<p><b>☔ wet (amber)</b> means the wind call stands — both apps agree — but one of them forecasts '+D.th.wet_mm+'mm+ of rain for '+D.th.wet_hours+'+ of the flying hours, so it&#39;s not a day to drive to. Rain past about day 8 comes from XC (GFS) alone; the Met Office model doesn&#39;t reach that far.</p>'
+'<p><b>A good day</b> = wind 11–18 mph, gusts up to 26, blowing <b>offshore</b> (out to sea so kites fly over water), for <b>at least 9 hours</b> between 8am and 8pm — a full day, because it&#39;s only worth leaving work for a full day, not a lucky couple of hours.</p>'
+'<p><b>Plan early, commit late.</b> A third model (ECMWF) rides along silently — tap any day to see all three. Summer winds are light; this fills with green from October to spring.</p></details></div>';
var dhCols=D.sites[0].d.filter(function(d){return d.ld>=0&&d.ld<=MAXLD;});
html+='<div class="cols"><div class="colL"><div class="dayhead"><div class="cname"><span class="widehint">small numbers = good hours<br>XC · Met Office (9+ = full day)</span></div><div class="strip7">'+dhCols.map(function(d){return '<div class="dh"><b>'+(d.ld===0?'Today':d.wd)+'</b><span>'+d.dd.split(' ')[0]+'</span></div>';}).join('')+'</div><div class="dhchev"></div></div>';
D.sites.forEach(function(s,i){
  var firm=s.d.filter(function(d){return d.ld>=0&&d.ld<=MAXLD;}),cells="";
  firm.forEach(function(d){var k=vcls(d.v);cells+='<div class="dc'+(d.ld>7?' out':'')+'" style="'+STY[k]+';font-size:12px;font-weight:700" onclick="pwOpen(event,'+i+','+d.ld+')" title="'+d.wd+' '+d.dd+'">'+cellTxt(d)+'<small>'+(d.xc?d.xc.hours:0)+'·'+(d.met?d.met.hours:0)+'</small></div>';});
  html+='<div class="card" id="card'+i+'"><div class="chead" onclick="pwTog('+i+')"><div><div class="cname">'+s.n+'</div><span class="csea">faces '+s.fc+'</span></div><div class="strip7">'+cells+'</div><span class="chev"></span></div><div class="panel" id="panel'+i+'"></div></div>';
});
html+='</div><div class="colR" id="side"></div></div>';
root.innerHTML=html;
if(WIDE){var cl=root.querySelector('.colL');cl.insertBefore(root.querySelector('.hero'),cl.firstChild);cl.appendChild(root.querySelector('details'));}
function bestFirm(s){var f=s.d.filter(function(d){return d.ld>=0&&d.ld<=7;});return f.reduce(function(a,d){return dscore(d)>dscore(a)?d:a;},f[0]);}
function windColor(v){if(v==null)return '#eee';return v<9?'#a9f3fb':v<13?'#c9f7fc':v<19?'#a6f79e':v<25?'#fbfb86':v<32?'#fbc9a0':v<39?'#f9a08c':'#f47c7c';}
function tempColor(t){if(t==null)return '#f3efe6';return t<5?'#cfe8f5':t<10?'#d9e6a8':t<16?'#d9cf5c':t<19?'#e0b85a':t<22?'#dba24c':t<26?'#d98e45':'#d7743c';}
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
  else if(gh.length){var a=Math.min.apply(null,gh),b=Math.max.apply(null,gh);sum='<div class="wsum">Fly-window <b>'+hl(a)+'–'+hl(b+1)+'</b> · '+(pk.mph||'?')+' mph, gust '+(pk.gust||'?')+' · wind '+(pk.from||'?')+' — the green rows'+rsuf+'</div>';}
  else{sum='<div class="wsum muted">No offshore in-band window this day — too light or wrong direction.</div>';}
  function mrow(lbl,rd,silent){var go=rd&&rd.go,h=rd?rd.hours:0;
    return '<div><span style="min-width:88px">'+lbl+(silent?' <span style="color:#a9a090">·watching</span>':'')+'</span>'
      +'<b style="color:'+(go?'#2f7d3f':'#a9a090')+'">'+(go?'✓ full day':'✗ only '+h+'h')+'</b></div>';}
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
    var col=d.v==='go'?"#2f7d3f":(d.v==='wet'||d.v==='split')?"#c98f12":"#b9afa0";
    var lab={go:'both agree',wet:'agreed but wet',split:'split',no:'no window'}[d.v];
    bars+='<div class="sb" title="'+d.wd+' '+d.dd+': '+lab+'"><div class="sbar" style="height:'+hp+'px;background:'+col+';opacity:'+(firm?.9:.4)+'"></div><div class="sl">'+d.wd[0]+'</div></div>';
  });
  var strip='<div class="blk"><div class="blkh" style="display:block">next two weeks — solid = firm, faded = rough outlook</div><div class="strip">'+bars+'</div></div>';
  return '<div class="verdict">'+verdict+'</div>'+chips+note+strip;
}
function showSide(i,ld){var s=D.sites[i];document.getElementById("side").innerHTML='<div class="sidehd">'+s.n+'<span>faces '+s.fc+' · offshore wind comes from the '+s.off_from+'</span></div>'+panelHTML(i);document.querySelectorAll(".card").forEach(function(c,k){c.classList.toggle("sel",k===i);});if(ld!=null)pwDay(i,ld);}
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
        '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>'
        '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
        '<style>' + CSS + '</style></head><body><div class="wrap">'
        '<div class="top"><h1>Patang Wind</h1></div>'
        '<p class="sub">UK beach game planner · updated ' + data["g"] + '</p>'
        + ('<p class="sub" style="opacity:.7;font-size:11px">' + data["src"] + '</p>' if data.get("src") else '') +
        '<div class="nav"><button class="nb on" data-s="forecast">Forecast</button><button class="nb" data-s="live">Wind map</button></div>'
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
