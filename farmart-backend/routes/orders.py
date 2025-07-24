from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, OrderItem, Animal, User, CartItem
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'customer':
            return jsonify({'error': 'Only customers can create orders'}), 403
        
        # Get cart items for the user
        cart_items = CartItem.query.filter_by(user_id=current_user_id).all()
        
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Calculate total amount
        total_amount = 0
        order_items_data = []
        
        for cart_item in cart_items:
            animal = cart_item.animal
            if not animal or not animal.is_available:
                return jsonify({'error': f'Animal {animal.name if animal else "Unknown"} is no longer available'}), 400
            
            item_total = animal.price * cart_item.quantity
            total_amount += item_total
            
            order_items_data.append({
                'animal_id': animal.id,
                'quantity': cart_item.quantity,
                'price': animal.price
            })
        
        # Create order
        order = Order(
            customer_id=current_user_id,
            total_amount=total_amount,
            status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Get order ID
        
        # Create order items
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                animal_id=item_data['animal_id'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(order_item)
        
        # Clear cart
        CartItem.query.filter_by(user_id=current_user_id).delete()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.user_type == 'customer':
            orders = Order.query.filter_by(customer_id=current_user_id).order_by(Order.created_at.desc()).all()
        elif user.user_type == 'farmer':
            # Get orders that contain the farmer's animals
            orders = db.session.query(Order).join(OrderItem).join(Animal).filter(
                Animal.farmer_id == current_user_id
            ).distinct().order_by(Order.created_at.desc()).all()
        else:
            return jsonify({'error': 'Invalid user type'}), 400
        
        return jsonify({
            'orders': [order.to_dict() for order in orders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check if user has access to this order
        has_access = False
        if user.user_type == 'customer' and order.customer_id == current_user_id:
            has_access = True
        elif user.user_type == 'farmer':
            # Check if any item in the order belongs to this farmer
            farmer_animals = db.session.query(OrderItem).join(Animal).filter(
                OrderItem.order_id == order_id,
                Animal.farmer_id == current_user_id
            ).first()
            if farmer_animals:
                has_access = True
        
        if not has_access:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'order': order.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.user_type != 'farmer':
            return jsonify({'error': 'Only farmers can update order status'}), 403
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check if farmer has animals in this order
        farmer_animals = db.session.query(OrderItem).join(Animal).filter(
            OrderItem.order_id == order_id,
            Animal.farmer_id == current_user_id
        ).first()
        
        if not farmer_animals:
            return jsonify({'error': 'You can only update orders containing your animals'}), 403
        
        data = request.get_json()
        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        if data['status'] not in ['pending', 'confirmed', 'rejected', 'completed']:
            return jsonify({'error': 'Invalid status'}), 400
        
        order.status = data['status']
        order.updated_at = datetime.utcnow()
        
        # If order is confirmed, mark animals as unavailable
        if data['status'] == 'confirmed':
            for item in order.order_items:
                if item.animal.farmer_id == current_user_id:
                    item.animal.is_available = False
        
        db.session.commit()
        
        return jsonify({
            'message': 'Order status updated successfully',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
