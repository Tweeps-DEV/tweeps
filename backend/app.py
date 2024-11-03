#!/usr/bin/env python3
"""Defines the backend entry point"""
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
from backend.extensions import bcrypt, db, limiter

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
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

if __name__ == "__main__":
    app = create_app()
    app.run()
