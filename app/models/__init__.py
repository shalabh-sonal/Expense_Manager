from app import db
from .user import User
from .expense import Expense, ExpenseParticipation, SplitMethod

from datetime import datetime

class PingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PingLog {self.timestamp}>'