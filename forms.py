from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Regexp

class UserLoginForm(FlaskForm):
    first = StringField("First Name", validators = [DataRequired()])
    last = StringField("Last Name", validators = [DataRequired()])
    username = StringField("Username", validators = [DataRequired(), Regexp(r'^\w+$')])
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    submit_button = SubmitField()

class UserSignInForm(FlaskForm):
    username = StringField("Username", validators = [DataRequired()])
    password = PasswordField("Password", validators = [DataRequired()])
    submit_button = SubmitField()