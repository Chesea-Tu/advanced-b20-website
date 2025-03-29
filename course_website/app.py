from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import case, func


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
    __tablename__ = 'grade'
    __table_args__ = (db.UniqueConstraint('username', 'name', name='_username_name_uc'),)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.Float, nullable=False)
    name = db.Column(db.String(100), nullable=False)

# 复查请求表
class Regrade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 哪一题/哪一项
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(10), default='Pending')  # 'Pending', 'Approved', 'Rejected'

class AnonymousFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instructor = db.Column(db.String(50), nullable=False)  # 教师用户名
    like_teaching = db.Column(db.Text, nullable=False)
    improve_teaching = db.Column(db.Text, nullable=False)
    like_labs = db.Column(db.Text, nullable=False)
    improve_labs = db.Column(db.Text, nullable=False)
    additional = db.Column(db.Text)  # 可为空
    status = db.Column(db.String(10), default='open')  # open / reviewed

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = "Username already exists."
            return render_template('register.html', error=error)

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_pw, user_type=user_type)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        session['username'] = user.username
        session['user_type'] = user.user_type

        # ✅ 注册后重定向放这里
        if user.user_type.lower() == 'student':
            return redirect('/student/dashboard')
        else:
            return redirect('/instructor/dashboard')

    # ✅ GET 请求直接显示注册页面
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_type'] = user.user_type

            if user.user_type.lower() == 'student':
                return redirect('/student/dashboard')
            else:
                return redirect('/instructor/dashboard')
        else:
            flash("Incorrect username or password.")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session['user_type'].lower() != 'student':
        return redirect('/login')
    return render_template('student/dashboard.html', username=session['username'])

@app.route('/instructor/dashboard')
def instructor_dashboard():
    if 'user_id' not in session or session['user_type'].lower() != 'instructor':
        return redirect('/login')
    return render_template('instructor/dashboard.html', username=session['username'])


@app.route('/instructor/regrade_requests')
def view_regrade_requests():
    if 'username' not in session or session['user_type'].lower() != 'instructor':
        return redirect('/login')

    status_order = case(
        (Regrade.status == 'Pending', 0),
        (Regrade.status == 'Rejected', 1),
        (Regrade.status == 'Approved', 2),
        else_=3
    )

    requests_raw = Regrade.query.order_by(status_order).all()
    all_grades = Grade.query.all()

    # 增加成绩信息
    requests = []
    for r in requests_raw:
        existing_grade = next((g.grade for g in all_grades if g.username == r.username and g.name == r.name), None)
        requests.append({
            'id': r.id,
            'username': r.username,
            'name': r.name,
            'message': r.message,
            'status': r.status,
            'grade': existing_grade
        })

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

@app.route('/instructor/student_grades')
def student_grades():
    if 'user_id' not in session or session['user_type'].lower() != 'instructor':
        return redirect('/login')

    all_grades = Grade.query.all()
    all_students = User.query.filter_by(user_type='student').all()
    categories = ['Assignment', 'Lab', 'Midterm', 'Final']
    categorized = {c: [] for c in categories}

    for c in categories:
        for student in all_students:
            # 看该学生是否已有这个成绩
            match = next(
                (g for g in all_grades if g.username == student.username and g.name.lower() == c.lower()), 
                None
            )
            categorized[c].append({
                'username': student.username,
                'grade': match.grade if match else '',
                'id': match.id if match else None,
                'assignment_name': c
            })

    return render_template('instructor/student_grades.html', grades=categorized)

@app.route('/instructor/update_grade', methods=['POST'])
def update_grade():
    if 'user_id' not in session or session['user_type'].lower() != 'instructor':
        return jsonify({'success': False}), 403

    data = request.get_json()
    username = data.get('username')
    assignment = data.get('assignment').strip().capitalize()  # 标准化大小写，如 'Midterm'
    grade_value = data.get('grade')

    print(f"Grade update request for: username={username}, assignment={assignment}, grade={grade_value}")

    # 查找所有匹配该用户和该 assignment（不区分大小写）
    matches = Grade.query.filter(
        Grade.username == username,
        func.lower(Grade.name) == assignment.lower()
    ).all()

    if matches:
        # 如果有多条，保留第一条，删掉其余的
        grade_entry = matches[0]
        grade_entry.grade = grade_value
        for extra in matches[1:]:
            print(f"Deleting duplicate: {extra.username} - {extra.name} - {extra.grade}")
            db.session.delete(extra)
        print("Existing grade updated and cleaned.")
    else:
        grade_entry = Grade(username=username, name=assignment, grade=grade_value)
        db.session.add(grade_entry)
        print("New grade created.")

    db.session.commit()
    return jsonify({'success': True})

@app.route('/debug/grades')
def debug_grades():
    grades = Grade.query.all()
    return "<br>".join([f"{g.username} - {g.name} - {g.grade}" for g in grades])

@app.route('/instructor/anon_feedback')
def instructor_feedback():
    if 'user_id' not in session or session['user_type'].lower() != 'instructor':
        return redirect('/login')

    username = session['username']
    feedbacks = AnonymousFeedback.query.filter_by(instructor=username).all()

    return render_template('instructor/anon_feedback.html', feedbacks=feedbacks, username=username)

@app.route('/instructor/update_feedback_status', methods=['POST'])
def update_feedback_status():
    if 'user_id' not in session or session['user_type'].lower() != 'instructor':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    feedback_id = data.get('feedback_id')
    feedback = AnonymousFeedback.query.get_or_404(feedback_id)

    feedback.status = 'reviewed'
    db.session.commit()

    return jsonify({'success': True})

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

@app.route('/student/anon_feedback', methods=['GET', 'POST'])
def student_feedback():
    if 'username' not in session or session['user_type'].lower() != 'student':
        return redirect('/login')

    instructors = User.query.filter_by(user_type='instructor').all()

    if request.method == 'POST':
        instructor = request.form.get('instructor')
        like_teaching = request.form.get('like_teaching')
        improve_teaching = request.form.get('improve_teaching')
        like_labs = request.form.get('like_labs')
        improve_labs = request.form.get('improve_labs')
        additional = request.form.get('additional')

        feedback = AnonymousFeedback(
            instructor=instructor,
            like_teaching=like_teaching,
            improve_teaching=improve_teaching,
            like_labs=like_labs,
            improve_labs=improve_labs,
            additional=additional
        )
        db.session.add(feedback)
        db.session.commit()
        flash("Your feedback has been submitted successfully!")
        return redirect(url_for('student_feedback'))

    return render_template('student/anon_feedback.html', instructors=instructors)

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

    # 每次都新建一个请求，不覆盖旧的
    new_request = Regrade(username=username, name=assignment, message=message)
    db.session.add(new_request)
    db.session.commit()

    return jsonify({
        "success": True,
        "status": new_request.status,
        "message": new_request.message
    })


# 首页
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
