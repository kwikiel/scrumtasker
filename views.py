from functools import wraps
from forms import AddTaskForm, RegisterForm, LoginForm
from flask import Flask, flash, redirect, render_template, \
    request, session, url_for, g
from flask.ext.sqlalchemy import SQLAlchemy
import datetime
# Config
app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import Task, User
# Helper functions


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

# Route handlers


@app.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    # Nice WTForms usage
    form = RegisterForm(request.form)
    if request.method == 'POST':
        form
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
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(name=request.form['name']).first()
            if user is not None and user.password == request.form['password']:
                session['logged_in'] = True
                session['user_id'] = user.id
                flash('Welcome!')
                return redirect(url_for('tasks'))
            else:
                error = 'Invalid username or password'
        else:
            error = "Both fields are required"
    return render_template('login.html', form=form, error=error)


# CRUD section

# Create
@app.route('/add', methods=['POST'])
@login_required
def new_task():
    form = AddTaskForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit() or True:
            new_task = Task(
                name = form.name.data,
                due_date = form.due_date.data,
                priority = form.priority.data,
                status = '1',
                posted_date = datetime.datetime.utcnow(),
                user_id = session['user_id']
                )
            db.session.add(new_task)
            db.session.commit()
    return redirect(url_for('tasks'))

# Update


@app.route('/complete/<int:task_id>')
@login_required
def complete(task_id):
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).update({"status": "0"})
    db.session.commit()
    flash('The task is complete. Nice')
    return redirect(url_for('tasks'))


# Delete
@app.route('/delete/<int:task_id>/')
@login_required
def delete_entry(task_id):
    new_id = task_id
    db.session.query(Task).filter_by(task_id=new_id).delete()
    db.session.commit()
    flash("The task was deleted. Add new one?")
    return redirect(url_for('tasks'))
