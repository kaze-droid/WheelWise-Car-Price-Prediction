from flask import Flask
import gzip
import pickle
import pandas as pd

# Create the flask app
app = Flask(__name__)

# Load configuration from config.cfg
app.config.from_pyfile('config.cfg')

# # Feature Engineering
# def featureEngineering(X):
#     df = pd.DataFrame(X.reset_index(drop=True))
#     df['mileagePerYear'] = df['mileage']/(2021 - df['year'])
#     return df

# with gzip.open('application/static/joblib_Model.gz', 'rb') as f:
#     model = pickle.load(f)

# Run the file routes.py
from application import routes