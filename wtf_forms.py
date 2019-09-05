from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
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
    text = TextAreaField('Text of the task')
    picture = FileField('Download an image')
    sentence = TextAreaField('sentences', validators=[DataRequired()])
    choice = TextAreaField('answer choice')
    correct = TextAreaField('correct answer', validators=[DataRequired()])
    hints = TextAreaField('hints')
    links = TextAreaField('Extra files')
