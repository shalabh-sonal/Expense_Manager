from flask_restful import Resource
from datetime import datetime

from app import db,swagger
from app.models import PingLog
from .user_resource import UserResource
from .auth_resource import UserLogin
from .expense_resource import ExpenseResource, ExpenseList
from .balance_sheet_resource import BalanceSheetResource


class PingResource(Resource):
    def get(self):

        ping_log = PingLog()
        db.session.add(ping_log)
        db.session.commit()
        
        print(f'log: {ping_log}')

        return {
            'status': 'success',
            'message': 'pong',
            'timestamp': datetime.now().isoformat()
        }, 200
    
def register_resources(api):
    """Register all API resources"""
    api.add_resource(PingResource, '/ping')
    
    # User endpoints
    api.add_resource(UserResource, '/api/users', '/api/users/<int:user_id>')
    api.add_resource(UserLogin, '/api/login')
    
    # Expense endpoints
    api.add_resource(ExpenseResource, '/api/expenses', '/api/expenses/<int:expense_id>')
    api.add_resource(ExpenseList, '/api/expenses/list')
    
    # Balance sheet endpoint
    api.add_resource(BalanceSheetResource, '/api/balance-sheet')


    # Register all paths with Swagger
    if swagger:
        for resource in [UserResource, UserLogin, ExpenseResource, 
                        ExpenseList, BalanceSheetResource]:
            for method in ['get', 'post', 'put', 'delete']:
                if hasattr(resource, method):
                    method_obj = getattr(resource, method)
                    if hasattr(method_obj, '__swagger_spec__'):
                        swagger.spec.path(
                            path=resource.endpoint,
                            operations={method: method_obj.__swagger_spec__}
                        )