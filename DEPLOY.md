# AIPLOS personal deployment

This package preserves your Python Ridge model and existing dashboard. It adds a Gunicorn WSGI entry point, password protection, HTTPS-origin checking, health check and configurable persistent SQLite storage. The built-in local HTTP server is not the deployment entry point.

## Render

1. Upload this folder's contents to a private GitHub repository. Put requirements.txt and render.yaml at the repository root.
2. In Render, create a Python Web Service connected to that repository. Choose a paid instance supporting a persistent disk. Review charges before creating resources.
3. Build command: `pip install -r requirements.txt && python build_model.py`
4. Start command: `gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120 --access-logfile -`
5. Attach a 1 GB persistent disk at `/var/data`.
6. Set environment variables:
   - `AIPLOS_DATA_DIR=/var/data/aiplos`
   - `AIPLOS_USERNAME=owner`
   - `AIPLOS_PASSWORD`: enter a unique random password of at least 20 characters directly in Render. Never commit it or paste it in chat.
   - `PUBLIC_ORIGIN`: the exact assigned HTTPS site URL, e.g. `https://your-assigned-name.onrender.com`, without a path or trailing slash. Replace this example with the real URL. Set it before the successful deployment; an unset origin fails closed.
   - `PYTHON_VERSION=3.12.8`
7. Set the health check path to `/healthz`, deploy, and open the assigned HTTPS URL. Use the browser's authentication prompt to sign in.

Alternatively, use render.yaml as a Blueprint. It explicitly requests paid compute and a persistent disk; review the Render estimate first. Enter the password and assigned origin as secrets/configuration in Render.

## Verification after deployment

- Without credentials, `/` and `/api/history` must return 401.
- Sign in, submit a questionnaire, and verify the returned score.
- Restart the service and verify saved check-ins remain.
- Export CSV; confirm only your records appear.
- `/healthz` is public but exposes no personal information.

## Scope

Single owner, protected by browser HTTP Basic authentication over HTTPS. It has no signup, recovery, or multi-user accounts. Close the browser session to clear cached Basic credentials, or rotate the password in Render. Do not share your password. Back up your SQLite database as needed; the disk provides persistence, not a complete backup policy.

Goals remain browser-local; they are not synced across devices. The assistant uses fixed questionnaire rules. The score reconstructs a survey formula and is not a forecast. The unchanged initial page uses labeled sample data until your first submission.

Train the model during every build; do not upload local check-in databases or untrusted model artifacts. Use one worker with SQLite and the persistent disk. This package is prepared for deployment but no hosted service has been created yet.
