'use strict';
let marketData=null,marketSelection=null;
const when=ms=>new Date(ms).toLocaleString('es-CR',{timeZone:'America/Costa_Rica',dateStyle:'short',timeStyle:'short'});
function paragraph(parent,text,className=''){const p=document.createElement('p');p.className=className;p.textContent=text;parent.append(p);return p;}
function marketDraw(record){
  const svg=$('market-chart');svg.replaceChildren();
  if(!record){svg.append(svgEl('text',{x:450,y:100,'text-anchor':'middle',fill:'#839580','font-size':13},'Sin emisiones de mercado. Crea la primera predicción para iniciar el registro.'));return;}
  const points=record.forecast,evals=record.evaluations;
  const vals=[record.base,...points.flatMap(p=>[p.kronos_close,p.timesfm_close,p.ensemble_close]),...evals.map(e=>e.actual_close)];
  const low=Math.min(...vals),high=Math.max(...vals),pad=Math.max((high-low)*.15,record.base*.0001);
  const x=i=>45+i*190,y=v=>175-(v-low+pad)/(high-low+2*pad)*135;
  for(let i=0;i<4;i++){const val=low-pad+(high-low+2*pad)*i/3;svg.append(svgEl('line',{x1:45,x2:805,y1:y(val),y2:y(val),stroke:'#e8eee5','stroke-dasharray':'3 5'}));svg.append(svgEl('text',{x:820,y:y(val)+4,fill:'#8b9c83','font-size':10},fmt(val,1)));}
  for(const key of ['kronos','timesfm','ensemble']){
    const p=[[x(0),y(record.base)],...points.map((f,i)=>[x(i+1),y(f[key+'_close'])])];
    svg.append(svgEl('path',{d:path(p),fill:'none',stroke:colors[key],'stroke-width':key==='ensemble'?3:1.8,'stroke-dasharray':key==='ensemble'?'none':'5 4'}));
  }
  const actual=[[x(0),y(record.base)],...evals.map(e=>[x(e.horizon),y(e.actual_close)])];
  svg.append(svgEl('path',{d:path(actual),fill:'none',stroke:'#253c34','stroke-width':2.5}));
  actual.forEach(p=>svg.append(svgEl('circle',{cx:p[0],cy:p[1],r:4,fill:'#253c34'})));
  for(let i=0;i<5;i++)svg.append(svgEl('text',{x:x(i),y:202,'text-anchor':'middle',fill:'#87967e','font-size':10},i?`+${i} h`:'Cierre base'));
  svg.append(svgEl('text',{x:45,y:18,fill:'#83947d','font-size':10},'Naranja: Kronos · Azul: TimesFM · Verde: combinación · Negro: mercado observado'));
}
function renderMarket(){
  const records=marketData.records,selectedRecord=records.find(r=>r.id===marketSelection)||records.at(-1);
  $('market-count').textContent=records.length;$('market-resolved').textContent=marketData.resolved_4h;
  const summary=marketData.summary.ensemble;
  $('market-hits').textContent=summary.n?`${summary.hits} / ${summary.n} (${fmt(summary.hits/summary.n*100,1)} %)`:'Sin resultados';
  $('market-mae').textContent=summary.mae_usdt===null?'Pendiente':fmt(summary.mae_usdt,2)+' USDT';
  const select=$('market-record');select.replaceChildren();
  if(!records.length){const opt=document.createElement('option');opt.textContent='Sin predicciones';select.append(opt);}
  records.forEach(r=>{const opt=document.createElement('option');opt.value=r.id;opt.textContent=when(r.issued_ms)+' · '+r.id;opt.selected=r===selectedRecord;select.append(opt);});
  $('market-suggestions').replaceChildren();for(const suggestion of marketData.suggestions){const li=document.createElement('li');li.textContent=suggestion;$('market-suggestions').append(li);}
  $('market-monitor').textContent=marketData.monitoring+' '+(marketData.last_check_ms?'Última revisión: '+when(marketData.last_check_ms)+'. ':'')+'Resumen solo +4 h; los cuatro horizontes de una emisión no son ensayos independientes.';
  $('market-status').classList.toggle('market-error',Boolean(marketData.error));
  if(!running)$('market-status').textContent=marketData.error?'No se pudo consultar el mercado: '+marketData.error:selectedRecord?`${selectedRecord.evaluations.length}/4 cierres contrastados. Los demás siguen pendientes.`:'Listo para registrar una predicción antes de conocer sus resultados.';
  $('market-table').replaceChildren();$('market-diagnosis').replaceChildren();$('market-probability').replaceChildren();
  marketDraw(selectedRecord);
  if(!selectedRecord){paragraph($('market-diagnosis'),'Sin resultados de mercado todavía. Los ejemplos sintéticos no se cuentan como aciertos.');paragraph($('market-probability'),'No hay probabilidad de acierto calibrada. Se registrará la dispersión del modelo antes de ver el mercado.');return;}
  $('market-issued').textContent='Emitida '+when(selectedRecord.issued_ms)+' · SHA256 '+selectedRecord.sha256.slice(0,12)+'… · '+fmt(selectedRecord.lead_to_first_close_minutes,1)+' min hasta el primer cierre';
  selectedRecord.forecast.forEach(f=>{
    const evaluation=selectedRecord.evaluations.find(e=>e.horizon===f.horizon),tr=document.createElement('tr');
    const values=[`+${f.horizon} h · ${when(f.target_close_ms)}`,fmt(f.kronos_close,2),fmt(f.timesfm_close,2),fmt(f.ensemble_close,2),evaluation?fmt(evaluation.actual_close,2):'Pendiente',evaluation?(evaluation.models.ensemble.direction_correct?'Dirección ✓':'Dirección ✕'):'Esperando cierre'];
    for(const text of values){const td=document.createElement('td');td.textContent=text;tr.append(td);}$('market-table').append(tr);
    if(evaluation){
      paragraph($('market-diagnosis'),`+${f.horizon} h · cierre real ${fmt(evaluation.actual_close,2)} USDT`,'analysis-title');
      for(const [model,title] of [['kronos','Kronos'],['timesfm','TimesFM'],['ensemble','Combinación']]){
        const m=evaluation.models[model];const scoreText=m.price_score===null?'sin puntuación relativa (mercado sin cambio)':`score precio ${fmt(m.price_score,1)}`;
        paragraph($('market-diagnosis'),`${title}: ${m.direction_correct?'dirección acertada':'dirección fallida'} · error ${fmt(m.absolute_error_usdt,2)} USDT (${fmt(m.error_bps,2)} pb) · ${scoreText}. ${m.diagnosis}`);
      }
      const e=evaluation.models.ensemble;
      paragraph($('market-diagnosis'),`Aporte del promedio: reduce el error frente a Kronos en ${fmt(e.vs_kronos_usdt,2)} USDT y frente a TimesFM en ${fmt(e.vs_timesfm_usdt,2)} USDT. Un valor negativo significa que lo empeora.`);
    }
    paragraph($('market-probability'),`+${f.horizon} h: ${Math.round(f.kronos_up_fraction*20)}/20 trayectorias de Kronos subían (${fmt(f.kronos_up_fraction*100,0)} % simulado, no calibrado). TimesFM q10–q90: ${fmt(f.timesfm_q10,2)}–${fmt(f.timesfm_q90,2)} USDT${evaluation?`; cierre ${evaluation.timesfm_inside_q10_q90?'dentro':'fuera'} del intervalo; Brier simulado Kronos ${fmt(evaluation.kronos_brier,3)}`:'. Resultado todavía pendiente.'}`);
  });
  if(!selectedRecord.evaluations.length)paragraph($('market-diagnosis'),'Las predicciones ya están registradas. El primer análisis se escribirá después del cierre objetivo; no existe un acierto o fallo observado todavía.');
  paragraph($('market-probability'),'q10–q90 es un intervalo nominal del 80 %, no una cobertura demostrada en BTC. Brier más bajo es mejor; no certifica calibración. El promedio 50/50 no tiene una probabilidad conjunta estimada.');
}
async function marketRefresh(){
  try{const response=await fetch('/api/market');marketData=await response.json();if(!response.ok)throw Error(marketData.error);renderMarket();}
  catch(error){$('market-status').textContent='Registro no disponible: '+error.message;$('market-status').classList.add('market-error');}
  $('market-run').disabled=running||Boolean(marketData?.records?.some(r=>r.evaluations.length<4));
}
async function marketAction(pathName){
  $('market-run').disabled=true;$('market-check').disabled=true;
  $('market-status').textContent=pathName.endsWith('run')?'Consultando contexto e iniciando inferencia prospectiva…':'Consultando cierres ya vencidos…';
  try{const response=await fetch(pathName,{method:'POST',headers:{'X-Panel-Request':'1'}});const data=await response.json();if(!response.ok)throw Error(data.error||data.message);if(pathName.endsWith('run')){if(pollId)clearTimeout(pollId);await refresh();}}
  catch(error){toast(error.message);$('market-status').textContent=error.message;}
  $('market-check').disabled=false;await marketRefresh();
}
$('market-run').addEventListener('click',()=>marketAction('/api/market-run'));
$('market-check').addEventListener('click',()=>marketAction('/api/market-check'));
$('market-record').addEventListener('change',event=>{marketSelection=event.target.value;renderMarket();});
setInterval(()=>{if(running&&state?.job?.kind==='market')$('market-status').textContent=state.job.events.at(-1)?.message||'Cargando modelos…';marketRefresh();},5000);
marketRefresh();
