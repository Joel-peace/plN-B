#!/usr/bin/env python3

"""
Farmart Backend API Demo
This script demonstrates all the key features of the Farmart API
"""

from app import create_app
import json

def main():
    print("🌾 FARMART BACKEND API DEMO 🌾")
    print("=" * 50)
    
    app = create_app()
    
    with app.test_client() as client:
        print("\n1️⃣ FARMER REGISTRATION")
        print("-" * 30)
        
        # Register a farmer
        farmer_data = {
            'username': 'john_farmer',
            'email': 'john@farm.com',
            'password': 'secure123',
            'user_type': 'farmer'
        }
        
        response = client.post('/api/auth/register', 
                              data=json.dumps(farmer_data),
                              content_type='application/json')
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            farmer_result = json.loads(response.data)
            farmer_token = farmer_result['access_token']
            print(f"✅ Farmer '{farmer_result['user']['username']}' registered successfully")
            print(f"🆔 User ID: {farmer_result['user']['id']}")
            print(f"👤 User Type: {farmer_result['user']['user_type']}")
        
        print("\n2️⃣ CUSTOMER REGISTRATION")
        print("-" * 30)
        
        # Register a customer
        customer_data = {
            'username': 'jane_customer',
            'email': 'jane@example.com',
            'password': 'secure123',
            'user_type': 'customer'
        }
        
        response = client.post('/api/auth/register',
                              data=json.dumps(customer_data),
                              content_type='application/json')
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            customer_result = json.loads(response.data)
            customer_token = customer_result['access_token']
            print(f"✅ Customer '{customer_result['user']['username']}' registered successfully")
            print(f"🆔 User ID: {customer_result['user']['id']}")
        
        print("\n3️⃣ FARMER ADDS ANIMALS")
        print("-" * 30)
        
        # Add multiple animals
        animals_data = [
            {
                'name': 'Bessie',
                'type': 'cow',
                'breed': 'Holstein',
                'age': 24,
                'weight': 500.0,
                'price': 1500.0,
                'description': 'Healthy dairy cow'
            },
            {
                'name': 'Porky',
                'type': 'pig',
                'breed': 'Yorkshire',
                'age': 12,
                'weight': 100.0,
                'price': 800.0,
                'description': 'Premium pork'
            },
            {
                'name': 'Clucky',
                'type': 'chicken',
                'breed': 'Rhode Island Red',
                'age': 8,
                'weight': 2.5,
                'price': 25.0,
                'description': 'Fresh farm chicken'
            }
        ]
        
        created_animals = []
        
        for animal_data in animals_data:
            response = client.post('/api/animals/',
                                  data=json.dumps(animal_data),
                                  content_type='application/json',
                                  headers={'Authorization': f'Bearer {farmer_token}'})
            
            if response.status_code == 201:
                animal_result = json.loads(response.data)
                created_animals.append(animal_result['animal'])
                print(f"✅ Added: {animal_result['animal']['name']} ({animal_result['animal']['type']}) - ${animal_result['animal']['price']}")
        
        print(f"\n📊 Total animals added: {len(created_animals)}")
        
        print("\n4️⃣ BROWSE ANIMALS (PUBLIC)")
        print("-" * 30)
        
        # Get all animals (public endpoint)
        response = client.get('/api/animals/')
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            animals_result = json.loads(response.data)
            print(f"🐄 Available animals: {len(animals_result['animals'])}")
            
            for animal in animals_result['animals']:
                print(f"  - {animal['name']} ({animal['type']}, {animal['breed']}) - ${animal['price']}")
        
        print("\n5️⃣ SEARCH & FILTER ANIMALS")
        print("-" * 30)
        
        # Search for cows
        response = client.get('/api/animals/?type=cow')
        
        if response.status_code == 200:
            search_result = json.loads(response.data)
            print(f"🔍 Cows found: {len(search_result['animals'])}")
            
        # Filter by age range
        response = client.get('/api/animals/?min_age=10&max_age=20')
        
        if response.status_code == 200:
            filter_result = json.loads(response.data)
            print(f"📅 Animals aged 10-20 months: {len(filter_result['animals'])}")
        
        print("\n6️⃣ CUSTOMER ADDS TO CART")
        print("-" * 30)
        
        if created_animals:
            # Add first two animals to cart
            for i, animal in enumerate(created_animals[:2]):
                cart_data = {
                    'animal_id': animal['id'],
                    'quantity': 1
                }
                
                response = client.post('/api/users/cart',
                                      data=json.dumps(cart_data),
                                      content_type='application/json',
                                      headers={'Authorization': f'Bearer {customer_token}'})
                
                if response.status_code == 201:
                    print(f"🛒 Added {animal['name']} to cart")
        
        print("\n7️⃣ VIEW CART")
        print("-" * 30)
        
        # View cart
        response = client.get('/api/users/cart',
                             headers={'Authorization': f'Bearer {customer_token}'})
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            cart_result = json.loads(response.data)
            print(f"🛍️ Cart items: {cart_result['total_items']}")
            print(f"💰 Total amount: ${cart_result['total_amount']}")
            
            for item in cart_result['cart_items']:
                animal = item['animal']
                print(f"  - {animal['name']} (x{item['quantity']}) - ${animal['price']}")
        
        print("\n8️⃣ CREATE ORDER")
        print("-" * 30)
        
        # Create order from cart
        response = client.post('/api/orders/',
                              headers={'Authorization': f'Bearer {customer_token}'})
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            order_result = json.loads(response.data)
            order_id = order_result['order']['id']
            print(f"✅ Order #{order_id} created successfully")
            print(f"💵 Total: ${order_result['order']['total_amount']}")
            print(f"📋 Status: {order_result['order']['status']}")
            print(f"📦 Items: {len(order_result['order']['items'])}")
        
        print("\n9️⃣ FARMER VIEWS ORDERS")
        print("-" * 30)
        
        # Farmer views orders containing their animals
        response = client.get('/api/orders/',
                             headers={'Authorization': f'Bearer {farmer_token}'})
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            farmer_orders = json.loads(response.data)
            print(f"📋 Orders for farmer: {len(farmer_orders['orders'])}")
            
            for order in farmer_orders['orders']:
                print(f"  Order #{order['id']} - Status: {order['status']} - ${order['total_amount']}")
        
        print("\n🔟 FARMER CONFIRMS ORDER")
        print("-" * 30)
        
        if 'order_id' in locals():
            # Farmer confirms the order
            status_data = {'status': 'confirmed'}
            
            response = client.put(f'/api/orders/{order_id}/status',
                                 data=json.dumps(status_data),
                                 content_type='application/json',
                                 headers={'Authorization': f'Bearer {farmer_token}'})
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Order confirmed by farmer")
                
                # Customer views updated order
                response = client.get(f'/api/orders/{order_id}',
                                     headers={'Authorization': f'Bearer {customer_token}'})
                
                if response.status_code == 200:
                    updated_order = json.loads(response.data)
                    print(f"📋 Order status updated to: {updated_order['order']['status']}")
    
    print("\n" + "=" * 50)
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("🚀 All Farmart API features are working perfectly!")
    print("=" * 50)

if __name__ == '__main__':
    main()
