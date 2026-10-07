# Architecture

[Back to README](../README.md)

## Two separate workflows

**Build time:** `build_model.py` calls `evaluate_model.run()`. The evaluator reads the CSV, removes duplicates, creates a grouped split, compares estimators and saves the training-only Random Forest pipeline with its metadata.

**Request time:** JavaScript collects a questionnaire and posts JSON to `/api/predict`. Gunicorn calls `wsgi.application`, which checks the request and delegates input validation to `app.validate`. `model.engineer` produces a one-row feature table, then the loaded pipeline performs preprocessing and prediction. The API returns JSON; JavaScript updates the dashboard and saves the response locally.

The joblib bundle is loaded on application import and reused across requests. Normal predictions do not retrain the model. If the artifact is missing, application import triggers training as a fallback.

## Responsibilities

| Layer | Files | Key boundary |
|---|---|---|
| Presentation | `templates/`, `static/` | Display, questionnaire, browser history and rule-based suggestions |
| HTTP | `wsgi.py` | Exact route allowlist, origin/content-type/body-size checks and response headers |
| Shared application | `app.py` | Validates schema and loads the saved bundle |
| Machine learning | `model.py` | Stateless feature engineering plus fitted scikit-learn pipeline |
| Experiment | `evaluate_model.py` | Split integrity, cross-validation, metrics and artifacts |

## Storage details

Production and `dev.py` use browser `localStorage` keys `aiplos-checkins-v1` and `aiplos-goals`. The production `/api/history` route returns an empty list; the frontend reads browser history instead. CSV report generation also happens in JavaScript.

Importing `app.py` currently creates a SQLite file/table, even under WSGI. However, the WSGI prediction handler never inserts check-ins into it. The legacy `app.Handler` does insert records when `python app.py` is used. Keeping this distinction explicit avoids confusing an initialized database with production history storage.

## Display versus prediction

Only the overall survey score is ML-predicted. Other cards are descriptive averages. The overall display scale maps 480–820.2 onto 0–100 with clipping. Score bands use 636 and 698.5, not clinical cutoffs.

Recommendations check sleep, activity, passion and stress against fixed thresholds. The assistant selects predefined responses. Neither recommendations nor “Top Factors” are feature attribution or causal explanations.
