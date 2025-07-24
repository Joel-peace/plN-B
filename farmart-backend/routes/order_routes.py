from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Order, OrderItem, Animal, User
from datetime import datetime

# Blueprint for order routes
order_bp = Blueprint('orders', __name__)

# ===== YOUR PERSON 2 RESPONSIBILITIES =====

@order_bp.route('/', methods=['GET'])
def get_all_orders():
    """
    GET /orders - Get all orders
    Your Person 2 responsibility
    """
    try:
        # Get query parameters for filtering
        status = request.args.get('status')  # FETCH /orders?status=confirmed
        customer_id = request.args.get('customer_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Order.query
        
        # Apply filters
        if status:
            query = query.filter(Order.status == status)
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        
        # Order by most recent first
        query = query.order_by(Order.created_at.desc())
        
        # Paginate results
        orders = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'orders': [order.to_dict() for order in orders.items],
            'pagination': {
                'total': orders.total,
                'pages': orders.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': orders.has_next,
                'has_prev': orders.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id):
    """
    GET /orders/{id} - Get specific order by ID
    Your Person 2 responsibility
    """
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        return jsonify({
            'success': True,
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@order_bp.route('/users/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """
    GET /users/{id}/orders - Get all orders for a specific user
    Your Person 2 responsibility
    """
    try:
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        # Build query
        query = Order.query.filter_by(customer_id=user_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        # Order by most recent first
        query = query.order_by(Order.created_at.desc())
        
        # Paginate
        orders = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type
            },
            'orders': [order.to_dict() for order in orders.items],
            'pagination': {
                'total': orders.total,
                'pages': orders.pages,
                'current_page': page,
                'per_page': per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@order_bp.route('/<int:order_id>/items', methods=['GET'])
def get_order_items(order_id):
    """
    GET /orders/{id}/items - Get all items for a specific order
    Your Person 2 responsibility
    """
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'items': [item.to_dict() for item in order.order_items],
            'items_count': len(order.order_items),
            'total_amount': order.total_amount
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@order_bp.route('/order_items', methods=['GET'])
def get_order_items_by_animal():
    """
    FETCH /order_items?animal_id=456 - Get order items by animal ID
    Your Person 2 responsibility (Bonus feature)
    """
    try:
        animal_id = request.args.get('animal_id', type=int)
        
        if not animal_id:
            return jsonify({
                'success': False,
                'error': 'animal_id parameter is required'
            }), 400
        
        # Verify animal exists
        animal = Animal.query.get(animal_id)
        if not animal:
            return jsonify({
                'success': False,
                'error': 'Animal not found'
            }), 404
        
        # Get order items for this animal
        order_items = OrderItem.query.filter_by(animal_id=animal_id).all()
        
        return jsonify({
            'success': True,
            'animal': animal.to_summary_dict(),
            'order_items': [item.to_dict() for item in order_items],
            'total_items': len(order_items)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== FARMER DASHBOARD RESPONSIBILITIES =====

@order_bp.route('/farmer/orders', methods=['GET'])
@jwt_required()
def get_farmer_orders():
    """
    GET /farmer/orders - Get orders for current farmer (Farmer Dashboard)
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'farmer':
            return jsonify({
                'success': False,
                'error': 'Only farmers can access this endpoint'
            }), 403
        
        # Get orders containing this farmer's animals
        orders = db.session.query(Order).join(OrderItem).join(Animal).filter(
            Animal.farmer_id == current_user_id
        ).distinct().order_by(Order.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'farmer': user.to_dict(),
            'orders': [order.to_dict() for order in orders],
            'total_orders': len(orders)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@order_bp.route('/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
def update_order_status(order_id):
    """
    PATCH /orders/{id}/status - Accept or deny order (Farmer Dashboard)
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'farmer':
            return jsonify({
                'success': False,
                'error': 'Only farmers can update order status'
            }), 403
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        # Check if farmer has animals in this order
        farmer_animals = db.session.query(OrderItem).join(Animal).filter(
            OrderItem.order_id == order_id,
            Animal.farmer_id == current_user_id
        ).first()
        
        if not farmer_animals:
            return jsonify({
                'success': False,
                'error': 'You can only update orders containing your animals'
            }), 403
        
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Status is required'
            }), 400
        
        new_status = data['status']
        if new_status not in ['pending', 'confirmed', 'rejected', 'completed']:
            return jsonify({
                'success': False,
                'error': 'Invalid status. Must be: pending, confirmed, rejected, or completed'
            }), 400
        
        # Update order
        old_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        # Add farmer notes if provided (Bonus feature)
        if 'farmer_notes' in data:
            order.farmer_notes = data['farmer_notes']
        
        # If order is confirmed, mark farmer's animals as unavailable
        if new_status == 'confirmed':
            for item in order.order_items:
                if item.animal.farmer_id == current_user_id:
                    item.animal.is_available = False
        
        # If order is rejected, make sure animals remain available
        elif new_status == 'rejected':
            for item in order.order_items:
                if item.animal.farmer_id == current_user_id:
                    item.animal.is_available = True
        
        # Recalculate total amount (Bonus feature)
        order.calculate_total_amount()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Order status updated from "{old_status}" to "{new_status}"',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
