from flask_restful import Resource, reqparse
from flasgger import swag_from
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from app.models.user import User
from app import db
from datetime import timedelta
import re

class AuthResource:
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='Name cannot be blank', location='json')
    parser.add_argument('mobile', type=str, required=True, help='Mobile number cannot be blank', location='json') 
    parser.add_argument('email', type=str, required=True, help='Email cannot be blank', location='json')
    parser.add_argument('password', type=str, required=True, help='Password cannot be blank', location='json')


class UserLogin(Resource, AuthResource):
    @swag_from({
        'tags': ['Authentication'],
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'email': {'type': 'string', 'format': 'email'},
                        'password': {'type': 'string', 'minLength': 8}
                    },
                    'required': ['email', 'password']
                }
            }
        ],
        'responses': {
            '200': {
                'description': 'Login successful',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'access_token': {'type': 'string'},
                        'user_id': {'type': 'integer'},
                        'email': {'type': 'string'}
                    }
                }
            },
            '401': {'description': 'Invalid credentials'},
            '422': {'description': 'Validation error'}
        }
    })
    def post(self):
        try:
            data = self.parser.parse_args()
            
            user = User.query.filter_by(email=data['email']).first()
            if not user:
                return {"message": "User not found"}, 401
                
            if not user.check_password(data['password']):
                return {"message": "Invalid password"}, 401
                
            access_token = create_access_token(
                identity=user.id,
                expires_delta=timedelta(days=1)
            )
            
            return {
                "access_token": access_token,
                "user_id": user.id,
                "email": user.email,
                "name": user.name
            }, 200
            
        except Exception as e:
            return {"message": "Error during login", "error": str(e)}, 500
        

# class UserRegister(Resource, AuthResource):
#     def post(self):
#         data = self.parser.parse_args()
        
#         # Validate email format
#         if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
#             return {"message": "Invalid email format"}, 400
        
#         # Validate password strength
#         if len(data['password']) < 8:
#             return {"message": "Password must be at least 8 characters long"}, 400
        
#         if User.query.filter_by(email=data['email']).first():
#             return {"message": "User already exists"}, 400
        
#         user = User(email=data['email'])
#         user.set_password(data['password'])
        
#         try:
#             db.session.add(user)
#             db.session.commit()
#             return {"message": "User created successfully"}, 201
#         except Exception as e:
#             db.session.rollback()
#             return {"message": f"Error creating user: {str(e)}"}, 500
