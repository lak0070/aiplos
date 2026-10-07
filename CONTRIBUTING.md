# Contributing

Start with [setup](docs/SETUP.md) and [architecture](docs/ARCHITECTURE.md). Keep changes focused and explain the problem, behaviour change and verification in your pull request.

## Before proposing a change

- Preserve the questionnaire field names and frontend/API response contract.
- Keep preprocessing inside the fitted pipeline; never fit it on the test partition.
- Do not use holdout results to select hyperparameters and then describe that same holdout as an independent final test.
- Preserve old history model labels; do not relabel earlier Ridge scores as Random Forest.
- Use comments to explain assumptions and boundaries, not every Python statement.
- Do not commit passwords, `.env`, SQLite check-ins, virtual environments or joblib binaries.

## Checks

```bash
python -m compileall -q app.py model.py evaluate_model.py build_model.py wsgi.py dev.py
node --check static/app.js
node --check static/evaluation.js
```

Node is optional and only needed for JavaScript syntax checks. For runtime changes, start `python dev.py`, open both pages, submit valid and invalid questionnaire data, then reload to check local history. For model changes, regenerate evaluation evidence and update the narrative report with the actual results and limitations. Do not run the expensive training process solely to verify prose changes.

The project has no declared open-source licence. Clarify project and dataset permissions before redistributing derivatives.
