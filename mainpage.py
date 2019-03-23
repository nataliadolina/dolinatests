import json

from flask import Flask, render_template, request, session
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from DB import DB, UsersModel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class LoginForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Enter')


base = DB()
users_base = UsersModel(base)


class RegistrateForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeatpassword = PasswordField('Repeat password', validators=[DataRequired()])
    submit = SubmitField('Done')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrateForm()
    if form.validate_on_submit():
        f1, f2 = form.username.data, form.password.data
        exists = users_base.exists(f1, f2)
        if exists[0]:
            form.username.data, form.password.data = '', ''
            return render_template('registration.html',
                                   text='пользователь с таким же именем уже существует. Смените логин', form=form)
        else:
            session['username'] = form.username.data
            nm = UsersModel(base)
            nm.insert(form.username.data, form.password.data)
            session['user_id'] = users_base.exists(form.username.data, form.password.data)[1]
            return redirect('/index')
    return render_template('registration.html', text='', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        exists = users_base.exists(request.form['username'], request.form['password'])
        if exists[0]:
            session['username'] = request.form['username']
            session['user_id'] = exists[1]
            return redirect('/index')
        return redirect('/failure')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('tasks.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
