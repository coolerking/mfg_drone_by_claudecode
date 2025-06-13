"""
Unit tests for main application
"""
import pytest
import sys
import os

# Add admin directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

@pytest.mark.unit
def test_app_creation(flask_app):
    """Test Flask app can be created"""
    assert flask_app is not None
    assert flask_app.config['TESTING'] is True

@pytest.mark.unit 
def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'

@pytest.mark.unit
def test_index_endpoint(client):
    """Test index endpoint returns HTML"""
    response = client.get('/')
    assert response.status_code == 200
    assert 'text/html' in response.content_type

@pytest.mark.unit
def test_app_config(flask_app):
    """Test app configuration"""
    assert flask_app.secret_key == 'test-secret-key'
    assert flask_app.config['WTF_CSRF_ENABLED'] is False

@pytest.mark.unit
def test_404_handling(client):
    """Test 404 error handling"""
    response = client.get('/nonexistent-endpoint')
    assert response.status_code == 404