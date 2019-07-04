from flask import Flask, render_template, request, session
from werkzeug.utils import redirect
from DB import DB, UsersModel, TasksModel, ScoresModel, ProgresssModel, Files, TaskUser
from wtf_forms import RegistrateForm, LoginForm, AddTaskForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

base = DB()
users_base = UsersModel(base)
users_base.init_table()
scores = ScoresModel(base)
scores.init_table()
files_base = Files(base)
files_base.init_table()
progress = ProgresssModel(base)
progress.init_table()
tasks_model = TasksModel(base)
tasks_model.init_table()
all_users = users_base.get_all()
task_user = TaskUser(base)
task_user.init_table()


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


@app.route('/homepage1', methods=['GET', 'POST'])
def popp():
    session.pop('list_id')
    return redirect('/homepage')


@app.route('/', methods=['GET', 'POST'])
@app.route('/homepage', methods=['GET', 'POST'])
def tasks():
    if 'username' in session:
        if 'list_id' not in session:
            session['list_id'] = 0
        return redirect('/all_tasks/{}'.format(session['list_id']))
    else:
        return redirect('/login')


@app.route('/add_task/<int:title>', methods=['GET', 'POST'])
def add_task(title):
    if 'username' not in session:
        return redirect('/login')
    form = AddTaskForm()
    if request.method == 'GET':
        if title != 0:
            title1, content, choices, correct_choice = tasks_model.get(title)[2:]
            form.title.data = title1
            form.sentence.data = content
            form.choice.data = choices
            form.correct.data = correct_choice
    elif request.method == 'POST':
        title1 = form.title.data
        sentence = form.sentence.data
        choice = form.choice.data
        correct = form.correct.data
        if len(sentence.split('\n')) != len(choice.split('\n')) or len(correct.split('\n')) != len(choice.split('\n')):
            return render_template('add_task.html', form=form, username=session['username'], users=all_users,
                                   text='invalid task. Number of strings in labels "sentences",'
                                        ' "answer choice", "correct answer" must be the same')
        if not title and title1 in [i[1] for i in tasks_model.get_all()]:
            return render_template('add_task.html', form=form, username=session['username'], users=all_users,
                                   text='task with such title already exists')
        else:
            not_title_index, title_index = title, title
            if not title:
                tasks_model.insert(title1, sentence, choice, correct)
                not_title_index = tasks_model.index()
            ides = [j[0] for j in all_users]
            checked = []
            flag = False
            f = request.files('file')
            if f:
                with open('static/' + f, 'w') as rf:
                    rf.write(f.read().decode('utf-8'))
            for i in ides:
                if request.form.get(str(i)):
                    checked.append(i)
            else:
                if session['list_id'] not in checked:
                    tasks_model.insert(title1, sentence, choice, correct)
                    title_index = tasks_model.index()
                    flag = True
                else:
                    tasks_model.update(title1, sentence, choice, correct, title)
            for i in checked:
                if not title:
                    task_user.insert(not_title_index, i)
                else:
                    if flag and title_index not in [i[1] for i in task_user.get_all(i)]:
                        task_user.insert(title_index, i)
                    elif not flag and not_title_index not in [i[1] for i in task_user.get_all(i)]:
                        task_user.insert(not_title_index, i)
            return redirect("/homepage")
    return render_template('add_task.html', form=form, username=session['username'], users=all_users)


@app.route('/all_tasks/<int:id>', methods=['GET', 'POST'])
def all_tasks(id):
    all, username = '', ''
    if 'username' not in session:
        return redirect('/login')
    if id != 0 and session['user_id'] in [1, 2]:
        all = [i[1] for i in task_user.get_all(id)]
        username = users_base.get(id)[1]
        session['list_id'] = id
    else:
        id = 0
    if id == 0:
        session['list_id'] = session['user_id']
        all = [i[1] for i in task_user.get_all(session['list_id'])]
        username = ''
    session['titles'] = []
    session['contents'] = []
    session['choices'] = []
    session['correct'] = []
    session['task_id'] = all
    session['hints'] = []
    for i in all:
        try:
            hints, title, content, choices, correct_choices = tasks_model.get(i)[1:]
            session['titles'].append(title)
            session['contents'].append(content.split('\n'))
            choices = [i.split() for i in choices.split('\n')]
            session['choices'].append(choices)
            session['correct'].append(correct_choices.split('\n'))
            hints = [i.split() for i in hints.split('\n')]
            session['hints'].append(hints)
        except Exception as e:
            all.pop(all.index(i))
    sc = progress.get_all(session['list_id'])
    scores_id = [i[-2] for i in sc]
    scores1 = []
    n_all = 0
    for i in all:
        if i in scores_id:
            n_correct = sc[scores_id.index(i)][2]
            n_all = sc[scores_id.index(i)][1]
        else:
            n_correct = 0
            try:
                n_all = len(session['contents'][all.index(i)])
            except IndexError:
                all.pop(all.index(i))
        scores1.append(str(n_correct) + '/' + str(n_all))
    session['scores'] = scores1
    print(session['contents'])
    return render_template('tasks.html', flag=True, n=range(len(all)), name=username)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_tasks(id):
    if 'username' not in session:
        return redirect('/login')
    tasks_model.delete(id)
    progress.delete(id, session['list_id'])
    task_user.delete(id, session['list_id'])
    return redirect('/all_tasks/{}'.format(session['list_id']))


@app.route('/task/<int:id>', methods=['GET', 'POST'])
def task(id):
    if 'username' not in session:
        return redirect('/login')
    num_correct = 0
    l = len(session['contents'][id])
    length = list(range(l))
    answers = ''
    correctness = ''
    task_id = session['task_id'][id]
    correct = progress.get_all(session['list_id'], task_id)
    try:
        c = correct[0][-3].split()
        answer = correct[0][3].split()
        prog = progress.get_all(session['list_id'], task_id)
        ides = [i[-2] for i in prog]
        print(prog)
    except IndexError:
        answer = []
        c = []
        ides = []
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
                    num_correct += 1
                    correctness += ' ' + 'true'
                else:
                    correctness += ' ' + 'false'
            answers += " " + ans
        if task_id in ides:
            progress.update(l, num_correct, answers, correctness, task_id, session['list_id'])
        else:
            progress.insert(l, num_correct, answers, correctness, task_id, session['list_id'])
        correct = progress.get_all(session['list_id'], task_id)
        if correct:
            c = correct[0][-3].split()
            if len(correct[0]) >= 2:
                answer = correct[0][3].split()
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
