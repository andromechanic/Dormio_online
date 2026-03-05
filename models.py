from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), nullable=False)  # student, warden, admin, principal
    full_name = db.Column(db.String(100), nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)

    # One-to-one student profile
    student_profile = db.relationship(
        "Student",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # Notifications relationship
    notifications = db.relationship(
        "Notification",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    sent_notifications = db.relationship(
        "Notification",
        foreign_keys="Notification.sender_id",
        backref="sender",
        lazy=True
    )

    # Complaints assigned to staff
    assigned_complaints = db.relationship(
        "Complaint",
        foreign_keys="Complaint.assigned_to",
        backref="assigned_user",
        lazy=True
    )

    # Bills created by staff
    created_bills = db.relationship(
        "Bill",
        foreign_keys="Bill.created_by",
        backref="creator",
        lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Student(db.Model):
    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    )

    rfid_code = db.Column(db.String(50), unique=True, nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)

    room_number = db.Column(db.String(20), nullable=False)
    contact = db.Column(db.String(20), nullable=False)

    semester = db.Column(db.Integer, default=1)
    course = db.Column(db.String(100))

    current_status = db.Column(db.String(10), default="OUT")  # IN or OUT

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    logs = db.relationship(
        "AttendanceLog",
        backref="student",
        lazy=True,
        cascade="all, delete-orphan"
    )

    bills = db.relationship(
        "Bill",
        backref="student",
        lazy=True,
        cascade="all, delete-orphan"
    )

    complaints = db.relationship(
        "Complaint",
        backref="student",
        lazy=True,
        cascade="all, delete-orphan"
    )

    payments = db.relationship(
        "Payment",
        backref="student",
        lazy=True,
        cascade="all, delete-orphan"
    )


class AttendanceLog(db.Model):
    __tablename__ = "attendance_log"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id", ondelete="CASCADE"),
        nullable=False
    )

    action = db.Column(db.String(10), nullable=False)  # IN or OUT

    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class Bill(db.Model):
    __tablename__ = "bill"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id", ondelete="CASCADE"),
        nullable=False
    )

    bill_type = db.Column(db.String(50), nullable=False)  # mess, electricity, rent

    amount = db.Column(db.Float, nullable=False)

    month = db.Column(db.String(20), nullable=False)  # January 2026

    semester = db.Column(db.Integer)

    due_date = db.Column(db.Date, nullable=False)

    paid = db.Column(db.Boolean, default=False)

    paid_date = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="SET NULL")
    )

    payments = db.relationship(
        "Payment",
        backref="bill",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id", ondelete="CASCADE"),
        nullable=False
    )

    bill_id = db.Column(
        db.Integer,
        db.ForeignKey("bill.id", ondelete="CASCADE"),
        nullable=False
    )

    amount = db.Column(db.Float, nullable=False)

    payment_method = db.Column(db.String(50))  # cash, online, card

    transaction_id = db.Column(db.String(100))

    payment_date = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    remarks = db.Column(db.Text)


class Complaint(db.Model):
    __tablename__ = "complaint"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id", ondelete="CASCADE"),
        nullable=False
    )

    ticket_id = db.Column(db.String(20), unique=True, nullable=False)

    category = db.Column(db.String(50), nullable=False)

    subject = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), default="open")

    priority = db.Column(db.String(20), default="medium")

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    resolved_at = db.Column(db.DateTime)

    assigned_to = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="SET NULL")
    )

    resolution_notes = db.Column(db.Text)

    @staticmethod
    def generate_ticket_id():
        return f"TKT{secrets.token_hex(4).upper()}"


class Notification(db.Model):
    __tablename__ = "notification"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="SET NULL")
    )

    parent_notification_id = db.Column(
        db.Integer,
        db.ForeignKey("notification.id", ondelete="SET NULL")
    )

    title = db.Column(db.String(200), nullable=False)

    message = db.Column(db.Text, nullable=False)

    type = db.Column(db.String(50))  # bill, complaint, attendance, general

    read = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
