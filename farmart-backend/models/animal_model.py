from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Animal(db.Model):
    __tablename__ = 'animals'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # sheep, cow, pig, chicken, etc.
    breed = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)  # in months
    weight = db.Column(db.Float, nullable=False)  # in kg
    price = db.Column(db.Float, nullable=False)
    min_price = db.Column(db.Float, nullable=True)  # For filtering
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    farmer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='animal', lazy=True)
    
    def to_dict(self):
        """Convert animal to dictionary for JSON response"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'breed': self.breed,
            'age': self.age,
            'weight': self.weight,
            'price': self.price,
            'min_price': self.min_price,
            'description': self.description,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'farmer_id': self.farmer_id,
            'farmer_name': self.farmer.username if self.farmer else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def to_summary_dict(self):
        """Lightweight version for listings"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'breed': self.breed,
            'price': self.price,
            'is_available': self.is_available,
            'farmer_id': self.farmer_id
        }
