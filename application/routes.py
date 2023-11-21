from application import app
from flask import render_template
from application.forms import PredictionForm
import pandas as pd

# userData = {
#     "loggedIn": True,
#     "user": {"username": "TestData"}
# }

@app.route('/')
def home():
    # return render_template("index.html", index=True, **userData)
    return render_template("index.html", index=True)

@app.route('/about')
def about():
    return render_template("about.html", about=True)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    form = PredictionForm()
    return render_template("predict.html", predict=True, form=form, title="WheelWise Car Prediction")

@app.route('/history')
def history():
    return render_template("history.html", history=True)


# API Routes
@app.route('/api/models/<brand>', methods=['GET'])
def getModels(brand):
    df = pd.read_csv('application/static/car_models.csv')
    if brand not in df['brand'].values:
        return 'Model Not Found!', 404
    # Filter
    df = df[df['brand'] == brand]
    # Sort
    df =  df.sort_values(by=['model']).reset_index(drop=True)
    # Convert to list json
    return df['model'].to_json(orient='index'), 200
