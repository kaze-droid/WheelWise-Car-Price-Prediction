from flask_wtf import FlaskForm
from wtforms import RadioField, IntegerField, FloatField, IntegerRangeField, SelectField, SubmitField
from wtforms.validators import Length, InputRequired, ValidationError, NumberRange

class PredictionForm(FlaskForm):
    brands = [('audi','Audi'),('bmw','BMW'),('merc','Mercedes'), ('ford', 'Ford'), ('hyundi', 'Hyundi'), ('skoda', 'Skoda'), ('toyota', 'Toyota'), ('vauxhall', 'Vauxhall'), ('vw', 'VolksWagen')]

    brand = SelectField('Brand', choices=brands, validators=[InputRequired()])
    model = SelectField('Model', validate_choice=False, validators=[InputRequired()])

    # Highest: 2020
    regYear = IntegerField('Registration Year', validators=[InputRequired(), NumberRange(min=1970, max=2020, message='Year must be between 1970 and 2020')])

    gearbox = RadioField('Gearbox', choices=[('Manual', 'Manual'), ('Semi-Auto', 'Semi-Auto'), ('Automatic', 'Automatic')], validators=[InputRequired()])

    # Highest: 6.6
    engineSize = FloatField('Engine Size', validators=[InputRequired(), NumberRange(min=0, max=7.5, message='Engine Size must be between 0 and 7.5')])

    # Highest: 323_000
    mileage = IntegerField('Mileage', validators=[InputRequired(), NumberRange(min=0, max=500_000, message='Mileage must be between 0 and 500,000')])

    fuelType = RadioField('Fuel Type', choices=[('Petrol', 'Petrol'), ('Diesel', 'Diesel'), ('Hybrid', 'Hybrid'), ('Electric', 'Electric')], validators=[InputRequired()])

    # Highest: 580
    roadTax = FloatField('Road Tax', validators=[InputRequired(), NumberRange(min=0, max=750, message='Road Tax must be between 0 and 750')])

    # Highest: 470.8
    milesPerGallon = FloatField('Miles Per Gallon', validators=[InputRequired(), NumberRange(min=0, max=500, message='Miles Per Gallon must be between 0 and 500')])

    submit = SubmitField('Predict Price')



