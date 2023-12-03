from application import app, ai_model, db, bcrypt, login_manager
from application.models import PredEntry, User
from datetime import datetime, timezone, timedelta
from flask import render_template, request, flash, redirect, send_file, json, jsonify
from application.forms import (
    PredictionForm,
    UserRegisterForm,
    UserLoginForm,
    UserChangeUsernameForm,
    UserChangePasswordForm,
    UserDeleteForm,
)
from flask_login import login_user, current_user, logout_user, login_required
import pandas as pd
import json
import os


# Since SGT is 8 hours ahead compared to UTC
SGT = timezone(timedelta(hours=8))

login_manager.init_app(app)
# Redirect to login page if user is not logged in
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))



@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html", index=True, title="Home")


@app.route("/about")
def about():
    return render_template("about.html", about=True, title="About")


@app.route("/predict", methods=["GET", "POST"])
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

    if request.method == "POST":
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

            # Get prediction using internal API
            data = {
                "brand": brand,
                "model": model,
                "year": year,
                "transmission": gearbox,
                "mileage": mileage,
                "fuelType": fuelType,
                "tax": tax,
                "mpg": mpg,
                "engineSize": engineSize,
            }

            response, status_code = predictAPI(data)

            if status_code != 200:
                flash("Error cannot proceed", "error")
                return redirect("/predict")
            
            prediction = response.json["prediction"]


            # Post the prediction to the database using internal API
            data = {
                "brand": brand,
                "model": model,
                "year": year,
                "transmission": gearbox,
                "mileage": mileage,
                "fuelType": fuelType,
                "tax": tax,
                "mpg": mpg,
                "engineSize": engineSize,
                "prediction": prediction,
                "user_id": current_user.id,
            }

            response2, status_code2 = predictAdd(data)
            if status_code == 200:
                # Show the prediction result
                flash(f"Your car is worth £{prediction:,.2f}.", "success")

            else:
                flash("Error cannot proceed", "error")
                return redirect("/predict")

        else:
            flash("Error cannot proceed", "error")

    return render_template(
        "predict.html",
        predict=True,
        form=form,
        title="Prediction",
        contentTitle="WheelWise Car Prediction",
    )


@app.route("/history")
@login_required
def history():
    # Get all the entries for the user using internal API
    response, status_code = getPredEntries(current_user.id)
    entries = response.json

    return render_template(
        "history.html",
        history=True,
        title="History",
        contentTitle="WheelWise Prediction History",
        entries=entries,
    )

# Used for removing entries
@app.route("/remove", methods=["POST"])
def remove():
    # Get the id from the form
    req = request.form
    id = req.get("id")
    # Delete the entry
    removePredEntry(id)
    # Redirect to history page
    return redirect("/history")


# Used for exporting history
@app.route("/export", methods=["POST"])
def export():
    # Get the file name
    file_name = exportPredEntries(current_user.id)

    # Return the csv file
    return send_file(file_name, mimetype="text/csv", as_attachment=True)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = UserRegisterForm()

    if request.method == "POST":
        if form.validate_on_submit():
            # Get the form data
            username = form.username.data
            email = form.email.data
            password = form.password.data
            
            # Add user using internal API
            data = {
                "username": username,
                "email": email,
                "password": password,
            }

            result = userAdd(data)

            if result.status_code == 200:
                flash("Account created successfully!", "success")
                return redirect("/login")
            else:
                flash(f"Error creating new user!", "error")

        else:
            flash(f"Error creating new user!", "error")
    return render_template(
        "register.html",
        register=True,
        form=form,
        title="Sign Up",
        contentTitle="WheelWise Registration",
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    form = UserLoginForm()

    if request.method == "POST":
        if form.validate_on_submit():
            # Get the form data
            email = form.email.data
            password = form.password.data
            remember = form.remember.data

            # Get the user using internal API
            data = {
                "email": email,
                "password": password,
                "remember": remember,
            }

            response, err_code = getUser(data)

            if err_code == 200:
                # Redirect to home page
                return redirect("/profile")
            else:
                flash(response.json["error"], "error")
                redirect("/login")
                
        else:
            flash("Error logging in!", "error")
    return render_template(
        "login.html",
        login=True,
        form=form,
        title="Login",
        contentTitle="WheelWise Login",
    )


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logoutUser()
    return redirect("/")


@app.route("/profile")
@login_required
def profile():
    usernameForm = UserChangeUsernameForm()
    passwordForm = UserChangePasswordForm()
    deleteForm = UserDeleteForm()
    return render_template(
        "profile.html",
        title="Profile",
        contentTitle="Profile Page",
        usernameForm=usernameForm,
        passwordForm=passwordForm,
        deleteForm=deleteForm,
    )

# Used for changing username
@app.route("/changeUsername", methods=["POST"])
def changeUsername():
    form = UserChangeUsernameForm()
    if form.validate_on_submit():
        # Get the form data
        new_username = form.username.data

        data = {
            "username": new_username,
        }
        response, status_code = changeUsernameAPI(data)
        if status_code == 200:
            flash("Username changed successfully!", "success")
        else:
            flash("Error changing username!", "error")
    else:
        flash("Username must not contain special characters!", "error")
    
    # Redirect to profile page
    return redirect("/profile")

# Used for changing password
@app.route("/changePassword", methods=["POST"])
def changePassword():
    form = UserChangePasswordForm()
    if form.validate_on_submit():
        # Get the form data
        new_password = form.password.data

        data = {
            "password": new_password,
        }

        response, status_code = changePasswordAPI(data)
        if status_code == 200:
            flash("Password changed successfully!", "success")
        else:
            flash("Error changing password!", "error")
    else:
        flash("Passwords do not match!", "error")
    
    # Redirect to profile page
    return redirect("/profile")

# Used for deleting account
@app.route("/deleteAccount", methods=["POST"])
def deleteAccount():
    form = UserDeleteForm()
    if form.validate_on_submit():
        # Get the form data
        username = form.username.data
        password = form.password.data

        data = {
            "username": username,
            "password": password,
        }

        response = deleteAccountAPI(data)
        if response.status_code == 200:
            flash("Account deleted successfully!", "success")
        else:
            flash("Error deleting account!", "error")
    else:
        flash("Error deleting account!", "error")
    
    # Redirect to 
    return redirect("/login")


@app.errorhandler(404)
def page_not_found(e):
    # 'e' is the exception object, which can be used to get the error description
    return (
        render_template(
            "404.html", title="Page Not Found", contentTitle="Page Not Found"
        ),
        404,
    )

# API Routes
# Used for getting the models for a brand
@app.route("/api/models/<brand>", methods=["GET"])
def getModels(brand):
    df = pd.read_csv("application/static/car_models.csv")
    if brand not in df["brand"].values:
        return "Model Not Found!", 404
    # Filter
    df = df[df["brand"] == brand]
    # Sort
    df = df.sort_values(by=["model"]).reset_index(drop=True)
    # Convert to list json
    return df["model"].to_json(orient="index"), 200

# Used for predicting the price of a car
@app.route("/api/predict", methods=["GET"])
def predictAPI(data=None):
    if data is None:
        # Read the json data
        data = request.get_json()

    # Create the input dataframe
    input_df = pd.DataFrame(
        data=[
            [
                data["brand"],
                data["model"],
                data["year"],
                data["transmission"],
                data["mileage"],
                data["fuelType"],
                data["tax"],
                data["mpg"],
                data["engineSize"],
            ]
        ],
        columns=[
            "brand",
            "model",
            "year",
            "transmission",
            "mileage",
            "fuelType",
            "tax",
            "mpg",
            "engineSize",
        ],
    )

    # Feature Engineering
    input_df = featureEngineering(input_df)

    # Get the prediction
    prediction = ai_model.predict(input_df)[0]

    # Return the prediction
    return jsonify({"prediction": prediction}), 200

# Used for adding a prediction to the database
@app.route("/api/predEntry/add", methods=["POST"])
def predictAdd(data=None):
    if data is None:
        # Read the json data
        data = request.get_json()

    # Create the new entry
    new_entry = PredEntry(
        brand=data["brand"],
        model=data["model"],
        year=data["year"],
        transmission=data["transmission"],
        mileage=data["mileage"],
        fuelType=data["fuelType"],
        tax=data["tax"],
        mpg=data["mpg"],
        engineSize=data["engineSize"],
        prediction=data["prediction"],
        prediction_date= datetime.now(SGT),
        user_id=data["user_id"],
    )

    # Add the entry
    result =  add_entry(new_entry)

    if result is None:
        return jsonify({'error': 'Failed to add entry'}),  500
    else:
        # return the result of the db action
        return jsonify({'id': result}), 200

# Used for getting all the predictions for a user
@app.route("/api/predEntry/<user_id>", methods=["GET"])
def getPredEntries(user_id):
    # Get all the entries for the user
    entries = get_entries(PredEntry, whereClause=PredEntry.user_id == user_id)

    if entries is None:
        return jsonify({'error': 'Failed to get entries'}),  500

    # Convert result to json
    entries = [
        {
            "id": entry.id,
            "brand": entry.brand,
            "model": entry.model,
            "year": entry.year,
            "transmission": entry.transmission,
            "engineSize": entry.engineSize,
            "fuelType": entry.fuelType,
            "mileage": entry.mileage,
            "tax": entry.tax,
            "mpg": entry.mpg,
            "prediction": entry.prediction,
            "prediction_date": entry.prediction_date.strftime("%d %b %Y %H:%M"),
        }
        for entry in entries
    ]

    # Return the json
    return jsonify(entries), 200

# Used for removing entries
@app.route("/api/predEntry/remove/<id>", methods=["GET"])
def removePredEntry(id=None):
    # Delete the entry
    entry = delete_entry(PredEntry, id)

    if entry is None:
        return jsonify({'error': 'Failed to delete entry'}),  500
    else:
        return jsonify({'id': id}), 200

# Used for exporting history
@app.route("/api/predEntry/export/<user_id>", methods=["GET"])
def exportPredEntries(user_id):
    dir_name = os.path.join(os.getcwd(), "outputs")

    # Create the outputs folder if it does not exist
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # Clear the outputs folder
    for file in os.listdir(dir_name):
        os.remove(os.path.join(dir_name, file))

    # Get all the entries for the user
    response, status_code = getPredEntries(user_id)
    entries = response.json

    # Create the dataframe
    df = pd.DataFrame(
        data=[
            [
                entry['brand'],
                entry['model'],
                entry['year'],
                entry['transmission'],
                entry['engineSize'],
                entry['fuelType'],
                entry['mileage'],
                entry['tax'],
                entry['mpg'],
                entry['prediction'],
                entry['prediction_date'],
            ]
            for entry in entries
        ],
        columns=[
            "Brand",
            "Model",
            "Year",
            "Transmission",
            "Engine Size",
            "Fuel Type",
            "Mileage",
            "Road Tax",
            "Miles Per Gallon",
            "Prediction",
            "Prediction Date",
        ],
    )

    file_name = os.path.join(dir_name, f"history{user_id}.csv")

    # Export to csv
    df.to_csv(file_name, index=False)

    return file_name

@app.route("/api/user/add", methods=["POST"])
def userAdd(data=None):
    if data is None:
        # Read the json data
        data = request.get_json()

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(data["password"])

    # Create the new user
    new_user = User(
        username=data["username"],
        email=data["email"],
        password=hashed_password,
        creation_date=datetime.now(SGT),
    )

    # Add the user
    result = add_entry(new_user)

    if result is None:
        return jsonify({'error': 'Email already exists'}),  401
    else:
        # Return the result of the db action
        return jsonify({'id': result}), 200

@app.route("/api/user", methods=["POST"])
def getUser(data=None):
    if data is None:
        # Read the json data
        data = request.get_json()

    # Get the user
    user = get_user(data["email"])

    # Check if user exists
    if user is None:
        # Return an error
        return jsonify({'error': 'Email does not exist'}),  404

    # Check if password is correct (hash from db matches form password)
    elif bcrypt.check_password_hash(user.password, data["password"]):
        login_user(user, remember=data["remember"])
        # Return the json
        return jsonify({"id": user.id}), 200

    else:
        # Return an error
        return jsonify({'error': 'Invalid Credentials'}),  401
    
# Used for logging out
@app.route("/api/user/logout", methods=["POST"])
def logoutUser():
    logout_user()
    return jsonify({"result": "ok"}), 200
    
# Used for changing username
@app.route("/api/user/changeUsername", methods=["POST"])
def changeUsernameAPI(data=None):
    if data is None:
        # Read the json data
        data = request.get_json()

    # Get the user (previously validated in login)
    user = get_user(current_user.email)

    # Update the username
    user = update_user(user, username=data["username"])

    if user is None:
        # Return an error
        return jsonify({'error': 'Failed to update username'}),  500
    else:
        # Return the result of the db action
        return jsonify({'id': user.id}), 200

# Used for changing password
@app.route("/api/user/changePassword", methods=["POST"])
def changePasswordAPI(data=None):
    if data is None:
        # Read the json data
        data = request.get_json()

    # Get the user (previously validated in login)
    user = get_user(current_user.email)

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(data["password"])

    # Update the password
    user = update_user(user, password=hashed_password)
    
    if user is None:
        # Return an error
        return jsonify({'error': 'Failed to update password'}),  500
    else:
        # Return the result of the db action
        return jsonify({'id': user.id}), 200

# Used for deleting account
@app.route("/api/user/deleteAccount", methods=["POST"])
def deleteAccountAPI(data=None):
    if data is None:
        # Read the json data
        data = request.get_json()

    # Get the user (previously validated in login)
    user = get_user(current_user.email)

    if user.username == data["username"] and bcrypt.check_password_hash(user.password, data["password"]):
        # Delete the user
        result = delete_entry(User, user.id)

        if result is None:
            # Return an error
            return jsonify({'error': 'Failed to delete account'}),  500
        else:
            # Return the result of the db action
            return jsonify({'id': user.id}), 200
    else:
        # Return an error
        return jsonify({'error': 'Invalid Credentials'}),  401

# Utility Functions
def featureEngineering(X):
    df = pd.DataFrame(X.reset_index(drop=True))
    df["mileagePerYear"] = df["mileage"] / (2021 - df["year"])
    return df

def add_entry(new_entry):
    try:
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id
    except Exception as e:
        db.session.rollback()
        return None


def get_entries(model, whereClause=True):
    try:
        entries = (
            db.session.execute(db.select(model).where(whereClause).order_by(model.id))
            .scalars()
            .all()
        )
        return entries
    except Exception as e:
        db.session.rollback()
        return None


def delete_entry(model, id):
    try:
        entry = db.get_or_404(model, id)
        db.session.delete(entry)
        db.session.commit()
        return entry.id
    except Exception as e:
        db.session.rollback()
        return None


def get_user(email):
    try:
        user = db.session.query(User).filter_by(email=email).first_or_404()
        return user
    except Exception as e:
        return None


def update_user(user, username=None, password=None):
    try:
        if username:
            user.username = username
        if password:
            user.password = password
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        return None
