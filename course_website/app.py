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
    user_type = db.Column(db.String(10), nullable=False)  # 'Student' or 'Instructor'

# 成绩表
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)  # 外键也可以连到 User.username
    grade = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 作业名或题目名

# 复查请求表
class Regrade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 哪一题/哪一项
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), default='Pending')  # 'Pending', 'Approved', 'Rejected'

# 投诉/建议表（Annoy Feed）
class AnnoyFeed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), default='open')  # 'open', 'reviewed'

# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        # 检查是否已存在用户
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = "Username already exists."
            return render_template('register.html', error=error)

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_pw, user_type=user_type)
        db.session.add(user)
        db.session.commit()

        # 注册后自动登录
        session['user_id'] = user.id
        session['username'] = user.username
        session['user_type'] = user.user_type

        return redirect('/dashboard')

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
            session['username'] = user.username
            return redirect('/dashboard')
        else:
            error = "Incorrect username or password."
    return render_template('login.html', error=error)

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    if session['user_type'].lower() == 'student':
        return render_template('student/dashboard.html')
    return render_template('instructor/dashboard.html')


# 首页
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
