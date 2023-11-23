from flask import Flask
import gzip
import pickle

# Create the flask app
app = Flask(__name__)

# Load configuration from config.cfg
app.config.from_pyfile('config.cfg')

# Load the model
with gzip.open('application/static/joblib_Model.gz', 'rb') as f:
    ai_model = pickle.load(f)

if __name__ == "__main__":
    # Run the app
    app.run(debug=True)

# Run the file routes.py
from application import routes