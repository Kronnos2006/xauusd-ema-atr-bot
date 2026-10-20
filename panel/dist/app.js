'use strict';
const $ = id => document.getElementById(id);
const colors = {history:'#9ba99d',kronos:'#d68d48',timesfm:'#7299cb',ensemble:'#218669'};
const fmt = (x, digits=3) => Number(x).toLocaleString('es-CR',{minimumFractionDigits:digits,maximumFractionDigits:digits});
const pct = x => `${x>=0?'+':''}${fmt(x*100,3)} %`;
const date = x => {const [d,t] = x.replace('T',' ').split(' ');return `${d.slice(8,10)} ene · ${t.slice(0,5)}`;};
const stages = ['input','kronos','timesfm','combine','verify'];
const explanations = {
  input:['UN PASADO COMPARTIDO','Se construyen 400 velas horarias con una tendencia suave y una oscilación. Es una serie artificial; ambos modelos reciben el mismo período.','400 velas · intervalo de 1 hora'],
  kronos:['EL MODELO DE VELAS','Kronos recibe apertura, máximo, mínimo, cierre, volumen e importe. Genera 20 trayectorias y promedia sus cierres futuros.','OHLCVA → 20 trayectorias → media'],
  timesfm:['EL MODELO DE SERIES','TimesFM 2.5 recibe únicamente los 400 cierres de esas mismas velas. Se extrae su pronóstico puntual mediano para las próximas cuatro horas.','400 cierres → 4 cierres previstos'],
  combine:['UNA COMBINACIÓN EXPLÍCITA','Cada retorno previsto se calcula desde el mismo último cierre. Se promedian al 50/50; no hay ajuste de pesos según los resultados.','r = 0,5 × rK + 0,5 × rT'],
  verify:['COMPROBAR ANTES DE MOSTRAR','Se comprueban fechas coincidentes, formas y valores finitos. Se guardan los resultados y las huellas SHA256 de los tres archivos de pesos.','Fechas + valores + revisiones + SHA256']
};
let state = null, result = null, horizon = 4, guide = null, timer = null, running = false, selected = 'combine', pollId = null, chartGeometry = null;

function toast(text){$('toast').textContent=text;$('toast').hidden=false;setTimeout(()=>$('toast').hidden=true,4000);}
function stepDetail(stage){
  selected=stage;
  const [title,body,formula]=explanations[stage]||explanations.combine;
  $('step-detail').replaceChildren();
  for(const [tag,cls,text] of [['span','eyebrow',title],['p','',body],['code','',formula]]){
    const element=document.createElement(tag);element.className=cls;element.textContent=text;$('step-detail').append(element);
  }
  document.querySelectorAll('.step').forEach(el=>el.classList.toggle('active',el.dataset.step===stage));
}
function svgEl(tag,attributes={},text){
  const el=document.createElementNS('http://www.w3.org/2000/svg',tag);
  for(const [key,value] of Object.entries(attributes))el.setAttribute(key,value);
  if(text!==undefined)el.textContent=text;return el;
}
function path(points){return points.map((p,i)=>`${i?'L':'M'}${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(' ');}
function spark(id,values,color){
  const svg=$(id);svg.replaceChildren();const lo=Math.min(...values),hi=Math.max(...values),span=hi-lo||1;
  const points=values.map((v,i)=>[i*120/(values.length-1),29-(v-lo)/span*24]);
  svg.append(svgEl('path',{d:path(points),fill:'none',stroke:color,'stroke-width':1.8,'stroke-linecap':'round','stroke-linejoin':'round'}));
}
function cards(){
  if(!result)return;
  const last=result.forecast.at(-1),base=result.history.at(-1).close;
  for(const [id,key,color] of [['k','kronos',colors.kronos],['t','timesfm',colors.timesfm],['e','ensemble',colors.ensemble]]){
    $(id+'-value').textContent=fmt(last[key+'_close']);
    $(id+'-return').textContent=pct(last[key+'_return']);
    $(id+'-return').classList.toggle('negative',last[key+'_return']<0);
    spark(id+'-spark',[base,...result.forecast.map(row=>row[key+'_close'])],color);
  }
  $('base-close').textContent=fmt(base);$('formula-k').textContent=pct(last.kronos_return);
  $('formula-t').textContent=pct(last.timesfm_return);$('formula-result').textContent='= '+pct(last.ensemble_return);
  $('forecast-table').replaceChildren();
  result.forecast.forEach((row,i)=>{
    const tr=document.createElement('tr');tr.className=i+1===horizon?'selected':'';
    for(const text of [`+${i+1} h`,fmt(row.kronos_close),fmt(row.timesfm_close),fmt(row.ensemble_close),pct(row.ensemble_return)]){
      const td=document.createElement('td');td.textContent=text;tr.append(td);
    }
    tr.tabIndex=0;tr.setAttribute('aria-label',`Mostrar horizonte ${i+1} horas`);
    const activate=()=>{stopReplay();guide=null;setHorizon(i+1);};
    tr.addEventListener('click',activate);tr.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();activate();}});
    $('forecast-table').append(tr);
  });
  const report=result.report;
  const entries={'Tipo de datos':'Sintéticos · KT-001','Contexto':'400 velas de 1 hora','Horizonte':'4 horas','Kronos':'20 trayectorias · T=1 · top_p=0,9','TimesFM':'2.5 · 200M · mediana','Pesos':'50 % Kronos / 50 % TimesFM','Dispositivo':'CPU · '+(report.torch_threads||4)+' hilos','Semilla':String(report.seed),'Rentabilidad':'No evaluada','Resultado':report.status};
  fillDl('parameters',entries);fillDl('revisions',report.revisions);
  for(const [name,hash] of Object.entries(report.sha256||{})){
    const dt=document.createElement('dt');dt.textContent='SHA256 · '+name.split('@')[0].split('/').at(-1);
    const dd=document.createElement('dd');dd.textContent=hash;$('revisions').append(dt,dd);
  }
  $('duration').textContent=fmt(report.elapsed_seconds,2)+' s';
  $('run-time').textContent=report.created_at?new Date(report.created_at).toLocaleString('es-CR',{timeZone:'America/Costa_Rica',dateStyle:'short',timeStyle:'short'}):'Evidencia guardada · KT-001';
  $('source-caption').textContent=result.source==='ejecucion_local'?'Salida de ejecución local':'Evidencia sintética guardada';
}
function fillDl(id,entries){
  $(id).replaceChildren();for(const [label,value] of Object.entries(entries)){
    const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=label;dd.textContent=value;$(id).append(dt,dd);
  }
}
function visibleModel(key){
  const guideAllows=guide===null|| (key==='kronos'&&guide>=1)||(key==='timesfm'&&guide>=2)||(key==='ensemble'&&guide>=3);
  return $('show-'+({kronos:'k',timesfm:'t',ensemble:'e'}[key])).checked&&guideAllows;
}
function draw(){
  if(!result)return;
  const svg=$('chart');svg.replaceChildren();$('tooltip').hidden=true;
  const count=Number($('window').value),hist=result.history.slice(-count),base=hist.at(-1).close;
  const W=900,H=340,L=14,R=68,T=40,B=45,plotW=W-L-R,plotH=H-T-B;
  const forecast=result.forecast.slice(0,horizon);
  const values=hist.flatMap(row=>[row.high,row.low]);
  for(const key of ['kronos','timesfm','ensemble'])if(visibleModel(key))values.push(...forecast.map(row=>row[key+'_close']));
  const min=Math.min(...values),max=Math.max(...values),pad=Math.max((max-min)*.13,.08),low=min-pad,high=max+pad;
  const x=i=>L+i/(hist.length+4-1)*plotW,y=v=>T+(high-v)/(high-low)*plotH;
  const boundary=x(hist.length-1),endX=x(hist.length+3);
  const defs=svgEl('defs'),gradient=svgEl('linearGradient',{id:'context-fill',x1:'0',y1:'0',x2:'0',y2:'1'});
  gradient.append(svgEl('stop',{offset:'0%','stop-color':'#b3c4b5','stop-opacity':'.17'}),svgEl('stop',{offset:'100%','stop-color':'#b3c4b5','stop-opacity':'0'}));defs.append(gradient);svg.append(defs);
  svg.append(svgEl('rect',{x:boundary,y:T-17,width:endX-boundary,height:plotH+17,fill:'#f0f7ef'}));
  for(let i=0;i<5;i++){
    const val=low+(high-low)*i/4,py=y(val);
    svg.append(svgEl('line',{x1:L,x2:W-R+5,y1:py,y2:py,stroke:'#edf0ea','stroke-width':1,'stroke-dasharray':'3 5'}));
    svg.append(svgEl('text',{x:W-R+15,y:py+3},fmt(val,2)));
  }
  const pts=hist.map((row,i)=>[x(i),y(row.close)]);
  svg.append(svgEl('path',{d:path(pts)+` L${x(hist.length-1)},${H-B} L${L},${H-B} Z`,fill:'url(#context-fill)'}));
  // Las velas mantienen OHLC sintetico; la linea suaviza la lectura en vista amplia.
  const candleWidth=Math.min(6,plotW/(hist.length+4)*.35);
  if(count<=72){hist.forEach((row,i)=>{
    const color=row.close>=row.open?'#93b09b':'#bec5b7';
    svg.append(svgEl('line',{x1:x(i),x2:x(i),y1:y(row.high),y2:y(row.low),stroke:color,'stroke-width':1,opacity:.6}));
    svg.append(svgEl('rect',{x:x(i)-candleWidth/2,y:Math.min(y(row.close),y(row.open)),width:candleWidth,height:Math.max(1,Math.abs(y(row.close)-y(row.open))),fill:color,opacity:.65}));
  });}
  svg.append(svgEl('path',{d:path(pts),fill:'none',stroke:colors.history,'stroke-width':1.9,'stroke-linejoin':'round'}));
  svg.append(svgEl('line',{x1:boundary,x2:boundary,y1:T-14,y2:H-B,stroke:'#b1c6ae','stroke-dasharray':'4 5'}));
  svg.append(svgEl('text',{x:boundary-9,y:17,'text-anchor':'end',fill:'#8fa087'},'ÚLTIMO CIERRE'));
  svg.append(svgEl('text',{x:boundary+9,y:31,fill:'#75916c'},'+ PRONÓSTICO'));
  for(const key of ['kronos','timesfm','ensemble']){
    if(!visibleModel(key))continue;
    const fp=[[boundary,y(base)],...forecast.map((row,i)=>[x(hist.length+i),y(row[key+'_close'])])];
    svg.append(svgEl('path',{d:path(fp),fill:'none',stroke:colors[key],'stroke-width':key==='ensemble'?3:2,'stroke-dasharray':key==='ensemble'?'none':'5 4','stroke-linecap':'round','stroke-linejoin':'round'}));
    fp.slice(1).forEach(p=>svg.append(svgEl('circle',{cx:p[0],cy:p[1],r:key==='ensemble'?3.5:2.6,fill:'white',stroke:colors[key],'stroke-width':1.8})));
  }
  const labels=new Set([0,Math.floor(hist.length/3),Math.floor(2*hist.length/3),hist.length-1]);
  for(const i of labels){svg.append(svgEl('text',{x:x(i),y:H-16,'text-anchor':i===0?'start':'middle'},date(hist[i].timestamp)));}
  for(let i=0;i<4;i++){
    svg.append(svgEl('text',{x:x(hist.length+i),y:H-16,'text-anchor':'middle',fill:'#8ea084'},`+${i+1} h`));
  }
  const cross=svgEl('line',{id:'crosshair',x1:0,x2:0,y1:T,y2:H-B,stroke:'#90a590','stroke-dasharray':'3 4',visibility:'hidden'});svg.append(cross);
  const marker=svgEl('circle',{id:'hover-marker',r:4,fill:'white',stroke:'#78997b','stroke-width':2,visibility:'hidden'});svg.append(marker);
  chartGeometry={x,y,L,R,T,B,plotW,hist,forecast,base,W,H};
}
function hover(event){
  if(!chartGeometry)return;
  const g=chartGeometry,rect=$('chart').getBoundingClientRect();
  const px=(event.clientX-rect.left)/rect.width*g.W;
  let i=Math.round((px-g.L)/g.plotW*(g.hist.length+3));i=Math.max(0,Math.min(i,g.hist.length+Math.max(horizon-1,-1)));
  const isFuture=i>=g.hist.length,row=isFuture?result.forecast[i-g.hist.length]:g.hist[i];if(!row)return;
  const cross=$('crosshair'),marker=$('hover-marker');cross.setAttribute('x1',g.x(i));cross.setAttribute('x2',g.x(i));cross.setAttribute('visibility','visible');
  marker.setAttribute('cx',g.x(i));marker.setAttribute('cy',g.y(isFuture?row.ensemble_close:row.close));marker.setAttribute('visibility','visible');
  const tip=$('tooltip');tip.replaceChildren();const title=document.createElement('strong');title.textContent=isFuture?`Pronóstico +${i-g.hist.length+1} h · ${date(row.timestamp)}`:date(row.timestamp)+' · entrada sintética';tip.append(title);
  const entries=isFuture?[['Kronos',fmt(row.kronos_close)],['TimesFM',fmt(row.timesfm_close)],['Combinación',fmt(row.ensemble_close)],['Retorno previsto',pct(row.ensemble_return)]]:[['Apertura',fmt(row.open)],['Máximo',fmt(row.high)],['Mínimo',fmt(row.low)],['Cierre',fmt(row.close)],['Volumen',fmt(row.volume,1)]];
  for(const [label,value] of entries){const line=document.createElement('div');line.className='tooltip-row';const a=document.createElement('span'),b=document.createElement('b');a.textContent=label;b.textContent=value;line.append(a,b);tip.append(line);}
  tip.hidden=false;const box=$('chart-box').getBoundingClientRect();tip.style.left=Math.min(Math.max(0,event.clientX-box.left+12),box.width-200)+'px';tip.style.top='40px';
}
function leave(){ $('tooltip').hidden=true;for(const id of ['crosshair','hover-marker'])$(id)?.setAttribute('visibility','hidden');}
function setHorizon(value){
  horizon=Number(value);$('horizon').value=horizon;$('horizon-value').textContent=horizon?`+${horizon} h`:'Contexto';
  if(guide===null&&!running)$('guide-note').textContent=horizon?`Mostrando ${horizon} de los 4 pasos futuros. Las tarjetas resumen siempre el horizonte +4 h.`:'Solo contexto de entrada; los pronósticos están ocultos.';
  cards();draw();
}
function stopReplay(){if(timer)clearInterval(timer);timer=null;$('play').innerHTML='<span>▶</span> Paso a paso';}
function play(){
  if(timer){stopReplay();return;}
  guide=0;setHorizon(0);stepDetail('input');$('guide-note').textContent='01 · Los dos modelos parten del mismo pasado. No reciben datos futuros.';
  $('play').innerHTML='<span>Ⅱ</span> Pausar guía';let step=0;
  timer=setInterval(()=>{
    step++;
    if(step===1){guide=1;stepDetail('kronos');setHorizon(4);$('guide-note').textContent='02 · La línea naranja muestra el promedio de 20 trayectorias de Kronos.';}
    else if(step===2){guide=2;stepDetail('timesfm');draw();$('guide-note').textContent='03 · La línea azul muestra los cierres previstos por TimesFM.';}
    else if(step===3){guide=3;stepDetail('combine');setHorizon(0);$('guide-note').textContent='04 · Observa cómo el promedio fijo une ambos pronósticos, hora por hora.';}
    else if(step<=7){setHorizon(step-3);}
    else{guide=null;stepDetail('verify');draw();$('guide-note').textContent='Guía completada. La animación reproduce resultados ya calculados; no ejecuta los modelos.';stopReplay();}
  },1300);
}
function renderJob(){
  const job=state.job;running=job.status==='running';
  $('run').disabled=running||!state.engine_available;
  $('run').innerHTML=running?'<span class="run-icon">◌</span> Ejecutando…':'<span class="run-icon">▶</span> Ejecutar demo sintética';
  $('execution').classList.toggle('running',running);$('execution').classList.toggle('error',job.status==='error');
  const active=stages.indexOf(job.stage);
  document.querySelectorAll('.step').forEach(el=>el.classList.toggle('pending',running&&stages.indexOf(el.dataset.step)>active));
  if(running){
    stepDetail(stages.includes(job.stage)?job.stage:'input');
    $('execution-title').textContent=job.kind==='market'?'Pronóstico prospectivo BTCUSDT en curso · CPU':'Inferencia sintética en curso · CPU';
    $('execution-message').textContent=job.events.at(-1)?.message||'Iniciando Python y cargando dependencias locales…';
    $('duration').textContent=Math.max(0,Math.floor((Date.now()-Date.parse(job.started_at))/1000))+' s';
    $('run-time').textContent='Tiempo transcurrido';
    $('guide-note').textContent='Los gráficos conservan la última salida completa hasta que finalice la nueva ejecución.';
  }else if(job.status==='error'){
    $('execution-title').textContent='La ejecución no pudo completarse';$('execution-message').textContent=job.error;
  }else if(job.status==='done'){
    $('execution-title').textContent=job.kind==='market'?'Pronóstico BTC registrado; pendiente del mercado':'Inferencia sintética completada y verificada';$('execution-message').textContent=job.kind==='market'?'La nueva predicción está en Control cruzado. El gráfico sintético se conserva como demostración.':'Kronos + TimesFM · ejecución local sin conexión · cuatro horizontes alineados.';
    if(job.kind==='market'){
      $('duration').textContent=fmt((Date.parse(job.finished_at)-Date.parse(job.started_at))/1000,2)+' s';
      $('run-time').textContent='Registro BTC · '+new Date(job.finished_at).toLocaleTimeString('es-CR',{timeZone:'America/Costa_Rica'});
    }
    if(!timer)$('guide-note').textContent='Salida actualizada. Explora las capas o reproduce la explicación paso a paso.';
  }else if(!state.engine_available){
    $('execution-title').textContent='Explorando evidencia guardada';$('execution-message').textContent='El entorno Python no está disponible. Consulta panel/README.md para preparar el motor.';
  }
}
async function refresh(){
  try{
    const response=await fetch('/api/state');if(!response.ok)throw Error('No se pudo leer el motor');
    const incoming=await response.json();const changed=!result||JSON.stringify(incoming.result.report)!==JSON.stringify(result.report);
    state=incoming;result=incoming.result;
    if(changed){cards();draw();}
    renderJob();
    if(running){pollId=setTimeout(refresh,1000);}else{pollId=null;}
  }catch(error){
    $('execution-title').textContent='Sin conexión con el panel local';$('execution-message').textContent='Vuelve a iniciar panel/server.py y recarga la página.';$('run').disabled=true;toast(error.message);
  }
}
async function run(){
  stopReplay();guide=null;setHorizon(4);
  try{
    $('run').disabled=true;
    const response=await fetch('/api/run',{method:'POST',headers:{'X-Panel-Request':'1'}});
    if(!response.ok){const data=await response.json();throw Error(data.message||data.error);}
    if(pollId)clearTimeout(pollId);await refresh();
  }catch(error){toast(error.message);$('run').disabled=false;}
}
$('run').addEventListener('click',run);$('play').addEventListener('click',play);
$('horizon').addEventListener('input',e=>{stopReplay();guide=null;setHorizon(e.target.value);});
$('window').addEventListener('change',draw);
for(const id of ['show-k','show-t','show-e'])$(id).addEventListener('change',draw);
$('reset').addEventListener('click',()=>{stopReplay();guide=null;setHorizon(4);$('guide-note').textContent='Vista completa de las cuatro horas de pronóstico.';});
$('chart').addEventListener('pointermove',hover);$('chart').addEventListener('pointerleave',leave);
document.querySelectorAll('.step').forEach(el=>el.addEventListener('click',()=>{if(running)return;stopReplay();guide=null;stepDetail(el.dataset.step);draw();}));
$('guide-nav').addEventListener('click',()=>{$('flow').scrollIntoView({behavior:'smooth',block:'center'});stepDetail('input');});
$('details-nav').addEventListener('click',()=>{$('evidence').open=true;$('evidence').scrollIntoView({behavior:'smooth',block:'center'});});
$('export').addEventListener('click',()=>{
  if(!result)return;const blob=new Blob([JSON.stringify(result,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='KT-001-resultados-sinteticos.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
document.addEventListener('visibilitychange',()=>{if(!document.hidden&&!pollId)refresh();});
refresh();stepDetail('combine');
