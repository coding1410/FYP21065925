from flask import Flask, render_template, request, redirect, url_for, session  # Importing necessary modules from Flask
from flask_sqlalchemy import SQLAlchemy # Importing SQLAlchemy for database management
from werkzeug.security import generate_password_hash, check_password_hash  #importing modules for password hashing for security 
import json
from flask import flash
from flask import session, redirect, url_for, render_template, flash

from flask_caching import Cache

app = Flask(__name__)
# Then register the Blueprint


app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # Cache timeout in seconds

cache = Cache(app)

db = SQLAlchemy(app)

class User(db.Model):   #specifies columns that will be stored in the database
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


@app.route('/')   # what happens when the actual links to the site are clicked
def home():
    if 'username' in session:
        return redirect(url_for('welcome'))
    return render_template('home.html')   #home html templete is ran

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST': 
        username = request.form['username']
        password = request.form['password']

        if len(password) < 7:
            msg = 'Password must be at least 7 characters long.'
        else:
            user = User.query.filter_by(username=username).first()
            if user:
                msg = 'Username already taken.'
            else:
                hashed_password = generate_password_hash(password)
                new_user = User(username=username, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
    
    return render_template('register.html', msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()  # Retrieve the user from the database to check if valid
        if user and check_password_hash(user.password, password): #if info matches up..
            session['username'] = user.username
            return redirect(url_for('welcome')) #direct to welcome route
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    if 'username' in session:
        return render_template('welcome.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))