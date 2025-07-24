import pytest
import json
from app_new import create_app
from models import db, User, Animal, Order, OrderItem

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        
        # Create test data
        # Create farmer user
        farmer = User(username='testfarmer', email='farmer@test.com', user_type='farmer')
        farmer.set_password('password123')
        db.session.add(farmer)
        db.session.flush()
        
        # Create customer user
        customer = User(username='testcustomer', email='customer@test.com', user_type='customer')
        customer.set_password('password123')
        db.session.add(customer)
        db.session.flush()
        
        # Create test animals
        animals = [
            Animal(name='Bessie', type='cow', breed='Holstein', age=24, weight=500, price=1500, farmer_id=farmer.id),
            Animal(name='Woolly', type='sheep', breed='Merino', age=18, weight=80, price=200, farmer_id=farmer.id),
            Animal(name='Porky', type='pig', breed='Yorkshire', age=12, weight=100, price=800, farmer_id=farmer.id)
        ]
        
        for animal in animals:
            db.session.add(animal)
        
        db.session.flush()
        
        # Create test order
        order = Order(customer_id=customer.id, total_amount=1700, status='pending')
        db.session.add(order)
        db.session.flush()
        
        # Create order items
        order_items = [
            OrderItem(order_id=order.id, animal_id=animals[0].id, quantity=1, price=1500),
            OrderItem(order_id=order.id, animal_id=animals[1].id, quantity=1, price=200)
        ]
        
        for item in order_items:
            db.session.add(item)
        
        db.session.commit()
        
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# ===== TEST YOUR PERSON 2 RESPONSIBILITIES =====

def test_get_all_animals(client):
    """Test GET /animals - Your Person 2 responsibility"""
    response = client.get('/api/animals/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] == True
    assert len(data['animals']) == 3
    assert 'pagination' in data

def test_get_animal_by_id(client):
    """Test GET /animals/{id} - Your Person 2 responsibility"""
    response = client.get('/api/animals/1')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['animal']['name'] == 'Bessie'

def test_get_farmer_animals(client):
    """Test GET /farmers/{id}/animals - Your Person 2 responsibility"""
    response = client.get('/api/animals/farmers/1/animals')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] == True
    assert len(data['animals']) == 3
    assert data['farmer']['username'] == 'testfarmer'

def test_filter_animals_by_type_and_price(client):
    """Test FETCH /animals?type=sheep&min_price=100 - Your Person 2 responsibility"""
    response = client.get('/api/animals/?type=sheep&min_price=100')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] == True
    assert len(data['animals']) == 1
    assert data['animals'][0]['type'] == 'sheep'
    assert data['animals'][0]['price'] >= 100

def test_get_all_orders(client):
    """Test GET /orders - Your Person 2 responsibility"""
    response = client.get('/api/orders/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] == True
    assert len(data['orders']) == 1

def test_get_order_by_id(client):
    """Test GET /orders/{id} - Your Person 2 responsibility"""
    response = client.get('/api/orders/1')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['order']['id'] == 1
    assert data['order']['total_amount'] == 1700

def test_get_user_orders(client):
    """Test GET /users/{id}/orders - Your Person 2 responsibility"""
    response = client.get('/api/orders/users/2/orders')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] == True
    assert len(data['orders']) == 1
    assert data['user']['username'] == 'testcustomer'

def test_filter_orders_by_status(client):
    """Test FETCH /orders?status=confirmed - Your Person 2 responsibility"""
    response = client.get('/api/orders/?status=pending')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] == True
    assert len(data['orders']) == 1
    assert data['orders'][0]['status'] == 'pending'

def test_get_order_items(client):
    """Test GET /orders/{id}/items - Your Person 2 responsibility"""
    response = client.get('/api/orders/1/items')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] == True
    assert len(data['items']) == 2
    assert data['total_amount'] == 1700

def test_get_order_items_by_animal(client):
    """Test FETCH /order_items?animal_id=456 - Your Person 2 responsibility"""
    response = client.get('/api/orders/order_items?animal_id=1')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] == True
    assert len(data['order_items']) == 1
    assert data['animal']['name'] == 'Bessie'

# ===== TEST FARMER DASHBOARD RESPONSIBILITIES =====

def test_farmer_dashboard_requires_auth(client):
    """Test that farmer dashboard endpoints require authentication"""
    response = client.get('/api/orders/farmer/orders')
    assert response.status_code == 401  # Unauthorized

def test_patch_order_status_requires_auth(client):
    """Test that PATCH order status requires authentication"""
    response = client.patch('/api/orders/1/status', 
                           json={'status': 'confirmed'})
    assert response.status_code == 401  # Unauthorized

def test_delete_animal_requires_auth(client):
    """Test that DELETE animal requires authentication"""
    response = client.delete('/api/animals/1')
    assert response.status_code == 401  # Unauthorized

# ===== TEST BONUS FEATURES =====

def test_order_total_calculation(client):
    """Test that order total is calculated correctly - Bonus feature"""
    response = client.get('/api/orders/1')
    data = json.loads(response.data)
    
    # Verify total is sum of all items
    expected_total = sum(item['subtotal'] for item in data['order']['items'])
    assert data['order']['total_amount'] == expected_total

def test_farmer_notes_field_exists(client):
    """Test that farmer_notes field exists - Bonus feature"""
    response = client.get('/api/orders/1')
    data = json.loads(response.data)
    
    assert 'farmer_notes' in data['order']

def test_many_to_many_relationship(client):
    """Test M:N relationship between animals and orders - Bonus feature"""
    response = client.get('/api/orders/1/items')
    data = json.loads(response.data)
    
    # Verify that order items contain animal information
    for item in data['items']:
        assert 'animal' in item
        assert item['animal'] is not None
        assert 'id' in item['animal']

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
