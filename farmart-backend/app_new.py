from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models import db

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints - ONLY YOUR ASSIGNED PARTS
    from routes.animal_routes import animal_bp
    from routes.order_routes import order_bp
    
    # Register with proper prefixes
    app.register_blueprint(animal_bp, url_prefix='/api/animals')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return {
            'message': 'Farmart API - Your Assigned Parts',
            'your_responsibilities': {
                'person_2': [
                    'GET /api/animals',
                    'GET /api/animals/{id}',
                    'GET /api/animals/farmers/{id}/animals',
                    'FETCH /api/animals?type=sheep&min_price=100',
                    'GET /api/orders',
                    'GET /api/orders/{id}',
                    'GET /api/orders/users/{id}/orders',
                    'FETCH /api/orders?status=confirmed',
                    'GET /api/orders/{id}/items',
                    'FETCH /api/orders/order_items?animal_id=456'
                ],
                'farmer_dashboard': [
                    'GET /api/orders/farmer/orders (see orders from users)',
                    'PATCH /api/orders/{id}/status (accept or deny)',
                    'DELETE /api/animals/{id}'
                ],
                'bonus_features': [
                    'Calculate total_amount of orders',
                    'Add farmer_notes',
                    'Handle M:N relationship between animals and orders'
                ]
            }
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
