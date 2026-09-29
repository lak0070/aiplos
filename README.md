# Free Render deployment — personal dashboard

Plan: free. No disk, database service, or other paid resources.

Build: pip install -r requirements.txt && python build_model.py
Start: gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --access-logfile -

Use the existing Render workspace My Workspace and region Singapore. Set AIPLOS_USERNAME=owner, AIPLOS_PASSWORD to a unique random secret of at least 20 characters, PUBLIC_ORIGIN to the exact HTTPS service origin, and AIPLOS_DATA_DIR=/tmp/aiplos. Enter the password directly in Render, not in GitHub or chat. Health endpoint: /healthz.

The supplied survey dataset is included at data/wellbeing.csv with explicit owner approval for private GitHub storage and training on Render.

History and goals are stored in localStorage on the current browser. The Python endpoint receives questionnaire inputs and returns Ridge predictions; it does not save new check-ins on the server. Clearing site data deletes history; separate devices have separate histories. CSV export contains check-in dates and scores. It is not a full questionnaire backup.

Free Render services may sleep after 15 minutes of inactivity and have a cold start. The app is password-protected for one owner, not a multi-user service. Demo data is labeled until the first browser check-in.
