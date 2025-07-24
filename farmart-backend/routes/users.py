from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, CartItem, Animal

users_bp = Blueprint('users', __name__)

@users_bp.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'customer':
            return jsonify({'error': 'Only customers can access cart'}), 403
        
        cart_items = CartItem.query.filter_by(user_id=current_user_id).all()
        
        total_amount = sum(item.animal.price * item.quantity for item in cart_items if item.animal)
        
        return jsonify({
            'cart_items': [item.to_dict() for item in cart_items],
            'total_amount': total_amount,
            'total_items': len(cart_items)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/cart', methods=['POST'])
@jwt_required()
def add_to_cart():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'customer':
            return jsonify({'error': 'Only customers can add items to cart'}), 403
        
        data = request.get_json()
        
        if 'animal_id' not in data:
            return jsonify({'error': 'animal_id is required'}), 400
        
        animal = Animal.query.get(data['animal_id'])
        if not animal:
            return jsonify({'error': 'Animal not found'}), 404
        
        if not animal.is_available:
            return jsonify({'error': 'Animal is not available'}), 400
        
        quantity = data.get('quantity', 1)
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be greater than 0'}), 400
        
        # Check if item already exists in cart
        existing_item = CartItem.query.filter_by(
            user_id=current_user_id,
            animal_id=data['animal_id']
        ).first()
        
        if existing_item:
            existing_item.quantity += quantity
        else:
            cart_item = CartItem(
                user_id=current_user_id,
                animal_id=data['animal_id'],
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        return jsonify({'message': 'Item added to cart successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/cart/<int:cart_item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(cart_item_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'customer':
            return jsonify({'error': 'Only customers can update cart items'}), 403
        
        cart_item = CartItem.query.get(cart_item_id)
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        if cart_item.user_id != current_user_id:
            return jsonify({'error': 'You can only update your own cart items'}), 403
        
        data = request.get_json()
        
        if 'quantity' in data:
            if data['quantity'] <= 0:
                return jsonify({'error': 'Quantity must be greater than 0'}), 400
            cart_item.quantity = data['quantity']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cart item updated successfully',
            'cart_item': cart_item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/cart/<int:cart_item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(cart_item_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'customer':
            return jsonify({'error': 'Only customers can remove cart items'}), 403
        
        cart_item = CartItem.query.get(cart_item_id)
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        if cart_item.user_id != current_user_id:
            return jsonify({'error': 'You can only remove your own cart items'}), 403
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({'message': 'Item removed from cart successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/cart/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'customer':
            return jsonify({'error': 'Only customers can clear cart'}), 403
        
        CartItem.query.filter_by(user_id=current_user_id).delete()
        db.session.commit()
        
        return jsonify({'message': 'Cart cleared successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
