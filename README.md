# AIPLOS — AI Personal Life OS

A wellbeing dashboard that estimates a **questionnaire-based work–life balance score** using a Python Random Forest regressor. Users submit lifestyle responses, see their score, and track check-ins in their browser.

**[Open dashboard](https://aiplos-personal.onrender.com)** · **[Live evaluation](https://aiplos-personal.onrender.com/evaluation)**

## Start here

| If you want to… | Read… |
|---|---|
| Run the project on your computer | [Setup guide](docs/SETUP.md) |
| Understand how the parts connect | [Architecture](docs/ARCHITECTURE.md) |
| Call or explain the prediction endpoint | [API reference](docs/API.md) |
| Understand training, validation and limitations | [Model guide](docs/MODEL.md) |
| Inspect recorded evaluation evidence | [Evaluation report](evaluation/REPORT.md) |
| Deploy the website | [Deployment guide](DEPLOY.md) |
| Understand dataset fields and provenance limitations | [Dataset notes](data/README.md) |
| Contribute a change | [Contributing guide](CONTRIBUTING.md) |

## What the application does

- Collects 20 numeric lifestyle responses, age group, gender category and a display name.
- Sends the questionnaire to a custom Python HTTP API; no external AI API is used.
- Returns a Random Forest prediction and a dataset-relative score band.
- Displays descriptive lifestyle cards, score trends and rule-based suggestions.
- Saves check-ins and goals in browser `localStorage`; exports score history as CSV.
- Provides an evaluation page comparing Random Forest, Ridge, Linear Regression and a mean baseline.

The assistant is rule-based, not an LLM. The “Top Factors” display is descriptive, not SHAP or measured feature importance. This project does not provide medical diagnosis or establish future wellbeing prediction.

## Quick start

Python 3.12 is the deployment target. From a terminal:

```bash
git clone https://github.com/lak0070/aiplos.git
cd aiplos
python -m venv .venv
```

Activate the environment: `source .venv/bin/activate` on macOS/Linux, or `.venv\Scripts\Activate.ps1` in Windows PowerShell. Then:

```bash
python -m pip install -r requirements.txt
python build_model.py
python dev.py
```

Open **http://127.0.0.1:8000**. The first build runs grouped cross-validation and can take several minutes. See [setup](docs/SETUP.md) for outputs and troubleshooting.

## Repository map

Runtime modules stay at the repository root so existing imports and Render commands remain stable.

| Path | Responsibility |
|---|---|
| `dev.py` | Local development server using the production WSGI routes |
| `wsgi.py` | HTTP routes, request checks and JSON responses |
| `app.py` | Shared validation/model loading; also contains the legacy SQLite server |
| `model.py` | Questionnaire schema, feature engineering, preprocessing and model configuration |
| `evaluate_model.py` | Grouped split, cross-validation, model comparisons and evidence generation |
| `build_model.py` | Deployment build entry point |
| `templates/` | Dashboard and evaluation HTML |
| `static/` | JavaScript behaviour and CSS |
| `data/` | Training CSV, dataset notes and locally generated model artifact |
| `evaluation/` | Recorded metrics, held-out predictions and split assignments |
| `docs/` | Setup, architecture, API and model guides |
| `requirements.txt` | Python dependency ranges |
| `render.yaml` | Render service configuration |

## Recorded model results

An 80/20 grouped split contains **12,392 training rows** and **3,098 test rows** after cleaning. Five-fold grouped cross-validation runs only within the training partition.

| Model | Test MAE ↓ | Test RMSE ↓ | Test R² ↑ |
|---|---:|---:|---:|
| Mean baseline | 36.2685 | 44.9092 | −0.000683 |
| Linear Regression | ≈0 | ≈0 | 1.000000 |
| Ridge, alpha=10 | 0.01725 | 0.02373 | 0.99999972 |
| **Random Forest (deployed)** | **6.8115** | **8.8591** | **0.961059** |

These values are from the [committed report](evaluation/REPORT.md); the live build may differ slightly with dependency versions. **R² is not classification accuracy.** Random Forest was selected after reviewing earlier Ridge results, so this reused holdout is a comparison set, not a fresh final test of that selection.

Linear Regression reconstructs the target almost exactly. This suggests a questionnaire-derived scoring formula, rather than near-perfect prediction of future wellbeing. Random Forest has larger errors than Ridge here. See [limitations](docs/MODEL.md#limitations).

## Storage and access

The repository and hosted dashboard are public. Hosted check-ins and goals stay in the current browser and do not sync between devices. Clearing site data removes them. Questionnaire inputs are sent to the backend for prediction, but the production prediction route does not insert them into a database. The legacy `python app.py` server has different SQLite behaviour; use `python dev.py` for the current website.

## Technology and reuse

HTML, CSS and JavaScript frontend; pandas/NumPy and scikit-learn model pipeline; joblib serialization; custom WSGI backend; Gunicorn on Render.

No project licence is currently declared. Public visibility alone does not grant an open-source licence. The original dataset publisher, source URL and redistribution licence still need verification; see [dataset notes](data/README.md).
