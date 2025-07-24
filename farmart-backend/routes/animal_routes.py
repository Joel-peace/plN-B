from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Animal, User
from sqlalchemy import or_, and_

# Blueprint for animal routes
animal_bp = Blueprint('animals', __name__)

# ===== YOUR PERSON 2 RESPONSIBILITIES =====

@animal_bp.route('/', methods=['GET'])
def get_all_animals():
    """
    GET /animals - Get all animal listings
    Your Person 2 responsibility
    """
    try:
        # Get query parameters for filtering and searching
        animal_type = request.args.get('type')  # e.g., type=sheep
        breed = request.args.get('breed')
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        min_price = request.args.get('min_price', type=float)  # e.g., min_price=100
        max_price = request.args.get('max_price', type=float)
        search = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Animal.query.filter_by(is_available=True)
        
        # Apply filters - FETCH /animals?type=sheep&min_price=100
        if animal_type:
            query = query.filter(Animal.type.ilike(f'%{animal_type}%'))
        if breed:
            query = query.filter(Animal.breed.ilike(f'%{breed}%'))
        if min_age:
            query = query.filter(Animal.age >= min_age)
        if max_age:
            query = query.filter(Animal.age <= max_age)
        if min_price:
            query = query.filter(Animal.price >= min_price)
        if max_price:
            query = query.filter(Animal.price <= max_price)
        if search:
            query = query.filter(or_(
                Animal.name.ilike(f'%{search}%'),
                Animal.type.ilike(f'%{search}%'),
                Animal.breed.ilike(f'%{search}%'),
                Animal.description.ilike(f'%{search}%')
            ))
        
        # Paginate results
        animals = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'animals': [animal.to_dict() for animal in animals.items],
            'pagination': {
                'total': animals.total,
                'pages': animals.pages,
                'current_page': page,
                'per_page': per_page,
                'has_next': animals.has_next,
                'has_prev': animals.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@animal_bp.route('/<int:animal_id>', methods=['GET'])
def get_animal_by_id(animal_id):
    """
    GET /animals/{id} - Get specific animal by ID
    Your Person 2 responsibility
    """
    try:
        animal = Animal.query.get(animal_id)
        if not animal:
            return jsonify({
                'success': False,
                'error': 'Animal not found'
            }), 404
        
        return jsonify({
            'success': True,
            'animal': animal.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@animal_bp.route('/farmers/<int:farmer_id>/animals', methods=['GET'])
def get_farmer_animals(farmer_id):
    """
    GET /farmers/{id}/animals - Get all animals for a specific farmer
    Your Person 2 responsibility
    """
    try:
        # Verify farmer exists
        farmer = User.query.filter_by(id=farmer_id, user_type='farmer').first()
        if not farmer:
            return jsonify({
                'success': False,
                'error': 'Farmer not found'
            }), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get farmer's animals
        animals = Animal.query.filter_by(farmer_id=farmer_id).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'farmer': {
                'id': farmer.id,
                'username': farmer.username,
                'email': farmer.email
            },
            'animals': [animal.to_dict() for animal in animals.items],
            'pagination': {
                'total': animals.total,
                'pages': animals.pages,
                'current_page': page,
                'per_page': per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ===== FARMER DASHBOARD RESPONSIBILITIES =====

@animal_bp.route('/<int:animal_id>', methods=['DELETE'])
@jwt_required()
def delete_animal(animal_id):
    """
    DELETE /animals/{id} - Delete animal (Farmer Dashboard responsibility)
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'farmer':
            return jsonify({
                'success': False,
                'error': 'Only farmers can delete animals'
            }), 403
        
        animal = Animal.query.get(animal_id)
        if not animal:
            return jsonify({
                'success': False,
                'error': 'Animal not found'
            }), 404
        
        if animal.farmer_id != current_user_id:
            return jsonify({
                'success': False,
                'error': 'You can only delete your own animals'
            }), 403
        
        db.session.delete(animal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Animal "{animal.name}" deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
