from application import app
from flask import render_template

@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    return render_template("index.html")