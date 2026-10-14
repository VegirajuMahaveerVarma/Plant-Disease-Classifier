from fastapi.testclient import TestClient
from app.main import app

def test_root_health_and_disease_library():
    with TestClient(app) as client:
        assert client.get('/').status_code == 200
        assert client.get('/health').status_code == 200
        response = client.get('/api/v1/diseases')
        assert response.status_code == 200
        assert len(response.json()['items']) >= 3

def test_prediction_requires_real_model():
    with TestClient(app) as client:
        if client.get('/health').json()['model'] == 'not_configured':
            response = client.post('/api/v1/predict', files={'file': ('leaf.png', b'not an image', 'image/png')})
            assert response.status_code == 503
            assert 'Model is not configured' in response.json()['detail']
