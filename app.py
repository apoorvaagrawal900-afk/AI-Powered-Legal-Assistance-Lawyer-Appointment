from flask import Flask
from models import db, User, Client, Lawyer
from config import Config
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import render_template, redirect, url_for, flash, request
from functools import wraps

app=Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash('Access denied.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('auth/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        role = request.form.get('role')
        phone = request.form.get('phone')
        location = request.form.get('location')
        
        # Validations
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')
        
        # Create user
        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Create profile based on role
        if role == 'client':
            client = Client(user_id=user.id, name=name, phone=phone, location=location)
            db.session.add(client)
        elif role == 'lawyer':
            lawyer = Lawyer(
            user_id=user.id, 
            name=name, 
            location=location, 
            phone=phone,
            specialization='Not specified',  # Default value
            experience_years=0,  # Default value
            fees=0.0,  # Default value
            bio='Profile not updated yet'  # Default value
            )
            db.session.add(lawyer)
        
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    total_users = User.query.count()
    total_clients = Client.query.count()
    total_lawyers = Lawyer.query.count()
    return render_template('admin/dashboard.html', 
                         total_users=total_users, 
                         total_clients=total_clients, 
                         total_lawyers=total_lawyers)

@app.route('/client/dashboard')
@login_required
@role_required('client')
def client_dashboard():
    client = Client.query.filter_by(user_id=current_user.id).first()
    return render_template('client/dashboard.html', client=client)

@app.route('/lawyer/dashboard')
@login_required
@role_required('lawyer')
def lawyer_dashboard():
    lawyer = Lawyer.query.filter_by(user_id=current_user.id).first()
    return render_template('lawyer/dashboard.html', lawyer=lawyer)

@app.route('/lawyer/profile/edit', methods=['GET', 'POST'])
@login_required
@role_required('lawyer')
def edit_profile():
    lawyer = Lawyer.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        lawyer.specialization = request.form.get('specialization')
        lawyer.experience_years = int(request.form.get('experience_years'))
        lawyer.fees = float(request.form.get('fees'))
        lawyer.phone = request.form.get('phone')
        lawyer.location = request.form.get('location')
        lawyer.bio = request.form.get('bio')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('lawyer_dashboard'))
    
    return render_template('lawyer/edit_profile.html', lawyer=lawyer)

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    total_users = User.query.count()
    total_clients = Client.query.count()
    total_lawyers = Lawyer.query.count()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users, 
                         total_clients=total_clients, 
                         total_lawyers=total_lawyers)

@app.route('/create_admin')
def create_admin():
    if User.query.filter_by(role='admin').first():
        return "Admin already exists!", 400
    
    admin = User(email='admin@lexai.com', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    
    return "Admin created! Email: admin@lexai.com, Password: admin123"

if __name__=="__main__":
    app.run(debug=True)
    
