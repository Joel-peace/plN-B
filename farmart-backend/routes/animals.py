from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Animal, User
from sqlalchemy import or_, and_

animals_bp = Blueprint('animals', __name__)

@animals_bp.route('/', methods=['GET'])
def get_all_animals():
    try:
        # Get query parameters for filtering and searching
        animal_type = request.args.get('type')
        breed = request.args.get('breed')
        min_age = request.args.get('min_age', type=int)
        max_age = request.args.get('max_age', type=int)
        search = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Animal.query.filter_by(is_available=True)
        
        # Apply filters
        if animal_type:
            query = query.filter(Animal.type.ilike(f'%{animal_type}%'))
        if breed:
            query = query.filter(Animal.breed.ilike(f'%{breed}%'))
        if min_age:
            query = query.filter(Animal.age >= min_age)
        if max_age:
            query = query.filter(Animal.age <= max_age)
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
            'animals': [animal.to_dict() for animal in animals.items],
            'total': animals.total,
            'pages': animals.pages,
            'current_page': page,
            'per_page': per_page,
            'has_next': animals.has_next,
            'has_prev': animals.has_prev
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@animals_bp.route('/<int:animal_id>', methods=['GET'])
def get_animal(animal_id):
    try:
        animal = Animal.query.get(animal_id)
        if not animal:
            return jsonify({'error': 'Animal not found'}), 404
        
        return jsonify({'animal': animal.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@animals_bp.route('/', methods=['POST'])
@jwt_required()
def create_animal():
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'farmer':
            return jsonify({'error': 'Only farmers can add animals'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'type', 'breed', 'age', 'weight', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new animal
        animal = Animal(
            name=data['name'],
            type=data['type'],
            breed=data['breed'],
            age=data['age'],
            weight=data['weight'],
            price=data['price'],
            description=data.get('description', ''),
            image_url=data.get('image_url', ''),
            farmer_id=current_user_id
        )
        
        db.session.add(animal)
        db.session.commit()
        
        return jsonify({
            'message': 'Animal added successfully',
            'animal': animal.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@animals_bp.route('/<int:animal_id>', methods=['PUT'])
@jwt_required()
def update_animal(animal_id):
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'farmer':
            return jsonify({'error': 'Only farmers can update animals'}), 403
        
        animal = Animal.query.get(animal_id)
        if not animal:
            return jsonify({'error': 'Animal not found'}), 404
        
        if animal.farmer_id != current_user_id:
            return jsonify({'error': 'You can only update your own animals'}), 403
        
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            animal.name = data['name']
        if 'type' in data:
            animal.type = data['type']
        if 'breed' in data:
            animal.breed = data['breed']
        if 'age' in data:
            animal.age = data['age']
        if 'weight' in data:
            animal.weight = data['weight']
        if 'price' in data:
            animal.price = data['price']
        if 'description' in data:
            animal.description = data['description']
        if 'image_url' in data:
            animal.image_url = data['image_url']
        if 'is_available' in data:
            animal.is_available = data['is_available']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Animal updated successfully',
            'animal': animal.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@animals_bp.route('/<int:animal_id>', methods=['DELETE'])
@jwt_required()
def delete_animal(animal_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'farmer':
            return jsonify({'error': 'Only farmers can delete animals'}), 403
        
        animal = Animal.query.get(animal_id)
        if not animal:
            return jsonify({'error': 'Animal not found'}), 404
        
        if animal.farmer_id != current_user_id:
            return jsonify({'error': 'You can only delete your own animals'}), 403
        
        db.session.delete(animal)
        db.session.commit()
        
        return jsonify({'message': 'Animal deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@animals_bp.route('/my-animals', methods=['GET'])
@jwt_required()
def get_farmer_animals():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or user.user_type != 'farmer':
            return jsonify({'error': 'Only farmers can access this endpoint'}), 403
        
        animals = Animal.query.filter_by(farmer_id=current_user_id).all()
        
        return jsonify({
            'animals': [animal.to_dict() for animal in animals]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
