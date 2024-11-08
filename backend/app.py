#!/usr/bin/env python3
"""Defines the backend entry point"""
import os
from backend.extensions import bcrypt, db, limiter
from config import config
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

migrate = Migrate()


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
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    limiter.init_app(app)
    CORS(app,
         resources={r"/*": {"origins": app.config['ALLOWED_ORIGINS']}})

    # Register Blueprints
    from routes import auth
    app.register_blueprint(auth.bp)

    return app


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'default'))
    app.run()
