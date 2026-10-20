"""Registro prospectivo descriptivo. GET publico; ninguna operacion de trading."""
import hashlib
import json
import math
from pathlib import Path
import threading
import time
import urllib.parse
import urllib.request

HOUR = 3600000
ENDPOINT = 'https://data-api.binance.vision'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def get_public(path, **params):
    if path not in ['/api/v3/time', '/api/v3/klines']:
        raise ValueError('Endpoint no autorizado')
    url = ENDPOINT+path+('?' + urllib.parse.urlencode(params) if params else '')
    request = urllib.request.Request(url, headers={'User-Agent':'KT-002-local-research/1.0'})
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read(2000000)
    return json.loads(raw), dict(url=url, sha256=hashlib.sha256(raw).hexdigest(), captured_ms=int(time.time()*1000))


def validate_candles(rows, now):
    closed = [row for row in rows if int(row[6]) < now]
    for i, row in enumerate(closed):
        opening = int(row[0]); end = int(row[6])
        o, h, l, c, v = map(float, row[1:6])
        amount = float(row[7])
        if opening % HOUR or end != opening+HOUR-1:
            raise ValueError('Intervalo de vela inconsistente')
        if not all(math.isfinite(x) for x in [o,h,l,c,v,amount]) or min(o,h,l,c)<=0 or min(v,amount)<0:
            raise ValueError('OHLCV no valido')
        if h<max(o,c) or l>min(o,c) or h<l:
            raise ValueError('Limites OHLC inconsistentes')
        if i and opening != int(closed[i-1][0])+HOUR:
            raise ValueError('Hueco o duplicado en velas')
    return closed


def direction(value):
    return 1 if value>0 else -1 if value<0 else 0


def score(base, predicted, actual):
    error = abs(predicted-actual)
    baseline = abs(base-actual)
    return dict(direction_correct=direction(predicted-base)==direction(actual-base),
                absolute_error_usdt=error, error_bps=error/base*10000,
                contribution_usdt=baseline-error,
                price_score=None if baseline<1e-9 else 100*(1-error/baseline),
                actual_return=actual/base-1, predicted_return=predicted/base-1)


def diagnose(base, predicted, actual, contribution):
    if direction(predicted-base)==direction(actual-base) and contribution>=0:
        return f'Aporte observado: direccion acertada y reduccion de {contribution:.2f} USDT en el error frente a mantener el ultimo cierre. No implica rentabilidad.'
    if direction(predicted-base)!=direction(actual-base):
        detail='Fallo de direccion: el mercado cerro en un sentido distinto al previsto.'
    elif abs(predicted-actual)<1e-9:
        detail='Direccion y precio coinciden con el cierre observado.'
    else:
        detail='Direccion acertada; '+('sobreestimo' if abs(predicted-base)>abs(actual-base) else 'subestimo')+' la magnitud del movimiento.'
    detail += ' '+('Redujo' if contribution>0 else 'Aumento' if contribution<0 else 'Igualo')+' el error frente a mantener el ultimo cierre.'
    return detail+' Las causas externas del movimiento no se pueden determinar con estos datos.'


class MarketLedger:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.last_check_ms = None
        self.last_error = None

    def exclusive(self, path, value):
        # Nombre exclusivo y flush: nunca sustituir un pronostico/evaluacion existente.
        with path.open('x', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.flush()
            import os
            os.fsync(stream.fileno())

    def records(self):
        result=[]
        for file in sorted(self.root.glob('*/forecast.json')):
            obj=json.loads(file.read_text(encoding='utf-8'))
            data=obj['prediction']
            if digest(data)!=obj['sha256']:
                raise ValueError('Huella del pronostico no coincide: '+file.parent.name)
            context_path=file.parent/'context.json'
            if context_path.exists() and digest(json.loads(context_path.read_text(encoding='utf-8')))!=data['context_sha256']:
                raise ValueError('Huella del contexto no coincide: '+file.parent.name)
            evaluations=[]
            for evaluation in sorted(file.parent.glob('evaluation-*.json')):
                checked=json.loads(evaluation.read_text(encoding='utf-8'))
                if checked['forecast_sha256']!=obj['sha256'] or digest(checked['assessment'])!=checked['sha256']:
                    raise ValueError('Huella de evaluacion inconsistente')
                evaluations.append(checked['assessment'])
            result.append(dict(**data, sha256=obj['sha256'], evaluations=evaluations))
        return result

    def snapshot(self):
        with self.lock:
            records=self.records()
            final=[e for r in records for e in r['evaluations'] if e['horizon']==4]
            metrics={}
            for name in ['kronos','timesfm','ensemble']:
                items=[e['models'][name] for e in final]
                metrics[name]=dict(n=len(items),hits=sum(x['direction_correct'] for x in items),
                    mae_usdt=sum(x['absolute_error_usdt'] for x in items)/len(items) if items else None,
                    contribution_usdt=sum(x['contribution_usdt'] for x in items)/len(items) if items else None)
            suggestions=['Todavia no hay 30 emisiones resueltas a +4 h. Recopilar evidencia antes de proponer ajustes de modelos.']
            if len(final)>=30:
                suggestions=[]
                for model in metrics:
                    if metrics[model]['contribution_usdt']<=0:
                        suggestions.append(f'Revisar el aporte de {model}: no supera persistencia en error medio. Proponer un ensayo futuro separado; no ajustar este registro.')
                suggestions.append('Auditar calibracion de probabilidades y cobertura por periodo en una muestra futura separada. No se aplico ningun cambio.')
            return dict(records=records, summary=metrics, resolved_4h=len(final),
                last_check_ms=self.last_check_ms,error=self.last_error,suggestions=suggestions,
                monitoring='Consulta cada 60 s mientras el servidor local este activo. Sin tareas de Windows.',
                protocol='KT-002 v1 · registro prospectivo descriptivo, sin PnL')

    def prepare(self, directory):
        with self.lock:
            records=self.records()
            if any(len(r['evaluations'])<4 for r in records):
                raise ValueError('Hay una prediccion pendiente. Espera sus cuatro cierres para evitar ventanas solapadas.')
            clock, clock_source=get_public('/api/v3/time')
            now=int(clock['serverTime'])
            if abs(now-int(time.time()*1000))>120000:
                raise ValueError('Reloj local y exchange difieren mas de dos minutos')
            raw, source=get_public('/api/v3/klines',symbol='BTCUSDT',interval='1h',limit=401)
            rows=validate_candles(raw,now)[-400:]
            if len(rows)!=400 or now-(int(rows[-1][6])+1)>=HOUR:
                raise ValueError('Contexto incompleto o desactualizado')
            cutoff=int(rows[-1][6])+1
            if any(r['cutoff_ms']==cutoff for r in records):
                raise ValueError('Ese cierre de contexto ya tiene un pronostico registrado')
            context=dict(symbol='BTCUSDT',interval='1h',cutoff_ms=cutoff,base=float(rows[-1][4]),
                raw=raw,rows=rows,source=source,clock_source=clock_source,captured_ms=now)
            self.exclusive(directory/'context.json',context)
            return context

    def seal(self, directory):
        with self.lock:
            context=json.loads((directory/'context.json').read_text(encoding='utf-8'))
            generated=json.loads((directory/'generated.json').read_text(encoding='utf-8'))
            clock,_=get_public('/api/v3/time')
            now=int(clock['serverTime'])
            if now>=context['cutoff_ms']+HOUR:
                raise ValueError('La primera hora objetivo ya vencio; no se registra como prediccion prospectiva')
            if len(generated['forecast'])!=4:
                raise ValueError('Se requieren cuatro horizontes')
            for horizon,row in enumerate(generated['forecast'],1):
                if row['horizon']!=horizon or row['target_close_ms']!=context['cutoff_ms']+horizon*HOUR:
                    raise ValueError('Fechas objetivo inconsistentes')
                for name in ['kronos_close','timesfm_close','ensemble_close','timesfm_q10','timesfm_q90']:
                    if not math.isfinite(row[name]) or row[name]<=0:
                        raise ValueError('Pronostico no finito o no positivo')
                if not 0<=row['kronos_up_fraction']<=1 or row['timesfm_q10']>row['timesfm_q90']:
                    raise ValueError('Dispersion no valida')
                if abs(row['ensemble_close']-(row['kronos_close']+row['timesfm_close'])/2)>1e-6:
                    raise ValueError('Pesos distintos de 50/50')
            if abs(now-int(time.time()*1000))>120000:
                raise ValueError('Reloj desincronizado')
            data=dict(id=directory.name,variant='KT-002',symbol='BTCUSDT',issued_ms=now,
                cutoff_ms=context['cutoff_ms'],base=context['base'],context_sha256=digest(context),
                source=context['source'],lead_to_first_close_minutes=(context['cutoff_ms']+HOUR-now)/60000,
                **generated)
            self.exclusive(directory/'forecast.json',dict(prediction=data,sha256=digest(data)))
            return data

    def reconcile(self):
        with self.lock:
            try:
                records=self.records()
                pending=[r for r in records if len(r['evaluations'])<4]
                if not pending:
                    self.last_check_ms=int(time.time()*1000);self.last_error=None;return
                clock,_=get_public('/api/v3/time');now=int(clock['serverTime'])
                for record in pending:
                    done={e['horizon'] for e in record['evaluations']}
                    due=[f for f in record['forecast'] if f['horizon'] not in done and f['target_close_ms']<=now-2000]
                    if not due:continue
                    raw,source=get_public('/api/v3/klines',symbol='BTCUSDT',interval='1h',
                        startTime=record['cutoff_ms'],endTime=min(record['cutoff_ms']+4*HOUR-1,now),limit=4)
                    closed=validate_candles(raw,now)
                    lookup={int(row[6])+1:row for row in closed}
                    for forecast in due:
                        target=forecast['target_close_ms']
                        if target not in lookup:continue
                        actual=float(lookup[target][4]);base=record['base'];models={}
                        for name in ['kronos','timesfm','ensemble']:
                            predicted=forecast[name+'_close'];metrics=score(base,predicted,actual)
                            metrics['diagnosis']=diagnose(base,predicted,actual,metrics['contribution_usdt'])
                            models[name]=metrics
                        models['ensemble']['vs_kronos_usdt']=models['kronos']['absolute_error_usdt']-models['ensemble']['absolute_error_usdt']
                        models['ensemble']['vs_timesfm_usdt']=models['timesfm']['absolute_error_usdt']-models['ensemble']['absolute_error_usdt']
                        outcome=1.0 if actual>base else 0.0
                        assessment=dict(horizon=forecast['horizon'],target_close_ms=target,checked_ms=now,
                            actual_close=actual,raw_candle=lookup[target],source=source,models=models,
                            kronos_brier=(forecast['kronos_up_fraction']-outcome)**2,
                            timesfm_inside_q10_q90=forecast['timesfm_q10']<=actual<=forecast['timesfm_q90'])
                        self.exclusive(self.root/record['id']/f"evaluation-{forecast['horizon']}.json",
                            dict(assessment=assessment,sha256=digest(assessment),forecast_sha256=record['sha256']))
                self.last_check_ms=now;self.last_error=None
            except Exception as error:
                self.last_error=str(error)
                raise
