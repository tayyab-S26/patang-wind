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
.xcw{overflow-x:auto;margin:2px 0 8px}
.xcw table{border-collapse:collapse;width:100%;font-size:12.5px}
.xcw th{font-size:10px;color:#a59c8a;font-weight:500;text-transform:uppercase;padding:0 0 5px}
.xcw td{padding:3px 3px;text-align:center;border-top:1px solid #f2ecdf}
.xcw td.tm{color:#5c5446;font-variant-numeric:tabular-nums;text-align:left;white-space:nowrap}
.xcw td.ar span{display:inline-block;color:#3b3aa0;font-weight:700;font-size:15px;line-height:1}
.xcw .wc{display:inline-block;min-width:28px;padding:2px 5px;border-radius:5px;font-weight:600;color:#3a3320}
.xcw .tc{display:inline-block;min-width:26px;padding:2px 5px;border-radius:5px;color:#5a3a1a}
.xcw td.rn{color:#9aa0a8;font-size:11.5px}
.xcw td.ic{font-size:15px}
.xcw tr.gd td{background:#eef7ea}
.xcw tr.gd td.tm{box-shadow:inset 3px 0 0 #2f7d3f;font-weight:600;color:#2f7d3f}
.nav{display:flex;gap:6px;margin:4px 0 16px}
.nb{border:1px solid #e7ded0;background:#fff;border-radius:9px;padding:7px 15px;font-size:13.5px;color:#5c5446;cursor:pointer}
.nb.on{background:#26211a;color:#fbf8f1;border-color:#26211a}
.sec{display:none}
.sec.on{display:block}
#lmap{height:60vh;min-height:380px;border-radius:12px;border:1px solid #e7ded0}
#livewrap{height:72vh;min-height:430px;border-radius:12px;overflow:hidden;border:1px solid #e7ded0;background:#eaf0f4}
.maplegend{font-size:12px;color:#8a8170;margin-top:8px;line-height:1.5}
.mkwrap{background:transparent;border:0}
.mk{width:40px;height:40px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.3)}
.mk .mka{font-size:13px;line-height:1;color:#fff;opacity:.92}
.mk .mkp{font-size:12px;line-height:1.1;font-weight:700;color:#fff}
.mk-hi{background:#2f7d3f}.mk-mid{background:#cf9518}.mk-lo{background:#a9a090}
.lpop b{font-size:14px}.lpop a{color:#2f7d3f;font-weight:600}
.leaflet-container{font:13px -apple-system,BlinkMacSystemFont,sans-serif}
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
function vcls(v){return v==='go'?'hi':v==='split'?'mid':'lo';}
function which(d){var y=[];if(d.xc&&d.xc.go)y.push('XC');if(d.met&&d.met.go)y.push('Met');return y;}
function cellTxt(d){if(d.v==='go')return 'GO';if(d.v==='split')return (which(d)[0]||'?')+'?';return '–';}
function mkTxt(d){return d.v==='go'?'✓':d.v==='split'?'?':'–';}
function dscore(d){return (d.v==='go'?200:d.v==='split'?100:0)+((d.xc?d.xc.hours:0)+(d.met?d.met.hours:0));}
var STY={hi:"background:#e7f3e3;color:#2f7d3f",mid:"background:#fbeed4;color:#9a6b12",lo:"background:#f4efe6;color:#8a8170"};
var root=document.getElementById("pwroot");
var b=D.best,html="";
html+='<div class="hero"><div><div class="hlbl">best full-day this week</div><div class="hsite">'+b.s+'</div><div class="hmeta">'+b.wd+' '+b.dd+' · '+b.mph+' mph, gust '+b.gust+' · wind '+b.frm+' (offshore)</div></div><div class="hnum"><b style="color:'+(b.v==='go'?'#2f7d3f':'#c98f12')+'">'+(b.v==='go'?'GO':'MAYBE')+'</b><span>'+(b.v==='go'?'XC + Met Office agree':'one model only — coin-flip')+'</span></div></div>';
html+='<details><summary>How to read this — tap to open</summary>'
+'<p><b>GO (green)</b> means the two apps you check on the day — <b>XCWeather</b> and the <b>Met Office</b> — <b>both</b> forecast a full offshore day. <b>maybe (amber)</b> means they split: one says go, one says no — the cell shows which one. Grey means neither.</p>'
+'<p><b>A good day</b> = wind 11–18 mph, gusts up to 26, blowing <b>offshore</b> (out to sea so kites fly over water), for <b>at least 9 hours</b> between 8am and 8pm — a full day, because it&#39;s only worth leaving work for a full day, not a lucky couple of hours.</p>'
+'<p><b>Plan early, commit late.</b> A third model (ECMWF) rides along silently — tap any day to see all three. Summer winds are light; this fills with green from October to spring.</p></details>';
var dhCols=D.sites[0].d.filter(function(d){return d.ld>=0&&d.ld<=7;});
html+='<div class="dayhead"><div class="cname"></div><div class="strip7">'+dhCols.map(function(d){return '<div class="dh"><b>'+(d.ld===0?'Today':d.wd)+'</b><span>'+d.dd.split(' ')[0]+'</span></div>';}).join('')+'</div><div class="dhchev"></div></div>';
D.sites.forEach(function(s,i){
  var firm=s.d.filter(function(d){return d.ld>=0&&d.ld<=7;}),cells="";
  firm.forEach(function(d){var k=vcls(d.v);cells+='<div class="dc" style="'+STY[k]+';font-size:12px;font-weight:700" onclick="pwOpen(event,'+i+','+d.ld+')" title="'+d.wd+' '+d.dd+'">'+cellTxt(d)+'</div>';});
  html+='<div class="card" id="card'+i+'"><div class="chead" onclick="pwTog('+i+')"><div><div class="cname">'+s.n+'</div><span class="csea">faces '+s.fc+'</span></div><div class="strip7">'+cells+'</div><span class="chev"></span></div><div class="panel" id="panel'+i+'"></div></div>';
});
root.innerHTML=html;
function bestFirm(s){var f=s.d.filter(function(d){return d.ld>=0&&d.ld<=7;});return f.reduce(function(a,d){return dscore(d)>dscore(a)?d:a;},f[0]);}
function windColor(v){if(v==null)return '#eee';return v<10?'#d7eefb':v<=18?'#c9edcc':v<=24?'#f3e7a3':v<=31?'#f4cd92':'#e89090';}
function tempColor(t){if(t==null)return '#f3efe6';return t<10?'#eef3f7':t<15?'#fbf0d8':t<20?'#f9e3b2':t<25?'#f3cd8c':t<30?'#ecab63':'#e3884a';}
function wIcon(c){c=c||0;if(c===0)return '☀';if(c<=2)return '⛅';if(c===3)return '☁';if(c>=45&&c<=48)return '🌫';if(c>=51&&c<=67)return '🌦';if(c>=71&&c<=77)return '🌨';if(c>=80&&c<=82)return '🌧';if(c>=95)return '⛈';return '☁';}
function angd(a,b){return Math.abs(((a-b+180)%360)-180);}
function goodHr(s,w,g,dr){if(w==null||g==null||w<D.th.mean_min||w>D.th.mean_max||g>D.th.gust_max)return false;if(s.face==null||dr==null)return true;return angd((dr+180)%360,s.face)<=D.th.offshore_arc;}
function winBlock(s,day){
  if(!day||!day.det){return '<div class="muted">No hourly forecast for this day yet (beyond the sharp model range).</div>';}
  var rows="",gh=[];
  day.det.forEach(function(r){
    var h=r[0],w=r[1],g=r[2],dr=r[3],tp=r[4],rn=r[5],wc=r[6],gd=goodHr(s,w,g,dr);
    if(gd)gh.push(h);
    rows+='<tr class="'+(gd?'gd':'')+'"><td class="tm">'+(h<10?'0'+h:h)+':00</td>'
      +'<td class="ar"><span style="transform:rotate('+((dr+180)%360)+'deg)">↑</span></td>'
      +'<td><span class="wc" style="background:'+windColor(w)+'">'+(w==null?'–':w)+'</span></td>'
      +'<td><span class="wc" style="background:'+windColor(g)+'">'+(g==null?'–':g)+'</span></td>'
      +'<td><span class="tc" style="background:'+tempColor(tp)+'">'+(tp==null?'–':tp)+'°</span></td>'
      +'<td class="rn">'+(rn>0?rn+' mm':'0')+'</td><td class="ic">'+wIcon(wc)+'</td></tr>';
  });
  var tbl='<div class="xcw"><table><tr><th>time</th><th></th><th>wind</th><th>gust</th><th>°C</th><th>rain</th><th></th></tr>'+rows+'</table></div>';
  var pk=day.pk||{},sum;
  if(gh.length){var a=Math.min.apply(null,gh),b=Math.max.apply(null,gh);sum='<div class="wsum">Fly-window <b>'+hl(a)+'–'+hl(b+1)+'</b> · '+(pk.mph||'?')+' mph, gust '+(pk.gust||'?')+' · wind '+(pk.from||'?')+' — the green rows</div>';}
  else{sum='<div class="wsum muted">No offshore in-band window this day — too light or wrong direction.</div>';}
  function mrow(lbl,rd,silent){var go=rd&&rd.go,h=rd?rd.hours:0;
    return '<div><span style="min-width:88px">'+lbl+(silent?' <span style="color:#a9a090">·watching</span>':'')+'</span>'
      +'<b style="color:'+(go?'#2f7d3f':'#a9a090')+'">'+(go?'✓ full day':'✗ only '+h+'h')+'</b></div>';}
  var msg=day.v==='go'?'Both your apps agree — the trustworthy call.'
         :day.v==='split'?('Your two apps disagree — a coin-flip, your judgement call.')
         :'Neither app gives a full offshore day.';
  if(day.v==='go'&&day.ec&&!day.ec.go)msg+=' ECMWF is the lone holdout — logged.';
  var conf='<div class="blk"><div class="blkh">the two apps you check — plus a silent watcher</div><div class="conf">'
   +mrow('XC (GFS)',day.xc,false)+mrow('Met Office',day.met,false)+mrow('ECMWF',day.ec,true)
   +'<div style="color:#8a8170;margin-top:6px">'+msg+'</div></div></div>';
  return sum+tbl+conf;
}
function panelHTML(i){
  var s=D.sites[i],sel=bestFirm(s);
  var fg=s.d.filter(function(d){return d.ld>=0&&d.ld<=7&&d.v==='go';});
  var mb=s.d.filter(function(d){return d.ld>=0&&d.ld<=7&&d.v==='split';});
  var verdict=fg.length?('Both apps agree on <b>'+fg[0].wd+' '+fg[0].dd+'</b>'+(fg.length>1?', also '+fg.slice(1).map(function(d){return d.wd;}).join(', '):'')+' — go.'):(mb.length?('No day both apps agree this week. Closest: <b>'+mb[0].wd+' '+mb[0].dd+'</b> — only '+(which(mb[0])[0]||'one')+' likes it, your call.'):'No offshore full-day here in the next 7 days — the lightest stretch of summer.');
  var note='<div class="blk"><div class="blkh">why this beach, this wind</div><div class="note">This beach faces the open sea to the <b>'+s.fc+'</b>. You need wind blowing that way (out to sea), i.e. <b>from the '+s.off_from+'</b> side — that keeps cut kites over open water, off the beach. Grey days are usually windy but blowing along the shore or onshore.</div></div>';
  var chips='<div class="blk"><div class="blkh">pick a day</div><div class="chips" id="chips'+i+'">'+s.d.filter(function(d){return d.ld>=0&&d.ld<=7;}).map(function(d){return '<div class="chip'+(d.ld===sel.ld?' on':'')+'" onclick="pwDay('+i+','+d.ld+')">'+(d.ld===0?'Today':d.wd)+' '+cellTxt(d)+'</div>';}).join('')+'</div><div id="win'+i+'">'+winBlock(s,sel)+'</div></div>';
  var bars="";
  s.d.filter(function(d){return d.ld>=1;}).forEach(function(d){
    var hp=(d.v==='go'?40:d.v==='split'?24:5)+2,firm=d.ld<=7;
    var col=d.v==='go'?"#2f7d3f":d.v==='split'?"#c98f12":"#b9afa0";
    var lab={go:'both agree',split:'split',no:'no window'}[d.v];
    bars+='<div class="sb" title="'+d.wd+' '+d.dd+': '+lab+'"><div class="sbar" style="height:'+hp+'px;background:'+col+';opacity:'+(firm?.9:.4)+'"></div><div class="sl">'+d.wd[0]+'</div></div>';
  });
  var strip='<div class="blk"><div class="blkh">next two weeks — solid = firm, faded = rough outlook</div><div class="strip">'+bars+'</div></div>';
  return '<div class="verdict">'+verdict+'</div>'+chips+note+strip;
}
window.pwTog=function(i){var c=document.getElementById("card"+i),open=c.classList.contains("open");if(!open){if(!document.getElementById("panel"+i).innerHTML){document.getElementById("panel"+i).innerHTML=panelHTML(i);}c.classList.add("open");}else{c.classList.remove("open");}};
window.pwOpen=function(e,i,ld){e.stopPropagation();var c=document.getElementById("card"+i);if(!document.getElementById("panel"+i).innerHTML){document.getElementById("panel"+i).innerHTML=panelHTML(i);}c.classList.add("open");pwDay(i,ld);};
window.pwDay=function(i,ld){var s=D.sites[i],day=s.d.filter(function(d){return d.ld===ld;})[0],w=document.getElementById("win"+i);if(w)w.innerHTML=winBlock(s,day);var ch=document.getElementById("chips"+i);if(ch){ch.querySelectorAll(".chip").forEach(function(x){x.classList.remove("on");});var idx=s.d.filter(function(d){return d.ld>=0&&d.ld<=7;}).findIndex(function(d){return d.ld===ld;});if(idx>=0)ch.children[idx].classList.add("on");}};
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
function drawMarkers(){MARKERS.forEach(function(m){MAP.removeLayer(m);});MARKERS=[];D.sites.forEach(function(s,i){var day=dayByLd(s,MAPLD);if(!day)return;var dir=genDir(day),toward=dir==null?0:(dir+180)%360;var icon=L.divIcon({className:'mkwrap',html:mkHTML(day,toward),iconSize:[40,40],iconAnchor:[20,20]});var mk=L.marker([s.lat,s.lon],{icon:icon}).addTo(MAP);var lab=day.v==='go'?'GO — both agree':day.v==='split'?('maybe — '+(which(day)[0]||'one')+' only'):'no fly window';mk.bindPopup('<div class="lpop"><b>'+s.n+'</b><br>'+lab+(day.v==='no'?'':' · '+winSum(s,day))+'<br>faces '+s.fc+' · <a href="#" onclick="pwGoCard('+i+');return false;">hourly →</a></div>');MARKERS.push(mk);});}
window.pwMapDay=function(ld){MAPLD=ld;buildMapDays();if(MAP)drawMarkers();};
function fitMap(){if(MAP)MAP.fitBounds(L.latLngBounds(D.sites.map(function(s){return [s.lat,s.lon];})),{padding:[40,40]});}
function initMap(){if(MAP)return;MAPLD=MAPLD||bestFirmLd();MAP=L.map('lmap',{scrollWheelZoom:false}).setView([51.6,0.6],7);L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',{attribution:'© OpenStreetMap, © CARTO',subdomains:'abcd',maxZoom:18}).addTo(MAP);buildMapDays();drawMarkers();fitMap();}
window.pwGoCard=function(i){pwShowSec('forecast');var c=document.getElementById('card'+i);if(!document.getElementById('panel'+i).innerHTML){document.getElementById('panel'+i).innerHTML=panelHTML(i);}c.classList.add('open');c.scrollIntoView({block:'start'});};
function pwShowSec(name){['forecast','map','live'].forEach(function(n){document.getElementById('sec-'+n).classList.toggle('on',n===name);});document.querySelectorAll('.nb').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-s')===name);});if(name==='map'){initMap();setTimeout(function(){if(MAP){MAP.invalidateSize();fitMap();}},120);}if(name==='live'){var lw=document.getElementById('livewrap');if(!lw.innerHTML){lw.innerHTML='<iframe width="100%" height="100%" style="border:0" loading="lazy" src="https://embed.windy.com/embed2.html?lat=51.4&lon=0.6&detailLat=51.4&detailLon=0.6&zoom=7&level=surface&overlay=wind&product=ecmwf&menu=&message=&marker=&calendar=now&pressure=&type=map&location=coordinates&detail=&metricWind=mph&metricTemp=%C2%B0C&radarRange=-1"></iframe>';}}}
document.querySelectorAll('.nb').forEach(function(b){b.addEventListener('click',function(){pwShowSec(b.getAttribute('data-s'));});});
'''

head = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>Patang Wind — prototype</title>'
        '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>'
        '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
        '<style>' + CSS + '</style></head><body><div class="wrap">'
        '<div class="top"><h1>Patang Wind</h1><span class="tag">prototype</span></div>'
        '<p class="sub">UK beach game planner · updated ' + data["g"] + '</p>'
        '<div class="nav"><button class="nb on" data-s="forecast">Forecast</button><button class="nb" data-s="map">Map</button><button class="nb" data-s="live">Live wind</button></div>'
        '<div id="sec-forecast" class="sec on"><div id="pwroot"></div></div>'
        '<div id="sec-map" class="sec"><div class="chips" id="mapdays" style="margin-bottom:10px"></div><div id="lmap"></div>'
        '<div class="maplegend">arrow = wind direction &middot; circle = verdict (green GO / amber split / grey no) &middot; tap a beach for its hourly</div></div>'
        '<div id="sec-live" class="sec"><div id="livewrap"></div>'
        '<p class="maplegend" style="margin-top:8px">Live animated wind from Windy &mdash; drag the time bar at the bottom. This is Windy&#39;s own map (no beach highlighting); use the Map tab for your spots.</p></div>'
        '<p class="foot">Each day is judged on the two models you check — <b>XCWeather (GFS)</b> and the '
        '<b>Met Office (UKMO)</b>, via <a href="https://open-meteo.com">Open-Meteo</a>. GREEN only when both '
        'agree it&#39;s a full offshore day (9+ hrs of 8am–8pm); amber when they split. ECMWF rides along '
        'silently so we can later check whose call comes true at each beach. '
        'Gusts are the least certain part — read it as a ranking, not a promise. Auto-updates planned 4&times;/day.</p>'
        '</div>')
foot = '<script>\nconst D=' + json.dumps(data, separators=(",", ":")) + ';\n(function(){' + JS + '})();\n</script></body></html>'

open(os.path.join(ROOT, "docs", "prototype.html"), "w").write(head + foot)
print("wrote docs/prototype.html |", os.path.getsize(os.path.join(ROOT, "docs", "prototype.html")), "bytes")
