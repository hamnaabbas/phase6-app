import sys
import os
import json
sys.path.insert(0, 'src')

os.environ['DATABASE_URL'] = 'sqlite:///test.db'
os.environ['SECRET_KEY'] = 'test-secret'
os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret'

from app import app, db, User, Item

def setup_function():
    with app.app_context():
        db.create_all()

def teardown_function():
    with app.app_context():
        db.drop_all()

def test_register():
    tester = app.test_client()
    response = tester.post('/api/register',
                          json={'username': 'testuser', 'email': 'test@example.com', 'password': 'password123'},
                          content_type='application/json')
    assert response.status_code == 201
    assert response.json['user']['username'] == 'testuser'

def test_login():
    tester = app.test_client()
    # Register first
    tester.post('/api/register',
               json={'username': 'loginuser', 'email': 'login@example.com', 'password': 'password123'},
               content_type='application/json')
    
    # Login
    response = tester.post('/api/login',
                          json={'username': 'loginuser', 'password': 'password123'},
                          content_type='application/json')
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_protected_endpoint_without_token():
    tester = app.test_client()
    response = tester.get('/api/items')
    assert response.status_code == 401

def test_full_workflow():
    tester = app.test_client()
    
    # Register
    tester.post('/api/register',
               json={'username': 'workflowuser', 'email': 'workflow@example.com', 'password': 'password123'},
               content_type='application/json')
    
    # Login
    login_response = tester.post('/api/login',
                                json={'username': 'workflowuser', 'password': 'password123'},
                                content_type='application/json')
    token = login_response.json['access_token']
    
    # Create item with token
    headers = {'Authorization': f'Bearer {token}'}
    item_response = tester.post('/api/items',
                               json={'name': 'Test Item', 'description': 'With auth'},
                               content_type='application/json',
                               headers=headers)
    assert item_response.status_code == 201
    
    # Get items with token
    get_response = tester.get('/api/items', headers=headers)
    assert get_response.status_code == 200
    assert len(get_response.json) >= 1