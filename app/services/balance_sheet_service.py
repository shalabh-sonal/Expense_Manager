from decimal import Decimal
from typing import Dict, List, Tuple
from datetime import datetime
import csv
from io import StringIO
from dataclasses import dataclass
from app.models.expense import Expense, ExpenseParticipation
from app.models.user import User
from sqlalchemy import func
from app import db

@dataclass
class UserBalance:
    user_id: int
    name: str
    total_paid: Decimal
    total_owed: Decimal
    net_balance: Decimal
    expenses_paid: List[Dict]
    expenses_involved: List[Dict]


class BalanceSheetService:
    @staticmethod
    def calculate_user_balance(user_id: int) -> UserBalance:
        """Calculate detailed balance for a specific user."""
        # Get user details
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Calculate expenses paid by user
        expenses_paid = db.session.query(
            Expense.id,
            Expense.description,
            Expense.amount,
            Expense.date,
            Expense.split_method
        ).filter(Expense.creator_id == user_id).all()

        total_paid = sum(expense.amount for expense in expenses_paid)

        # Calculate expenses where user is involved
        expenses_involved = db.session.query(
            Expense.id,
            Expense.description,
            ExpenseParticipation.share_amount
        ).join(
            ExpenseParticipation
        ).filter(
            ExpenseParticipation.user_id == user_id
        ).all()

        total_owed = sum(expense.share_amount for expense in expenses_involved)

        # Format expenses for response
        expenses_paid_list = [
            {
                'id': exp.id,
                'description': exp.description,
                'amount': float(exp.amount),
                'date': exp.date.strftime('%Y-%m-%d %H:%M:%S'),
                'split_method': exp.split_method.value
            }
            for exp in expenses_paid
        ]

        expenses_involved_list = [
            {
                'id': exp.id,
                'description': exp.description,
                'share_amount': float(exp.share_amount)
            }
            for exp in expenses_involved
        ]

        return UserBalance(
            user_id=user_id,
            name=user.name,
            total_paid=total_paid,
            total_owed=total_owed,
            net_balance=total_paid - total_owed,
            expenses_paid=expenses_paid_list,
            expenses_involved=expenses_involved_list
        )
        
    @staticmethod
    def calculate_group_balance() -> List[Dict]:
        """Calculate balances for all users and optimize settlements."""
        users = User.query.all()
        balances = []

        for user in users:
            user_balance = BalanceSheetService.calculate_user_balance(user.id)
            balances.append({
                'user_id': user.id,
                'name': user.name,
                'net_balance': float(user_balance.net_balance)
            })

        return BalanceSheetService.optimize_settlements(balances)


    @staticmethod
    def generate_balance_sheet_csv(user_id: int = None) -> Tuple[str, str]:
        """Generate a CSV balance sheet for download."""
        output = StringIO()
        writer = csv.writer(output)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if user_id:
            # Individual user balance sheet
            balance = BalanceSheetService.calculate_user_balance(user_id)
            filename = f"user_{user_id}_balance_{timestamp}.csv"

            # Write header
            writer.writerow(['Personal Balance Sheet'])
            writer.writerow(['Name', balance.name])
            writer.writerow(['Total Paid', float(balance.total_paid)])
            writer.writerow(['Total Owed', float(balance.total_owed)])
            writer.writerow(['Net Balance', float(balance.net_balance)])
            
            # Write expenses paid
            writer.writerow([])
            writer.writerow(['Expenses Paid'])
            writer.writerow(['ID', 'Description', 'Amount', 'Date', 'Split Method'])
            for expense in balance.expenses_paid:
                writer.writerow([
                    expense['id'],
                    expense['description'],
                    expense['amount'],
                    expense['date'],
                    expense['split_method']
                ])

            # Write expenses involved
            writer.writerow([])
            writer.writerow(['Expenses Involved'])
            writer.writerow(['ID', 'Description', 'Share Amount'])
            for expense in balance.expenses_involved:
                writer.writerow([
                    expense['id'],
                    expense['description'],
                    expense['share_amount']
                ])

        else:
            # Group balance sheet
            balances = BalanceSheetService.calculate_group_balance()
            filename = f"group_balance_{timestamp}.csv"

            # Write header
            writer.writerow(['Group Balance Sheet'])
            writer.writerow(['Recommended Settlements'])
            writer.writerow(['From', 'To', 'Amount'])
            
            for settlement in balances:
                writer.writerow([
                    settlement['from_user'],
                    settlement['to_user'],
                    settlement['amount']
                ])

        return filename, output.getvalue()