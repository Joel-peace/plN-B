# Farmart Backend API

A Flask-based REST API for connecting farmers directly with customers, eliminating middlemen in farm animal sales.

## Features

### Farmer Features
- User registration and authentication
- Add, update, edit, and delete animals for sale
- View and manage orders
- Confirm or reject orders

### Customer Features
- User registration and authentication  
- Browse all available animals
- Search animals by type and breed
- Filter animals by breed and age
- Add animals to cart
- Checkout and place orders
- View order history

## Tech Stack
- **Backend**: Python Flask
- **Database**: PostgreSQL
- **Authentication**: JWT tokens
- **Testing**: Pytest

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info

### Animals
- `GET /api/animals/` - Get all animals (with filtering/search)
- `GET /api/animals/{id}` - Get specific animal
- `POST /api/animals/` - Create new animal (farmers only)
- `PUT /api/animals/{id}` - Update animal (farmers only)
- `DELETE /api/animals/{id}` - Delete animal (farmers only)
- `GET /api/animals/my-animals` - Get farmer's animals

### Cart Management
- `GET /api/users/cart` - Get cart items
- `POST /api/users/cart` - Add item to cart
- `PUT /api/users/cart/{id}` - Update cart item
- `DELETE /api/users/cart/{id}` - Remove from cart
- `DELETE /api/users/cart/clear` - Clear entire cart

### Orders
- `POST /api/orders/` - Create order from cart
- `GET /api/orders/` - Get user's orders
- `GET /api/orders/{id}` - Get specific order
- `PUT /api/orders/{id}/status` - Update order status (farmers only)

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd farmart-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` file with your database credentials and secret keys.

5. Set up PostgreSQL database:
```bash
# Create database
createdb farmart_db

# Update DATABASE_URL in .env file
DATABASE_URL=postgresql://username:password@localhost:5432/farmart_db
```

6. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Testing

Run tests using pytest:
```bash
pytest test_app.py -v
```

## Database Models

### User
- id, username, email, password_hash, user_type, created_at

### Animal  
- id, name, type, breed, age, weight, price, description, image_url, is_available, farmer_id, created_at

### Order
- id, customer_id, status, total_amount, created_at, updated_at

### OrderItem
- id, order_id, animal_id, quantity, price

### CartItem
- id, user_id, animal_id, quantity, created_at

## Usage Examples

### Register a Farmer
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "farmer_john",
    "email": "john@farm.com", 
    "password": "secure123",
    "user_type": "farmer"
  }'
```

### Add an Animal (Farmer)
```bash
curl -X POST http://localhost:5000/api/animals/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Bessie",
    "type": "cow",
    "breed": "Holstein", 
    "age": 24,
    "weight": 500.0,
    "price": 1500.0,
    "description": "Healthy dairy cow"
  }'
```

### Search Animals
```bash
curl "http://localhost:5000/api/animals/?type=cow&breed=Holstein&min_age=12&max_age=36"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests to ensure they pass
6. Submit a pull request

## License

MIT License
