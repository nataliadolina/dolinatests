from flask import Flask, render_template, request, session
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from DB import DB, UsersModel, TasksModel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class LoginForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Enter')


base = DB()
users_base = UsersModel(base)
users_base.init_table()
print(users_base.get_all())


class RegistrateForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeatpassword = PasswordField('Repeat password', validators=[DataRequired()])
    submit = SubmitField('Done')


class AddTaskForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    sentence = TextAreaField('sentences', validators=[DataRequired()])
    choice = TextAreaField('answer choice', validators=[DataRequired()])
    correct = TextAreaField('answer choice', validators=[DataRequired()])
    submit = SubmitField('Add')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrateForm()
    if form.validate_on_submit():
        f1, f2 = form.username.data, form.password.data
        exists = users_base.exists(f1, f2)
        if exists[0]:
            form.username.data = ''
            return render_template('registration.html',
                                   text='User with such name already exists. Please change the login', form=form)
        elif f2 != form.repeatpassword.data:
            form.password.data = ''
            return render_template('registration.html',
                                   text='Passwords do not match. Please check your spelling and try again', form=form)
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
        return render_template('login.html', title='Authorization', text='invalid login or password', form=form)
    return render_template('login.html', title='Authorization', text='', form=form)


@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('tasks.html')


@app.route('/', methods=['GET', 'POST'])
@app.route('/homepage', methods=['GET', 'POST'])
def tasks():
    if 'username' in session:
        return render_template('tasks.html', flag=False)
    else:
        return redirect('/login')


users = [x[1] for x in users_base.get_all()]
ides = [x[0] for x in users_base.get_all()]
ides_names = {}
for i in range(len(users)):
    ides_names[ides[i]] = users[i]
ides_names = sorted(list(ides_names.items()), key=lambda x: x[1])
nm = TasksModel(base)
nm.init_table()


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if 'username' not in session:
        return redirect('/login')
    form = AddTaskForm()
    if form.validate_on_submit():
        title = form.title.data
        sentence = form.sentence.data
        choice = form.choice.data
        correct = form.correct.data
        for i in ides:
            if request.form.get(str(i)):
                print(request.form.get(str(i)))
                nm.insert(title, sentence, choice, correct, i)
                print(nm.get_all())
        return redirect("/index")
    return render_template('add_task.html', form=form, username=session['username'], users=ides_names)


print(nm.get_all())


@app.route('/all_tasks', methods=['GET', 'POST'])
def all_tasks():
    if 'username' not in session:
        return redirect('/login')
    all = nm.get_all(session['user_id'])
    titles = [x[1] for x in all]
    n = range(len(titles))
    ides_tasks = [x[0] for x in all]
    session['task_id'] = ides_tasks
    session['titles'] = titles
    contents = [i.split('\n') for i in [x[2] for x in all]]
    session['contents'] = contents
    choices = [i.split('\n') for i in [x[3] for x in all]]
    choices1 = []
    arr = []
    for i in choices:
        for j in i:
            arr.append(j.split())
        choices1.append(arr)
        arr = []
    session['choices'] = choices1
    correct_choices = [x[4] for x in all]
    session['correct'] = correct_choices
    print(session['titles'], session['contents'], session['choices'], session['correct'])
    return render_template('tasks.html', flag=True, n=n)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_tasks(id):
    if 'username' not in session:
        return redirect('/login')
    nm.delete(id)
    return redirect('/all_tasks')


@app.route('/task/<int:id>', methods=['GET', 'POST'])
def task(id):
    if 'username' not in session:
        return redirect('/login')
    length = list(range(len(session['contents'][id])))
    print(length)
    return render_template('task.html', i=id, length=length)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
