from application import app, ai_model, db, bcrypt, login_manager
from application.models import PredEntry, User
from datetime import datetime, timezone, timedelta
from flask import render_template, request, flash, redirect
from application.forms import PredictionForm, UserRegisterForm, UserLoginForm
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd
import json

login_manager.init_app(app)
# Redirect to login page if user is not logged in
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html", index=True)

@app.route('/about')
def about():
    return render_template("about.html", about=True)

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    form = PredictionForm()
    # Get the brand option
    brand = form.brand.data
    # Get the model option
    modelsJSON, errCode = getModels(brand)

    if errCode == 200:
        # Get all the keys out of json
        models = list(json.loads(modelsJSON).values())
        form.model.choices = [(m, m.capitalize()) for m in models]
    
    # If model option does not exist for brand
    else:
        # Set choice to empty so it will raise error
        form.model.choices = []

    if request.method == 'POST':
        if form.validate_on_submit():
            # Get the form data
            brand = form.brand.data
            model = form.model.data
            year = form.regYear.data
            gearbox = form.gearbox.data
            mileage = form.mileage.data
            fuelType = form.fuelType.data
            tax = form.roadTax.data
            mpg = form.milesPerGallon.data
            engineSize = form.engineSize.data

            # Create the input dataframe
            input_df = pd.DataFrame(data=[[brand, model, year, gearbox, mileage, fuelType, tax, mpg, engineSize]],
                                    columns=['brand', 'model', 'year', 'transmission', 'mileage',  'fuelType', 'tax', 'mpg', 'engineSize'])

            # Feature Engineering
            input_df = featureEngineering(input_df)

            # Get the prediction
            prediction = ai_model.predict(input_df)[0]

            # Since SGT is 8 hours ahead compared to UTC
            SGT = timezone(timedelta(hours=8))

            # Get the user id
            user_id = current_user.id

            # Create the new entry
            new_entry = PredEntry(brand=brand, 
                                  model=model, 
                                  year=year, 
                                  transmission=gearbox, 
                                  mileage=mileage, 
                                  fuelType=fuelType, 
                                  tax=tax, 
                                  mpg=mpg, 
                                  engineSize=engineSize, 
                                  prediction= round(prediction, 2), 
                                  prediction_date=datetime.now(SGT),
                                  user_id=user_id)
            add_entry(new_entry)

            # Show the prediction result
            flash(f"Your car is worth £{prediction:,.2f}.", "success")

        else:
            flash("Error cannot proceed", "error")



    return render_template("predict.html", predict=True, form=form, title="WheelWise Car Prediction")

@app.route('/history')
@login_required
def history():
    user_id = current_user.id
    return render_template("history.html", history=True, title="WheelWise Prediction History", entries=get_entries(PredEntry, whereClause=PredEntry.user_id==user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserRegisterForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            # Get the form data
            username = form.username.data
            email = form.email.data
            password = form.password.data
            # Hash the password
            hashed_password = bcrypt.generate_password_hash(password)

            # Since SGT is 8 hours ahead compared to UTC
            SGT = timezone(timedelta(hours=8))

            # Create the new user
            new_user = User(username=username, email=email, password=hashed_password, creation_date=datetime.now(SGT))
            add_entry(new_user)

            flash("Account created successfully!", "success")
        else:
            flash(f"Error creating new user!", "error")
    return render_template("register.html", register=True, form=form, title="WheelWise Register")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            # Get the form data
            email = form.email.data
            password = form.password.data

            # Get the user
            user = get_user(email)

            # Check if user exists and password is correct (hash from db matches form password)
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect('/')
            else:
                flash("Login unsuccessful!", "error")
        else:
            flash("Error logging in!", "error")
    return render_template("login.html", login=True, form=form, title="WheelWise Login")

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')

# Used for removing entries
@app.route('/remove', methods=['POST'])
def remove():
    # Get the id from the form
    req = request.form
    id = req.get('id')
    # Delete the entry
    delete_entry(PredEntry, id)
    # Redirect to history page
    return redirect('/history')


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

# Utility Functions
def featureEngineering(X):
    df = pd.DataFrame(X.reset_index(drop=True))
    df['mileagePerYear'] = df['mileage']/(2021 - df['year'])
    return df

# Prediction Entries
def add_entry(new_entry):
    try:
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id
    except Exception as e:
        db.session.rollback()
        flash(e, "error")

def get_entries(model, whereClause=True):
    try:
        entries = db.session.execute(db.select(model).where(whereClause).order_by(model.id)).scalars().all()
        return entries
    except Exception as e:
        db.session.rollback()
        flash(e, "error")
        return 0

def delete_entry(model, id):
    try:
        entry = db.get_or_404(model, id)
        db.session.delete(entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(e, "error")
        return 0
    
def get_user(email):
    try:
        user = User.query.filter_by(email=email).first()
        return user
    except Exception as e:
        flash(e, "error")
        return 0
    