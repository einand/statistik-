const assert=require('node:assert/strict'),E=require('../dist/assets/score-engine.js');
const near=(a,b)=>assert(Math.abs(a-b)<1e-8,`${a} != ${b}`);
assert.deepEqual(E.percentilePoints({a:1,b:1,c:3},1),{a:25,b:25,c:100});assert.deepEqual(E.percentilePoints({a:1,b:1,c:3},-1),{a:75,b:75,c:0});assert.deepEqual(E.percentilePoints({a:7,b:7,c:7},1),{a:50,b:50,c:50});
const input={maxAge:5,municipalities:Object.fromEntries(Array.from({length:6},(_,i)=>[String(i),{name:'Kommun '+i}])),series:{},metadata:{}};
for(const spec of Object.values(E.METRICS))for(const key of spec.keys){input.series[key]={2025:Object.fromEntries(Array.from({length:6},(_,i)=>[String(i),spec.direction===1?i:5-i]))};}
let r=E.build(input,2026);assert.equal(r.ranked,6);assert.equal(r.rows[0].code,'5');assert.equal(r.rows[0].score,100);assert.equal(r.rows.at(-1).score,0);assert.equal(r.rows[0].rank,1);assert.equal(r.rows.at(-1).rank,6);
assert.equal(E.build(input,2024).ranked,0,'future observations must not leak');assert.equal(E.build(input,2031).ranked,0,'old observations must expire');
let x=structuredClone(input);delete x.series.unsafe[2025]['5'];assert.equal(E.build(x,2026).rows.find(r=>r.code==='5').score,null,'a missing whole theme must prevent ranking');const ignoreSafety={...E.DEFAULT_WEIGHTS,safety:0};assert.equal(E.build(x,2026,ignoreSafety).rows[0].code,'5');
x=structuredClone(input);delete x.series.lifeMale[2025]['5'];const h=E.build(x,2026).rows.find(r=>r.code==='5');assert.equal(h.themes.find(t=>t.id==='health').coverage,.5);near(h.coverage,.925);assert.equal(h.eligible,true);assert.equal(E.metricObservation(x,'life',2026,'5'),null,'one sex must not replace the two-part life measure');
x=structuredClone(input);for(const key in x.series)x.series[key][2025]['4']=x.series[key][2025]['5'];r=E.build(x,2026);assert.equal(r.rows[0].rank,1);assert.equal(r.rows[1].rank,1);assert.equal(r.rows[2].rank,3,'competition ranks after tied displayed scores');
assert.throws(()=>E.build(input,2026,Object.fromEntries(E.THEMES.map(t=>[t.id,0]))));
for(const row of r.rows){assert(row.score>=0&&row.score<=100);assert(!/[0-9]/.test(row.comment),'plain comments have no numbers');}
const live=require('../dist/data/score-input.json'),current=E.build(live,2026);assert.equal(current.rows.length,290);assert(current.ranked>200);for(const row of current.rows)for(const t of row.themes)for(const m of t.metrics)if(m.year!=null){assert(m.year<=2026);assert(2026-m.year<=5);}
console.log('PASS percentile direction/ties, historical cutoff, missing themes, life denominator, coverage, custom weights and real municipal data.');
