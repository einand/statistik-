/* Only years with a finite municipal score are displayed. */
(function(root){'use strict';
root.scoreChart=function(series,selectedYear){
 const nf=new Intl.NumberFormat('sv-SE',{maximumFractionDigits:1}),valid=series.filter(p=>Number.isFinite(p.score));
 if(!valid.length)return '<small>Ingen poänghistorik med tillräckligt underlag.</small>';
 const first=valid[0].year,last=valid[valid.length-1].year,x=year=>valid.length===1?150:28+valid.findIndex(p=>p.year===year)/(valid.length-1)*244,y=s=>102-s*.8;
 let path='',drawing=false;
 for(const p of valid){path+=(drawing?'L':'M')+x(p.year).toFixed(1)+' '+y(p.score).toFixed(1)+' ';drawing=true;}
 const points=valid.map(p=>'<circle cx="'+x(p.year)+'" cy="'+y(p.score)+'" r="'+(p.year===selectedYear?4:2)+'" fill="'+(p.year===selectedYear?'#a45c28':'#42705a')+'"><title>'+p.year+': '+nf.format(p.score)+' poäng</title></circle>').join('');
 return '<figure style="margin:10px 0;max-width:440px;min-width:0"><figcaption style="font-size:.8rem">Poäng över tid · år med underlag</figcaption><svg viewBox="0 0 300 130" role="img" aria-label="Boendepoäng för tillgängliga år från '+first+' till '+last+'. Skala noll till hundra. Exakta värden finns i årslistan nedanför." style="display:block;width:100%;min-width:100px;height:auto">'+[0,50,100].map(n=>'<line x1="28" x2="272" y1="'+y(n)+'" y2="'+y(n)+'" stroke="currentColor" opacity=".18"/><text x="23" y="'+(y(n)+3)+'" text-anchor="end" fill="currentColor" font-size="9">'+n+'</text>').join('')+'<path d="'+path+'" fill="none" stroke="#42705a" stroke-width="2"/>'+points+'<text x="28" y="120" fill="currentColor" font-size="10">'+first+'</text><text x="272" y="120" text-anchor="end" fill="currentColor" font-size="10">'+last+'</text></svg><details style="font-size:.75rem"><summary>Alla års poäng</summary>'+valid.map(p=>'<div>'+p.year+': '+(Number.isFinite(p.score)?nf.format(p.score)+' poäng':'För lite underlag')+'</div>').join('')+'</details></figure>';
};
})(window);
