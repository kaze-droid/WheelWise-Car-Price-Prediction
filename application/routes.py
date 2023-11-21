from application import app
from flask import render_template
from application.forms import PredictionForm

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
