# Farmart Backend - Your Assigned Parts

## 👤 **Your Responsibilities**

### 🐮 **Person 2 – Animals & Orders**
- Manage all animal listings
- Handle orders and order items
- Implement filtering and search

### 🚜 **Farmer Dashboard Backend**
- View orders from customers
- Accept/reject orders
- Delete animals

---

## 📋 **Your Specific Endpoints**

### 🐄 **Animal Management (Person 2)**

#### `GET /api/animals`
Get all animal listings with filtering
```bash
curl "http://localhost:5000/api/animals"
curl "http://localhost:5000/api/animals?type=sheep&min_price=100"
```

#### `GET /api/animals/{id}`
Get specific animal by ID
```bash
curl "http://localhost:5000/api/animals/1"
```

#### `GET /api/animals/farmers/{id}/animals`
Get all animals for a specific farmer
```bash
curl "http://localhost:5000/api/animals/farmers/1/animals"
```

### 📦 **Order Management (Person 2)**

#### `GET /api/orders`
Get all orders with filtering
```bash
curl "http://localhost:5000/api/orders"
curl "http://localhost:5000/api/orders?status=confirmed"
```

#### `GET /api/orders/{id}`
Get specific order by ID
```bash
curl "http://localhost:5000/api/orders/1"
```

#### `GET /api/orders/users/{id}/orders`
Get all orders for a specific user
```bash
curl "http://localhost:5000/api/orders/users/2/orders"
```

#### `GET /api/orders/{id}/items`
Get all items for a specific order
```bash
curl "http://localhost:5000/api/orders/1/items"
```

#### `GET /api/orders/order_items?animal_id=456`
Get order items by animal ID (Bonus)
```bash
curl "http://localhost:5000/api/orders/order_items?animal_id=1"
```

### 🚜 **Farmer Dashboard**

#### `GET /api/orders/farmer/orders`
See orders from users (requires farmer auth)
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:5000/api/orders/farmer/orders"
```

#### `PATCH /api/orders/{id}/status`
Accept or deny orders (requires farmer auth)
```bash
curl -X PATCH \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"status": "confirmed", "farmer_notes": "Order accepted!"}' \
     "http://localhost:5000/api/orders/1/status"
```

#### `DELETE /api/animals/{id}`
Delete animal (requires farmer auth)
```bash
curl -X DELETE \
     -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:5000/api/animals/1"
```

---

## 🎯 **Bonus Features Implemented**

### ✅ **Calculate total_amount of orders**
- Orders automatically calculate total from order items
- Available in order responses

### ✅ **Add farmer_notes**
- Farmers can add notes when updating order status
- Notes stored in `farmer_notes` field

### ✅ **Handle M:N relationship between animals and orders**
- Many-to-Many relationship via `order_items` table
- Animals can be in multiple orders
- Orders can contain multiple animals

---

## 🏗️ **Project Structure**

```
farmart-backend/
├── models/
│   ├── __init__.py          # Models package
│   ├── user_model.py        # User model
│   ├── animal_model.py      # Animal model (Your responsibility)
│   └── order_model.py       # Order & OrderItem models (Your responsibility)
├── routes/
│   ├── animal_routes.py     # Animal endpoints (Your responsibility)
│   └── order_routes.py      # Order endpoints (Your responsibility)
├── app_new.py              # Main application (Your parts only)
├── test_your_parts.py      # Tests for your endpoints
├── config.py               # Configuration
└── requirements.txt        # Dependencies
```

---

## 🧪 **Testing Your Parts**

Run tests for your specific endpoints:
```bash
python -m pytest test_your_parts.py -v
```

Start the server:
```bash
python app_new.py
```

Visit: http://localhost:5000 to see your endpoint documentation

---

## 🔄 **API Response Format**

All your endpoints return consistent JSON responses:

### Success Response:
```json
{
  "success": true,
  "data": { /* your data */ },
  "pagination": { /* if applicable */ }
}
```

### Error Response:
```json
{
  "success": false,
  "error": "Error message"
}
```

---

## 🚀 **Ready for Integration**

Your backend parts are:
- ✅ **Properly structured** to avoid merge conflicts
- ✅ **Fully tested** with comprehensive test suite
- ✅ **Well documented** with clear API endpoints
- ✅ **Bonus features** implemented
- ✅ **Ready for frontend integration**

Your teammates can now build the frontend using your API endpoints without conflicts!
