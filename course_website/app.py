from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import case

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

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    username = session['username']

    if session['user_type'].lower() == 'student':
        return render_template('student/dashboard.html', username=username)
    return render_template('instructor/dashboard.html', username=username)


# 查看所有复查请求（老师端）
@app.route('/instructor/regrade_requests')
def view_regrade_requests():
    if 'username' not in session or session['user_type'].lower() != 'instructor':
        return redirect('/login')

    # 排序：Pending → Rejected → Approved
    status_order = case(
        (Regrade.status == 'Pending', 0),
        (Regrade.status == 'Rejected', 1),
        (Regrade.status == 'Approved', 2),
        else_=3
    )

    requests = Regrade.query.order_by(status_order).all()
    username = session['username']
    return render_template('instructor/regrade_requests.html', requests=requests, username=username)


# 更新复查请求状态（老师端）
@app.route('/instructor/regrade_requests/update/<int:request_id>', methods=['POST'])
def update_regrade_status(request_id):
    if 'username' not in session or session['user_type'].lower() != 'instructor':
        return redirect('/login')

    new_status = request.form.get('status')
    request_entry = Regrade.query.get_or_404(request_id)
    request_entry.status = new_status
    db.session.commit()

    return redirect(url_for('view_regrade_requests'))

@app.route('/instructor/syllabus')
def instructor_syllabus():
    return render_template('instructor/syllabus.html')

@app.route('/instructor/calendar')
def instructor_calendar():
    return render_template('instructor/calendar.html')

@app.route('/instructor/lectures')
def instructor_lectures():
    return render_template('instructor/lectures.html')

@app.route('/instructor/labs')
def instructor_labs():
    return render_template('instructor/labs.html')

@app.route('/instructor/assignments')
def instructor_assignments():
    return render_template('instructor/assignments.html')

@app.route('/instructor/resources')
def instructor_resources():
    return render_template('instructor/resources.html')

@app.route('/instructor/anon_feedback')
def instructor_feedback():
    if 'username' not in session or session['user_type'].lower() != 'instructor':
        return redirect('/login')

    # open 的放前面，reviewed 的放后面
    feedbacks = AnnoyFeed.query.order_by(
        db.case(
            (AnnoyFeed.status == 'open', 0),
            (AnnoyFeed.status == 'reviewed', 1),
        )
    ).all()

    return render_template('instructor/anon_feedback.html', feedbacks=feedbacks)
  
@app.route('/instructor/anon_feedback/update/<int:feedback_id>', methods=['POST'])
def update_feedback_status(feedback_id):
    if 'username' not in session or session['user_type'].lower() != 'instructor':
        return redirect('/login')

    new_status = request.form.get('status')
    feedback = AnnoyFeed.query.get_or_404(feedback_id)
    feedback.status = new_status
    db.session.commit()
    
    return redirect(url_for('instructor_feedback'))

@app.route('/instructor/student_grades')
def student_grades():
    if 'username' not in session:
        return redirect('/login')
    
    username = session['username']
    grades_query = Grade.query.filter_by(username=username).all()

    grades = {'Assignment': [], 'Lab': [], 'Midterm': [], 'Final': []}
    for g in grades_query:
        if 'assign' in g.name.lower():
            grades['Assignment'].append(g.grade)
        elif 'lab' in g.name.lower():
            grades['Lab'].append(g.grade)
        elif 'midterm' in g.name.lower():
            grades['Midterm'].append(g.grade)
        elif 'final' in g.name.lower():
            grades['Final'].append(g.grade)

    return render_template('instructor/student_grades.html', grades=grades)


@app.route('/student/syllabus')
def student_syllabus():
    return render_template('student/syllabus.html')

@app.route('/student/calendar')
def student_calendar():
    return render_template('student/calendar.html')

@app.route('/student/lectures')
def student_lectures():
    return render_template('student/lectures.html')

@app.route('/student/labs')
def student_labs():
    return render_template('student/labs.html')

@app.route('/student/assignments')
def student_assignments():
    return render_template('student/assignments.html')

@app.route('/student/resources')
def student_resources():
    return render_template('student/resources.html')

@app.route('/student/anon_feedback')
def student_feedback():
    return render_template('student/anon_feedback.html')

@app.route('/view_grades')
def view_grades():
    if 'user_id' not in session or session['user_type'].lower() != 'student':
        return redirect('/login')
    
    username = session['username']
    grades = Grade.query.filter_by(username=username).all()

    # 分类成绩
    categorized_grades = {
        'Assignments': [],
        'Labs': [],
        'Midterm': [],
        'Final': []
    }

    for g in grades:
        if 'assignment' in g.name.lower():
            categorized_grades['Assignments'].append(g)
        elif 'lab' in g.name.lower():
            categorized_grades['Labs'].append(g)
        elif 'midterm' in g.name.lower():
            categorized_grades['Midterm'].append(g)
        elif 'final' in g.name.lower():
            categorized_grades['Final'].append(g)

    # ✅ 查询学生提交的 remark 请求，并按 name 分类
    regrades_raw = Regrade.query.filter_by(username=username).all()
    regrades = {}
    for r in regrades_raw:
        regrades.setdefault(r.name, []).append(r)

    # ✅ 将 regrades 传入模板
    return render_template(
        'student/view_grades.html',
        grades=categorized_grades,
        username=username,
        regrades=regrades
    )

@app.route('/submit_remark', methods=['POST'])
def submit_remark():
    if 'user_id' not in session:
        return jsonify({"success": False}), 403

    data = request.get_json()
    assignment = data['assignment']
    message = data['message']
    username = session['username']

    existing = Regrade.query.filter_by(username=username, name=assignment).first()
    if existing:
        existing.message = message
        existing.status = 'Pending'
    else:
        request_obj = Regrade(username=username, name=assignment, message=message)
        db.session.add(request_obj)
    
    db.session.commit()
    return jsonify({"success": True})



# 首页
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
