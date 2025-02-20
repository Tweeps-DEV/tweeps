#!/usr/bin/env python3
import jwt
import logging
import os
from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS
from functools import wraps
from logging.handlers import RotatingFileHandler
from marshmallow import Schema, fields, validate, ValidationError
from models.user import User
from app import db, cache
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from typing import Tuple, Dict, Any
import re

load_dotenv()

logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler(
    'auth.log',
    maxBytes=10485760,
    backupCount=5,
    encoding='utf-8'
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(process)d] - %(message)s'
)
handler.setFormatter(formatter)
logger = logging.getLogger('auth')
logger.addHandler(handler)

bp = Blueprint('auth', __name__)

CORS(bp, resources={
    r"/api/auth/*": {
        "origins": os.getenv("ALLOWED_ORIGINS", "").split(","),
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"],
        "expose_headers": ["Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# Constants
TOKEN_EXPIRY = int(os.getenv('TOKEN_EXPIRY_HOURS', 24))
REFRESH_TOKEN_EXPIRY = int(os.getenv('REFRESH_TOKEN_EXPIRY_DAYS', 30))
MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
LOGIN_ATTEMPT_TIMEOUT = int(os.getenv('LOGIN_ATTEMPT_TIMEOUT', 15)) # minutes
PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 8))

class UserSchema(Schema):
    username = fields.Str(required=True, validate=[validate.Length(min=3, max=30), validate.Regexp(r'^[\w\-]+$')])
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=[
        validate.Length(min=PASSWORD_MIN_LENGTH),
        validate.Regexp(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$')
    ])
    phone_contact = fields.Str(required=False, validate=validate.Regexp(r'^\+?1?\d{9,15}$'))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

def generate_tokens(user_id: int) -> Dict[str, str]:
    """Generate access and refresh tokens and store session in cache."""
    try:
        now = datetime.now(timezone.utc)
        access_expiration = now + timedelta(hours=TOKEN_EXPIRY)
        refresh_expiration = now + timedelta(days=REFRESH_TOKEN_EXPIRY)

        access_token = jwt.encode(
            {'id': user_id, 'exp': access_expiration, 'iat': now, 'type': 'access'},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )

        refresh_token = jwt.encode(
            {'id': user_id, 'exp': refresh_expiration, 'iat': now, 'type': 'refresh'},
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )

        # Store session in cache with expiration matching the access token
        cache.set(f'session_{user_id}', {'access': access_token, 'refresh': refresh_token}, timeout=TOKEN_EXPIRY * 3600)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    except Exception as e:
        logger.error(f"Token generation error for user {user_id}: {str(e)}")
        raise

def verify_session(session_token: str) -> Tuple[bool, str]:
    """Verify if the session token is valid."""
    try:
        decoded = jwt.decode(
            session_token,
            current_app.config['SECRET_KEY'],
            algorithms=["HS256"]
        )
        user_id = decoded['id']

        cached_session = cache.get(f'session_{user_id}')
        if cached_session and cached_session.get('access') == session_token:
            return True, "Session is valid"
        return False, "Invalid session"
    except jwt.ExpiredSignatureError:
        return False, "Expired session"
    except jwt.InvalidTokenError:
        return False, "Invalid token"

@bp.route('/api/auth/verify', methods=['GET'])
def verify() -> Tuple[Dict[str, Any], int]:
    """Endpoint to verify session validity."""
    token = request.headers.get('Authorization', '').split(" ")[-1]
    if not token:
        token = request.cookies.get('session')

    if not token:
        return jsonify({'message': 'Token is missing!'}), 401

    valid, message = verify_session(token)
    if valid:
        return jsonify({'valid': True}), 200
    return jsonify({'valid': False, 'message': message}), 401

@bp.route('/api/auth/signup', methods=['POST'])
def signup() -> Tuple[Dict[str, Any], int]:
    try:
        data = request.get_json() or {}

        errors = UserSchema().validate(data)
        if errors:
            return jsonify({'errors': errors}), 400

        if User.query.filter(User.email.ilike(data['email'])).first():
            return jsonify({'message': 'Email already exists'}), 400

        if User.query.filter(User.username.ilike(data['username'])).first():
            return jsonify({'message': 'Username already exists'}), 400

        new_user = User(
            username=data['username'],
            email=data['email'],
            phone_contact=data.get('phone_contact')
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'user': {
                'id': str(new_user.id),
                'name': new_user.username,
                'email': new_user.email,
                'phone_contact': new_user.phone_contact
            }
        }), 201
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Registration failed'}), 500

@bp.route('/api/auth/login', methods=['POST'])
def login() -> Tuple[Dict[str, Any], int]:
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        errors = LoginSchema().validate(data)
        if errors:
            return jsonify({'errors': errors}), 400

        email = data['email'].lower()

        user = User.query.filter(User.email.ilike(email)).first()
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Invalid credentials'}), 401

        if not user.is_active:
            return jsonify({'message': 'Account is disabled'}), 403

        tokens = generate_tokens(user.id)
        logger.info(f"Successful login: {email}")

        response = jsonify({
            'tokens': tokens,
            'user': {
                'id': str(user.id),
                'name': user.username,
                'email': user.email,
                'phone_contact': user.phone_contact
            }
        })
        response.set_cookie(
            'session',
            tokens['access_token'],
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=TOKEN_EXPIRY * 3600
        )
        return response, 200
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed'}), 500

@bp.route('/api/auth/logout', methods=['POST'])
def logout() -> Tuple[Dict[str, str], int]:
    try:
        token = request.headers.get('Authorization', '').split(" ")[-1]
        if not token:
            token = request.cookies.get('session')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        decoded = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=["HS256"]
        )
        user_id = decoded['id']

        # Clear session from Redis
        cache.delete(f'session_{user_id}')
        return jsonify({'message': 'Successfully logged out'}), 200
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'message': 'Logout failed'}), 500

@bp.route('/api/auth/session', methods=['GET'])
def session() -> Tuple[Dict[str, Any], int]:
    """Handle Next.js session requests with compatibility layer"""
    token = request.headers.get('Authorization', '').split(" ")[-1]

    if not token:
        token = request.cookies.get('session')

    if not token:
        return jsonify({'user': None}), 200

    try:
        data = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=["HS256"]
        )

        if data.get('type') != 'access':
            return jsonify({'user': None}), 200

        user_id = data['id']
        user = User.query.get(user_id)

        if not user or not user.is_active:
            return jsonify({'user': None}), 200

        return jsonify({
            'user': {
                'id': str(user.id),
                'name': user.username,
                'email': user.email
            }
        }), 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return jsonify({'user': None}), 200
    except Exception as e:
        logger.error(f"Session error: {str(e)}")
        return jsonify({'user': None}), 200

@bp.route('/api/auth/_log', methods=['POST'])
def auth_log() -> Tuple[Dict[str, bool], int]:
    """Handle Next.js auth logging requests with compatibility layer"""
    try:
        data = request.get_json()
        if data and 'type' in data:
            logger.info(f"Auth event: {data['type']}")
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Auth log error: {str(e)}")
        return jsonify({'success': False}), 200
