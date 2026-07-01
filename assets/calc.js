/* Orbital Stewardship — ORS engine + calculator UI. Mirrors model/calibrate.py. */
(function(){
  const DATA = window.ODCF_DATA, C = DATA.calib, PRICE = C.contribution.price_per_ors_usd;

  function interp(x,xs,ys){if(x<=xs[0])return ys[0];if(x>=xs[xs.length-1])return ys[ys.length-1];for(let i=0;i<xs.length-1;i++){if(x>=xs[i]&&x<=xs[i+1]){const f=(x-xs[i])/(xs[i+1]-xs[i]);return ys[i]+f*(ys[i+1]-ys[i]);}}return ys[ys.length-1];}
  function sd(a){const s=C.spatial_density;for(let i=0;i<s.alt_low_km.length;i++){if(a>=s.alt_low_km[i]&&a<s.alt_high_km[i])return s.density[i];}return Math.min.apply(null,s.density);}
  function kh(a,B){const b=interp(a,C.kh_lifetime.alt_km,C.kh_lifetime.life_yr);const sc=(B&&B>0)?B/C.constants.B_REF:1;return Math.min(Math.max(b*sc,C.normalization.OPI.life_floor_yr),C.normalization.OPI.life_cap_yr);}
  function nl(v,lo,hi){if(!(v>0))return 0;return Math.min(Math.max((Math.log10(v)-lo)/(hi-lo),0),1);}
  function rel(a){const g=C.gating;if(a<=g.rel_full_km)return 1;if(a>=g.rel_taper_km)return g.rel_high;const f=(a-g.rel_full_km)/(g.rel_taper_km-g.rel_full_km);return 1-f*(1-g.rel_high);}
  function score(o){
    const fp=(C.fp_by_class[o.oc]!==undefined)?C.fp_by_class[o.oc]:C.constants.fp_default;
    const dgpRaw=Math.pow(o.mass,0.75)*o.mat*(0.5+0.5*fp);
    const B=(o.mass&&o.xsect>0)?o.mass/(C.constants.CD*o.xsect):C.constants.B_REF;
    const life=kh(o.alt,B), cpfRaw=sd(o.alt)*o.xsect;
    const DGP=nl(dgpRaw,C.normalization.DGP.lo,C.normalization.DGP.hi);
    const OPI=nl(life,C.normalization.OPI.lo,C.normalization.OPI.hi);
    const CPF=nl(cpfRaw,C.normalization.CPF.lo,C.normalization.CPF.hi);
    const core=C.weights.DGP*DGP+C.weights.OPI*OPI+C.weights.CPF*CPF;
    return {DGP,OPI,CPF,life,B,ORS:core*rel(o.alt)*(o.active?C.gating.active_factor:1)};
  }
  const $=id=>document.getElementById(id);
  function inputs(){const c=DATA.categories[+$('cat').value];
    return {oc:c.oc,mass:+$('mass').value,xsect:+$('xsect').value,alt:+$('alt').value,mat:+$('mat').value,active:$('active').checked,count:Math.max(1,+$('count').value),label:c.label};}
  function fmt(v){if(v>=1e9)return '$'+(v/1e9).toFixed(2)+'B';if(v>=1e6)return '$'+(v/1e6).toFixed(2)+'M';if(v>=1e3)return '$'+(v/1e3).toFixed(1)+'k';return '$'+v.toFixed(0);}
  let last=null;
  function compute(){const o=inputs(),s=score(o);last={o,s};
    $('orsv').textContent=s.ORS.toFixed(3);
    $('orsclass').textContent=s.ORS>0.6?'high':s.ORS>0.3?'moderate':'low';
    const bar=(n,val,c,w)=>'<div class="bar"><div class="t"><span>'+n+' <span class="muted mono">w='+w+'</span></span><span class="mono">'+val.toFixed(3)+'</span></div><div class="track"><div class="fill" style="width:'+(val*100)+'%;background:'+c+'"></div></div></div>';
    $('bars').innerHTML=bar('Debris generation (DGP)',s.DGP,'#0b539c',C.weights.DGP)+bar('Orbital persistence (OPI)',s.OPI,'#0b539c',C.weights.OPI)+bar('Collision probability (CPF)',s.CPF,'#0b539c',C.weights.CPF);
    $('stats').innerHTML=
      '<div class="statrow"><span>Estimated orbital lifetime</span><span>'+(s.life>=1000?Math.round(s.life).toLocaleString()+' yr':s.life.toFixed(1)+' yr')+'</span></div>'+
      '<div class="statrow"><span>Ballistic coefficient</span><span>'+s.B.toFixed(0)+' kg/m²</span></div>'+
      '<div class="statrow"><span>Collision-relevance factor</span><span>'+rel(o.alt).toFixed(2)+'</span></div>'+
      '<div class="statrow"><span>Active-object factor</span><span>'+(o.active?C.gating.active_factor.toFixed(2):'1.00')+'</span></div>';
    let fl='';
    if(!o.active && s.life>25) fl+='<div class="flagline warn">Exceeds the 25-year post-mission disposal guideline (no active disposal).</div>';
    if(o.active && s.life<=25) fl+='<div class="flagline ok">Within the 25-year post-mission disposal guideline.</div>';
    $('flags').innerHTML=fl;
    const per=PRICE*s.ORS, tot=per*o.count;
    $('clbl').textContent=o.count>1?('Annual contribution — '+o.count.toLocaleString()+' objects'):'Annual contribution';
    $('contrib').textContent=fmt(tot);
    $('share').textContent=o.count>1?(fmt(per)+' each · '+fmt(PRICE)+'/ORS'):(fmt(PRICE)+'/ORS point');
    renderCompare(s.ORS);
  }
  const scen=[];
  window.addGroup=function(){if(!last)compute();const o=last.o,s=last.s;scen.push({label:o.label,count:o.count,ors:s.ORS,contrib:PRICE*s.ORS*o.count});$('scencard').hidden=false;renderScen();};
  window.rmg=function(i){scen.splice(i,1);if(!scen.length){$('scencard').hidden=true;return;}renderScen();return false;};
  function renderScen(){const tb=document.querySelector('#scen tbody');tb.innerHTML='';let ors=0,ct=0,n=0;
    scen.forEach((g,i)=>{ors+=g.ors*g.count;ct+=g.contrib;n+=g.count;
      tb.innerHTML+='<tr><td>'+g.label+'</td><td class="num">'+g.count.toLocaleString()+'</td><td class="num">'+g.ors.toFixed(3)+'</td><td class="num">'+fmt(g.contrib)+'</td><td><a href="#" onclick="return rmg('+i+')">✕</a></td></tr>';});
    $('scentot').innerHTML='<td><b>Total</b></td><td class="num">'+n.toLocaleString()+'</td><td class="num">'+ors.toFixed(2)+'</td><td class="num"><b>'+fmt(ct)+'</b></td><td></td>';}
  function renderCompare(my){const rows=DATA.comparison.slice().sort((a,b)=>b.ors-a.ors);const max=Math.max(my,rows[0].ors);const tb=document.querySelector('#cmp tbody');
    tb.innerHTML='<tr style="background:var(--bg2)"><td><b>Your object</b></td><td class="muted">input</td><td class="num"><b>'+my.toFixed(3)+'</b></td><td><div class="cmpbar"><div style="width:'+(my/max*100)+'%;background:var(--ok)"></div></div></td></tr>';
    rows.forEach(r=>{tb.innerHTML+='<tr><td>'+r.name+'</td><td class="muted small">'+r.type+'</td><td class="num">'+r.ors.toFixed(3)+'</td><td><div class="cmpbar"><div style="width:'+(r.ors/max*100)+'%"></div></div></td></tr>';});}
  window.compute=compute;
  document.addEventListener('DOMContentLoaded',function(){
    const cat=$('cat');DATA.categories.forEach((c,i)=>{const o=document.createElement('option');o.value=i;o.textContent=c.label;cat.appendChild(o);});
    function fill(){const c=DATA.categories[+cat.value];$('mass').value=c.mass;$('xsect').value=c.xsect;$('alt').value=c.alt;$('active').checked=c.active;compute();}
    cat.addEventListener('change',fill);
    document.querySelectorAll('.calc input,.calc select').forEach(e=>e.addEventListener('keydown',ev=>{if(ev.key==='Enter')compute();}));
    cat.value=1;fill();
  });
})();
