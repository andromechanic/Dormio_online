from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, warden, admin, principal
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship with Student (one-to-one)
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    rfid_code = db.Column(db.String(50), unique=True, nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    room_number = db.Column(db.String(20), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.Integer, default=1)
    course = db.Column(db.String(100))
    current_status = db.Column(db.String(10), default='OUT')  # IN or OUT
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    logs = db.relationship('AttendanceLog', backref='student', lazy=True, cascade='all, delete-orphan')
    bills = db.relationship('Bill', backref='student', lazy=True, cascade='all, delete-orphan')
    complaints = db.relationship('Complaint', backref='student', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='student', lazy=True, cascade='all, delete-orphan')

class AttendanceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # IN or OUT
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    bill_type = db.Column(db.String(50), nullable=False)  # mess, electricity, rent
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.String(20), nullable=False)  # e.g., "January 2026"
    semester = db.Column(db.Integer)
    due_date = db.Column(db.Date, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationship
    payments = db.relationship('Payment', backref='bill', lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    bill_id = db.Column(db.Integer, db.ForeignKey('bill.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # cash, online, card
    transaction_id = db.Column(db.String(100))
    payment_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    remarks = db.Column(db.Text)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    ticket_id = db.Column(db.String(20), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # maintenance, cleanliness, food, electrical, other
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    resolved_at = db.Column(db.DateTime)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    resolution_notes = db.Column(db.Text)
    
    @staticmethod
    def generate_ticket_id():
        return f"TKT{secrets.token_hex(4).upper()}"

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))  # bill, complaint, attendance, general
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
