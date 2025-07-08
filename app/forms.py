# app/forms.py


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from .models import User

class RegistrationForm(FlaskForm):
    username = StringField('Nom d’utilisateur',
        validators=[DataRequired(), Length(3,50)])
    email = StringField('Email',
        validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Mot de passe',
        validators=[DataRequired(), Length(6,128)])
    password2 = PasswordField('Confirmer le mot de passe',
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('S’inscrire')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Ce nom d’utilisateur est déjà pris.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Cet email est déjà utilisé.')

class LoginForm(FlaskForm):
    username = StringField('Nom d’utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    submit = SubmitField('Se connecter')