from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Import all models
from .user_model import User
from .animal_model import Animal
from .order_model import Order, OrderItem

# Export all models for easy import
__all__ = ['db', 'User', 'Animal', 'Order', 'OrderItem']
