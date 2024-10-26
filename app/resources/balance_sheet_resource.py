from urllib import request
from flask_restful import Resource
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import send_file, make_response
from app.services.balance_sheet_service import BalanceSheetService
from io import StringIO

class BalanceSheetResource(Resource):
    @jwt_required()
    @swag_from({
        'tags': ['Balance Sheet'],
        'parameters': [
            {
                'name': 'format',
                'in': 'query',
                'type': 'string',
                'enum': ['json', 'csv'],
                'default': 'json',
                'required': False,
                'description': 'Response format (json or csv)'
            }
        ],
        'responses': {
            '200': {
                'description': 'Balance sheet retrieved successfully',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'user_id': {'type': 'integer', 'example': 1},
                                'name': {'type': 'string', 'example': 'John Doe'},
                                'total_paid': {'type': 'number', 'format': 'float', 'example': 500.00},
                                'total_owed': {'type': 'number', 'format': 'float', 'example': 250.00},
                                'net_balance': {'type': 'number', 'format': 'float', 'example': 250.00},
                                'expenses_paid': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'id': {'type': 'integer', 'example': 1},
                                            'description': {'type': 'string', 'example': 'Dinner'},
                                            'amount': {'type': 'number', 'format': 'float', 'example': 100.50},
                                            'date': {'type': 'string', 'format': 'date-time', 'example': '2024-10-26T10:30:00'},
                                            'split_method': {'type': 'string', 'example': 'EQUAL'}
                                        }
                                    }
                                },
                                'expenses_involved': {
                                    'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        'properties': {
                                            'id': {'type': 'integer', 'example': 2},
                                            'description': {'type': 'string', 'example': 'Groceries'},
                                            'share_amount': {'type': 'number', 'format': 'float', 'example': 25.50}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    'text/csv': {
                        'schema': {
                            'type': 'string',
                            'format': 'binary'
                        }
                    }
                }
            },
            '400': {
                'description': 'Invalid request'
            },
            '401': {
                'description': 'Authentication required'
            },
            '500': {
                'description': 'Server error'
            }
        }
    })
    def get(self):
        user_id = get_jwt_identity()
        response_format = request.args.get('format', 'json')
        try:
            # Get user balance
            balance = BalanceSheetService.calculate_user_balance(user_id)
            
            # Generate CSV
            filename, csv_data = BalanceSheetService.generate_balance_sheet_csv(user_id)
            
            # Create in-memory file
            csv_buffer = StringIO(csv_data)
            
            # Return file for download
            return send_file(
                csv_buffer,
                mimetype='text/csv',
                as_attachment=True,
                download_name=filename
            )
        except ValueError as e:
            return {"message": str(e)}, 400  
        except Exception as e:
            return {"message": f"Error generating balance sheet: {str(e)}"}, 500