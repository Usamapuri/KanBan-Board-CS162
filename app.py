# importing all the required packages and Libraries 
import os # os helps to handle the files paths
from flask import Flask, render_template, url_for, redirect, request, session, flash, g 
# SQL Alchemy for creating the database 
from flask_sqlalchemy import SQLAlchemy
# create the login page 
from flask_login import LoginManager, current_user, login_user,login_required, UserMixin




#Setting up the flask app
app = Flask(__name__)
path = os.path.abspath(os.getcwd()) + '\\test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path
app.config['SECRET_KEY'] = 'Opps1234'


database = SQLAlchemy(app)

class KanBan(database.Model):
    '''
    Creating a Table for Tasks
    '''
    __tablename__ = 'KanBan'
    id = database.Column(database.Integer, primary_key = True)
    task = database.Column(database.String(120), unique=True, nullable=False)
    task_status = database.Column(database.String(10), nullable=False)
    user_id = database.Column(database.Integer, database.ForeignKey('User.id'))


class User(database.Model, UserMixin):
    '''
    Creating a Table for User Login
    '''
    __tablename__ = 'User'
    id = database.Column(database.Integer, primary_key = True)
    user_name = database.Column(database.String(50))
    email = database.Column(database.String(50))
    password = database.Column(database.String(50))
    task_id = database.relationship('KanBan', backref = 'user', lazy = 'dynamic')

    
database.create_all()
database.session.commit()

#__________________________________________________________ LOGIN PAGE______________________________________________________________________

auth = LoginManager()
auth.init_app(app)
auth.login_view = 'login'

@auth.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/signup', methods = ['GET', 'POST'])
def signup():
    '''
    Function for Sign Up
    '''
    if request.method == 'POST':
        app_user = User.query.filter_by(user_name = request.form['user_name']).first()
        if app_user is not None:
            text = "This Username already exists"
            return render_template('signup.html', error=text)
        if len(request.form['pwd']) < 8:
            text = "Sorry! Password should be greater than 8 characters"
            return render_template('signup.html', error=text)
        if request.form['pwd'] != request.form['repwd']:
            text = 'Sorry! The passwords you entered donnot match'
            return render_template('signup.html', error=text)
        
        new_user = User(user_name = request.form['user_name'], password = request.form['pwd'])
        database.session.add(new_user)
        database.session.commit()
        flash('Sign Up Successfull')
        return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template('signup.html')


@app.route('/login', methods=['GET','POST'])
def login():
    '''
    Function For Login
    '''
    if request.method == 'POST':
        app_user = User.query.filter_by(user_name = request.form['user_name'], password = request.form['pwd']).first()
        if app_user is None:
            text = "This Username and Password Configuration is Invalid"
            return render_template('login.html', error=text)
        login_user(app_user)
        return redirect(url_for('homepage'))
    elif request.method == 'GET' :
        return render_template('login.html')


@app.route('/logout', methods= ['GET','POST'])
def logout():
    '''
    Function for Logout 
    '''
    session.pop('logged_in', None)
    return redirect('login')
#_____________________________________ KANBAN APP_________________________________________________




@app.route('/', methods=['GET'])
@login_required
def homepage():
    g.user = current_user
    to_do  = []
    do_ing = []
    do_ne = []
    tasklst = KanBan.query.filter_by(user_id= g.user.id).all()
    for i in tasklst:
        if i.task_status == 'todo':
            to_do.append(i)
        elif i.task_status == 'doing':
            do_ing.append(i)
        elif i.task_status == 'done':
            do_ne.append(i)
    return render_template('index.html', to_do = to_do, do_ing = do_ing, do_ne = do_ne)

@app.route('/addtask', methods = ['POST'])
def add_task():
    g.user = current_user
    todo_task = KanBan(task= request.form['tasktodo'], task_status = 'todo')
    todo_task.user = g.user
    database.session.add(todo_task)
    database.session.commit()
    return redirect(url_for('homepage'))


@app.route('/doingboard', methods = ['POST'])
def doingboard():
    '''
    This function changes the status of the task as 
    well as takes it from the todo column to the Doing column
    '''
    form_id = request.form
    form = form_id.to_dict()
    task_id = next(iter(form))
    task = KanBan.query.filter_by(id=int(task_id)).first()
    task.task_status = 'doing'
    database.session.commit()
    return redirect(url_for('homepage'))


@app.route('/doneboard', methods = ['POST'])
def doneboard():
    """
    This function changes the task status
    from doing to done and moves it to the next column 
    """
    form_id = request.form
    form = form_id.to_dict()
    task_id = next(iter(form))
    task = KanBan.query.filter_by(id=int(task_id)).first()
    task.task_status = 'done'
    database.session.commit()
    return redirect(url_for('homepage'))


@app.route('/deletetask', methods = ['POST'])
def deletetask():
    '''
    This function deletes the task 
    '''
    form_id = request.form
    form = form_id.to_dict()
    task_id = next(iter(form))
    task = KanBan.query.filter_by(id=int(task_id)).first()
    database.session.delete(task)
    database.session.commit()
    return redirect(url_for('homepage'))

#________________________________________________RUNNING THE APP_____________________________________________
if __name__ == '__main__':
    app.run(debug=True)
