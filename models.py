
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'client', 'lawyer', 'admin'
    is_approved = db.Column(db.Boolean, default=False)  # ← NEW
    is_blacklisted = db.Column(db.Boolean, default=False)  # ← NEW
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    # Relationships
    client_profile = db.relationship('Client', backref='user', uselist=False)
    lawyer_profile = db.relationship('Lawyer', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    location = db.Column(db.String(100))
    
    # Relationships
    documents = db.relationship('Document', back_populates='client', lazy=True)
    appointments = db.relationship('Appointment', back_populates='client', lazy=True)

class Lawyer(db.Model):
    __tablename__ = 'lawyers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    fees = db.Column(db.Float, default=0.0)
    phone = db.Column(db.String(15))
    location = db.Column(db.String(100))
    bio = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=False)
    
    # Relationships
    appointments = db.relationship('Appointment', back_populates='lawyer', lazy=True)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, completed
    reason = db.Column(db.Text)  # For Milestone 3
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client=db.relationship('Client', back_populates='appointments')
    lawyer=db.relationship('Lawyer', back_populates='appointments')

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    document = db.relationship('Document', back_populates='questions', lazy=True)

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    summary = db.Column(db.Text)  # For Milestone 3

    client = db.relationship('Client', back_populates='documents', lazy=True)
    questions = db.relationship('Question', back_populates='document', lazy=True, cascade='all, delete-orphan')


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # Property, Employment, Family, etc.
    description = db.Column(db.Text)