from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'some_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment3.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# 用户表
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)

# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        hashed_pw = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        user_type = request.form['user_type']
        user = User(username=username, password=hashed_pw, user_type=user_type)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and bcrypt.check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['user_type'] = user.user_type
            return redirect('/dashboard')
        else:
            error = "Incorrect username or password."
    return render_template('login.html', error=error)

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    if session['user_type'] == 'student':
        return render_template('student_dashboard.html')
    return render_template('instructor_dashboard.html')

# 保护内容页面
@app.route('/labs')
def labs():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('labs.html')

# 首页
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
