# Render deployment

[Back to README](README.md)

The existing service is `aiplos-personal`, configured as a free Python web service in Singapore. The public dashboard does not require login. `render.yaml` is the configuration reference.

## Commands

Build:

```bash
pip install -r requirements.txt && python build_model.py
```

Start:

```bash
gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --access-logfile -
```

Health-check path: `/healthz`.

| Variable | Value / purpose |
|---|---|
| `PYTHON_VERSION` | `3.12.8`, as declared in `render.yaml` |
| `PUBLIC_ORIGIN` | Exact HTTPS origin, e.g. `https://aiplos-personal.onrender.com`, with no path |
| `AIPLOS_DATA_DIR` | `/tmp/aiplos`, the legacy SQLite initialization location |
| `PORT` | Supplied by the hosting platform |

## Lifecycle

Render installs dependencies, trains/evaluates the models and saves the Random Forest artifact. Gunicorn loads it at startup. Predictions use the saved pipeline; no external model API is required. Existing automatic deployments track `main`, so repository changes can trigger a new build.

No persistent disk or hosted database is configured. Browser-local history survives server restarts but not browser-data clearing. Free hosting can have cold starts after inactivity; this configuration does not promise continuous availability.

## Verify a deployment

- `/healthz` returns HTTP 200 and `{"status":"ok"}`.
- `/` and `/evaluation` load.
- `/api/evaluation` reports Random Forest and the new build's metrics.
- A valid questionnaire produces a numeric score and `model: "Random Forest"`.
- Invalid input is rejected, and a browser reload retains the saved local check-in.

A public repository exposes its tracked code, dataset and history. Never commit secrets, personal check-in databases or `.env` files. The dataset's original licence still needs verification; public visibility is not a licence grant.
