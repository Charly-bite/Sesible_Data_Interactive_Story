from flask import Flask, request, jsonify, send_file, send_from_directory, redirect, session, url_for
import threading
from flask_cors import CORS
import os
import sqlite3
import json
import client_data
import uuid
from build_db import DB_PATH, build_db

# --- IMPORTANT: Rename code.py to client_data.py to avoid module conflict ---
# If you have not already, rename your code.py file to client_data.py
# and update any imports accordingly.

EXPECTED_LABELS = client_data.EXPECTED_LABELS
DATA_DIRECTORY = client_data.DATA_DIRECTORY
DB_EXISTS = os.path.exists(DB_PATH)

# List of blocked persons (tuple of nombre, paterno, materno) in lowercase
BLOCKED_FULL_NAMES = [
    ("carlos alberto", "aceves", "cabrera"),
]
# Optional blocked identifiers (CURP, CVE, etc.) -- lowercase
BLOCKED_IDENTIFIERS = set([
    # Add known unique identifiers (lowercased). These will be blocked as well.
    'aecc940910hjccbr04',
    'accbcr94091014h600',
])


# Authentication configuration: load from environment variables or auth.json
def load_auth_config():
    """Return (username, password) from env vars or auth.json; fall back to defaults."""
    user = os.environ.get('AUTH_USER')
    pwd = os.environ.get('AUTH_PASSWORD')
    if user and pwd:
        return user, pwd
    try:
        if os.path.exists('auth.json'):
            with open('auth.json', 'r', encoding='utf-8') as fh:
                j = json.load(fh)
                u = j.get('username')
                p = j.get('password')
                if u and p:
                    return u, p
    except Exception:
        pass
    # sensible defaults (kept for backward compatibility)
    return 'Storytelling', 'DatosSensibles2025$'


AUTH_USER, AUTH_PASSWORD = load_auth_config()

def load_multiple_client_data(filepaths):
    """Backwards compatibility wrapper to client_data.load_multiple_client_data."""
    return client_data.load_multiple_client_data(filepaths)

_cached_data = None
# _data_list holds the list of records (same as _cached_data)
_data_list = None
# simple indexes: field -> { lower_value: [indices] }
_indexes = {}
# Fields we will index for faster lookups. Keep this small to save memory.
INDEX_FIELDS = ['NOMBRE', 'PATERNO', 'MATERNO', 'CURP']


def build_indexes(data_list):
    """Build simple inverted indexes mapping lowercase value -> list of indices.

    This stores integer indices to keep memory overhead lower than duplicating
    full records.
    """
    global _indexes
    _indexes = {f: {} for f in INDEX_FIELDS}
    for i, rec in enumerate(data_list):
        for f in INDEX_FIELDS:
            val = rec.get(f)
            if not val:
                continue
            key = val.lower()
            _indexes[f].setdefault(key, []).append(i)


_data_lock = threading.Lock()


def get_data(use_cache=True):
    """Return loaded client data, with optional in-memory caching.

    This uses the `client_data` loader so we avoid code duplication. When data
    is first loaded we also build the in-memory indexes for the common fields.
    """
    global _cached_data, _data_list
    if use_cache and _cached_data is not None:
        return _cached_data

    data_files = [os.path.join(DATA_DIRECTORY, f) for f in os.listdir(DATA_DIRECTORY) if f.lower().endswith('.csv')]
    # Protect loading so only one thread loads at a time
    with _data_lock:
        # Another thread may have loaded while waiting for the lock
        if use_cache and _cached_data is not None:
            return _cached_data
        _cached_data = client_data.load_multiple_client_data(data_files)
    # Ensure we always return a list (empty) rather than None for safety
    if _cached_data is None:
        _cached_data = []

    _data_list = _cached_data
    # Build indexes in a try/except to avoid crashing the server on index issues
    try:
        build_indexes(_data_list)
    except Exception as e:
        # If indexing fails, log to stderr and continue without indexes
        import sys
        print(f"Warning: Failed to build indexes: {e}", file=sys.stderr)
        _indexes.clear()

    return _cached_data


def get_db_connection():
    """Return a new sqlite3 connection with row factory as dict.

    Caller should close the connection when done.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# Create the Flask app and allow CORS for all routes
app = Flask(__name__)
# Secret key for session signing. In production set via environment variable.
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-change-me-Storytelling-2025-!')
CORS(app)


@app.before_request
def require_login_for_pages():
    """Global enforcement: require session login for non-public pages.

    - Allow: /login, moodboard assets, /auth.json.example, /api/status
    - For other /api/* endpoints return JSON 401 when unauthenticated
    - For page requests redirect to /login when unauthenticated
    """
    public_prefixes = ('/moodboard', '/static')
    public_paths = ('/login', '/auth.json.example', '/api/status')
    path = request.path

    # Always allow public prefixes and paths
    if any(path.startswith(p) for p in public_prefixes) or path in public_paths:
        return None

    # If user is authenticated, enforce page-token for normal pages
    if session.get('user') == AUTH_USER:
        # Allow API calls if authenticated
        if path.startswith('/api/'):
            return None
        # Allow public prefixes/paths even when authenticated
        if any(path.startswith(p) for p in public_prefixes) or path in public_paths:
            return None
        # For page requests require a one-time page token (consumed on use)
        token = session.pop('page_token', None)
        if token:
            return None
        # No valid page token: require fresh login
        return redirect(url_for('login'))

    # If not authenticated: handle API vs page requests
    if path.startswith('/api/'):
        return jsonify({'error': 'unauthorized', 'message': 'authentication required'}), 401
    return redirect(url_for('login'))


@app.route('/', methods=['GET'])
def home():
    """Serve the main HTML page."""
    # Require login to access the main page (use configured auth user)
    if session.get('user') != AUTH_USER:
        return redirect(url_for('login'))
    return send_file('historia.html')


@app.route('/historia.html', methods=['GET'])
def historia_file():
    """Also protect direct requests to /historia.html so users can't bypass login."""
    if session.get('user') != AUTH_USER:
        return redirect(url_for('login'))
    return send_file('historia.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Render login page (GET) and handle login submission (POST).

    Accepts form-encoded or JSON payload with 'username' and 'password'.
    On successful authentication sets session['user'] and redirects to '/'.
    """
    # Allow simple JSON or form posts
    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form or {}
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '')

        # Credentials (configurable via env or auth.json)
        if username == AUTH_USER and password == AUTH_PASSWORD:
            session['user'] = AUTH_USER
            # Issue a one-time page token so the served page is valid for a single load.
            session['page_token'] = uuid.uuid4().hex
            return redirect(url_for('home'))
        # Authentication failed: redirect back to login with error
        return redirect(url_for('login', error=1))

    # GET -> serve login page
    return send_file('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user', None)
    session.pop('page_token', None)
    return redirect(url_for('login'))


@app.route('/moodboard/<path:filename>')
def moodboard_files(filename):
    """Serve files from the moodboard directory (images, css, etc.).

    This allows the front-end to request /moodboard/images/logo.png and similar
    assets without needing a separate static server.
    """
    return send_from_directory('moodboard', filename)

@app.route('/api/search', methods=['POST'])
def search():
    try:
        req = request.get_json(silent=True) or {}
        # Require an authenticated session for API search
        if session.get('user') != AUTH_USER:
            return jsonify({'error': 'unauthorized', 'message': 'authentication required'}), 401
        search_type = req.get('type')

        # Pagination / limits
        limit = int(req.get('limit') or 100)
        if limit <= 0 or limit > 1000:
            limit = 100
        offset = int(req.get('offset') or 0)

        # If SQLite DB exists, use it for all searches
        if os.path.exists(DB_PATH):
            conn = get_db_connection()
            cur = conn.cursor()

            def row_to_dict(row):
                return {k: row[k] for k in row.keys()}

            def is_blocked_row_dict(d):
                # Normalize and check blocked full names and identifiers
                nombre = (d.get('NOMBRE') or '').strip().lower()
                paterno = (d.get('PATERNO') or '').strip().lower()
                materno = (d.get('MATERNO') or '').strip().lower()
                full = ' '.join([nombre, paterno, materno]).strip()
                # Exact tuple match
                if (nombre, paterno, materno) in BLOCKED_FULL_NAMES:
                    return True
                # Also block if the concatenated full name contains the blocked full name
                for bn, bp, bm in BLOCKED_FULL_NAMES:
                    blocked_full = ' '.join([bn, bp, bm]).strip()
                    if blocked_full and blocked_full in full:
                        return True
                # Check identifiers (CURP, CVE) if present
                curp = (d.get('CURP') or '').strip().lower()
                cve = (d.get('CVE') or '').strip().lower()
                if curp in BLOCKED_IDENTIFIERS or cve in BLOCKED_IDENTIFIERS:
                    return True
                return False

            if search_type == 'single':
                label = req.get('label')
                value = (req.get('value') or '').strip()
                if not label or value == '':
                    conn.close()
                    return jsonify([])
                if label in ['NOMBRE', 'PATERNO', 'MATERNO', 'CURP']:
                    cur.execute(f"SELECT * FROM clients WHERE \"{label}_LC\" = ? LIMIT ? OFFSET ?", (value.lower(), limit, offset))
                else:
                    # Use case-insensitive match using COLLATE NOCASE
                    cur.execute(f"SELECT * FROM clients WHERE \"{label}\" = ? COLLATE NOCASE LIMIT ? OFFSET ?", (value, limit, offset))
                rows = cur.fetchall()
                conn.close()
                results = [row_to_dict(r) for r in rows]
                # Filter blocked persons
                results = [r for r in results if not is_blocked_row_dict(r)]
                return jsonify(results)

            elif search_type == 'paterno_or_materno':
                term = (req.get('term') or '').strip().lower()
                if not term:
                    conn.close()
                    return jsonify([])
                cur.execute("SELECT * FROM clients WHERE PATERNO_LC = ? OR MATERNO_LC = ? LIMIT ? OFFSET ?", (term, term, limit, offset))
                rows = cur.fetchall()
                conn.close()
                results = [row_to_dict(r) for r in rows]
                results = [r for r in results if not is_blocked_row_dict(r)]
                return jsonify(results)

            elif search_type == 'paterno_and_materno':
                paterno = (req.get('paterno') or '').strip().lower()
                materno = (req.get('materno') or '').strip().lower()
                if not paterno or not materno:
                    conn.close()
                    return jsonify([])
                cur.execute("SELECT * FROM clients WHERE PATERNO_LC = ? AND MATERNO_LC = ? LIMIT ? OFFSET ?", (paterno, materno, limit, offset))
                rows = cur.fetchall()
                conn.close()
                results = [row_to_dict(r) for r in rows]
                results = [r for r in results if not is_blocked_row_dict(r)]
                return jsonify(results)

            elif search_type == 'full_name':
                nombre = (req.get('nombre') or '').strip().lower()
                paterno = (req.get('paterno') or '').strip().lower()
                materno = (req.get('materno') or '').strip().lower()
                if not nombre or not paterno or not materno:
                    conn.close()
                    return jsonify([])
                cur.execute("SELECT * FROM clients WHERE NOMBRE_LC = ? AND PATERNO_LC = ? AND MATERNO_LC = ? LIMIT ? OFFSET ?", (nombre, paterno, materno, limit, offset))
                rows = cur.fetchall()
                conn.close()
                results = [row_to_dict(r) for r in rows]
                results = [r for r in results if not is_blocked_row_dict(r)]
                return jsonify(results)

    # Fallback: no DB - use in-memory approach (may be slow)
        data = get_data()
        results = []
        def records_from_indices(indices):
            return [data[i] for i in indices]

        if search_type == 'single':
            label = req.get('label')
            value = (req.get('value') or '').lower()
            if label in _indexes and value:
                indices = _indexes.get(label, {}).get(value, [])
                results = records_from_indices(indices)
            else:
                for record in data:
                    if (record.get(label) or '').lower() == value:
                        results.append(record)

        elif search_type == 'paterno_or_materno':
            term = (req.get('term') or '').lower()
            if not term:
                results = []
            else:
                p_idx = set(_indexes.get('PATERNO', {}).get(term, []))
                m_idx = set(_indexes.get('MATERNO', {}).get(term, []))
                if p_idx or m_idx:
                    results = records_from_indices(sorted(p_idx.union(m_idx)))
                else:
                    results = client_data.search_clients_paterno_or_materno(data, term)

        elif search_type == 'paterno_and_materno':
            paterno = (req.get('paterno') or '').lower()
            materno = (req.get('materno') or '').lower()
            if paterno and materno and 'PATERNO' in _indexes and 'MATERNO' in _indexes:
                p_list = set(_indexes.get('PATERNO', {}).get(paterno, []))
                m_list = set(_indexes.get('MATERNO', {}).get(materno, []))
                common = sorted(p_list.intersection(m_list))
                results = records_from_indices(common)
            else:
                results = client_data.search_clients_paterno_and_materno(data, paterno, materno)

        elif search_type == 'full_name':
            nombre = (req.get('nombre') or '').lower()
            paterno = (req.get('paterno') or '').lower()
            materno = (req.get('materno') or '').lower()
            if nombre and paterno and materno and all(f in _indexes for f in ('NOMBRE','PATERNO','MATERNO')):
                n_idx = set(_indexes['NOMBRE'].get(nombre, []))
                p_idx = set(_indexes['PATERNO'].get(paterno, []))
                m_idx = set(_indexes['MATERNO'].get(materno, []))
                common = sorted(n_idx.intersection(p_idx).intersection(m_idx))
                results = records_from_indices(common)
            else:
                results = client_data.search_clients_full_name(data, nombre, paterno, materno)

        # Filter blocked persons from in-memory results as well
        def is_blocked_record(rec):
            nombre = (rec.get('NOMBRE') or '').strip().lower()
            paterno = (rec.get('PATERNO') or '').strip().lower()
            materno = (rec.get('MATERNO') or '').strip().lower()
            full = ' '.join([nombre, paterno, materno]).strip()
            if (nombre, paterno, materno) in BLOCKED_FULL_NAMES:
                return True
            for bn, bp, bm in BLOCKED_FULL_NAMES:
                blocked_full = ' '.join([bn, bp, bm]).strip()
                if blocked_full and blocked_full in full:
                    return True
            curp = (rec.get('CURP') or '').strip().lower()
            cve = (rec.get('CVE') or '').strip().lower()
            if curp in BLOCKED_IDENTIFIERS or cve in BLOCKED_IDENTIFIERS:
                return True
            return False

        filtered = [r for r in results if not is_blocked_record(r)]
        return jsonify(filtered)
    except Exception as e:
        # Log exception to server console and return JSON error response
        import traceback, sys
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        return (
            jsonify({
                'error': 'internal_server_error',
                'message': str(e),
                'trace': tb.splitlines()[-20:]
            }),
            500,
        )


@app.route('/api/reload', methods=['POST'])
def reload_data():
    """Force reload the data from CSV files.

    Useful for manual refreshes after updating the dataset.
    """
    # Trigger a rebuild of the SQLite DB in background. Do not block the caller.
    def _rebuild():
        try:
            build_db()
        except Exception:
            import traceback
            traceback.print_exc()

    t = threading.Thread(target=_rebuild, daemon=True)
    t.start()
    return jsonify({"reloaded": True, "started": True})


@app.route('/api/status', methods=['GET'])
def status():
    """Return basic readiness and record count."""
    # Do not trigger loading here; report current cached state
    ready = bool(_cached_data)
    records = len(_cached_data) if _cached_data else 0
    return jsonify({
        'ready': ready,
        'records': records,
        'indexed_fields': list(_indexes.keys())
    })

if __name__ == '__main__':
    # Start data loading in a background thread so the server can accept
    # connections (and return a 'not ready' status) while CSVs are loaded.
    def _background_load():
        try:
            print('Background: checking/creating SQLite DB...')
            # If DB already exists, skip heavy in-memory loading
            if not os.path.exists(DB_PATH):
                print('Background: DB not found, building DB...')
                build_db()
                print('Background: DB build complete')
            else:
                print('Background: DB already exists, skipping build')
        except Exception as e:
            import traceback
            traceback.print_exc()

    loader_thread = threading.Thread(target=_background_load, daemon=True)
    loader_thread.start()

    print('Starting server (data may still be loading in background)')
    # disable the reloader so we don't get multiple processes with duplicate loaders
    app.run(debug=False, threaded=True, use_reloader=False)


# Global error handler to always return JSON for unhandled exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    import traceback, sys
    tb = traceback.format_exc()
    print(tb, file=sys.stderr)
    return jsonify({'error': 'internal_server_error', 'message': str(e), 'trace': tb.splitlines()[-20:]}), 500
