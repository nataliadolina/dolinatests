import json

from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    with open("json/logins_passwords", "rt", encoding="utf8") as f:
        f = json.loads(f.read())
    if form.validate_on_submit():
        for i in range(len(f)):
            if request.form['username'] in f[i]['login'] and request.form['password'] in f[i]['password']:
                return redirect('/index')
        return redirect('/failure')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('base.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
