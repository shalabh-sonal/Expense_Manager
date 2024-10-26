from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Dict
from flask import current_app as app
from app.exceptions.exception import (
    ExpenseCalculationError,
    InvalidAmountError,
    InvalidParticipantsError,
    InvalidSplitMethodError
)
from abc import ABC, abstractmethod


class ExpenseSplitStrategy(ABC):
    @abstractmethod
    def calculate_shares(self, total_amount: Decimal, participants_data: Dict) -> Dict[int, Decimal]:
        """
        Calculate expense shares for participants
        
        Args:
            total_amount: Total expense amount
            participants_data: Dictionary containing participant data
            
        Returns:
            Dictionary mapping user IDs to their share amounts
            
        Raises:
            ExpenseCalculationError: If calculation fails
        """
        pass

    def _validate_amount(self, amount: Decimal) -> None:
        """Validate expense amount"""
        try:
            if amount <= Decimal('0'):
                raise InvalidAmountError("Expense amount must be positive")
        except InvalidOperation:
            raise InvalidAmountError("Invalid expense amount format")

    def _validate_participants(self, participants: Dict) -> None:
        """Validate participants data"""
        if not participants:
            raise InvalidParticipantsError("No participants provided")
        
        if not isinstance(participants, dict):
            raise InvalidParticipantsError("Participants data must be a dictionary")


class EqualSplitStrategy(ExpenseSplitStrategy):
    def calculate_shares(self, total_amount: Decimal, participants_data: Dict) -> Dict[int, Decimal]:
        try:
            self._validate_amount(total_amount)
            self._validate_participants(participants_data)

            num_participants = len(participants_data)
            if num_participants == 0:
                raise InvalidParticipantsError("No participants for equal split")

            share_amount = (total_amount / num_participants).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Ensure rounding doesn't affect total
            shares = {user_id: share_amount for user_id in participants_data.keys()}
            rounding_adjustment = total_amount - sum(shares.values())
            
            if rounding_adjustment != 0:
                # Add any rounding difference to first participant
                first_user_id = next(iter(shares))
                shares[first_user_id] += rounding_adjustment

            return shares

        except (InvalidOperation, ArithmeticError) as e:
            app.logger.error(f"Error calculating equal shares: {str(e)}")
            raise ExpenseCalculationError(f"Error calculating equal shares: {str(e)}")


# class EqualSplitStrategy(ExpenseSplitStrategy):
#     def calculate_shares(self, total_amount, participants_data:dict):
#         num_participants = len(participants_data)
#         share_amount = Decimal(total_amount) / num_participants
#         return {p['user_id']: share_amount for p in participants_data.keys()}

class ExactSplitStrategy(ExpenseSplitStrategy):
    def calculate_shares(self, total_amount: Decimal, participants_data: Dict) -> Dict[int, Decimal]:
        try:
            self._validate_amount(total_amount)
            self._validate_participants(participants_data)

            # Convert all shares to Decimal and validate
            shares = {
                user_id: Decimal(str(share)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                for user_id, share in participants_data.items()
            }

            total_shares = sum(shares.values())
            if total_shares != total_amount:
                raise InvalidAmountError(
                    f"Sum of shares ({total_shares}) does not equal total amount ({total_amount})"
                )

            return shares

        except (InvalidOperation, ArithmeticError) as e:
            app.logger.error(f"Error calculating exact shares: {str(e)}")
            raise ExpenseCalculationError(f"Error calculating exact shares: {str(e)}")


# class ExactSplitStrategy(ExpenseSplitStrategy):
#     def calculate_shares(self, total_amount, participants_data:dict):
#         # shares = {p['user_id']: Decimal(p['share']) for p in participants_data}
#         if sum(participants_data.values()) != Decimal(total_amount):
#             raise ValueError("Sum of shares must equal total amount")
#         return participants_data


class PercentageSplitStrategy(ExpenseSplitStrategy):
    def calculate_shares(self, total_amount: Decimal, participants_data: Dict) -> Dict[int, Decimal]:
        try:
            self._validate_amount(total_amount)
            self._validate_participants(participants_data)

            # Convert percentages to Decimal and validate
            percentages = {
                user_id: Decimal(str(percentage))
                for user_id, percentage in participants_data.items()
            }

            total_percentage = sum(percentages.values())
            if total_percentage != Decimal('100'):
                raise InvalidParticipantsError(
                    f"Sum of percentages ({total_percentage}) must equal 100"
                )

            # Calculate shares
            shares = {
                user_id: (percentage * total_amount / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                for user_id, percentage in percentages.items()
            }

            # Handle rounding adjustments
            total_shares = sum(shares.values())
            rounding_adjustment = total_amount - total_shares
            
            if rounding_adjustment != 0:
                # Add any rounding difference to the participant with the highest percentage
                max_percentage_user = max(percentages.items(), key=lambda x: x[1])[0]
                shares[max_percentage_user] += rounding_adjustment

            return shares

        except (InvalidOperation, ArithmeticError) as e:
            app.logger.error(f"Error calculating percentage shares: {str(e)}")
            raise ExpenseCalculationError(f"Error calculating percentage shares: {str(e)}")



# class PercentageSplitStrategy(ExpenseSplitStrategy):
#     def calculate_shares(self, total_amount, participants_data:dict):
#         # shares = {p['user_id']: Decimal(p['percentage']) for p in participants_data}
#         if sum(participants_data.values()) != Decimal('100'):
#             raise ValueError("Percentages must sum to 100")
#         return {user_id: (percentage * Decimal(total_amount) / 100)
#                 for user_id, percentage in participants_data.items()}

class ExpenseCalculator:
    def __init__(self):
        self._strategies = {
            'equal': EqualSplitStrategy(),
            'exact': ExactSplitStrategy(),
            'percentage': PercentageSplitStrategy()
        }

    def calculate_shares(self, split_method: str, total_amount: Decimal, participants_data: Dict) -> Dict[int, Decimal]:
        """
        Calculate expense shares based on split method
        
        Args:
            split_method: Method to split expense ('equal', 'exact', or 'percentage')
            total_amount: Total expense amount
            participants_data: Dictionary containing participant data
            
        Returns:
            Dictionary mapping user IDs to their share amounts
            
        Raises:
            InvalidSplitMethodError: If split method is invalid
            ExpenseCalculationError: If calculation fails
        """
        try:
            if split_method not in self._strategies:
                raise InvalidSplitMethodError(f"Invalid split method: {split_method}")

            strategy = self._strategies[split_method]
            return strategy.calculate_shares(total_amount, participants_data)

        except ExpenseCalculationError:
            raise
        except Exception as e:
            app.logger.error(f"Unexpected error in expense calculation: {str(e)}")
            raise ExpenseCalculationError(f"Failed to calculate expense shares: {str(e)}")