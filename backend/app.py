#!/usr/bin/env python3
"""Defines the backend entry point"""
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from backend.extensions import bcrypt, db, limiter

def create_app(config_name='default'):
    """
    Create and configure an instance of the Flask application.

    Args:
        config_name (str): The name of the configuration to use.
        Defaults to 'default'.

    Returns:
        Flask: A configured Flask application instance.

    This function:
    1. Creates a new Flask app instance
    2. Loads the configuration based on the provided config_name
    3. Initializes all extensions with this app instance
    4. Sets up CORS with allowed origins from the config
    5. Registers blueprints for authentication and main routes
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/*": {"origins": app.config['ALLOWED_ORIGINS']}})
    bcrypt.init_app(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    limiter.init_app(app)

    register_blueprints(app)

    return app

def register_blueprints(app):
    from backend.routes.auth import bp as auth_bp  # Import routes inside the function
    app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'default'))
    app.run()