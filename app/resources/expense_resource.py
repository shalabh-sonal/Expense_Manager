from flasgger import swag_from
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.services.balance_sheet_service import BalanceSheetService
from app.models.expense import Expense, ExpenseParticipation, SplitMethod
from app.services.expense_calculator import ExpenseCalculator
from app import db
from decimal import Decimal

class ExpenseResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('description', type=str, required=True, location='json')
    parser.add_argument('amount', type=float, required=True, location='json')
    parser.add_argument('split_method', type=str, required=True, 
                       choices=('equal', 'exact', 'percentage'), location='json')
    parser.add_argument('participants', type=dict, required=True, location='json')

    @jwt_required()
    @swag_from({
        'tags': ['Expenses'],
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'description': {'type': 'string'},
                        'amount': {'type': 'number'},
                        'split_method': {
                            'type': 'string',
                            'enum': ['equal', 'exact', 'percentage']
                        },
                        'participants': {
                            'type': 'object',
                            'additionalProperties': {
                                'type': 'object',
                                'properties': {
                                    'share': {'type': 'number'},
                                    'percentage': {'type': 'number'}
                                }
                            }
                        }
                    },
                    'required': ['description', 'amount', 'split_method', 'participants']
                }
            }
        ],
        'responses': {
            '201': {
                'description': 'Expense created successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'expense_id': {'type': 'integer'}
                    }
                }
            },
            '400': {
                'description': 'Invalid input'
            },
            '500': {
                'description': 'Server error'
            }
        }
    })
    def post(self):
        data = self.parser.parse_args()
        creator_id = get_jwt_identity()
        
        try:
            # Create expense
            expense = Expense(
                description=data['description'],
                amount=Decimal(str(data['amount'])),
                split_method=SplitMethod(data['split_method']),
                creator_id=creator_id
            )
            db.session.add(expense)
            db.session.flush()  # Get expense ID without committing
            
            # Calculate shares
            calculator = ExpenseCalculator()
            shares = calculator.calculate_shares(
                data['split_method'],
                data['amount'],
                data['participants']
            )
            
            # Create participations
            for user_id, share in shares.items():
                participation = ExpenseParticipation(
                    expense_id=expense.id,
                    user_id=user_id,
                    share_amount=share,
                    share_percentage=(Decimal(str(data['participants'][user_id]['percentage']))
                                   if data['split_method'] == 'percentage' else None)
                )
                db.session.add(participation)
            
            db.session.commit()
            return {"message": "Expense created successfully", "expense_id": expense.id}, 201
            
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error creating expense: {str(e)}"}, 500


    @jwt_required()
    @swag_from({
        'tags': ['Expenses'],
        'parameters': [
            {
                'name': 'expense_id',
                'in': 'path',
                'type': 'integer',
                'required': False,
                'description': 'ID of the expense to retrieve'
            }
        ],
        'responses': {
            '200': {
                'description': 'Expense details retrieved successfully',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer', 'example': 1},
                                'description': {'type': 'string', 'example': 'Dinner'},
                                'amount': {'type': 'number', 'format': 'float', 'example': 100.50},
                                'split_method': {'type': 'string', 'example': 'EQUAL'},
                                'creator_id': {'type': 'integer', 'example': 1},
                                'date': {'type': 'string', 'format': 'date-time', 'example': '2024-10-26T10:30:00'},
                                'participations': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'user_id': {'type': 'integer', 'example': 2},
                                            'share_amount': {'type': 'number', 'format': 'float', 'example': 50.25},
                                            'share_percentage': {'type': 'number', 'format': 'float', 'example': 50.0}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            '403': {
                'description': 'Unauthorized to view this expense'
            },
            '404': {
                'description': 'Expense not found'
            }
        }
    })
    def get(self, expense_id=None):
        user_id = get_jwt_identity()
        
        if expense_id:
            expense = Expense.query.get(expense_id)
            if not expense:
                return {"message": "Expense not found"}, 404
                
            # Check if user is creator or participant
            if (expense.creator_id != user_id and 
                not any(p.user_id == user_id for p in expense.participations)):
                return {"message": "Unauthorized to view this expense"}, 403
                
            return {
                "id": expense.id,
                "description": expense.description,
                "amount": float(expense.amount),
                "split_method": expense.split_method.value,
                "creator_id": expense.creator_id,
                "date": expense.date.isoformat(),
                "participations": [{
                    "user_id": p.user_id,
                    "share_amount": float(p.share_amount),
                    "share_percentage": float(p.share_percentage) if p.share_percentage else None
                } for p in expense.participations]
            }
        
        # Get all expenses where user is a participant
        expenses = Expense.query.filter(
            (Expense.creator_id == user_id) |
            (Expense.participations.any(ExpenseParticipation.user_id == user_id))
        ).all()
        
        return [{
            "id": e.id,
            "description": e.description,
            "amount": float(e.amount),
            "split_method": e.split_method.value,
            "date": e.date.isoformat()
        } for e in expenses]

  
# overall expenses
class ExpenseList(Resource):
    @jwt_required()
    @swag_from({
        'tags': ['Balances'],
        'summary': 'Get balance summary for all users',
        'description': 'Returns a list of net balances for all users in the system',
        'responses': {
            '200': {
                'description': 'List of user balances retrieved successfully',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'balances': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'user_id': {
                                                'type': 'integer',
                                                'example': 1,
                                                'description': 'Unique identifier of the user'
                                            },
                                            'name': {
                                                'type': 'string',
                                                'example': 'John Doe',
                                                'description': 'Name of the user'
                                            },
                                            'net_balance': {
                                                'type': 'number',
                                                'format': 'float',
                                                'example': 125.50,
                                                'description': 'Net balance for the user (positive means others owe them money)'
                                            }
                                        },
                                        'required': ['user_id', 'name', 'net_balance']
                                    }
                                }
                            }
                        },
                        'examples': {
                            'multiple_users': {
                                'value': {
                                    'balances': [
                                        {
                                            'user_id': 1,
                                            'name': 'John Doe',
                                            'net_balance': 125.50
                                        },
                                        {
                                            'user_id': 2,
                                            'name': 'Jane Smith',
                                            'net_balance': -75.25
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            '401': {
                'description': 'Authentication required',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'msg': {
                                    'type': 'string',
                                    'example': 'Missing JWT token'
                                }
                            }
                        }
                    }
                }
            },
            '500': {
                'description': 'Server error',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'message': {
                                    'type': 'string',
                                    'example': 'Internal server error occurred'
                                }
                            }
                        }
                    }
                }
            }
        },
        'security': [
            {
                'Bearer': []
            }
        ]
    })
    def get(self):
        users = User.query.all()
        balances = []

        for user in users:
            user_balance = BalanceSheetService.calculate_user_balance(user.id)
            balances.append({
                'user_id': user.id,
                'name': user.name,
                'net_balance': float(user_balance.net_balance)
            })
        
        return {'balances': balances}