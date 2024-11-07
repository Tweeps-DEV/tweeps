#!/usr/bin/env python3
"""Defines the backend entry point"""
from flask import Flask
from flask_cors import CORS
import os
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.extensions import bcrypt, db, limiter
from backend.routes import bp as main_bp
from backend.routes.auth import bp as auth_bp
from backend.routes.menu import bp as menu_bp  # Import the new menu blueprint

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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'

    CORS(app, resources={r"/*": {"origins": app.config.get('ALLOWED_ORIGINS', '*')}})
    bcrypt.init_app(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    limiter.init_app(app)

    with app.app_context():
        from backend.models import User, Order, OrderItem, MenuItem, Storage  # Import all models
        db.create_all()

    register_blueprints(app)

    return app

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(menu_bp)  # Register the new menu blueprint

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)