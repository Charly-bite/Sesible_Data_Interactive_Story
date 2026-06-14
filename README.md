# Datos Sensibles — Interactive Story & Secure Query Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/Flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)

An interactive web application and secure query engine designed for browsing and analyzing client records. Built as a case study for **Securing Data in the Cloud**, the application examines historical data breaches (e.g., the 2016 INE Electoral Register leak) to demonstrate secure hosting practices, encryption controls, and access restrictions.

> [!CAUTION]
> **Privacy and Compliance Notice:**
> The dataset processed by this application may contain personally identifiable information (PII). This repository features deliberate query restrictions and identifier exclusions for demonstration purposes. Ensure compliance with local privacy laws (e.g., GDPR, CCPA, Ley Federal de Protección de Datos Personales) and do not deploy sensitive data to public cloud environments without proper authorization.

---

## System Architecture

The application is structured as a single-instance Python Flask service serving a glassmorphic frontend interface:

```mermaid
graph TD
    Client[Browser Frontend] -->|Auth Session| Server[Flask API Server]
    
    subgraph Frontend Pages
        login[login.html - Glassmorphic login]
        historia[historia.html - Interactive UI & Search]
    end
    
    subgraph Flask Backend (api.py)
        A[Session Middleware] -->|Query Routing| S[Search API]
        S -->|Option 1: Index Lookups| SQLite[(SQLite DB: data.db)]
        S -->|Option 2: Fallback| Mem[In-memory CSV Cache]
        Filter[Blocked Record Filter] -->|Sanitize Results| Client
    end
    
    Client -.->|Request Static Assets| login
    Client -.->|Interact with Story| historia
    historia -->|Ajax POST /api/search| A
    S -.-> Filter
```

---

## File Structure

```
Sesible_Data_Interactive_Story/
│
├── Data/                       # Local directory for raw CSV datasets (git-ignored)
├── moodboard/                  # Frontend styling sheets, images, and layout assets
├── scripts/                    # Helper scripts for networking and deployment (e.g. ngrok)
├── tests/                      # Pytest unit tests for validating query and filter behavior
│
├── api.py                      # Core Flask web server, auth middleware, and query routes
├── client_data.py              # CSV parsing utility and index management
├── build_db.py                 # SQLite database compiler for high-speed local queries
├── database.py                 # DB connection and abstraction layer (Postgres / SQLite)
│
├── login.html                  # Overhauled premium Glassmorphism login page
├── historia.html               # Main interactive dashboard and query client
├── historia.js                 # Frontend API integration and client-side rendering engine
├── historia.json               # Local metadata file storing story chapters/information
│
├── render.yaml                 # Infrastructure-as-code declaration for Render.com deployment
├── requirements.txt            # Application dependencies
└── README.md                   # This instruction manual
```

---

## Getting Started

Follow these steps to configure, seed, and launch the application on your local machine.

### 1. Environment Configuration
Create and activate a Python virtual environment:
```bash
# Create environment
python3 -m venv .venv

# Activate environment (Unix/macOS)
source .venv/bin/activate

# Activate environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
Install the required application packages:
```bash
pip install -r requirements.txt
```

### 3. Database Seeding & Mock Data
The database engine expects dataset columns aligned with `client_data.EXPECTED_LABELS`. 
1. Create or place your CSV files in the `Data/` directory.
2. Compile the local SQLite database for fast lookups:
   ```bash
   python build_db.py
   ```

### 4. Run the Server
Launch the Flask backend server:
```bash
python api.py
```
Visit `http://127.0.0.1:5000/` in your browser.

> [!TIP]
> Use the default development credentials for verification:
> * **Username**: `Storytelling`
> * **Password**: `DatosSensibles2025$`
> (These can be overridden by copying `auth.json.example` to `auth.json` or defining the `AUTH_USER`/`AUTH_PASSWORD` environment variables).

---

## API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/login` | `GET` / `POST` | Serves and validates session credentials. |
| `/logout` | `GET` | Invalidates active user session. |
| `/api/status` | `GET` | Returns database readiness and record count. |
| `/api/reload` | `POST` | Rebuilds the SQLite database asynchronously in the background. |
| `/api/search` | `POST` | Queries the client database with specific options. |

### Search JSON Payloads:
*   **Single Field**: `{"type":"single", "label":"NOMBRE", "value":"Juan"}`
*   **Or Search (Paterno or Materno)**: `{"type":"paterno_or_materno", "term": "Perez"}`
*   **And Search (Paterno and Materno)**: `{"type":"paterno_and_materno", "paterno":"Perez", "materno":"Lopez"}`
*   **Full Name**: `{"type":"full_name", "nombre":"JUAN", "paterno":"PEREZ", "materno":"LOPEZ"}`

---

## Security Filters

The search endpoints pass all outputs through a strict output filtration layer (`BLOCKED_FULL_NAMES` and `BLOCKED_IDENTIFIERS` in `api.py`). If a search result matches a blocked profile, it is filtered out of the API JSON response to demonstrate selective disclosure and access restrictions.

---

## Testing

Ensure code changes are valid by running the test suite:
```bash
pip install -r requirements-dev.txt
pytest -v
```

---

## Production Deployment on Render

This repository includes a `render.yaml` configuration to allow quick deployment as a Web Service.

### Build Configuration:
*   **Build Command**: `pip install -r requirements.txt && python build_db.py || true`
*   **Start Command**: `gunicorn api:app --bind 0.0.0.0:$PORT`

### Environment Variables:
Ensure you configure these on your Render dashboard:
- `AUTH_USER`: Custom username for logging in.
- `AUTH_PASSWORD`: Custom secure password.
- `FLASK_SECRET`: A cryptographically secure secret string for session cookies.
- `DATABASE_URL`: (Optional) Remote PostgreSQL connection string.

---

## Public Demo via ngrok

To temporarily expose your local server publicly for demonstrations:
1. Run `./scripts/install_ngrok.sh` to fetch the binary (or install it manually).
2. Authenticate the agent:
   ```bash
   ngrok authtoken <your-auth-token>
   ```
3. Boot the Flask app and tunnel:
   ```bash
   ./scripts/ngrok.sh
   ```
