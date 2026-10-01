# Free Render deployment — personal dashboard

Plan: free. No disk, database service, or other paid resources.

Build: pip install -r requirements.txt && python build_model.py
Start: gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --access-logfile -

Use the existing Render workspace My Workspace and region Singapore. Set PUBLIC_ORIGIN to the exact HTTPS service origin, and AIPLOS_DATA_DIR=/tmp/aiplos. Health endpoint: /healthz.

The supplied survey dataset is included at data/wellbeing.csv with explicit owner approval for private GitHub storage and training on Render.

History and goals are stored in localStorage on the current browser. The Python endpoint receives questionnaire inputs and returns Ridge predictions; it does not save new check-ins on the server. Clearing site data deletes history; separate devices have separate histories. CSV export contains check-in dates and scores. It is not a full questionnaire backup.

Free Render services may sleep after 15 minutes of inactivity and have a cold start. The app is publicly accessible without a username or password. Each visitor has separate browser-local history. Demo data is labeled until the first browser check-in.

Evaluation: the build now runs evaluate_model.py through build_model.py. The production Ridge uses only the training partition (12,392 rows), retaining 3,098 holdout rows. Visit /evaluation for metrics and limitations. See evaluation/REPORT.md for the recorded evaluation.
