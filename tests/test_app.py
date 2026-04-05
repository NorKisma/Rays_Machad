import pytest
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_app_creation(app):
    assert app is not None

def test_home_page(client):
    response = client.get('/')
    # Assuming the app redirects to login or has a home page. 
    # Just checking for not 404 for now, or 302 (redirect)
    assert response.status_code in [200, 302]
