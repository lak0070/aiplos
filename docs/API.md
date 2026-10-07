# API reference

[Back to README](../README.md)

The website uses a custom WSGI HTTP API, not Flask, FastAPI or an external AI service. Paths below describe `wsgi.py`, used by production and `dev.py`.

## Routes

| Method | Path | Response |
|---|---|---|
| GET | `/` | Dashboard HTML |
| GET | `/evaluation` | Evaluation HTML |
| GET | `/api/evaluation` | Build-generated evaluation JSON |
| GET | `/api/history` | Empty array; the frontend uses browser history |
| GET | `/healthz` | `{"status":"ok"}`; liveness only, not a full prediction test |
| GET | `/static/app.js`, `/static/evaluation.js`, `/static/style.css` | Explicit frontend assets |
| POST | `/api/predict` | Score, model label, band and check-in details |

No hosted dataset-download, model-download or server-side CSV-report route exists. The metrics download uses `/api/evaluation`. The full CSV evidence is available in this public repository.

## Prediction request

Send `Content-Type: application/json` and an `Origin` header matching `PUBLIC_ORIGIN`. Browser `fetch()` supplies the origin for the same-origin POST. A direct API client must set it explicitly. Body size must be 1–16,000 bytes. All numeric fields must be whole numbers in the [documented ranges](../data/README.md).

Example payload (illustrative inputs, not a real person's record):

```json
{
  "name": "Demo User",
  "AGE": "21 to 35",
  "GENDER": "Female",
  "FRUITS_VEGGIES": 3,
  "DAILY_STRESS": 5,
  "PLACES_VISITED": 4,
  "CORE_CIRCLE": 5,
  "SUPPORTING_OTHERS": 5,
  "SOCIAL_NETWORK": 5,
  "ACHIEVEMENT": 5,
  "DONATION": 2,
  "BMI_RANGE": 1,
  "TODO_COMPLETED": 5,
  "FLOW": 4,
  "DAILY_STEPS": 6,
  "LIVE_VISION": 5,
  "SLEEP_HOURS": 7,
  "LOST_VACATION": 2,
  "DAILY_SHOUTING": 2,
  "SUFFICIENT_INCOME": 2,
  "PERSONAL_AWARDS": 4,
  "TIME_FOR_PASSION": 4,
  "WEEKLY_MEDITATION": 4
}
```

Save that object as a local `request.json`. With `dev.py` running, on macOS/Linux:

```bash
curl http://127.0.0.1:8000/api/predict \
  -H 'Content-Type: application/json' \
  -H 'Origin: http://127.0.0.1:8000' \
  --data-binary @request.json
```

On Windows use `curl.exe` and a single command line. For the hosted API, replace both URLs with `https://aiplos-personal.onrender.com` (keeping `/api/predict` on the request URL).

## Successful response

| Field | Meaning |
|---|---|
| `model` | `Random Forest` |
| `score` | Numeric prediction in original survey score units |
| `band` | Lower, middle or higher range in this dataset |
| `inputs` | Validated questionnaire values, including server-supplied current date |
| `name` | Trimmed display name, 1–60 characters; not a predictor |
| `created` | Server-local ISO timestamp, to seconds, without an explicit timezone offset |

The frontend saves this object in localStorage. The POST does not write a production database record.

## Error responses

Errors have an `error` string. Current routes return 400 for invalid questionnaire/JSON values, 403 for origin mismatch, 413 for empty or oversized bodies, 415 for non-JSON content, 404 for unknown GET paths, 405 for unsupported methods/routes, and 500 for unexpected prediction failures. The legacy 500 text mentions saving a check-in even though this route does not persist it.

## Access boundaries

There is no username/password authentication. Origin checking is a browser request restriction, not authorization: a non-browser client can supply an Origin header. Route allowlisting prevents arbitrary file serving. This prototype does not implement per-user accounts or application-level rate limiting.
