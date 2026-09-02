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
            # Check approval status



            if not user.is_approved:
                flash('Your account is pending admin approval. Please wait for approval.', 'warning')
                return render_template('auth/login.html')
            
            # Check blacklist status
            if user.is_blacklisted:
                flash('Your account has been blacklisted. Contact admin for support.', 'error')
                return render_template('auth/login.html')
            
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
        # User create karte waqt
        user = User(email=email, role=role, is_approved=False, is_blacklisted=False)
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

@app.route('/client/profile/edit', methods=['GET', 'POST'])
@login_required
@role_required('client')
def edit_client_profile():
    client = Client.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        client.name = request.form.get('name')
        client.phone = request.form.get('phone')
        client.location = request.form.get('location')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('client_dashboard'))
    
    return render_template('client/edit_profile.html', client=client)



@app.route('/admin/users')
@login_required
@role_required('admin')
def manage_users():
    # Get all users with their profiles
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@app.route('/admin/user/<int:user_id>/approve')
@login_required
@role_required('admin')
def approve_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_approved = True
        user.is_blacklisted = False  # Approve karne pe blacklist remove karo
        db.session.commit()
        flash(f'{user.role.title()} approved successfully!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/user/<int:user_id>/reject')
@login_required
@role_required('admin')
def reject_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_approved = False
        db.session.commit()
        flash(f'{user.role.title()} approval rejected.', 'warning')
    return redirect(url_for('manage_users'))

@app.route('/admin/user/<int:user_id>/blacklist')
@login_required
@role_required('admin')
def blacklist_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_blacklisted = True
        db.session.commit()
        flash(f'{user.role.title()} blacklisted successfully!', 'error')
    return redirect(url_for('manage_users'))

@app.route('/admin/user/<int:user_id>/unblacklist')
@login_required
@role_required('admin')
def unblacklist_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_blacklisted = False
        db.session.commit()
        flash(f'{user.role.title()} removed from blacklist.', 'success')
    return redirect(url_for('manage_users'))

@app.route('/create_admin')
def create_admin():
    if User.query.filter_by(role='admin').first():
        return "Admin already exists!", 400
    
    admin = User(email='admin@lexai.com', role='admin',is_approved=True, is_blacklisted=False)
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    
    return "Admin created! Email: admin@lexai.com, Password: admin123"

if __name__=="__main__":
    app.run(debug=True)
    
