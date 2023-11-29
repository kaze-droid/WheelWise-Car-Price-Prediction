from application import db
from flask_login import UserMixin

# One to many relationship between User and PredEntry
class PredEntry(db.Model):
    __tablename__ = 'predictions'
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    transmission = db.Column(db.String(10), nullable=False)
    engineSize = db.Column(db.Float, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)
    fuelType = db.Column(db.String(10), nullable=False)
    tax = db.Column(db.Float, nullable=False)
    mpg = db.Column(db.Float, nullable=False)
    prediction = db.Column(db.Float, nullable=False)
    prediction_date = db.Column(db.DateTime, nullable=False)
    # Add foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    # Add relationship to PredEntry
    entries = db.relationship('PredEntry', backref='user', lazy=True)

