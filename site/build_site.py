#!/usr/bin/env python3
"""
Build the Orbital Stewardship single-page site -> ../index.html
Light scientific/editorial theme. Embeds the validated ORS engine + calibration,
the empirical spatial-density profile, and operator risk shares.
"""
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
calib = json.load(open(os.path.join(ROOT, "model", "calibration.json")))
scored = os.path.join(ROOT, "data", "processed", "scored_catalogue.csv")

# comparison objects + categories reused from the calculator payload
import pandas as pd
sc = pd.read_csv(scored, low_memory=False)
def pick(k):
    m = sc[sc["name"].astype(str).str.contains(k, case=False, na=False)]
    m = m[m["mass"].notna() & m["xSectAvg"].notna() & m["env_alt_km"].notna()]
    return m.head(1)
named = pd.concat([pick(k) for k in ["ZARYA","Hubble","Envisat","Starlink","Zenit","Delta 4","Ariane 5","CZ-","Iridium 33","OneWeb"]]).drop_duplicates("norad_id")
spread = sc[sc["mass"].notna() & sc["xSectAvg"].notna()].iloc[::max(1,len(sc)//8)].head(8)
comp = pd.concat([named, spread]).drop_duplicates("norad_id").head(20)
comparison = [{"name":str(r["name"])[:32],"type":str(r.get("OBJECT_TYPE") or ""),"ors":round(float(r["ORS"]),3)} for _,r in comp.iterrows()]

CATEGORIES = [
  {"label":"Active satellite — large (>1000 kg)","oc":"Payload","mass":2000,"xsect":15,"active":True,"alt":600},
  {"label":"Active satellite — medium (250–1000 kg)","oc":"Payload","mass":500,"xsect":6,"active":True,"alt":550},
  {"label":"Active smallsat (50–250 kg)","oc":"Payload","mass":150,"xsect":2,"active":True,"alt":500},
  {"label":"CubeSat (<50 kg)","oc":"Payload","mass":10,"xsect":0.1,"active":True,"alt":450},
  {"label":"Defunct / non-operational satellite","oc":"Payload","mass":1000,"xsect":10,"active":False,"alt":800},
  {"label":"Rocket upper stage / body","oc":"Rocket Body","mass":2000,"xsect":12,"active":False,"alt":800},
  {"label":"Mission-related object (adapter, cover)","oc":"Payload Mission Related Object","mass":50,"xsect":1,"active":False,"alt":700},
  {"label":"Fragmentation debris","oc":"Payload Fragmentation Debris","mass":5,"xsect":0.05,"active":False,"alt":800},
]
OPERATORS = [["United States",34.5],["Unattributed / orphan debris",28.4],["Russia",18.2],["China",11.0],["France",2.2],["United Kingdom",1.4],["Japan",0.7],["India",0.4]]

DATA = json.dumps({"calib":calib,"comparison":comparison,"categories":CATEGORIES,"operators":OPERATORS}, separators=(",",":"))
PRICE_M = calib["contribution"]["price_per_ors_usd"]/1e6
SCORED = f"{calib['scored_count']:,}"

TEMPLATE = r"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Orbital Stewardship — Pricing the Risk of Space Debris</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --paper:#fbfaf7; --ink:#181712; --muted:#6c675d; --line:#e6e2d8; --panel:#ffffff;
  --accent:#14509a; --accent2:#c0532a; --good:#2f8f6b; --warn:#b5731a;
  --dgp:#c0532a; --opi:#b5901a; --cpf:#14509a;
  --serif:"Newsreader",Georgia,"Times New Roman",serif; --sans:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
*{box-sizing:border-box} html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.65;font-size:17px}
.wrap{max-width:1080px;margin:0 auto;padding:0 22px}
h1,h2,h3{font-family:var(--serif);font-weight:500;line-height:1.15;letter-spacing:-.01em}
h2{font-size:34px;margin:0 0 6px} h3{font-size:20px;margin:0 0 6px}
p{margin:0 0 16px} a{color:var(--accent);text-decoration:none}
.eyebrow{font-family:var(--sans);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent2);font-weight:600;margin-bottom:10px}
/* nav */
nav{position:sticky;top:0;z-index:50;background:rgba(251,250,247,.86);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
nav .wrap{display:flex;align-items:center;justify-content:space-between;height:60px}
.brand{font-family:var(--serif);font-size:19px;font-weight:600}
.navlinks a{color:var(--muted);font-size:14px;margin-left:24px} .navlinks a:hover{color:var(--ink)}
@media(max-width:720px){.navlinks{display:none}}
/* hero */
.hero{padding:76px 0 40px;border-bottom:1px solid var(--line)}
.hero h1{font-size:56px;margin:0 0 18px;max-width:16ch}
.hero .lede{font-size:21px;color:var(--muted);max-width:60ch;font-family:var(--serif)}
.hero .cta{display:inline-block;margin-top:26px;background:var(--accent);color:#fff;padding:12px 22px;border-radius:8px;font-weight:600;font-size:15px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-top:52px}
@media(max-width:720px){.stats{grid-template-columns:repeat(2,1fr)}}
.stat .n{font-family:var(--serif);font-size:40px;font-weight:600;color:var(--accent)}
.stat .l{font-size:13px;color:var(--muted)}
section{padding:66px 0;border-bottom:1px solid var(--line)}
.lead-col{max-width:66ch}
.callout{border-left:3px solid var(--accent2);padding:6px 0 6px 20px;margin:24px 0;font-family:var(--serif);font-size:20px;color:#3a352c}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:26px}
@media(max-width:760px){.cards{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px}
.card .k{font-size:12px;letter-spacing:.1em;text-transform:uppercase;font-weight:600;margin-bottom:8px}
.card p{font-size:14.5px;color:var(--muted);margin:0}
.dgpk{color:var(--dgp)} .opik{color:var(--opi)} .cpfk{color:var(--cpf)}
.figure{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:22px;margin-top:26px}
.figure .cap{font-size:13px;color:var(--muted);margin-top:12px}
.opbars .row{display:flex;align-items:center;gap:12px;margin:7px 0;font-size:14px}
.opbars .nm{width:190px;color:var(--ink)} .opbars .tr{flex:1;background:#f0ede4;border-radius:5px;height:16px;overflow:hidden}
.opbars .fl{height:100%;background:var(--accent)} .opbars .vv{width:52px;text-align:right;color:var(--muted)}
/* calculator (light) */
.calc{display:grid;grid-template-columns:360px 1fr;gap:20px;margin-top:26px}
@media(max-width:820px){.calc{grid-template-columns:1fr}}
.cpanel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}
label{display:block;font-size:11px;color:var(--muted);margin:12px 0 4px;text-transform:uppercase;letter-spacing:.05em;font-weight:600}
input,select{width:100%;padding:9px 10px;background:#fff;border:1px solid var(--line);border-radius:8px;color:var(--ink);font-size:14px;font-family:var(--sans)}
.frow{display:flex;gap:10px}.frow>div{flex:1}
.chk{display:flex;align-items:center;gap:8px;margin-top:12px}.chk input{width:auto}
button{margin-top:14px;width:100%;padding:11px;background:var(--accent);border:none;border-radius:9px;color:#fff;font-weight:600;font-size:15px;cursor:pointer;font-family:var(--sans)}
button.ghost{background:#fff;border:1px solid var(--accent);color:var(--accent)}
.orsv{font-family:var(--serif);font-size:52px;font-weight:600;line-height:1}
.mut{color:var(--muted);font-size:13px}
.bar{margin:9px 0}.bar .t{display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px}
.track{height:11px;background:#f0ede4;border-radius:6px;overflow:hidden}.fill{height:100%;border-radius:6px}
.statrow{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--line);font-size:14px}.statrow span:first-child{color:var(--muted)}
.contrib{background:#f4f1ea;border-radius:10px;padding:14px;margin-top:14px;text-align:center}
.contrib .amt{font-family:var(--serif);font-size:30px;font-weight:600;color:var(--good)}
table{width:100%;border-collapse:collapse;font-size:13px;margin-top:8px}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line)}th{color:var(--muted);font-weight:600}.r{text-align:right}
.cmpbar{height:8px;background:#f0ede4;border-radius:4px;overflow:hidden;min-width:60px}.cmpbar>div{height:100%;background:var(--accent)}
.flag{padding:8px 11px;border-radius:8px;font-size:13px;margin-top:10px}
.flag.warn{background:#fbf0dd;border:1px solid var(--warn);color:#8a5610}
.flag.ok{background:#e7f4ee;border:1px solid var(--good);color:#1f6b4f}
.tag{font-size:11px;color:var(--muted)} .hl{color:var(--accent);font-weight:600}
footer{padding:40px 0 70px;color:var(--muted);font-size:13px}
.disc{background:#f4f1ea;border-radius:10px;padding:14px 16px;font-size:13px;color:var(--muted);margin-top:20px}
</style></head><body>
<nav><div class="wrap"><div class="brand">Orbital Stewardship</div>
<div class="navlinks"><a href="#problem">The Problem</a><a href="#model">The Model</a><a href="#method">Method &amp; Data</a><a href="#fund">The Fund</a></div></div></nav>

<header class="hero"><div class="wrap">
  <div class="eyebrow">A data-driven approach to space debris liability</div>
  <h1>Every object in orbit imposes a cost. Almost no one pays it.</h1>
  <p class="lede">Low Earth orbit is a shared commons being polluted by the debris of past launches. This is an interactive model that quantifies the orbital-debris risk of any object — or an entire constellation — and prices the contribution it would owe a proposed Orbital Debris Compensation Fund.</p>
  <a class="cta" href="#model">Try the model ↓</a>
  <div class="stats">
    <div class="stat"><div class="n">34,000+</div><div class="l">tracked objects on orbit today</div></div>
    <div class="stat"><div class="n">~130M</div><div class="l">untracked fragments &gt;1&nbsp;mm (estimated)</div></div>
    <div class="stat"><div class="n">__SCORED__</div><div class="l">objects scored by this model</div></div>
    <div class="stat"><div class="n">40&nbsp;J/g</div><div class="l">energy that turns a collision catastrophic</div></div>
  </div>
</div></header>

<section id="problem"><div class="wrap lead-col">
  <div class="eyebrow">The Problem</div>
  <h2>The tragedy of the orbital commons</h2>
  <p>The near-Earth environment is a shared resource that underpins communications, navigation, Earth observation and security. Like any commons, it is vulnerable to over-use: each operator captures the benefit of a launch while the risk it creates — debris — is spread across everyone else. The cost is a classic negative externality, and it is no longer abstract. Operational satellites now perform regular, fuel-burning collision-avoidance manoeuvres against a rising tide of junk.</p>
  <div class="callout">Beyond a critical density, collisions generate debris faster than the atmosphere can remove it — a self-sustaining cascade first described by Donald Kessler. Key LEO bands are already at or beyond that threshold.</div>
  <p>The law was built for a different problem. The 1972 Liability Convention makes a launching state liable for in-orbit damage only where <em>fault</em> can be proven — but a lethal fragment from a decades-old break-up, after successive collisions, cannot be traced to anyone. The most probable cause of satellite failure is also the least legally actionable. The response, this project argues, is to stop assigning blame after the fact and start pricing risk before it is created.</p>
</div></section>

<section id="model"><div class="wrap">
  <div class="eyebrow">The Model</div>
  <h2>Score any object. Price its contribution.</h2>
  <p class="lead-col">Choose an object type — from a single CubeSat to a defunct rocket body to a 5,000-satellite megaconstellation — and adjust its mass, altitude and disposal profile. The model computes an Orbital Risk Score and the annual fund contribution it implies. Everything runs on real catalogue data, live in your browser.</p>
  <div class="calc">
    <div class="cpanel">
      <label>Object type</label><select id="cat"></select>
      <div class="frow"><div><label>Number of objects</label><input id="count" type="number" value="1" min="1"/></div>
        <div><label>Perigee altitude (km)</label><input id="alt" type="number" value="550"/></div></div>
      <div class="frow"><div><label>Mass each (kg)</label><input id="mass" type="number" value="500"/></div>
        <div><label>Cross-section (m²)</label><input id="xsect" type="number" value="6"/></div></div>
      <div class="frow"><div><label>Material</label><select id="mat"><option value="0.5">Low (plastics)</option><option value="1.0" selected>Medium (aluminium)</option><option value="2.86">High (steel)</option></select></div>
        <div><div class="chk" style="margin-top:32px"><input id="active" type="checkbox"/><label style="margin:0;text-transform:none">Active / controllable</label></div></div></div>
      <button onclick="compute()">Compute risk &amp; contribution</button>
      <button class="ghost" onclick="addGroup()">+ Add to scenario</button>
    </div>
    <div>
      <div class="cpanel">
        <div style="display:flex;align-items:flex-end;gap:16px"><div><div class="orsv" id="orsv">—</div><div class="mut">Orbital Risk Score, per object (0–1)</div></div><div id="verdict" class="tag"></div></div>
        <div id="bars" style="margin:14px 0"></div><div id="stats"></div><div id="flags"></div>
        <div class="contrib"><div class="mut" id="clbl">Estimated annual ODCF contribution</div><div class="amt" id="contrib">—</div><div class="tag" id="share"></div></div>
      </div>
      <div class="cpanel" style="margin-top:16px" id="scencard" hidden>
        <b>Your scenario</b>
        <table id="scen"><thead><tr><th>Group</th><th class="r">Count</th><th class="r">ORS ea.</th><th class="r">Contribution</th><th></th></tr></thead><tbody></tbody></table>
        <div class="statrow" style="border:none;font-weight:600"><span id="scentotlbl">Scenario total</span><span id="scentot">—</span></div>
      </div>
      <div class="cpanel" style="margin-top:16px"><b>How one object compares to real catalogue objects</b>
        <table id="cmp"><thead><tr><th>Object</th><th>Type</th><th class="r">ORS</th><th></th></tr></thead><tbody></tbody></table></div>
    </div>
  </div>
</div></section>

<section id="method"><div class="wrap">
  <div class="eyebrow">Method &amp; Data</div>
  <h2>How the score is built</h2>
  <p class="lead-col">The Orbital Risk Score is a transparent, weighted combination of three factors, each normalised against the real population of objects in orbit. No black boxes: every constant is documented and every input is a measured or estimated physical quantity.</p>
  <div class="cards">
    <div class="card"><div class="k dgpk">Debris Generation</div><p>How much lethal debris the object would create in a break-up — driven by mass (via NASA's Standard Breakup Model), material density, and its likelihood of spontaneous fragmentation.</p></div>
    <div class="card"><div class="k opik">Orbital Persistence</div><p>How long it lingers. Orbital lifetime from atmospheric-decay physics — a defunct object at 800 km can persist for centuries, keeping its risk in play the entire time.</p></div>
    <div class="card"><div class="k cpfk">Collision Probability</div><p>How crowded its neighbourhood is. Measured directly from the catalogue as the object density of its altitude shell, multiplied by the object's own cross-section.</p></div>
  </div>

  <div class="figure">
    <h3>Where the traffic is: measured object density in low Earth orbit</h3>
    <svg id="density" viewBox="0 0 900 300" width="100%"></svg>
    <div class="cap">Computed directly from the merged catalogue in 25 km shells. The data reproduces the textbook debris peak near 800 km <em>and</em> reveals the newer congestion of the ~500 km satellite-constellation band that older studies predate.</div>
  </div>

  <p style="margin-top:30px">The model fuses two authoritative catalogues: the European Space Agency's <strong>DISCOS</strong> database (91,591 objects — mass, size, type) and the US <strong>Space-Track</strong> catalogue (69,677 objects — orbits). Merged on a common identifier, they yield a working population of tens of thousands of on-orbit objects, of which roughly 21,000 are fully specified and scored without any estimation. The full parameter set, its sources, and its known gaps are documented alongside the model.</p>
  <div class="disc">This is a transparent parametric model built for public understanding and policy illustration. It is calibrated on real data but is not a substitute for the high-fidelity conjunction-assessment systems operated by ESA and NASA. Figures are indicative.</div>
</div></section>

<section id="fund"><div class="wrap">
  <div class="eyebrow">The Solution</div>
  <h2>The Orbital Debris Compensation Fund</h2>
  <p class="lead-col">Modelled on the compensation regimes that govern oil pollution and nuclear power, the ODCF is an international risk pool. Rather than chasing fault after a collision, it charges each new launch a contribution proportional to the risk it adds — turning an unpriced externality into a line on a mission budget.</p>
  <div class="callout">Contribution = price per unit of risk × the object's Orbital Risk Score. The fund raises its annual target from the flow of new launches, which sets a price of roughly $__PRICE__ million per ORS point at current launch rates.</div>
  <p class="lead-col">Because the price attaches to risk, operators control their bill directly: deorbit on time, passivate stored energy, keep satellites manoeuvrable, or fly lower — and the score, and the contribution, fall. The money funds two things the current regime cannot: no-fault compensation for victims of untraceable debris, and active removal of the highest-risk objects already up there.</p>
  <div class="figure">
    <h3>Whose risk is it? Modelled contribution share by launching state</h3>
    <div class="opbars" id="opbars"></div>
    <div class="cap">Aggregate Orbital Risk Score by country of origin, on-orbit population. The large unattributed share is orphan debris with no identifiable owner — precisely the gap a no-fault fund exists to cover.</div>
  </div>
</div></section>

<footer><div class="wrap">
  <p>Orbital Stewardship — an interactive model operationalising the proposed Orbital Debris Compensation Fund.<br/>
  Data: ESA DISCOS · US Space-Track · NASA Standard Breakup Model &amp; ORDEM · empirical density from the merged catalogue. Model figures are indicative and for policy illustration.</p>
</div></footer>

<script>
const DATA=__DATA__, C=DATA.calib, PRICE=C.contribution.price_per_ors_usd;
function interp(x,xs,ys){if(x<=xs[0])return ys[0];if(x>=xs[xs.length-1])return ys[ys.length-1];for(let i=0;i<xs.length-1;i++){if(x>=xs[i]&&x<=xs[i+1]){const f=(x-xs[i])/(xs[i+1]-xs[i]);return ys[i]+f*(ys[i+1]-ys[i]);}}return ys[ys.length-1];}
function sd(a){const s=C.spatial_density;for(let i=0;i<s.alt_low_km.length;i++){if(a>=s.alt_low_km[i]&&a<s.alt_high_km[i])return s.density[i];}return Math.min(...s.density);}
function kh(a,B){const b=interp(a,C.kh_lifetime.alt_km,C.kh_lifetime.life_yr);const sc=(B&&B>0)?B/C.constants.B_REF:1;return Math.min(Math.max(b*sc,C.normalization.OPI.life_floor_yr),C.normalization.OPI.life_cap_yr);}
function nl(v,lo,hi){if(!(v>0))return 0;return Math.min(Math.max((Math.log10(v)-lo)/(hi-lo),0),1);}
function rel(a){const g=C.gating;if(a<=g.rel_full_km)return 1;if(a>=g.rel_taper_km)return g.rel_high;const f=(a-g.rel_full_km)/(g.rel_taper_km-g.rel_full_km);return 1-f*(1-g.rel_high);}
function score(o){const fp=(C.fp_by_class[o.oc]!==undefined)?C.fp_by_class[o.oc]:C.constants.fp_default;
  const dgpRaw=Math.pow(o.mass,0.75)*o.mat*(0.5+0.5*fp);const B=(o.mass&&o.xsect>0)?o.mass/(C.constants.CD*o.xsect):C.constants.B_REF;
  const life=kh(o.alt,B),cpfRaw=sd(o.alt)*o.xsect;
  const DGP=nl(dgpRaw,C.normalization.DGP.lo,C.normalization.DGP.hi),OPI=nl(life,C.normalization.OPI.lo,C.normalization.OPI.hi),CPF=nl(cpfRaw,C.normalization.CPF.lo,C.normalization.CPF.hi);
  const core=C.weights.DGP*DGP+C.weights.OPI*OPI+C.weights.CPF*CPF;
  return {DGP,OPI,CPF,life,ORS:core*rel(o.alt)*(o.active?C.gating.active_factor:1)};}
function inputs(){const c=DATA.categories[+document.getElementById('cat').value];
  return {oc:c.oc,mass:+document.getElementById('mass').value,xsect:+document.getElementById('xsect').value,alt:+document.getElementById('alt').value,mat:+document.getElementById('mat').value,active:document.getElementById('active').checked,count:Math.max(1,+document.getElementById('count').value),label:c.label};}
function fmt$(v){if(v>=1e9)return '$'+(v/1e9).toFixed(2)+'B';if(v>=1e6)return '$'+(v/1e6).toFixed(2)+'M';if(v>=1e3)return '$'+(v/1e3).toFixed(1)+'k';return '$'+v.toFixed(0);}
let last=null;
function compute(){const o=inputs(),s=score(o);last={o,s};
  document.getElementById('orsv').textContent=s.ORS.toFixed(3);
  document.getElementById('verdict').innerHTML='<span class="hl">'+(s.ORS>0.6?'High risk':s.ORS>0.3?'Moderate risk':'Low risk')+'</span>';
  const bar=(n,val,c,w)=>`<div class="bar"><div class="t"><span>${n} <span class="tag">(weight ${w})</span></span><span>${val.toFixed(3)}</span></div><div class="track"><div class="fill" style="width:${val*100}%;background:${c}"></div></div></div>`;
  document.getElementById('bars').innerHTML=bar('Debris Generation',s.DGP,'var(--dgp)',C.weights.DGP)+bar('Orbital Persistence',s.OPI,'var(--opi)',C.weights.OPI)+bar('Collision Probability',s.CPF,'var(--cpf)',C.weights.CPF);
  document.getElementById('stats').innerHTML=`<div class="statrow"><span>Estimated orbital lifetime</span><span>${s.life>=1000?Math.round(s.life).toLocaleString()+' yr':s.life.toFixed(1)+' yr'}</span></div><div class="statrow"><span>Collision-relevance factor</span><span>${rel(o.alt).toFixed(2)}</span></div><div class="statrow"><span>Active discount</span><span>${o.active?C.gating.active_factor.toFixed(2):'1.00'}</span></div>`;
  let flags='';
  if(!o.active && s.life>25) flags+=`<div class="flag warn">⚠ Exceeds the 25-year post-mission disposal guideline (est. lifetime ${s.life>=1000?Math.round(s.life).toLocaleString():s.life.toFixed(0)} yr, no active disposal).</div>`;
  if(o.active && s.life<=25) flags+=`<div class="flag ok">✓ Consistent with post-mission disposal guidance (active, decays within 25 yr).</div>`;
  if(o.count>=100 && o.alt<700) flags+=`<div class="flag warn">⚠ Large low-orbit constellation: studies project ~300 disabling collisions over 30 yr at a 10,000-satellite population, rising sharply beyond.</div>`;
  document.getElementById('flags').innerHTML=flags;
  const per=PRICE*s.ORS,tot=per*o.count;
  document.getElementById('clbl').textContent=o.count>1?`Annual ODCF contribution — ${o.count.toLocaleString()} objects`:'Estimated annual ODCF contribution';
  document.getElementById('contrib').textContent=fmt$(tot)+' / yr';
  document.getElementById('share').textContent=o.count>1?`${fmt$(per)}/yr each · ${fmt$(PRICE)} per ORS point`:`priced at ${fmt$(PRICE)} per ORS point`;
  renderCompare(s.ORS);}
const scen=[];
function addGroup(){if(!last)compute();const o=last.o,s=last.s;scen.push({label:o.label,count:o.count,ors:s.ORS,contrib:PRICE*s.ORS*o.count});document.getElementById('scencard').hidden=false;renderScen();}
function rmg(i){scen.splice(i,1);if(!scen.length){document.getElementById('scencard').hidden=true;return;}renderScen();}
function renderScen(){const tb=document.querySelector('#scen tbody');tb.innerHTML='';let ors=0,ct=0,n=0;scen.forEach((g,i)=>{ors+=g.ors*g.count;ct+=g.contrib;n+=g.count;tb.innerHTML+=`<tr><td>${g.label}</td><td class="r">${g.count.toLocaleString()}</td><td class="r">${g.ors.toFixed(3)}</td><td class="r">${fmt$(g.contrib)}</td><td><a href="#" class="tag" onclick="rmg(${i});return false">✕</a></td></tr>`;});document.getElementById('scentotlbl').textContent=`Scenario total (${n.toLocaleString()} objects)`;document.getElementById('scentot').textContent=ors.toFixed(2)+' ORS · '+fmt$(ct)+'/yr';}
function renderCompare(my){const rows=DATA.comparison.slice().sort((a,b)=>b.ors-a.ors);const max=Math.max(my,...rows.map(r=>r.ors));const tb=document.querySelector('#cmp tbody');
  tb.innerHTML=`<tr style="background:#f4f1ea"><td><b>▶ Your object</b></td><td class="tag">input</td><td class="r"><b>${my.toFixed(3)}</b></td><td><div class="cmpbar"><div style="width:${my/max*100}%;background:var(--good)"></div></div></td></tr>`;
  rows.forEach(r=>{tb.innerHTML+=`<tr><td>${r.name}</td><td class="tag">${r.type}</td><td class="r">${r.ors.toFixed(3)}</td><td><div class="cmpbar"><div style="width:${r.ors/max*100}%"></div></div></td></tr>`;});}
// density chart
(function(){const s=C.spatial_density,W=900,H=300,pad=40;const xs=s.alt_low_km,ys=s.density;const xmin=200,xmax=2000,ymax=Math.max(...ys);
  const X=a=>pad+(a-xmin)/(xmax-xmin)*(W-pad-10),Y=d=>H-pad-(d/ymax)*(H-pad-14);
  let path='M '+X(xs[0])+' '+Y(0);xs.forEach((a,i)=>path+=' L '+X(a)+' '+Y(ys[i]));path+=' L '+X(xs[xs.length-1])+' '+Y(0)+' Z';
  let g='';[400,800,1200,1600,2000].forEach(t=>{g+=`<line x1="${X(t)}" y1="14" x2="${X(t)}" y2="${H-pad}" stroke="#eee"/><text x="${X(t)}" y="${H-pad+18}" font-size="11" fill="#999" text-anchor="middle">${t} km</text>`;});
  const ann=(a,txt)=>{const px=X(a);return `<line x1="${px}" y1="18" x2="${px}" y2="${H-pad}" stroke="#c0532a" stroke-dasharray="3 3"/><text x="${px+5}" y="30" font-size="11" fill="#c0532a">${txt}</text>`;};
  document.getElementById('density').innerHTML=g+`<path d="${path}" fill="rgba(20,80,154,.14)" stroke="#14509a" stroke-width="1.5"/>`+ann(488,'~500 km constellations')+ann(812,'~800 km debris peak');
})();
// operator bars
(function(){const max=Math.max(...DATA.operators.map(o=>o[1]));document.getElementById('opbars').innerHTML=DATA.operators.map(o=>`<div class="row"><div class="nm">${o[0]}</div><div class="tr"><div class="fl" style="width:${o[1]/max*100}%;background:${o[0].indexOf('Unattr')>=0?'#c0532a':'#14509a'}"></div></div><div class="vv">${o[1]}%</div></div>`).join('');})();
// init calc
(function(){const cat=document.getElementById('cat');DATA.categories.forEach((c,i)=>{const o=document.createElement('option');o.value=i;o.textContent=c.label;cat.appendChild(o);});
  function fill(){const c=DATA.categories[+cat.value];document.getElementById('mass').value=c.mass;document.getElementById('xsect').value=c.xsect;document.getElementById('alt').value=c.alt;document.getElementById('active').checked=c.active;compute();}
  cat.addEventListener('change',fill);document.querySelectorAll('.cpanel input,.cpanel select').forEach(e=>e.addEventListener('keydown',ev=>{if(ev.key==='Enter')compute();}));cat.value=1;fill();
})();
</script></body></html>"""

html = (TEMPLATE.replace("__DATA__", DATA)
                .replace("__SCORED__", SCORED)
                .replace("__PRICE__", f"{PRICE_M:.1f}"))
open(os.path.join(ROOT, "index.html"), "w").write(html)
print(f"wrote index.html ({len(html)//1024} KB); comparison={len(comparison)}; price/ORS=${PRICE_M:.2f}M")
