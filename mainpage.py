from flask import Flask, render_template, request, session
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from DB import DB, UsersModel, TasksModel, ScoresModel, ProgressModel

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
scores = ScoresModel(base)
scores.init_table()


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
            users_base.insert(form.username.data, form.password.data)
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


tasks_model = TasksModel(base)
tasks_model.init_table()
all_users = users_base.get_all()


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
        for i in [j[0] for j in all_users]:
            if request.form.get(str(i)):
                tasks_model.insert(title, sentence, choice, correct, i)
        return redirect("/index")
    return render_template('add_task.html', form=form, username=session['username'], users=all_users)


@app.route('/all_tasks/<int:id>', methods=['GET', 'POST'])
def all_tasks(id):
    if 'username' not in session:
        return redirect('/login')
    if id == 0:
        all = tasks_model.get_all(session['user_id'])
    else:
        all = tasks_model.get_all(id)
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
    correct_choices = [x[4].split('\n') for x in all]
    session['correct'] = correct_choices
    sc = scores.get_all()
    scores_id = [i[-1] for i in sc]
    scores1 = []
    for i in ides_tasks:
        if i in scores_id:
            n_correct = sc[scores_id.index(i)][-2]
            n_all = sc[scores_id.index(i)][-3]
        else:
            n_correct = 0
            n_all = len(session['contents'][ides_tasks.index(i)])
        scores1.append(str(n_correct) + '/' + str(n_all))
    session['scores'] = scores1
    return render_template('tasks.html', flag=True, n=n)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_tasks(id):
    if 'username' not in session:
        return redirect('/login')
    tasks_model.delete(id)
    scores.delete(id)
    progress.delete(id)
    return redirect('/all_tasks')


progress = ProgressModel(base)
progress.init_table()


@app.route('/task/<int:id>', methods=['GET', 'POST'])
def task(id):
    if 'username' not in session:
        return redirect('/login')
    k = 0
    l = len(session['contents'][id])
    length = list(range(l))
    answers = ''
    correctness = ''
    task_id = session['task_id'][id]
    c = []
    if request.method == 'POST':
        session['scores'] = []
        for i in length:
            ans = request.form[str(i)]
            if ans == session['correct'][id][i].strip():
                k += 1
                correctness += ' ' + 'true'
            else:
                correctness += ' ' + 'false'
            answers += " " + ans
        print([i[-1] for i in scores.get_all()])
        if task_id in [i[-1] for i in progress.get_all()]:
            progress.update(answers, correctness, task_id)
        else:
            progress.insert(answers, correctness, task_id)
        if task_id not in [i[-1] for i in scores.get_all()]:
            scores.insert(l, k, task_id)
        else:
            scores.update(session['task_id'][id], k)
        correct = progress.get_all(task_id)
        print(progress.get_all())
        print(scores.get_all())
        if correct:
            c = [i[-2].split() for i in correct][id]
        else:
            c = []
    return render_template('task.html', i=id, length=length, correct=c)


@app.route('/all_users')
def users():
    l = list(range(len(all_users)))
    return render_template('all_users.html', length=l, users=all_users)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
