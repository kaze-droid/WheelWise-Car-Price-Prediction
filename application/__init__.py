from flask import Flask
import gzip
import pickle
from flask_sqlalchemy import SQLAlchemy
import os

# Instantiate SQLAlchemy to handle db process
db = SQLAlchemy()

# Create the flask app
app = Flask(__name__)

# Load configuration from config.cfg
app.config.from_pyfile('config.cfg')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with app.app_context():
    db.init_app(app)
    from .models import PredEntry
    db.create_all()
    db.session.commit()
    print("Database created")

# Load the model
with gzip.open('application/static/joblib_Model.gz', 'rb') as f:
    ai_model = pickle.load(f)

if __name__ == "__main__":
    # Run the app
    app.run(debug=True)

# Run the file routes.py
from application import routes