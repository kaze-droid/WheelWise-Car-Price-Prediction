from application import db

class PredEntry(db.Model):
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

