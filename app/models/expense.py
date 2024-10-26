from app import db
from datetime import datetime, timezone
from enum import Enum

class SplitMethod(Enum):
    EQUAL = 'equal'
    EXACT = 'exact'
    PERCENTAGE = 'percentage'

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    split_method = db.Column(db.Enum(SplitMethod), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    participations = db.relationship('ExpenseParticipation', backref='expense', lazy=True)


class ExpenseParticipation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    share_amount = db.Column(db.Numeric(10, 2), nullable=False)
    share_percentage = db.Column(db.Numeric(5, 2), nullable=True)
    
    __table_args__ = (
        db.UniqueConstraint('expense_id', 'user_id', name='unique_expense_user'),
    )