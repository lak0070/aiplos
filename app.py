"""AIPLOS local Python web app. Run: python app.py"""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import date, datetime
import json, sqlite3, csv, io, threading, webbrowser, os
import pandas as pd
import model

ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('AIPLOS_DATA_DIR', str(ROOT / 'data')))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB = DATA_DIR / 'checkins.sqlite3'
model.SOURCE = ROOT / 'data' / 'wellbeing.csv'
model.ARTIFACT = ROOT / 'data' / 'random_forest_life_os_model.joblib'
if not model.ARTIFACT.exists():
    print('Training your Random Forest model from the supplied dataset…')
    model.train_model()
bundle = model.joblib.load(model.ARTIFACT)
with sqlite3.connect(DB) as con:
    con.execute('CREATE TABLE IF NOT EXISTS checkins (id INTEGER PRIMARY KEY, created TEXT, name TEXT, inputs TEXT, score REAL)')


def records():
    with sqlite3.connect(DB) as con:
        rows = con.execute('SELECT id,created,name,inputs,score FROM checkins ORDER BY id').fetchall()
    return [dict(id=r[0], created=r[1], name=r[2], inputs=json.loads(r[3]), score=r[4]) for r in rows]


def validate(data):
    if not isinstance(data, dict): raise ValueError('Expected a questionnaire object.')
    row = {'Timestamp': date.today().isoformat()}
    for field, choices in [('AGE',model.AGE_OPTIONS),('GENDER',model.GENDER_OPTIONS)]:
        if data.get(field) not in choices: raise ValueError(f'Choose a valid {field.lower()}.')
        row[field] = data[field]
    for field, (low,high) in model.BOUNDS.items():
        value = data.get(field)
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not float(value).is_integer() or not low <= value <= high:
            raise ValueError(f'{field} must be a whole number from {low} to {high}.')
        row[field] = int(value)
    name = data.get('name','').strip() if isinstance(data.get('name',''),str) else ''
    if not 1 <= len(name) <= 60: raise ValueError('Enter a name of 1–60 characters.')
    return row,name


class Handler(BaseHTTPRequestHandler):
    def send(self, value, status=200, content_type='application/json; charset=utf-8'):
        body = json.dumps(value).encode() if content_type.startswith('application/json') else value
        self.send_response(status); self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(len(body))); self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/api/history': return self.send(records())
        if path == '/api/report':
            out=io.StringIO(); writer=csv.writer(out); writer.writerow(['Date','Work-life balance score'])
            for r in records(): writer.writerow([r['created'],round(r['score'],2)])
            return self.send(out.getvalue().encode(),content_type='text/csv; charset=utf-8')
        files={'/':('templates/index.html','text/html; charset=utf-8'), '/static/style.css':('static/style.css','text/css'), '/static/app.js':('static/app.js','text/javascript')}
        if path not in files: return self.send({'error':'Not found'},404)
        file,mime=files[path]; return self.send((ROOT/file).read_bytes(),content_type=mime)
    def do_POST(self):
        if self.path != '/api/predict': return self.send({'error':'Not found'},404)
        # JSON-only, same-origin local requests; no permissive CORS.
        if self.headers.get('Content-Type','').split(';')[0] != 'application/json': return self.send({'error':'JSON required'},415)
        origin=self.headers.get('Origin')
        if origin and origin not in ('http://127.0.0.1:8000','http://localhost:8000'): return self.send({'error':'Origin not allowed'},403)
        try:
            size=int(self.headers.get('Content-Length',0))
            if not 0 < size <= 16000: raise ValueError('Invalid request size.')
            row,name=validate(json.loads(self.rfile.read(size)))
            score=float(bundle['pipeline'].predict(model.engineer(pd.DataFrame([row]),include_target=False))[0])
            with sqlite3.connect(DB) as con:
                con.execute('INSERT INTO checkins(created,name,inputs,score) VALUES(?,?,?,?)',(datetime.now().isoformat(timespec='seconds'),name,json.dumps(row),score))
            self.send({'score':score,'band':model.band(score)})
        except (ValueError,TypeError,KeyError) as error: self.send({'error':str(error)},400)
        except Exception:
            self.send({'error':'Could not save this check-in. Please try again.'},500)

if __name__ == '__main__':
    print('AIPLOS is ready: http://127.0.0.1:8000  (Ctrl+C to stop)')
    ThreadingHTTPServer(('127.0.0.1',8000),Handler).serve_forever()
