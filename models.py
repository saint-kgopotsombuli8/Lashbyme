from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False) # Storing as YYYY-MM-DD for easy querying
    time = db.Column(db.String(10), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Financials and Status
    base_price = db.Column(db.Integer, nullable=False)
    final_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Confirmed, Completed, Cancelled
    payment_status = db.Column(db.String(20), default='Pending') # Pending, Paid

    # Client Tracking (Basic tracking by email)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CalendarEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False) # Political, Economic, Society, Personal
    date = db.Column(db.String(20), nullable=False) # YYYY-MM-DD
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)