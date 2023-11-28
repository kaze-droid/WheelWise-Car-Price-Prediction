from application import app, ai_model, db
from application.models import PredEntry
from datetime import datetime, timezone, timedelta
from flask import render_template, request, flash
from application.forms import PredictionForm
import pandas as pd
import json

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

            # # Round the prediction to 2 decimal places
            # prediction = round(prediction, 2)

            # Since SGT is 8 hours ahead compared to UTC
            SGT = timezone(timedelta(hours=8))

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
                                  prediction_date=datetime.now(SGT))
            add_entry(new_entry)

            # Show the prediction result
            flash(f"Your car is worth £{prediction:,.2f}.", "success")

        else:
            flash("Error cannot proceed", "error")



    return render_template("predict.html", predict=True, form=form, title="WheelWise Car Prediction")

@app.route('/history')
def history():
    return render_template("history.html", history=True, title="WheelWise Prediction History", entries=get_entries())

# Used for removing entries
@app.route('/remove', methods=['POST'])
def remove():
    # Get the id from the form
    req = request.form
    id = req.get('id')
    # Delete the entry
    delete_entry(id)
    # Redirect to history page
    return render_template("history.html", history=True, title="WheelWise Prediction History", entries=get_entries())


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

def get_entries():
    try:
        entries = db.session.execute(db.select(PredEntry).order_by(PredEntry.id)).scalars().all()
        return entries
    except Exception as e:
        db.session.rollback()
        flash(e, "error")
        return 0

def delete_entry(id):
    try:
        entry = db.get_or_404(PredEntry, id)
        db.session.delete(entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(e, "error")
        return 0