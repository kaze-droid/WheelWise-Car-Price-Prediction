from flask_wtf import FlaskForm
from wtforms import RadioField, IntegerField, FloatField, IntegerRangeField, SelectField, SubmitField
from wtforms.validators import Length, InputRequired, ValidationError, NumberRange

class PredictionForm(FlaskForm):
    brands = [('1','1'),('2','2'),('3','3')]
    # Get models from database
    models = [('4','4'),('5','5'),('6','6')]
    brand = SelectField('Brand', choices=brands, validators=[InputRequired()])
    model = SelectField('Model', choices=models, validators=[InputRequired()])

    # Highest: 2020
    regYear = IntegerField('Registration Year', validators=[InputRequired(), NumberRange(min=1970, max=2020)])

    gearbox = RadioField('Gearbox', choices=[('manual', 'Manual'), ('semiauto', 'Semi-Auto'), ('automatic', 'Automatic')], validators=[InputRequired()])

    # Highest: 6.6
    engineSize = FloatField('Engine Size', validators=[InputRequired(), NumberRange(min=0, max=7.5)])

    # Highest: 323_000
    mileage = IntegerRangeField('Mileage', validators=[InputRequired(), NumberRange(min=0, max=500_000)])

    fuelType = RadioField('Fuel Type', choices=[('petrol', 'Petrol'), ('diesel', 'Diesel'), ('hybrid', 'Hybrid'), ('electric', 'Electric')], validators=[InputRequired()])

    # Highest: 580
    roadTax = FloatField('Road Tax', validators=[InputRequired(), NumberRange(min=0, max=750)])

    # Highest: 470.8
    milesPerGallon = FloatField('Miles Per Gallon', validators=[InputRequired(), NumberRange(min=0, max=500)])

    submit = SubmitField('Predict Price')


