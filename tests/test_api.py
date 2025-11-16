import json
import os
import sys
# Ensure project root is importable for tests
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import api


def make_sample_data():
    return [
        {
            "CVE": "1",
            "NOMBRE": "Juan",
            "PATERNO": "Perez",
            "MATERNO": "Lopez",
            "CURP": "XXX"
        }
    ]


def test_home():
    client = api.app.test_client()
    # Log in first (session cookie will persist in the test client)
    creds = {'username': api.AUTH_USER, 'password': api.AUTH_PASSWORD}
    # follow redirects so we land on the home page
    # Use form data (Flask's test client will encode correctly)
    client.post('/login', data=creds, follow_redirects=True)
    # Some test runners do not preserve session cookies across requests; ensure session is set
    with client.session_transaction() as sess:
        sess['user'] = api.AUTH_USER
    resp = client.get('/')
    assert resp.status_code == 200
    # Home returns HTML; check for a known string in the template
    html = resp.get_data(as_text=True)
    assert 'La historia de una brecha' in html or 'Datos Sensibles' in html


def test_search_single(monkeypatch):
    sample = make_sample_data()
    monkeypatch.setattr(api, 'get_data', lambda use_cache=True: sample)
    # Ensure DB mode is disabled for these tests so the in-memory loader is used
    monkeypatch.setattr(api, 'DB_PATH', '/tmp/does_not_exist_12345.db')
    client = api.app.test_client()
    client.post('/login', data={'username': api.AUTH_USER, 'password': api.AUTH_PASSWORD}, follow_redirects=True)
    with client.session_transaction() as sess:
        sess['user'] = api.AUTH_USER

    payload = {"type": "single", "label": "NOMBRE", "value": "juan"}
    resp = client.post('/api/search', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 200
    results = resp.get_json()
    assert len(results) == 1


def test_search_paterno_or_materno(monkeypatch):
    sample = make_sample_data()
    monkeypatch.setattr(api, 'get_data', lambda use_cache=True: sample)
    # Ensure DB mode is disabled for these tests so the in-memory loader is used
    monkeypatch.setattr(api, 'DB_PATH', '/tmp/does_not_exist_12345.db')
    client = api.app.test_client()
    client.post('/login', data={'username': api.AUTH_USER, 'password': api.AUTH_PASSWORD}, follow_redirects=True)
    with client.session_transaction() as sess:
        sess['user'] = api.AUTH_USER

    payload = {"type": "paterno_or_materno", "term": "Perez"}
    resp = client.post('/api/search', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 200
    results = resp.get_json()
    assert len(results) == 1


def test_search_full_name(monkeypatch):
    sample = make_sample_data()
    monkeypatch.setattr(api, 'get_data', lambda use_cache=True: sample)
    # Ensure DB mode is disabled for these tests so the in-memory loader is used
    monkeypatch.setattr(api, 'DB_PATH', '/tmp/does_not_exist_12345.db')
    client = api.app.test_client()
    client.post('/login', data={'username': api.AUTH_USER, 'password': api.AUTH_PASSWORD}, follow_redirects=True)
    with client.session_transaction() as sess:
        sess['user'] = api.AUTH_USER

    payload = {"type": "full_name", "nombre": "Juan", "paterno": "Perez", "materno": "Lopez"}
    resp = client.post('/api/search', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 200
    results = resp.get_json()
    assert len(results) == 1
