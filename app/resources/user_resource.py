# from app.auth.jwt_manager import admin_required
import re
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from app.models.user import User
from app import db


class UserResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, required=True, help='Name cannot be blank', location='json')
    parser.add_argument('mobile', type=str, required=True, help='Mobile number cannot be blank', location='json') 
    parser.add_argument('email', type=str, required=True, help='Email cannot be blank', location='json')
    
    @swag_from({
        'tags': ['Users'],
        'summary': 'Create a new user',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'email': {'type': 'string', 'format': 'email'},
                        'mobile': {'type': 'string'},
                        'password': {'type': 'string', 'format': 'password'}
                    },
                    'required': ['name', 'email', 'mobile', 'password']
                }
            }
        ],
        'responses': {
            201: {
                'description': 'User created successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'user_id': {'type': 'integer'}
                    }
                }
            },
            400: {
                'description': 'Invalid input data',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            },
            500: {
                'description': 'Internal server error'
            }
        }
    })
    def post(self):
        data = self.parser.parse_args()
        
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return {"message": "Invalid email format"}, 400
        
        # Validate password strength
        if len(data['password']) < 8:
            return {"message": "Password must be at least 8 characters long"}, 400


        if User.query.filter_by(email=data['email']).first():
            return {"message": "User with this email already exists"}, 400
            
        try:
            user = User(
                name=data['name'],
                email=data['email'],
                mobile=data['mobile']
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            return {
                "message": "User created successfully",
                "user_id": user.id
            }, 201
            
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error creating user: {str(e)}"}, 500

    @jwt_required()
    @swag_from({
        'tags': ['Users'],
        'summary': 'Get user information',
        'parameters': [
            {
                'name': 'user_id',
                'in': 'path',
                'type': 'integer',
                'required': False,
                'description': 'User ID (optional - if not provided, returns all users)'
            },
            {
                'name': 'Authorization',
                'in': 'header',
                'type': 'string',
                'required': True,
                'description': 'JWT token'
            }
        ],
        'responses': {
            200: {
                'description': 'User information retrieved successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'email': {'type': 'string'},
                        'mobile': {'type': 'string'}
                    }
                }
            },
            404: {
                'description': 'User not found'
            }
        }
    })
    def get(self, user_id=None):
        try:
            if user_id:
                user = User.query.get(user_id)
                if not user:
                    return {"message": "User not found"}, 404
                return {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "mobile": user.mobile
                }

            users = User.query.all()
            return [{
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "mobile": user.mobile
            } for user in users]
        except Exception as e:
            return {"message": f"Error retrieving user(s): {str(e)}"}, 500
    

    @jwt_required()
    @swag_from({
        'tags': ['Users'],
        'summary': 'Update user information',
        'parameters': [
            {
                'name': 'user_id',
                'in': 'path',
                'type': 'integer',
                'required': True
            },
            {
                'name': 'Authorization',
                'in': 'header',
                'type': 'string',
                'required': True,
                'description': 'JWT token'
            },
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'email': {'type': 'string', 'format': 'email'},
                        'mobile': {'type': 'string'}
                    }
                }
            }
        ],
        'responses': {
            200: {
                'description': 'User updated successfully'
            },
            403: {
                'description': 'Unauthorized to modify this user'
            },
            404: {
                'description': 'User not found'
            }
        }
    })
    def put(self, user_id):
        data = self.parser.parse_args()
        user = User.query.get(user_id)
        
        if not user:
            return {"message": "User not found"}, 404
            
        if get_jwt_identity() != user_id:
            return {"message": "Unauthorized to modify this user"}, 403
        
        try:
            user.name = data['name']
            user.mobile = data['mobile']
            user.email = data['email']
            db.session.commit()
            return {"message": "User updated successfully"}
        except Exception as e:
            db.session.rollback()
            return {"message": f"Error updating user: {str(e)}"}, 500


