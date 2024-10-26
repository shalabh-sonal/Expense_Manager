import os

class BaseConfig:
    """Base configuration."""
    # SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    DEBUG = False
    TESTING = False
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    # UPLOAD_FOLDER = 'uploads'
    # MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://eklavya:test123@localhost:5432/expenses_db')

# class ProductionConfig(BaseConfig):
#     """Production configuration."""
#     DEBUG = False
#     SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://eklavya:test123@localhost:5432/test_db')

# Map environment names to config classes
config = {
    'development': DevelopmentConfig,
    # 'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration class based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])