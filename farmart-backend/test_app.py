import pytest
import json
from app import create_app
from models import db, User, Animal

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Register a test farmer
    farmer_data = {
        'username': 'testfarmer',
        'email': 'farmer@test.com',
        'password': 'password123',
        'user_type': 'farmer'
    }
    
    response = client.post('/api/auth/register', 
                          data=json.dumps(farmer_data),
                          content_type='application/json')
    
    try:
        farmer_token = json.loads(response.data)['access_token']
    except KeyError:
        print('Register Farmer Response:', response.status_code, response.data)

    # Register a test customer
    customer_data = {
        'username': 'testcustomer',
        'email': 'customer@test.com',
        'password': 'password123',
        'user_type': 'customer'
    }

    response = client.post('/api/auth/register',
                          data=json.dumps(customer_data),
                          content_type='application/json')

    try:
        customer_token = json.loads(response.data)['access_token']
    except KeyError:
        print('Register Customer Response:', response.status_code, response.data)
    
    return {
        'farmer': {'Authorization': f'Bearer {farmer_token}'},
        'customer': {'Authorization': f'Bearer {customer_token}'}
    }

def test_user_registration(client):
    """Test user registration"""
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'user_type': 'farmer'
    }
    
    response = client.post('/api/auth/register',
                          data=json.dumps(user_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'access_token' in data
    assert data['user']['username'] == 'testuser'

def test_user_login(client):
    """Test user login"""
    # First register a user
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'user_type': 'farmer'
    }
    
    client.post('/api/auth/register',
               data=json.dumps(user_data),
               content_type='application/json')
    
    # Now login
    login_data = {
        'username': 'testuser',
        'password': 'password123'
    }
    
    response = client.post('/api/auth/login',
                          data=json.dumps(login_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data

def test_create_animal(client, auth_headers):
    """Test animal creation by farmer"""
    animal_data = {
        'name': 'Bessie',
        'type': 'cow',
        'breed': 'Holstein',
        'age': 24,
        'weight': 500.0,
        'price': 1500.0,
        'description': 'Healthy dairy cow'
    }
    
    response = client.post('/api/animals/',
                          data=json.dumps(animal_data),
                          content_type='application/json',
                          headers=auth_headers['farmer'])
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['animal']['name'] == 'Bessie'

def test_get_animals(client, auth_headers):
    """Test getting all animals"""
    # First create an animal
    animal_data = {
        'name': 'Bessie',
        'type': 'cow',
        'breed': 'Holstein',
        'age': 24,
        'weight': 500.0,
        'price': 1500.0
    }
    
    client.post('/api/animals/',
               data=json.dumps(animal_data),
               content_type='application/json',
               headers=auth_headers['farmer'])
    
    # Now get all animals
    response = client.get('/api/animals/')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['animals']) > 0

def test_add_to_cart(client, auth_headers):
    """Test adding animal to cart"""
    # First create an animal
    animal_data = {
        'name': 'Bessie',
        'type': 'cow',
        'breed': 'Holstein',
        'age': 24,
        'weight': 500.0,
        'price': 1500.0
    }
    
    response = client.post('/api/animals/',
                          data=json.dumps(animal_data),
                          content_type='application/json',
                          headers=auth_headers['farmer'])
    
    animal_id = json.loads(response.data)['animal']['id']
    
    # Add to cart
    cart_data = {
        'animal_id': animal_id,
        'quantity': 1
    }
    
    response = client.post('/api/users/cart',
                          data=json.dumps(cart_data),
                          content_type='application/json',
                          headers=auth_headers['customer'])
    
    assert response.status_code == 201

if __name__ == '__main__':
    pytest.main([__file__])
