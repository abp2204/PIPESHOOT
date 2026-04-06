from fastapi.testclient import TestClient
from app.main import create_app


def test_health():
    app = create_app()
    client = TestClient(app)
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'


def test_analyze_smoke():
    app = create_app()
    client = TestClient(app)
    r = client.post('/analyze', data={'logs': 'ModuleNotFoundError: No module named pandas'})
    assert r.status_code == 200
    j = r.json()
    assert 'result' in j