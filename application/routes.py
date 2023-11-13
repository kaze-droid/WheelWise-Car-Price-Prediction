from application import app
from flask import render_template

@app.route('/')
def home():
    return render_template("index.html", index=True)

@app.route('/about')
def about():
    return render_template("about.html", about=True)

@app.route('/predict')
def predict():
    return render_template("predict.html", predict=True)

@app.route('/history')
def history():
    return render_template("history.html", history=True)
