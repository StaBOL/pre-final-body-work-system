import pytest
from backend.app import create_app
from backend.models import db, User

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register(client):
    resp = client.post('/api/register', json={'email':'test@ex.com','password':'123'})
    assert resp.status_code == 201

def test_login(client):
    client.post('/api/register', json={'email':'test@ex.com','password':'123'})
    resp = client.post('/api/login', json={'email':'test@ex.com','password':'123'})
    assert 'access_token' in resp.get_json()