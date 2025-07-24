from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('pending', 'confirmed', 'rejected', 'completed', name='order_status'), default='pending')
    total_amount = db.Column(db.Float, nullable=False)
    farmer_notes = db.Column(db.Text, nullable=True)  # Bonus feature
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert order to dictionary for JSON response"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.username if self.customer else None,
            'customer_email': self.customer.email if self.customer else None,
            'status': self.status,
            'total_amount': self.total_amount,
            'farmer_notes': self.farmer_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'items': [item.to_dict() for item in self.order_items],
            'items_count': len(self.order_items)
        }
    
    def to_summary_dict(self):
        """Lightweight version for listings"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.username if self.customer else None,
            'status': self.status,
            'total_amount': self.total_amount,
            'items_count': len(self.order_items),
            'created_at': self.created_at.isoformat()
        }
    
    def calculate_total_amount(self):
        """Calculate total amount from order items - Bonus feature"""
        total = sum(item.price * item.quantity for item in self.order_items)
        self.total_amount = total
        return total


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  # Price at time of order
    
    def to_dict(self):
        """Convert order item to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'animal_id': self.animal_id,
            'animal': self.animal.to_summary_dict() if self.animal else None,
            'quantity': self.quantity,
            'price': self.price,
            'subtotal': self.price * self.quantity
        }
