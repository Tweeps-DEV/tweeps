#!/usr/bin/env python3
"""Defines the backend entry point"""
from config import Config
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
limiter = Limiter(app)

from backend.routes import auth  # Import routes after creating the app
app.register_blueprint(auth.bp)

if __name__ == "__main__":
    app.run()
