import logging
import boto3
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db, bcrypt, limiter
from app.models import User, Task
from functools import wraps

# Logging setup for security monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

def now_ist():
    return datetime.now(IST).replace(tzinfo=None)

# S3 configuration
S3_BUCKET = 'secureapp-backups-pranav-950639281860-ap-south-1-an'
S3_REGION = 'ap-south-1'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

main = Blueprint('main', __name__)

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Health Check
@main.route('/health')
def health():
    return jsonify({'status': 'healthy', 'app': 'SecureApp', 'version': '1.0'}), 200

# Home
@main.route('/')
def index():
    return redirect(url_for('main.login'))

# Register
@main.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('main.register'))
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

# Login
@main.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            logger.info(f"SUCCESSFUL_LOGIN: email={email} ip={request.remote_addr}")
            return redirect(url_for('main.dashboard'))
        logger.warning(f"FAILED_LOGIN_ATTEMPT: email={email} ip={request.remote_addr}")
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

# Logout
@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# Dashboard
@main.route('/dashboard')
@login_required
def dashboard():
    now_dt = now_ist()
    if current_user.role == 'admin':
        tasks = Task.query.all()
        all_users = User.query.all()
        users = sorted(all_users, key=lambda u: (u.id != current_user.id))
        return render_template('admin_dashboard.html', tasks=tasks, users=users, now_dt=now_dt)
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', tasks=tasks, now_dt=now_dt)

# Profile page
@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# Upload profile picture to S3
@main.route('/profile/upload', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'file' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(url_for('main.profile'))
    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('main.profile'))
    if not allowed_file(file.filename):
        flash('Only image files allowed (png, jpg, jpeg, gif, webp).', 'danger')
        return redirect(url_for('main.profile'))
    try:
        filename = secure_filename(f"profile_{current_user.id}_{file.filename}")
        s3_key = f"profiles/{filename}"
        s3 = boto3.client('s3', region_name=S3_REGION)
        s3.upload_fileobj(file, S3_BUCKET, s3_key,
                          ExtraArgs={'ContentType': file.content_type})
        profile_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        current_user.profile_picture = profile_url
        db.session.commit()
        flash('Profile picture uploaded successfully to S3!', 'success')
        logger.info(f"PROFILE_UPLOAD: user={current_user.email} file={filename}")
    except Exception as e:
        logger.error(f"S3_UPLOAD_ERROR: user={current_user.email} error={str(e)}")
        flash('Upload failed. Please try again.', 'danger')
    return redirect(url_for('main.profile'))

# Add Task
@main.route('/task/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority', 'medium')
        deadline_str = request.form.get('deadline')
        deadline = None
        if deadline_str:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            if deadline <= now_ist().replace(second=0, microsecond=0):
                flash('Deadline cannot be in the past.', 'danger')
                return render_template('add_task.html')
        task = Task(title=title, description=description, priority=priority,
                    deadline=deadline, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('add_task.html')

# Edit Task
@main.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and current_user.role != 'admin':
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.status = request.form.get('status')
        task.priority = request.form.get('priority', 'medium')
        deadline_str = request.form.get('deadline')
        if deadline_str:
            new_deadline = datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            if new_deadline <= now_ist().replace(second=0, microsecond=0) and task.status != 'completed':
                flash('Deadline cannot be in the past.', 'danger')
                return render_template('edit_task.html', task=task)
            task.deadline = new_deadline
        else:
            task.deadline = None
        db.session.commit()
        flash('Task updated!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('edit_task.html', task=task)

# Delete Task
@main.route('/task/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and current_user.role != 'admin':
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.dashboard'))
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted!', 'success')
    return redirect(url_for('main.dashboard'))

# Delete User (Admin only)
@main.route('/user/delete/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot delete admin users.', 'danger')
        return redirect(url_for('main.dashboard'))
    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('main.dashboard'))
