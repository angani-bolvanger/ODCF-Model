#!/usr/bin/env python3
"""
Generate a self-contained ODCF calculator (single HTML file, no dependencies).
Bakes in calibration + real comparison objects. JS engine mirrors calibrate.py.

Features: friendly object categories, constellation counts, scenario builder
(mix groups), flow-basis contribution (fixed $1B), 25-year disposal flag,
and constellation collision context.
"""
import os, json
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")

calib = json.load(open(os.path.join(HERE, "calibration.json")))
scored = pd.read_csv(os.path.join(PROC, "scored_catalogue.csv"), low_memory=False)

def pick(keyword):
    m = scored[scored["name"].astype(str).str.contains(keyword, case=False, na=False)]
    m = m[m["mass"].notna() & m["xSectAvg"].notna() & m["env_alt_km"].notna()]
    return m.head(1)

named = pd.concat([pick(k) for k in
    ["ZARYA", "Hubble", "Envisat", "Starlink", "Zenit", "Delta 4", "Ariane 5",
     "CZ-", "Iridium 33", "Cosmos 2251", "Terra", "OneWeb"]]).drop_duplicates("norad_id")
spread = scored[scored["mass"].notna() & scored["xSectAvg"].notna() & scored["env_alt_km"].notna()]
spread = spread.iloc[::max(1, len(spread)//10)].head(10)
comp = pd.concat([named, spread]).drop_duplicates("norad_id").head(24)
comp_records = [{
    "name": str(r["name"])[:34], "type": str(r.get("OBJECT_TYPE") or ""),
    "ors": round(float(r["ORS"]), 3),
} for _, r in comp.iterrows()]

# friendly categories -> {objectClass for FP, mass, xsect(m^2), active, altitude}
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

payload = {"calib": calib, "comparison": comp_records, "categories": CATEGORIES}
DATA_JSON = json.dumps(payload, separators=(",", ":"))

HTML = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>ODCF — Orbital Risk & Contribution Calculator</title>
<style>
  :root{--bg:#0b1020;--panel:#141b2f;--panel2:#1b2540;--line:#26314f;--text:#e8ecf7;
    --muted:#93a0c0;--accent:#4da3ff;--dgp:#ff8a5c;--opi:#ffd15c;--cpf:#5cc8ff;--good:#3ad29f;--bad:#ff6b6b;--warn:#ffb454;}
  *{box-sizing:border-box} body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--text);line-height:1.5}
  .wrap{max-width:1100px;margin:0 auto;padding:28px 20px 60px}
  h1{font-size:24px;margin:0 0 4px} .sub{color:var(--muted);margin:0 0 20px;font-size:14px}
  .grid{display:grid;grid-template-columns:370px 1fr;gap:20px}
  @media(max-width:880px){.grid{grid-template-columns:1fr}}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px}
  label{display:block;font-size:12px;color:var(--muted);margin:12px 0 4px;text-transform:uppercase;letter-spacing:.03em}
  input,select{width:100%;padding:9px 10px;background:var(--panel2);border:1px solid var(--line);border-radius:8px;color:var(--text);font-size:14px}
  .row{display:flex;gap:10px}.row>div{flex:1}
  .chk{display:flex;align-items:center;gap:8px;margin-top:14px}.chk input{width:auto}
  button{margin-top:14px;width:100%;padding:11px;background:var(--accent);border:none;border-radius:9px;color:#04101f;font-weight:700;font-size:15px;cursor:pointer}
  button.ghost{background:transparent;border:1px solid var(--accent);color:var(--accent)}
  .ors-big{font-size:52px;font-weight:800;line-height:1}.ors-lbl{color:var(--muted);font-size:13px}
  .bars{margin:16px 0}.bar{margin:10px 0}.bar .t{display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px}
  .track{height:12px;background:var(--panel2);border-radius:6px;overflow:hidden}.fill{height:100%;border-radius:6px}
  .stat{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--line);font-size:14px}.stat span:first-child{color:var(--muted)}
  .contrib{background:var(--panel2);border-radius:10px;padding:14px;margin-top:14px;text-align:center}
  .contrib .amt{font-size:30px;font-weight:800;color:var(--good)}
  table{width:100%;border-collapse:collapse;font-size:13px;margin-top:8px}
  th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line)}th{color:var(--muted);font-weight:600}.r{text-align:right}
  .cmpbar{height:8px;background:var(--panel2);border-radius:4px;overflow:hidden;min-width:60px}.cmpbar>div{height:100%;background:var(--accent)}
  .tag{font-size:11px;color:var(--muted)}.hl{color:var(--accent);font-weight:700}
  .flag{padding:8px 11px;border-radius:8px;font-size:13px;margin-top:10px}
  .flag.warn{background:rgba(255,180,84,.13);border:1px solid var(--warn);color:var(--warn)}
  .flag.ok{background:rgba(58,210,159,.1);border:1px solid var(--good);color:var(--good)}
  .note{font-size:12px;color:var(--muted);margin-top:10px}
</style></head><body><div class="wrap">
  <h1>ODCF — Orbital Risk &amp; Contribution Calculator</h1>
  <p class="sub">Estimate the orbital-debris risk of launching an object or a constellation, and the annual contribution it would owe an Orbital Debris Compensation Fund. Calibrated on __SCORED__ real on-orbit objects · fund target fixed at $1B/yr · price __PRICE__/ORS point (flow basis).</p>
  <div class="grid">
    <div class="card">
      <label>Object type</label>
      <select id="cat"></select>
      <div class="row"><div>
        <label>Number of objects</label><input id="count" type="number" value="1" min="1"/>
      </div><div>
        <label>Perigee altitude (km)</label><input id="alt" type="number" value="550"/>
      </div></div>
      <div class="row"><div>
        <label>Mass each (kg)</label><input id="mass" type="number" value="500"/>
      </div><div>
        <label>Cross-section each (m²)</label><input id="xsect" type="number" value="6"/>
      </div></div>
      <div class="row"><div>
        <label>Material</label><select id="mat">
          <option value="0.5">Low (plastics)</option><option value="1.0" selected>Medium (aluminium)</option><option value="2.86">High (steel)</option>
        </select></div><div>
        <div class="chk" style="margin-top:34px"><input id="active" type="checkbox"/><label style="margin:0;text-transform:none">Active / controllable</label></div>
      </div></div>
      <button onclick="compute()">Compute risk &amp; contribution</button>
      <button class="ghost" onclick="addGroup()">+ Add to scenario</button>
      <div class="note">Pick a type to autofill typical values, then adjust. Use “Number of objects” for constellations (e.g. 1,000 satellites). Build mixed scenarios with “Add to scenario”.</div>
    </div>

    <div>
      <div class="card">
        <div style="display:flex;align-items:flex-end;gap:16px">
          <div><div class="ors-big" id="orsv">—</div><div class="ors-lbl">Orbital Risk Score, per object (0–1)</div></div>
          <div id="verdict" class="tag"></div>
        </div>
        <div class="bars" id="bars"></div>
        <div id="stats"></div>
        <div id="flags"></div>
        <div class="contrib">
          <div class="ors-lbl" id="clbl">Estimated annual ODCF contribution</div>
          <div class="amt" id="contrib">—</div>
          <div class="tag" id="share"></div>
        </div>
      </div>

      <div class="card" style="margin-top:16px" id="scencard" hidden>
        <b>Your scenario</b>
        <table id="scen"><thead><tr><th>Group</th><th class="r">Count</th><th class="r">ORS ea.</th><th class="r">Contribution</th><th></th></tr></thead><tbody></tbody></table>
        <div class="stat" style="border:none;font-weight:700"><span id="scentotlbl">Scenario total</span><span id="scentot">—</span></div>
      </div>

      <div class="card" style="margin-top:16px">
        <b>How one object compares to real catalogue objects</b>
        <table id="cmp"><thead><tr><th>Object</th><th>Type</th><th class="r">ORS</th><th></th></tr></thead><tbody></tbody></table>
      </div>
    </div>
  </div>
</div>
<script>
const DATA=__DATA__, C=DATA.calib, PRICE=C.contribution.price_per_ors_usd;
function interp(x,xs,ys){if(x<=xs[0])return ys[0];if(x>=xs[xs.length-1])return ys[ys.length-1];for(let i=0;i<xs.length-1;i++){if(x>=xs[i]&&x<=xs[i+1]){const f=(x-xs[i])/(xs[i+1]-xs[i]);return ys[i]+f*(ys[i+1]-ys[i]);}}return ys[ys.length-1];}
function sd(a){const s=C.spatial_density;for(let i=0;i<s.alt_low_km.length;i++){if(a>=s.alt_low_km[i]&&a<s.alt_high_km[i])return s.density[i];}return Math.min(...s.density);}
function kh(a,B){const b=interp(a,C.kh_lifetime.alt_km,C.kh_lifetime.life_yr);const sc=(B&&B>0)?B/C.constants.B_REF:1;return Math.min(Math.max(b*sc,C.normalization.OPI.life_floor_yr),C.normalization.OPI.life_cap_yr);}
function nl(v,lo,hi){if(!(v>0))return 0;return Math.min(Math.max((Math.log10(v)-lo)/(hi-lo),0),1);}
function rel(a){const g=C.gating;if(a<=g.rel_full_km)return 1;if(a>=g.rel_taper_km)return g.rel_high;const f=(a-g.rel_full_km)/(g.rel_taper_km-g.rel_full_km);return 1-f*(1-g.rel_high);}
function score(o){const fp=(C.fp_by_class[o.oc]!==undefined)?C.fp_by_class[o.oc]:C.constants.fp_default;
  const dgpRaw=Math.pow(o.mass,0.75)*o.mat*(0.5+0.5*fp);
  const B=(o.mass&&o.xsect>0)?o.mass/(C.constants.CD*o.xsect):C.constants.B_REF;
  const life=kh(o.alt,B), cpfRaw=sd(o.alt)*o.xsect;
  const DGP=nl(dgpRaw,C.normalization.DGP.lo,C.normalization.DGP.hi);
  const OPI=nl(life,C.normalization.OPI.lo,C.normalization.OPI.hi);
  const CPF=nl(cpfRaw,C.normalization.CPF.lo,C.normalization.CPF.hi);
  const core=C.weights.DGP*DGP+C.weights.OPI*OPI+C.weights.CPF*CPF;
  return {DGP,OPI,CPF,life,ORS:core*rel(o.alt)*(o.active?C.gating.active_factor:1)};}
function inputs(){const c=DATA.categories[+document.getElementById('cat').value];
  return {oc:c.oc,mass:+document.getElementById('mass').value,xsect:+document.getElementById('xsect').value,
    alt:+document.getElementById('alt').value,mat:+document.getElementById('mat').value,
    active:document.getElementById('active').checked,count:Math.max(1,+document.getElementById('count').value),label:c.label};}
function fmt$(v){if(v>=1e9)return '$'+(v/1e9).toFixed(2)+'B';if(v>=1e6)return '$'+(v/1e6).toFixed(2)+'M';if(v>=1e3)return '$'+(v/1e3).toFixed(1)+'k';return '$'+v.toFixed(0);}
let last=null;
function compute(){const o=inputs(),s=score(o);last={o,s};
  document.getElementById('orsv').textContent=s.ORS.toFixed(3);
  const v=s.ORS>0.6?'High risk':s.ORS>0.3?'Moderate risk':'Low risk';
  document.getElementById('verdict').innerHTML='<span class="hl">'+v+'</span>';
  const bar=(n,val,c,w)=>`<div class="bar"><div class="t"><span>${n} <span class="tag">(weight ${w})</span></span><span>${val.toFixed(3)}</span></div><div class="track"><div class="fill" style="width:${val*100}%;background:${c}"></div></div></div>`;
  document.getElementById('bars').innerHTML=bar('Debris Generation',s.DGP,'var(--dgp)',C.weights.DGP)+bar('Orbital Persistence',s.OPI,'var(--opi)',C.weights.OPI)+bar('Collision Probability',s.CPF,'var(--cpf)',C.weights.CPF);
  document.getElementById('stats').innerHTML=
    `<div class="stat"><span>Estimated orbital lifetime</span><span>${s.life>=1000?Math.round(s.life).toLocaleString()+' yr':s.life.toFixed(1)+' yr'}</span></div>`+
    `<div class="stat"><span>Collision-relevance factor</span><span>${rel(o.alt).toFixed(2)}</span></div>`+
    `<div class="stat"><span>Active discount</span><span>${o.active?C.gating.active_factor.toFixed(2):'1.00'}</span></div>`;
  // policy flags (from ESA/NASA guidance)
  let flags='';
  if(!o.active && s.life>25) flags+=`<div class="flag warn">⚠ Exceeds the 25-year post-mission disposal guideline (est. lifetime ${s.life>=1000?Math.round(s.life).toLocaleString():s.life.toFixed(0)} yr with no active disposal).</div>`;
  if(o.active && s.life<=25) flags+=`<div class="flag ok">✓ Consistent with post-mission disposal guidance (active/controllable, decays within 25 yr).</div>`;
  if(o.count>=100 && o.alt<700) flags+=`<div class="flag warn">⚠ Large low-orbit constellation: studies project ~300 disabling collisions over 30 yr for a 10,000-satellite population, rising sharply beyond.</div>`;
  document.getElementById('flags').innerHTML=flags;
  // contribution (flow basis)
  const per=PRICE*s.ORS, tot=per*o.count;
  document.getElementById('clbl').textContent=o.count>1?`Annual ODCF contribution — ${o.count.toLocaleString()} objects`:'Estimated annual ODCF contribution';
  document.getElementById('contrib').textContent=fmt$(tot)+' / yr';
  document.getElementById('share').textContent=o.count>1?`${fmt$(per)}/yr each · priced at ${fmt$(PRICE)} per ORS point`:`priced at ${fmt$(PRICE)} per ORS point`;
  renderCompare(s.ORS);}
const scen=[];
function addGroup(){if(!last)compute();const o=last.o,s=last.s;
  scen.push({label:o.label,count:o.count,ors:s.ORS,contrib:PRICE*s.ORS*o.count});
  document.getElementById('scencard').hidden=false;renderScen();}
function rmg(i){scen.splice(i,1);if(!scen.length){document.getElementById('scencard').hidden=true;return;}renderScen();}
function renderScen(){const tb=document.querySelector('#scen tbody');tb.innerHTML='';let ors=0,ct=0,n=0;
  scen.forEach((g,i)=>{ors+=g.ors*g.count;ct+=g.contrib;n+=g.count;
    tb.innerHTML+=`<tr><td>${g.label}</td><td class="r">${g.count.toLocaleString()}</td><td class="r">${g.ors.toFixed(3)}</td><td class="r">${fmt$(g.contrib)}</td><td><a href="#" class="tag" onclick="rmg(${i});return false">✕</a></td></tr>`;});
  document.getElementById('scentotlbl').textContent=`Scenario total (${n.toLocaleString()} objects)`;
  document.getElementById('scentot').textContent=ors.toFixed(2)+' ORS · '+fmt$(ct)+'/yr';}
function renderCompare(my){const rows=DATA.comparison.slice().sort((a,b)=>b.ors-a.ors);const max=Math.max(my,...rows.map(r=>r.ors));
  const tb=document.querySelector('#cmp tbody');
  tb.innerHTML=`<tr style="background:var(--panel2)"><td><b>▶ Your object</b></td><td class="tag">input</td><td class="r"><b>${my.toFixed(3)}</b></td><td><div class="cmpbar"><div style="width:${my/max*100}%;background:var(--good)"></div></div></td></tr>`;
  rows.forEach(r=>{tb.innerHTML+=`<tr><td>${r.name}</td><td class="tag">${r.type}</td><td class="r">${r.ors.toFixed(3)}</td><td><div class="cmpbar"><div style="width:${r.ors/max*100}%"></div></div></td></tr>`;});}
(function(){const cat=document.getElementById('cat');
  DATA.categories.forEach((c,i)=>{const o=document.createElement('option');o.value=i;o.textContent=c.label;cat.appendChild(o);});
  function fill(){const c=DATA.categories[+cat.value];document.getElementById('mass').value=c.mass;document.getElementById('xsect').value=c.xsect;
    document.getElementById('alt').value=c.alt;document.getElementById('active').checked=c.active;compute();}
  cat.addEventListener('change',fill);
  document.querySelectorAll('input,select').forEach(e=>e.addEventListener('keydown',ev=>{if(ev.key==='Enter')compute();}));
  cat.value=1;fill();
})();
</script></body></html>"""

html = (HTML.replace("__DATA__", DATA_JSON)
            .replace("__SCORED__", f"{calib['scored_count']:,}")
            .replace("__PRICE__", f"${calib['contribution']['price_per_ors_usd']/1e6:.2f}M"))
out = os.path.join(ROOT, "calculator.html")
open(out, "w").write(html)
print(f"categories: {len(CATEGORIES)}, comparison: {len(comp_records)}")
print(f"price/ORS: ${calib['contribution']['price_per_ors_usd']:,.0f}")
print(f"wrote {out} ({len(html)//1024} KB)")
