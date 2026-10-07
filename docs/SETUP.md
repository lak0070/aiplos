# Local setup

[Back to README](../README.md)

## Requirements

Use Python 3.12 (the Render configuration specifies 3.12.8), Git and a modern browser. Run all commands from the repository root. Dependencies are ranges rather than an exact lockfile; evaluation records the installed versions.

## Install and train

```bash
python -m venv .venv
```

Activate with `.venv\Scripts\Activate.ps1` in Windows PowerShell or `source .venv/bin/activate` on macOS/Linux.

```bash
python -m pip install -r requirements.txt
python build_model.py
```

The build compares four models, performs five-fold grouped cross-validation and writes:

| Output | Purpose |
|---|---|
| `data/random_forest_life_os_model.joblib` | Fitted training-only Random Forest pipeline and metadata |
| `evaluation/summary.json` | Metrics, configuration, dataset hash and environment versions |
| `evaluation/holdout_predictions.csv` | Actual and predicted held-out scores |
| `evaluation/split_manifest.csv` | Cleaned row index and train/test assignment |

The script overwrites these generated files. `evaluation/REPORT.md` is a separately maintained narrative snapshot; update it deliberately when changing the recorded experiment. Model binaries and SQLite databases are ignored by Git.

## Run the website

```bash
python dev.py
```

Visit http://127.0.0.1:8000 and use **Update My Data**. The evaluation page is http://127.0.0.1:8000/evaluation. Stop the server with Ctrl+C. The development runner binds only to loopback and sets the matching local origin. It uses the same `wsgi.application` routes as production; it is not a production server.

If the model artifact is missing, importing the application starts training automatically. Build explicitly first so training failures are easier to diagnose.

## Optional command-line questionnaire

```bash
python model.py
```

This loads or builds the model, then asks whether to enter a questionnaire. To train without prompts, use `python build_model.py`, not `model.py --train-only`.

## Troubleshooting

| Symptom | Check |
|---|---|
| First start is slow | Training/cross-validation may still be running; inspect terminal output. |
| Missing dependency | Activate the virtual environment and install `requirements.txt`. |
| Port 8000 is occupied | Stop the existing process before restarting. |
| Browser reports origin error | Open exactly `http://127.0.0.1:8000` when using `dev.py`. |
| Old saved scores show Ridge | Historical records keep their model labels; submit a new check-in for Random Forest. |
| Training CSV not found | Confirm `data/wellbeing.csv` exists in the cloned repository. |

Do not use `python app.py` for the current browser dashboard. That legacy server stores records in SQLite, lacks the evaluation routes and returns a smaller prediction response than the current frontend expects.
