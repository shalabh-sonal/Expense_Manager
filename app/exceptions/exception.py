
class ExpenseCalculationError(Exception):
    """Base exception for expense calculation errors"""
    pass

class InvalidAmountError(ExpenseCalculationError):
    """Raised when the amount is invalid"""
    pass

class InvalidParticipantsError(ExpenseCalculationError):
    """Raised when participants data is invalid"""
    pass

class InvalidSplitMethodError(ExpenseCalculationError):
    """Raised when split method is invalid"""
    pass