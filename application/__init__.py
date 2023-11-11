from flask import Flask

# Create the flask app
app = Flask(__name__)

# Load configuration from config.cfg
app.config.from_pyfile('config.cfg')

# Run the file routes.py
from application import routes