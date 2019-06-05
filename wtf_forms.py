from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Enter')


class RegistrateForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeatpassword = PasswordField('Repeat password', validators=[DataRequired()])
    submit = SubmitField('Done')


class AddTaskForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    sentence = TextAreaField('sentences', validators=[DataRequired()])
    choice = TextAreaField('answer choice', validators=[DataRequired()])
    correct = TextAreaField('correct answer', validators=[DataRequired()])
    submit = SubmitField('Add')
