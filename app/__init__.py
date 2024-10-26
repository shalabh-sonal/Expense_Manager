from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flasgger import Swagger
from flask_cors import CORS
from flask_log_request_id import RequestID, RequestIDLogFilter
import logging

from .config.config import get_config


db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
swagger = None

def create_app():
    app = Flask(__name__)

    CORS(app)

    # Initialize API
    api = Api(app)
    
    # Configuration
    app.config.from_object(get_config())
    
    # Set up logging with request ID
    setup_logging(app)


    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)


    # Initialize Swagger
    global swagger
    if swagger is None:
        swagger = setup_swagger(app)

    from .models import User, Expense, ExpenseParticipation, PingLog
    Migrate(app, db) # how tables and others formed after this?


    print("all..........good.....")

    with app.app_context():
        from .resources import register_resources
        register_resources(api)


    return app

def setup_logging(app):
    """Set up the logging for the application with a request ID."""

    RequestID(app)

    app.logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s %(request_id)s - %(message)s")
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIDLogFilter())

    # Add handlers to the app's logger
    app.logger.addHandler(console_handler)

    # Set the app's logging level
    app.logger.setLevel(logging.DEBUG)
    app.logger.info("Logging is set up with request ID")


# openapi:3.0 is used 
def setup_swagger(app):

    template = {
        "openapi": "3.0.0",  # Changed from "3.0.2" to "3.0.0"
        "info": {
            "title": "Expense Sharing API",
            "description": "API for managing expenses and user accounts",
            "version": "1.0.0",
            "contact": {
                "email": "your-email@example.com"
            }
        },
        "components": {
            "securitySchemes": {
                "Bearer": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT Authorization header using the Bearer scheme."
                }
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs",
        "openapi": "3.0.0"  # Add this line to specify OpenAPI version in config
    }

    Swagger(app, config=swagger_config, template=template)
