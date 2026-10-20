"""Panel local KT-001. Solo inferencia sintetica fija, sin conexion de mercado."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import uuid
import signal
from market import MarketLedger
from config import model_python, data_directory

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent
STAGES = ['input', 'kronos', 'timesfm', 'combine', 'verify', 'done']


def load_result(directory, source):
    report = json.loads((directory/'report.json').read_text(encoding='utf-8'))
    if report.get('data') != 'synthetic' or report.get('variant') != 'KT-001':
        raise ValueError('Solo resultados sinteticos KT-001')
    def rows(name):
        with (directory/name).open(encoding='utf-8', newline='') as stream:
            return [{k: v if k == 'timestamp' else float(v) for k, v in row.items()}
                    for row in csv.DictReader(stream)]
    return dict(report=report, history=rows('synthetic_input.csv'),
                forecast=rows('synthetic_ensemble.csv'), source=source)


class Engine:
    def __init__(self, start_monitor=True):
        self.lock = threading.Lock()
        self.job = dict(status='idle', stage=None, events=[])
        self.result = load_result(PROJECT/'docs/evidencia/KT-001', 'evidencia_guardada')
        self.python = model_python()
        self.ready = self.python.is_file()
        self.data_dir = data_directory()
        self.market = MarketLedger(self.data_dir/'market-records')
        self.auto = os.environ.get('KRONOS_AUTO_FORECAST','0')=='1'
        self.next_auto_attempt = 0
        self.stop = threading.Event()
        self.worker = None
        if start_monitor:threading.Thread(target=self.monitor, daemon=True).start()

    def auto_tick(self):
        if not self.auto or not self.ready or time.monotonic()<self.next_auto_attempt:
            return
        with self.lock:
            if self.job['status']=='running':return
        records=self.market.records()
        if any(len(record['evaluations'])<4 for record in records):return
        # Una emision por ventana de cuatro horas, sin ajustar parametros.
        if records and int(time.time()*1000)<records[-1]['forecast'][-1]['target_close_ms']+5000:return
        self.next_auto_attempt=time.monotonic()+900
        self.start('market')

    def monitor(self):
        while not self.stop.wait(60):
            try:
                self.market.reconcile()
                self.auto_tick()
            except Exception:
                pass  # El error queda visible en el estado del registro.

    def snapshot(self):
        with self.lock:
            return dict(job=json.loads(json.dumps(self.job)), result=self.result,
                        engine_available=self.ready,auto_forecast=self.auto)

    def start(self, kind='synthetic'):
        with self.lock:
            if self.stop.is_set():return False,'Servidor deteniendose'
            if self.job['status'] == 'running':
                return False, 'Ya hay una ejecucion en curso'
            if not self.ready:
                return False, 'Falta el entorno Python local de los modelos'
            self.job = dict(id=uuid.uuid4().hex[:12], kind=kind,status='running', stage='starting',
                            started_at=datetime.now(timezone.utc).isoformat(), events=[])
        self.worker=threading.Thread(target=self.work, daemon=True)
        self.worker.start()
        return True, 'started'

    def work(self):
        with self.lock:
            job_id = self.job['id']
            kind = self.job['kind']
        directory = (self.data_dir/'market-records' if kind=='market' else self.data_dir/'runtime')/job_id
        directory.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env.update(HF_HUB_OFFLINE='1', PYTHONUTF8='1', PYTHONUNBUFFERED='1')
        command = [str(self.python), '-X', 'utf8',
                   '-u', str(PROJECT/'tools/kronos_timesfm_smoke.py'),
                   '--output-dir', str(directory), '--progress']
        process = None
        try:
            if kind=='market':
                with self.lock:
                    self.job['stage']='input'
                    self.job['events'].append(dict(stage='input',message='Consultando 400 velas BTCUSDT cerradas en Binance'))
                self.market.prepare(directory)
                command=[str(self.python),'-X','utf8','-u',
                    str(PROJECT/'tools/kronos_timesfm_market.py'),'--directory',str(directory)]
            process = subprocess.Popen(command, cwd=PROJECT, env=env, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, encoding='utf-8',
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            def expire():
                if process.poll() is None:
                    process.kill()
            timeout = threading.Timer(240, expire)
            timeout.daemon = True
            timeout.start()
            output = []
            try:
                for line in process.stdout:
                    output.append(line)
                    if line.startswith('@PANEL '):
                        event = json.loads(line[7:])
                        if event['stage'] in STAGES:
                            event['at'] = datetime.now(timezone.utc).isoformat()
                            with self.lock:
                                self.job['events'].append(event)
                                self.job['stage'] = event['stage']
                returncode = process.wait()
            finally:
                timeout.cancel()
            if returncode:
                # Detalle tecnico local; el navegador recibe mensaje resumido.
                (directory/'error.txt').write_text(''.join(output), encoding='utf-8')
                raise RuntimeError('La inferencia no termino. Revisa '+str(directory/'error.txt'))
            if kind=='market':
                self.market.seal(directory)
                result=None
            else:
                result = load_result(directory, 'ejecucion_local')
            with self.lock:
                if result is not None:self.result = result
                self.job.update(status='done', stage='done',
                    finished_at=datetime.now(timezone.utc).isoformat())
        except Exception as error:
            if process is not None and process.poll() is None:
                process.kill()
            with self.lock:
                self.job.update(status='error', error=str(error),
                                finished_at=datetime.now(timezone.utc).isoformat())


class Handler(BaseHTTPRequestHandler):
    def allowed_host(self):
        return self.headers.get('Host', '') in {
            f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}

    def send(self, code, data, content_type='application/json; charset=utf-8'):
        payload = json.dumps(data, allow_nan=False).encode('utf-8') if isinstance(data, dict) else data
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if not self.allowed_host():
            return self.send(403, dict(error='Host no permitido'))
        path = self.path.split('?')[0]
        if path == '/api/state':
            return self.send(200, self.server.engine.snapshot())
        if path == '/api/export':
            return self.send(200, self.server.engine.snapshot()['result'])
        if path == '/api/market':
            try:
                snapshot=self.server.engine.market.snapshot()
                snapshot['automatic_forecasts']=self.server.engine.auto
                if self.server.engine.auto:
                    snapshot['monitoring']+=' Generacion automatica activada: nueva emision al resolver la ventana previa, sin solapar.'
                return self.send(200,snapshot)
            except Exception as error:return self.send(500,dict(error=str(error)))
        files = {'/':'index.html', '/index.html':'index.html', '/app.js':'app.js', '/market.js':'market.js', '/style.css':'style.css'}
        if path not in files:
            return self.send(404, dict(error='No encontrado'))
        file = BASE/'dist'/files[path]
        return self.send(200, file.read_bytes(),
                         (mimetypes.guess_type(file.name)[0] or 'text/plain')+'; charset=utf-8')

    def do_POST(self):
        origin = self.headers.get('Origin')
        expected = {f'http://127.0.0.1:{self.server.server_port}',
                    f'http://localhost:{self.server.server_port}'}
        if not self.allowed_host() or self.headers.get('X-Panel-Request') != '1' or (origin and origin not in expected):
            return self.send(403, dict(error='Solicitud no permitida'))
        if self.path not in ['/api/run','/api/market-run','/api/market-check']:
            return self.send(404, dict(error='No encontrado'))
        if int(self.headers.get('Content-Length', '0')) > 0:
            return self.send(400, dict(error='La prueba usa parametros fijos'))
        if self.path=='/api/market-check':
            try:
                self.server.engine.market.reconcile()
                return self.send(200,dict(message='Revision de cierres completada'))
            except Exception as error:
                return self.send(502,dict(error=str(error)))
        okay, message = self.server.engine.start('market' if self.path=='/api/market-run' else 'synthetic')
        return self.send(202 if okay else 409, dict(message=message))

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    server.engine = Engine()
    def request_stop(signum, frame):
        server.engine.stop.set()
        threading.Thread(target=server.shutdown,daemon=True).start()
    signal.signal(signal.SIGTERM,request_stop)
    print(f'Panel Kronos + TimesFM: http://127.0.0.1:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.engine.stop.set()
        if server.engine.worker is not None:
            server.engine.worker.join(timeout=290)
        server.server_close()
