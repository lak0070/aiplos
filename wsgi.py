"""Public dashboard WSGI entry point for Gunicorn."""
import os, json
from datetime import datetime
from urllib.parse import urlsplit

ORIGIN=os.environ.get('PUBLIC_ORIGIN','').rstrip('/')
if not ORIGIN.startswith('https://') or urlsplit(ORIGIN).path:
    raise RuntimeError('Set PUBLIC_ORIGIN to your exact HTTPS origin, without a path.')
import app as core

def application(env,start):
    path=env.get('PATH_INFO','/')
    def reply(data,status='200 OK',mime='application/json; charset=utf-8',extra=()):
        body=json.dumps(data).encode() if mime.startswith('application/json') else data
        headers=[('Content-Type',mime),('Content-Length',str(len(body))),('Cache-Control','no-store'),('X-Content-Type-Options','nosniff'),('X-Frame-Options','DENY'),('Referrer-Policy','same-origin'),('Strict-Transport-Security','max-age=31536000'),('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")]
        start(status,headers+list(extra));return [body]
    if path=='/healthz':return reply({'status':'ok'})
    method=env.get('REQUEST_METHOD','GET')
    if method=='GET':
        if path=='/api/history':return reply([])
        if path=='/api/evaluation':return reply(json.loads((core.ROOT/'evaluation/summary.json').read_text()))
        files={'/evaluation':('templates/evaluation.html','text/html; charset=utf-8'),'/static/evaluation.js':('static/evaluation.js','text/javascript; charset=utf-8'),'/':('templates/index.html','text/html; charset=utf-8'),'/static/style.css':('static/style.css','text/css; charset=utf-8'),'/static/app.js':('static/app.js','text/javascript; charset=utf-8')}
        if path in files:
            name,mime=files[path];return reply((core.ROOT/name).read_bytes(),mime=mime)
        return reply({'error':'Not found'},'404 Not Found')
    if method!='POST' or path!='/api/predict':return reply({'error':'Method not allowed'},'405 Method Not Allowed')
    if env.get('CONTENT_TYPE','').split(';')[0]!='application/json':return reply({'error':'JSON required'},'415 Unsupported Media Type')
    if env.get('HTTP_ORIGIN')!=ORIGIN:return reply({'error':'Origin not allowed'},'403 Forbidden')
    try:
        length=int(env.get('CONTENT_LENGTH','0'))
        if not 0<length<=16000:return reply({'error':'Request too large or empty'},'413 Content Too Large')
        row,name=core.validate(json.loads(env['wsgi.input'].read(length)))
        score=float(core.bundle['pipeline'].predict(core.model.engineer(core.pd.DataFrame([row]),include_target=False))[0])
        return reply({'score':score,'band':core.model.band(score),'inputs':row,'name':name,'created':datetime.now().isoformat(timespec='seconds')})
    except (ValueError,TypeError,KeyError):return reply({'error':'Check all questionnaire fields and try again.'},'400 Bad Request')
    except Exception:
        import logging
        logging.exception('Prediction failed')
        return reply({'error':'Could not save this check-in.'},'500 Internal Server Error')
