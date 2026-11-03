
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
    # appointments = db.relationship('Appointment', back_populates='client', lazy=True)
    legal_issues=db.relationship('LegalIssue', back_populates='client', lazy=True)

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
    

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time)
    status = db.Column(db.String(20), default='pending')
    reason = db.Column(db.Text)
    mode = db.Column(db.String(20), default='online')
    legal_issue_id = db.Column(db.Integer, db.ForeignKey('legal_issues.id'))
    slot_id = db.Column(db.Integer, db.ForeignKey('appointment_slots.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client = db.relationship('Client', backref='appointments')
    lawyer = db.relationship('Lawyer', backref='appointments')
    legal_issue = db.relationship('LegalIssue', backref='appointments')
    slot = db.relationship('AppointmentSlot', backref='appointments')


class AppointmentSlot(db.Model):
    __tablename__ = 'appointment_slots'
    
    id = db.Column(db.Integer, primary_key=True)
    lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    
    lawyer = db.relationship('Lawyer', backref='slots')

# Consultation Chat Message (per appointment)
class ConsultationMessage(db.Model):
    __tablename__ = 'consultation_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    appointment = db.relationship('Appointment', backref='chat_messages')
    sender = db.relationship('User', backref='consultation_messages')

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
    # category = db.Column(db.String(100))  # NEW: AI-detected case category

    client = db.relationship('Client', back_populates='documents', lazy=True)
    questions = db.relationship('Question', back_populates='document', lazy=True, cascade='all, delete-orphan')

# Legal Issue Table (for issue classification)
class LegalIssue(db.Model):
    __tablename__ = 'legal_issues'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    suggested_lawyer_ids = db.Column(db.Text)  # JSON string of lawyer IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    client = db.relationship('Client', back_populates='legal_issues', lazy=True)

# Appointment Slot Table (for booking slots)

# Case Table (ongoing legal matter)
class Case(db.Model):
    __tablename__ = 'cases'
    
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(50), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'), nullable=False)
    legal_issue_id = db.Column(db.Integer, db.ForeignKey('legal_issues.id'))
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    status = db.Column(db.String(50), default='In Progress')  # Created, In Progress, Closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    client = db.relationship('Client', backref='cases')
    lawyer = db.relationship('Lawyer', backref='cases')
    legal_issue = db.relationship('LegalIssue', backref='cases')
    appointment = db.relationship('Appointment', backref='cases')

# Case Update Table (progress tracking)
class CaseUpdate(db.Model):
    __tablename__ = 'case_updates'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    milestone = db.Column(db.String(200))
    status = db.Column(db.String(50))
    message = db.Column(db.Text, nullable=False)
    next_action = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    case = db.relationship('Case', backref='updates')
    author = db.relationship('User', backref='case_updates')


# Case Message Table (chat within case)
class CaseMessage(db.Model):
    __tablename__ = 'case_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    case = db.relationship('Case', backref='messages')
    sender = db.relationship('User', backref='case_messages')


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # Property, Employment, Family, etc.
    description = db.Column(db.Text)

# Review Table (client reviews lawyer after case/consultation)
class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    lawyer_id = db.Column(db.Integer, db.ForeignKey('lawyers.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    case = db.relationship('Case', backref='reviews')
    appointment = db.relationship('Appointment', backref='reviews')
    client = db.relationship('Client', backref='reviews')
    lawyer = db.relationship('Lawyer', backref='reviews')

class LegalHelpConversation(db.Model):
    __tablename__ = 'legal_help_conversations'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer,
        db.ForeignKey('clients.id'),
        nullable=False,
        index=True
    )
    title = db.Column(db.String(120), nullable=False, default='New conversation')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship(
        'LegalHelpMessage',
        back_populates='conversation',
        cascade='all, delete-orphan',
        order_by='LegalHelpMessage.id'
    )


class LegalHelpMessage(db.Model):
    __tablename__ = 'legal_help_messages'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey('legal_help_conversations.id'),
        nullable=False,
        index=True
    )
    role = db.Column(db.String(10), nullable=False)  # user / model
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    conversation = db.relationship(
        'LegalHelpConversation',
        back_populates='messages'
    )