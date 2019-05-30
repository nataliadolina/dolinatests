import sqlite3

from flask import Flask, render_template, request, session
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from DB import DB, UsersModel, TasksModel, ScoresModel, ProgressModel, Files

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class LoginForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Enter')


base = DB()
users_base = UsersModel(base)
users_base.init_table()
scores = ScoresModel(base)
scores.init_table()
files_base = Files(base)
files_base.init_table()


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
            return redirect('/homepage')
    return render_template('registration.html', text='', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        exists = users_base.exists(request.form['username'], request.form['password'])
        if exists[0]:
            session['username'] = request.form['username']
            session['user_id'] = exists[1]
            return redirect('/homepage')
        return render_template('login.html', title='Authorization', text='invalid login or password', form=form)
    return render_template('login.html', title='Authorization', text='', form=form)


@app.route('/', methods=['GET', 'POST'])
@app.route('/homepage', methods=['GET', 'POST'])
def tasks():
    if 'username' in session:
        return redirect('/all_tasks/0')
    else:
        return redirect('/login')


tasks_model = TasksModel(base)
tasks_model.init_table()
all_users = users_base.get_all()


@app.route('/add_task/<string:title>', methods=['GET', 'POST'])
def add_task(title):
    if 'username' not in session:
        return redirect('/login')
    form = AddTaskForm()
    title2 = True
    if not title.isalpha():
        title2 = False
    if title2:
        title1, content, choices, correct_choice = tasks_model.get(title)[1:-1]
        id = tasks_model.get(title)[0]
        form.title.data = title1
        form.sentence.data = content
        form.choice.data = choices
        form.correct.data = correct_choice
    if request.method == 'POST':
        title1 = form.title.data
        sentence = form.sentence.data
        choice = form.choice.data
        correct = form.correct.data
        if len(sentence.split('\n')) != len(choice.split('\n')) or len(correct.split('\n')) != len(choice.split('\n')):
            return render_template('add_task.html', form=form, username=session['username'], users=all_users,
                                   text='invalid task. Number of strings in labels "sentences",'
                                        ' "answer choice", "correct answer" must be the same')
        if not title2 and title1 in [i[1] for i in tasks_model.get_all()]:
            return render_template('add_task.html', form=form, username=session['username'], users=all_users,
                                   text='task with such title already exists')
        else:
            print(request.form)
            for i in [j[0] for j in all_users]:
                if request.form.get(str(i)):
                    '''
                    if request.form.get('file'):
                        file_input = open(request['file'], "rb")
                        file = file_input.read()
                        file_input.close()
                        binary = sqlite3.Binary(file)
                        files_base.insert(binary, ind)
                        '''
                    if not title2:
                        tasks_model.insert(title1, sentence, choice, correct, i)
                        ind = tasks_model.index()
                    else:
                        tasks_model.update(title1, sentence, choice, correct, id)
            return redirect("/homepage")
    return render_template('add_task.html', form=form, username=session['username'], users=all_users)


@app.route('/all_tasks/<int:id>', methods=['GET', 'POST'])
def all_tasks(id):
    all, username = '', ''
    if 'username' not in session:
        return redirect('/login')
    if id != 0 and session['user_id'] in [1, 2]:
        all = tasks_model.get_all(id)
        username = users_base.get(id)[1]
    else:
        id = 0
    if id == 0:
        all = tasks_model.get_all(session['user_id'])
        username = ''
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
    return render_template('tasks.html', flag=True, n=n, name=username)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_tasks(id):
    if 'username' not in session:
        return redirect('/login')
    tasks_model.delete(id)
    scores.delete(id)
    progress.delete(id)
    return redirect('/all_tasks/{}'.format(session['user_id']))


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
    correct = progress.get_all(task_id)
    if correct:
        c = correct[0][-2].split()
        answer = correct[0][1].split()
    else:
        c = []
        answer = []
    if request.method == 'POST':
        session['scores'] = []
        ans1 = ''
        for i in length:
            ans = request.form[str(i)]
            try:
                ans1 = session['correct'][id][i].strip()
            except Exception as e:
                correctness += ' ' + 'false'
            finally:
                if ans == ans1:
                    k += 1
                    correctness += ' ' + 'true'
                else:
                    correctness += ' ' + 'false'
            answers += " " + ans
        if task_id in [i[-1] for i in progress.get_all()]:
            progress.update(answers, correctness, task_id)
        else:
            progress.insert(answers, correctness, task_id)
        if task_id not in [i[-1] for i in scores.get_all()]:
            scores.insert(l, k, task_id)
        else:
            scores.update(session['task_id'][id], k)
        correct = progress.get_all(task_id)
        if correct:
            c = correct[0][-2].split()
        else:
            c = []
        if len(correct[0]) >= 2:
            answer = correct[0][1].split()
        else:
            answer = []
    return render_template('task.html', i=id, length=length, correct=c, answer=answer, choices=session['choices'][id])


@app.route('/all_users')
def users():
    l = list(range(len(all_users)))
    return render_template('all_users.html', length=l, users=all_users)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
