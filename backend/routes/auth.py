#!/usr/bin/env python3
"""Defines auth routes"""
import jwt
import logging
import os
from app import db
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from extensions import limiter
from flask import Blueprint, request, jsonify, url_for, redirect, current_app
from flask_cors import CORS
from functools import wraps
from logging.handlers import RotatingFileHandler
from marshmallow import Schema, fields, validate, ValidationError
from models.user import User


load_dotenv()
logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

bp = Blueprint('auth', __name__)
CORS(bp,
     resources={r"/*": {"origins": os.getenv("ALLOWED_ORIGINS").split(",")}})


class UserSchema(Schema):
    """Schema for user registration validation"""
    username = fields.Str(required=True,
                          validate=validate.Length(min=3, max=30))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda p: len(p) >= 8)


class LoginSchema(Schema):
    """Schema for login validation"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda p: len(p) >= 8)


# Authentication decorator
def token_required(f):
    """
    A decorator to protect routes that require authentication.

    This decorator:
    1. Checks for the presence of a valid JWT token in the request header
    2. Decodes and validates the token
    3. Retrieves the user associated with the token

    Args:
        f (function): The view function to be decorated

    Returns:
        function: The decorated function

    Raises:
        401 Unauthorized: If the token is missing, invalid, or expired
        500 Internal Server Error: If an unexpected error occurs on validation
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split(" ")[1]
            data = jwt.decode(token,
                              os.getenv('SECRET_KEY'),
                              algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['id']).first()

            if not current_user:
                raise jwt.InvalidTokenError('User not found')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        except Exception as e:
            app.logger.error(f"Error in token_required: {str(e)}")
            return jsonify({'message': 'Something went wrong'}), 500
        return f(current_user, *args, **kwargs)
    return decorated


@bp.route('/api/auth/signup', methods=['POST'])
@limiter.limit("5 per minute")
def signup():
    """
    Handle user signup requests.

    This function:
    1. Validates the incoming JSON data
    2. Checks if the username or email already exists
    3. Creates a new user with a hashed password
    4. Adds the new user to the database

    Returns:
        tuple: A tuple containing a JSON response and an HTTP status code.
            Success: ({'message': 'New user created!'}, 201)
            Failure: (error_message, appropriate_status_code)

    Raises:
        400 Bad Request: If fields are missing or if username/email exists
        500 Internal Server Error: If an unexpected error occurs
    """
    try:
        data = request.get_json()
        if not data:
            current_app.logger.error("No JSON data received")
            return jsonify({'message': 'No data provided'}), 400

        if current_app.debug:
            info = f"Received signup request with data: {data}"
            current_app.logger.info(info)

        UserSchema().load(data)

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400

        new_user = User(username=data['username'], email=data['email'])
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'message': 'New user created!',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email
            }
        }), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error in signup: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Something went wrong'}), 500


@bp.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """
    Handle user login requests.

    This function:
    1. Validates the incoming authorization header
    2. Checks if the user exists
    3. Verifies the password
    4. Generates a JWT token for authenticated users

    Returns:
        tuple: A tuple containing a JSON response and an HTTP status code.
            Success: ({'token': jwt_token}, 200)
            Failure: (error_message, appropriate_status_code)

    Raises:
        401 Unauthorized: If login credentials are invalid or missing
        500 Internal Server Error: If an unexpected error occurs
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        LoginSchema().load(data)

        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Invalid credentials!'}), 401

        expiration_time = datetime.now(timezone.utc) + timedelta(hours=24)

        token = jwt.encode(
            {
                'user_id': user.id,
                'exp': expiration_time
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({'token': token})
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        current_app.logger.error(f"Error in login: {str(e)}")
        return jsonify({'message': 'Something went wrong'}), 500
