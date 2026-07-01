/* draws #density (spatial density profile) and #opbars (operator shares) if present */
(function(){
  const D = window.ODCF_DATA; if(!D) return;
  const dens = document.getElementById('density');
  if(dens){
    const s=D.calib.spatial_density, W=900,H=300,pad=42;
    const xs=s.alt_low_km.map((v,i)=>(v+s.alt_high_km[i])/2), ys=s.density;
    const xmin=200,xmax=2000,ymax=Math.max.apply(null,ys);
    const X=a=>pad+(a-xmin)/(xmax-xmin)*(W-pad-12), Y=d=>H-pad-(d/ymax)*(H-pad-16);
    let path='M '+X(xs[0])+' '+Y(0); xs.forEach((a,i)=>path+=' L '+X(a).toFixed(1)+' '+Y(ys[i]).toFixed(1)); path+=' L '+X(xs[xs.length-1])+' '+Y(0)+' Z';
    let g=''; [400,800,1200,1600,2000].forEach(t=>{g+='<line x1="'+X(t)+'" y1="16" x2="'+X(t)+'" y2="'+(H-pad)+'" stroke="#eef1f4"/><text x="'+X(t)+'" y="'+(H-pad+18)+'" font-size="11" fill="#8a949d" text-anchor="middle" font-family="monospace">'+t+' km</text>';});
    const ann=(a,txt)=>{const px=X(a);return '<line x1="'+px+'" y1="20" x2="'+px+'" y2="'+(H-pad)+'" stroke="#0b539c" stroke-dasharray="3 3" opacity=".6"/><text x="'+(px+5)+'" y="32" font-size="11" fill="#0b539c" font-family="monospace">'+txt+'</text>';};
    dens.setAttribute('viewBox','0 0 '+W+' '+H); dens.setAttribute('width','100%');
    dens.innerHTML=g+'<path d="'+path+'" fill="rgba(11,83,156,.12)" stroke="#0b539c" stroke-width="1.5"/>'+ann(488,'~500 km')+ann(812,'~800 km');
  }
  const op = document.getElementById('opbars');
  if(op){const max=Math.max.apply(null,D.operators.map(o=>o[1]));
    op.innerHTML=D.operators.map(o=>'<div class="row"><div class="nm">'+o[0]+'</div><div class="tr"><div class="fl" style="width:'+(o[1]/max*100)+'%;background:'+(o[0].indexOf('Unattr')>=0?'#8a5a12':'#0b539c')+'"></div></div><div class="vv">'+o[1]+'%</div></div>').join('');
  }
})();
