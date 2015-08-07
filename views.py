from functools import wraps
from forms import AddTaskForm, RegisterForm, LoginForm
from flask import Flask, flash, redirect, render_template, \
    request, session, url_for, g
from forms import AddTaskForm
from flask.ext.sqlalchemy import SQLAlchemy
#Config
app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import Task, User
#Helper functions


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

#Route handlers
@app.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    #Nice WTForms usage
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(
                    form.name.data,
                    form.email.data,
                    form.password.data,
                )
            db.session.add(new_user)
            db.session.commit()
            flash("Thank for registering. Please login.")
            return redirect(url_for('login'))
        else:
            error = "not validated template"
    return render_template("register.html", form=form, error=error)

@app.route('/tasks')
@login_required

def tasks():
    open_tasks = db.session.query(Task) \
            .filter_by(status='1').order_by(Task.due_date.asc())
    closed_tasks = db.session.query(Task) \
            .filter_by(status='0').order_by(Task.due_date.asc())
    return render_template(
        'tasks.html',
        form=AddTaskForm(request.form),
        open_tasks=open_tasks,
        closed_tasks=closed_tasks
    )
    g.db.close()


@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    flash('Goodbye!')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] \
                or request.form['password'] != app.config['PASSWORD']:
                    error = 'Invalid Credentials. Please try again.'
                    return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            flash('Welcome!')
            return redirect(url_for('tasks'))
    return render_template('login.html')


#CRUD section

#Create
@app.route('/add', methods=['POST'])
@login_required
def new_task():
    form = AddTaskForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit() or True:
            new_task = Task(
                    form.name.data,
                    form.due_date.data,
                    form.priority.data,
                    '1'
                    )
            db.session.add(new_task)
            db.session.commit()
    return redirect(url_for('tasks'))

#Update


@app.route('/complete/<int:task_id>')
@login_required
def complete(task_id):
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).update({"status": "0"})
    db.session.commit()
    flash('The task is complete. Nice')
    return redirect(url_for('tasks'))


#Delete
@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).delete()
    db.session.commit()
    flash("The task was deleted. Add new one?")
    return redirect(url_for('tasks'))
