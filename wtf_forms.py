from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrateForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    repeatpassword = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Готово')


class AddTaskForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField('Текст задания')
    # picture = FileField()
    sentence = TextAreaField('Предложения', validators=[DataRequired()])
    choice = TextAreaField('Выбор ответа (разделите вырианты ответа знаком //.'
                           ' \n Варианты ответа для каждого предложения пишутся с новой строки.)')
    correct = TextAreaField('Правильный ответ')
    hints = TextAreaField('Подсказки')
    links = TextAreaField('Дополнительные файлы')
