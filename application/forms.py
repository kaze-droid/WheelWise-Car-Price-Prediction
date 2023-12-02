from flask_wtf import FlaskForm
from wtforms import RadioField, IntegerField, FloatField, SelectField, BooleanField, SubmitField
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import Length, InputRequired, ValidationError, NumberRange, EqualTo
from application.models import User

# Prediction Form
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

# User Registration form
class UserRegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=20)], render_kw={'placeholder': 'JohnDoe'})
    email = EmailField('Email', validators=[InputRequired()], render_kw={'placeholder': 'johndoe@gmail.com'})
    password = PasswordField('Password', validators=[InputRequired(), EqualTo('confirmPassword', message='Passwords must match'), Length(min=12, max=80)], render_kw={'placeholder': '********'})
    confirmPassword = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match')], render_kw={'placeholder': '********'})
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        # Make sure username does not contain spaces
        if ' ' in username.data:
            raise ValidationError('Username cannot contain spaces!')
        # Make sure no special characters in username
        elif not username.data.isalnum():
            raise ValidationError('Username can only contain letters and numbers!')

    def validate_email(self, email):
        # Check if email already exists
        existing_email = User.query.filter_by(email=email.data).first()

        if existing_email:
            raise ValidationError('Email already exists!')
    
# User Login form
class UserLoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired()], render_kw={'placeholder': 'JohnDoe@gmail.com'})
    remember = BooleanField('Remember Me?', default=False)
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

# User Change username
class UserChangeUsernameForm(FlaskForm):
    username = StringField('New Username', validators=[InputRequired(), Length(min=2, max=20)], render_kw={'placeholder': 'JohnDoe'})
    submit = SubmitField('Change Username')

    def validate_username(self, username):
        # Make sure username does not contain spaces
        if ' ' in username.data:
            raise ValidationError('Username cannot contain spaces!')
        # Make sure no special characters in username
        elif not username.data.isalnum():
            raise ValidationError('Username can only contain letters and numbers!')
        
# User Change password
class UserChangePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired(), EqualTo('confirmPassword', message='Passwords must match'), Length(min=12, max=80)], render_kw={'placeholder': '********'})
    confirmPassword = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match')], render_kw={'placeholder': '********'})
    submit = SubmitField('Change Password')

# User Delete account
class UserDeleteForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=20)], render_kw={'placeholder': 'JohnDoe'})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=12, max=80)], render_kw={'placeholder': '********'})
    delete = SubmitField('Delete Account')
    