from functools import wraps
from app import swagger  # Import the global swagger instance

def swagger_decorator(swagger_spec):
    """
    A decorator that wraps swag_from and handles the global swagger instance
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if swagger and hasattr(swagger, 'spec'):
                # Add the spec to the global swagger instance
                endpoint = f.__name__
                swagger.spec.path(endpoint=endpoint, operations=swagger_spec)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
