import logging
import boto3
import bleach
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db, bcrypt, limiter
from app.models import User, Task
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IST = timezone(timedelta(hours=5, minutes=30))

def now_ist():
    return datetime.now(IST).replace(tzinfo=None)

S3_BUCKET = 'secureapp-backups-pranav-950639281860-ap-south-1-an'
S3_REGION = 'ap-south-1'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

main = Blueprint('main', __name__)

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

# JWT API Login - returns access token
@main.route('/api/login', methods=['POST'])
@limiter.limit("10 per minute")
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        access_token = create_access_token(
            identity=user.id,
            additional_claims={'role': user.role, 'email': user.email}
        )
        logger.info(f"API_LOGIN_SUCCESS: email={email} ip={get_client_ip()}")
        return jsonify({
            'access_token': access_token,
            'user': {'id': user.id, 'username': user.username, 'role': user.role}
        }), 200
    logger.warning(f"API_LOGIN_FAILED: email={email} ip={get_client_ip()}")
    return jsonify({'error': 'Invalid credentials'}), 401

# JWT Protected API endpoint - get current user info
@main.route('/api/me', methods=['GET'])
@jwt_required()
def api_me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }), 200

# JWT Protected API - get tasks
@main.route('/api/tasks', methods=['GET'])
@jwt_required()
def api_tasks():
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'status': t.status,
        'priority': t.priority,
        'deadline': t.deadline.isoformat() if t.deadline else None
    } for t in tasks]), 200

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
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
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
            logger.info(f"SUCCESSFUL_LOGIN: email={email} ip={get_client_ip()}")
            return redirect(url_for('main.dashboard'))
        logger.warning(f"FAILED_LOGIN_ATTEMPT: email={email} ip={get_client_ip()}")
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
    sort = request.args.get('sort', 'created_desc')

    def sort_tasks(task_list):
        no_deadline = [t for t in task_list if not t.deadline]
        with_deadline = [t for t in task_list if t.deadline]
        if sort == 'deadline_asc':
            with_deadline.sort(key=lambda t: t.deadline)
            return with_deadline + no_deadline
        elif sort == 'deadline_desc':
            with_deadline.sort(key=lambda t: t.deadline, reverse=True)
            return no_deadline + with_deadline
        elif sort == 'created_asc':
            return sorted(task_list, key=lambda t: t.created_at)
        else:  # created_desc (default)
            return sorted(task_list, key=lambda t: t.created_at, reverse=True)

    if current_user.role == 'admin':
        tasks = sort_tasks(Task.query.all())
        all_users = User.query.all()
        users = sorted(all_users, key=lambda u: (u.id != current_user.id))
        return render_template('admin_dashboard.html', tasks=tasks, users=users, now_dt=now_dt, sort=sort)
    tasks = sort_tasks(Task.query.filter_by(user_id=current_user.id).all())
    return render_template('dashboard.html', tasks=tasks, now_dt=now_dt, sort=sort)

# Profile page
@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

# Update profile (username, email, password)
@main.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    new_username = request.form.get('username', '').strip()
    new_email = request.form.get('email', '').strip()
    new_password = request.form.get('new_password', '').strip()
    current_password = request.form.get('current_password', '').strip()

    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('main.profile'))

    if new_username and new_username != current_user.username:
        if User.query.filter_by(username=new_username).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('main.profile'))
        current_user.username = new_username

    if new_email and new_email != current_user.email:
        if User.query.filter_by(email=new_email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('main.profile'))
        current_user.email = new_email

    if new_password:
        if len(new_password) < 6:
            flash('New password must be at least 6 characters.', 'danger')
            return redirect(url_for('main.profile'))
        current_user.set_password(new_password)

    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('main.profile'))

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
        flash('Profile picture uploaded successfully!', 'success')
        logger.info(f"PROFILE_UPLOAD: user={current_user.email} file={filename}")
    except Exception as e:
        logger.error(f"S3_UPLOAD_ERROR: user={current_user.email} error={str(e)}")
        flash('Upload failed. Please try again.', 'danger')
    return redirect(url_for('main.profile'))

# Delete own account
@main.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    password = request.form.get('password', '')
    if not current_user.check_password(password):
        flash('Incorrect password. Account not deleted.', 'danger')
        return redirect(url_for('main.profile'))
    if current_user.role == 'admin':
        flash('Admin accounts cannot be deleted.', 'danger')
        return redirect(url_for('main.profile'))
    Task.query.filter_by(user_id=current_user.id).delete()
    db.session.delete(current_user)
    db.session.commit()
    flash('Your account has been deleted.', 'success')
    return redirect(url_for('main.login'))

# Add Task
@main.route('/task/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form.get('title')
        description = bleach.clean(request.form.get('description', ''), strip=True)
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
        task.description = bleach.clean(request.form.get('description', ''), strip=True)
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
