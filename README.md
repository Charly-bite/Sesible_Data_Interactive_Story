# Datos Sensibles — API & Tests
https://sesible-data-interactive-story.onrender.com/
Small Flask application + frontend for browsing/searching a dataset of client records exported as CSVs.

This repository contains:

- `api.py` — Flask backend with search endpoints and a small authentication layer.
- `client_data.py` — CSV loader and in-memory search helpers used by the API.
- `build_db.py` — utility to build an SQLite `data.db` to speed up searches for large CSV datasets.
- `Data/` — place your CSV files here (exported from other systems). See `client_data.py` for expected headers.
- `historia.html` / `historia.js` and `login.html` — very small static frontend pages to interact with the API.
- `moodboard/` — layout, assets and styles used by the small UI.
- `tests/` — unit tests used by CI and to validate behavior.

Repository: https://github.com/Charly-bite/Sesible_Data_Interactive_Story

Important note on privacy
-- The dataset may contain personally identifiable information. This project is educational and includes deliberate controls (blocked names/identifiers) — please do not deploy a copy of this data publicly without ensuring compliance with privacy laws and institutional policy.

Quick start (local development)

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install runtime dependencies:

```bash
pip install -r requirements.txt
```

3. Prepare data (CSV files)

Place CSVs inside the `Data/` directory. The loader expects headers comparable to `client_data.EXPECTED_LABELS`. If you are testing without large data, create a small sample CSV.

4. Build the sqlite DB (optional but recommended for large datasets):

```bash
python build_db.py
```

5. Start the API server:

```bash
python api.py
```

6. Open the front-end
- Visit `http://127.0.0.1:5000/` in your browser. Login using credentials from `auth.json.example` or provide env variables `AUTH_USER`/`AUTH_PASSWORD`.

Configuration
- `auth.json` (optional): copy `auth.json.example` into `auth.json` to set the app credentials.
- Environment variables (overrides `auth.json`):
	- `AUTH_USER` and `AUTH_PASSWORD` — override login credentials.
	- `FLASK_SECRET` — set a secure secret for Flask sessions.

API endpoints
- POST /api/search — search records. JSON payload examples:
	- single-field search: {"type":"single", "label":"NOMBRE", "value":"Juan"}
	- pat/mat OR: {"type":"paterno_or_materno", "term": "Perez"}
	- pat+mat AND: {"type":"paterno_and_materno", "paterno":"Perez", "materno":"Lopez"}
	- full name: {"type":"full_name","nombre":"JUAN","paterno":"PEREZ","materno":"LOPEZ"}

- GET /api/status — returns JSON with readiness and record counts.
- POST /api/reload — triggers a background rebuild of the SQLite DB (safe to call while server is running).

Security and blocking rules
- The app intentionally blocks a set of names and identifiers configured in `api.py`. These rules are for demonstration and should be adapted to your policy.

Testing

Install dev/test dependencies and run pytest:

```bash
pip install -r requirements-dev.txt
pytest -q
```

Notes/Assumptions
- `client_data.py` is the canonical CSV loader; there used to be a `code.py` file before renaming. If you kept `code.py` rename it to `client_data.py` to avoid import conflicts.

Contributing

This project welcomes small improvements and fixes. If you plan larger changes (e.g. switching to a proper authentication layer or adding API rate limiting), open an issue first so we can discuss the design.

Optional follow-ups
- Add a `LICENSE` file (MIT recommended) if you want to open-source the repository. This README does not change project licensing.
- Add a simple GitHub Actions workflow to run tests and build the DB as a sanity check.

Expose the local site with ngrok
--------------------------------

If you want to share the interactive page for testing or demos, use ngrok to create a secure public URL that tunnels to your local server.

1. Install ngrok:

	- Quick install script (Linux x86_64):

	  ./scripts/install_ngrok.sh

	- Or follow instructions at https://ngrok.com/download for other platforms.

2. Authenticate ngrok (run once after signing up on ngrok):

	ngrok authtoken <your-token>

3. Start the server and tunnel (this script starts `python api.py` and opens a tunnel to port 5000):

	chmod +x ./scripts/*.sh
	./scripts/ngrok.sh

	If you prefer a different port, pass it as an argument: `./scripts/ngrok.sh 8000`

4. The script prints a public URL (for example: https://a1b2c3.ngrok.io). Open it and log-in with your credentials.

Troubleshooting
---------------
- If the public URL does not show up immediately, check `/tmp/ngrok.log` for ngrok startup messages.
- If your local server uses gunicorn (recommended for production) you can run it first, then open an ngrok tunnel to the same port, eg: `gunicorn api:app --bind 0.0.0.0:8000` then `ngrok http 8000`.
- If you prefer an integrated approach inside Python, see the `pyngrok` library, but be aware of additional dependencies and token setup.
	- Fallback: If your system ngrok binary is out-of-date or incompatible with your ngrok account, you can use `pyngrok` (it downloads a modern ngrok agent for you):

		./scripts/pyngrok.sh

		This starts the Flask app and creates a public URL using `pyngrok`. If you want to set the auth token with an environment variable instead of `~/.ngrok2/ngrok.yml` use `NGROK_AUTH_TOKEN`:

		NGROK_AUTH_TOKEN=xxx ./scripts/pyngrok.sh

Large files, DB and Git LFS

- If your `data.db` is large (for example > 100MB), pushing directly to GitHub will fail. We prepared the repository for Git LFS by adding `.gitattributes`; to upload the DB with LFS do the following locally:

	1. Install Git LFS: https://git-lfs.github.com
	2. Initialize LFS in your repo: `git lfs install`
	3. Track the DB file: `git lfs track "data.db"` (this updates `.gitattributes`)
	4. Stage LFS files: `git add .gitattributes data.db`
	5. Commit: `git commit -m "Add data.db via Git LFS"`
	6. Push: `git push origin main` — the DB will be uploaded to LFS storage instead of Git objects

- Caveat: GitHub applies storage/transfer quotas to LFS; large (>1GB) files may require a paid plan. If you need larger storage or don’t want to use LFS, consider one of the following:
	- Upload `data.db` to Render's persistent disk (for production/deployment) and do not commit it to the repository.
	- Upload `data.db` as a GitHub release asset and attach a small sample DB in the repository for CI/tests.
	- Use an object store (S3 or similar) and download the DB during the build step in Render.

Deploying on Render.com

This project can be deployed as a simple Web Service on Render. Minimal steps:

1. Create a new Web Service on Render and connect your GitHub repository.
2. Set the runtime to Python. Leave the default branch set to `main`.
3. Set the Build Command and Start Command to:

	Build Command: pip install -r requirements.txt && python build_db.py || true
	Start Command: gunicorn api:app --bind 0.0.0.0:$PORT

4. Add environment variables on Render:
	- AUTH_USER and AUTH_PASSWORD — override the login credentials
	- FLASK_SECRET — a secure secret for sessions

5. If you need to process large CSV files, add a persistent disk to the service and upload your CSVs there. Update `build_db.py` or the `DATA_DIRECTORY` in `client_data.py` to point to that disk so the DB can be built during deployment.

  Quick example: download `data.db` from a private S3 bucket during the build

  1. Set these Environment variables on Render (Environment → Environment Variables):
	  - AWS_ACCESS_KEY_ID
	  - AWS_SECRET_ACCESS_KEY
	  - AWS_DEFAULT_REGION
	  - Optionally: DATA_DIRECTORY (for where the DB will be written)
  2. In Render Build Command, download the DB into the `DATA_DIRECTORY` and build the DB if needed:

	  pip install -r requirements.txt
	# Download using Python (uses boto3 and IAM):
	python scripts/fetch_db_from_s3.py s3://my-bucket/path/to/data.db || true
	  python build_db.py || true

  This will keep your `data.db` private (it is stored in S3) and the instance will download it during each deploy.

Notes for debugging
- Check the Render Build Logs for a line that says "Downloading ..." followed by "Downloaded to" coming from `fetch_db_from_s3.py`. If you don't see these lines, either the script didn't run or there was an error; look earlier in the build logs for Python/boto3 errors.
- If you prefer `awscli` instead of boto3, you can add `pip install awscli` to the build command and use `aws s3 cp` as before.
6. Optional: use `render.yaml` included in the repository to declare the service. After the first deploy, you can edit the service settings in the Render dashboard.

Note that the `Data/` directory is ignored in the public repository by default to avoid committing large/sensitive CSVs. For a persistent copy, use a disk, or store the CSVs in a private object store and download during the build phase.

Contact
- Repository owner: Charly-bite — https://github.com/Charly-bite
