#!/usr/bin/env python3
"""Defines auth routes"""
import jwt
import logging
import os
from app import db, cache
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from extensions import limiter
from flask import Blueprint, request, jsonify, current_app
from flask_cors import CORS
from functools import wraps
from logging.handlers import RotatingFileHandler
from marshmallow import Schema, fields, validate, ValidationError
from models.user import User
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

# Configure CORS with more specific settings
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
LOGIN_ATTEMPT_TIMEOUT = int(os.getenv('LOGIN_ATTEMPT_TIMEOUT', 15))  # minutes
PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 8))

class UserSchema(Schema):
    """Schema for user registration validation with enhanced security rules"""
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=30),
            validate.Regexp(
                r'^[\w\-]+$',
                error='Username can only contain letters, numbers, underscores, and hyphens'
            )
        ]
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=PASSWORD_MIN_LENGTH),
            validate.Regexp(
                r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
                error='Password must contain at least one letter, one number, and one special character'
            )
        ]
    )
    phone_contact = fields.Str(
        required=False,
        validate=validate.Regexp(
            r'^\+?1?\d{9,15}$',
            error='Invalid phone number format'
        )
    )

class LoginSchema(Schema):
    """Schema for login validation"""
    email = fields.Email(required=True)
    password = fields.Str(required=True)

def generate_tokens(user_id: int) -> Dict[str, str]:
    """Generate secure access and refresh tokens with rate limiting"""
    try:
        active_tokens = cache.get(f'user_tokens_{user_id}') or 0
        if active_tokens > 5:  # Limit concurrent sessions
            raise ValueError('Too many active sessions')

        now = datetime.now(timezone.utc)
        access_expiration = now + timedelta(hours=TOKEN_EXPIRY)
        refresh_expiration = now + timedelta(days=REFRESH_TOKEN_EXPIRY)

        access_token = jwt.encode(
            {
                'id': user_id,
                'exp': access_expiration,
                'iat': now,
                'type': 'access'
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )

        refresh_token = jwt.encode(
            {
                'id': user_id,
                'exp': refresh_expiration,
                'iat': now,
                'type': 'refresh'
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )

        cache.incr(f'user_tokens_{user_id}')

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    except Exception as e:
        logger.error(f"Token generation error for user {user_id}: {str(e)}")
        raise

def token_required(f):
    """Enhanced token verification decorator with additional security checks"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').split(" ")[-1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            if cache.get(f'blacklisted_token_{token}'):
                raise jwt.InvalidTokenError('Token has been revoked')

            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )

            if data.get('type') != 'access':
                raise jwt.InvalidTokenError('Invalid token type')

            current_user = User.query.filter_by(id=data['id']).first()
            if not current_user:
                raise jwt.InvalidTokenError('User not found')

            if not current_user.is_active:
                raise jwt.InvalidTokenError('User account is disabled')

            rate_limit_key = f'rate_limit_{current_user.id}'
            if cache.get(rate_limit_key):
                raise jwt.InvalidTokenError('Too many requests')
            cache.set(rate_limit_key, 1, timeout=1)  # 1 request per second per user

            return f(current_user, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'message': str(e)}), 401
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return jsonify({'message': 'Authentication failed'}), 500

    return decorated

def check_login_attempts(email: str) -> bool:
    """Check if user has exceeded maximum login attempts"""
    key = f'login_attempts_{email}'
    attempts = cache.get(key) or 0
    return attempts >= MAX_LOGIN_ATTEMPTS

def record_login_attempt(email: str, success: bool) -> None:
    """Record login attempt and handle rate limiting"""
    key = f'login_attempts_{email}'
    if success:
        cache.delete(key)
    else:
        attempts = cache.get(key) or 0
        cache.set(key, attempts + 1, timeout=LOGIN_ATTEMPT_TIMEOUT * 60)

@bp.route('/api/auth/signup', methods=['POST'])
@limiter.limit("5 per minute")
def signup() -> Tuple[Dict[str, Any], int]:
    """Production-grade signup endpoint with enhanced security"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        if 'phone' in data:
            data['phone_contact'] = data.pop('phone')

        errors = UserSchema().validate(data)
        if errors:
            return jsonify({'errors': errors}), 400

        if User.query.filter(User.email.ilike(data['email'])).first():
            return jsonify({'message': 'Email already exists'}), 400

        if User.query.filter(User.username.ilike(data['username'])).first():
            return jsonify({'message': 'Username already exists'}), 400

        new_user = User(
            username=data['username'].strip(),
            email=data['email'].lower().strip(),
            phone_contact=data.get('phone_contact', '').strip()
        )
        new_user.set_password(data['password'])
        new_user.validate()

        db.session.add(new_user)
        db.session.commit()

        tokens = generate_tokens(new_user.id)

        logger.info(f"New user registered: {new_user.email}")

        return jsonify({
            'tokens': tokens,
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
@limiter.limit("10 per minute")
def login() -> Tuple[Dict[str, Any], int]:
    """Production-grade login endpoint with security features"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        errors = LoginSchema().validate(data)
        if errors:
            return jsonify({'errors': errors}), 400

        email = data['email'].lower().strip()

        if check_login_attempts(email):
            return jsonify({
                'message': f'Too many login attempts. Please try again in {LOGIN_ATTEMPT_TIMEOUT} minutes'
            }), 429

        user = User.query.filter(User.email.ilike(email)).first()
        if not user or not user.check_password(data['password']):
            record_login_attempt(email, False)
            return jsonify({'message': 'Invalid credentials'}), 401

        if not user.is_active:
            return jsonify({'message': 'Account is disabled'}), 403

        tokens = generate_tokens(user.id)

        record_login_attempt(email, True)
        logger.info(f"Successful login: {email}")

        return jsonify({
            'tokens': tokens,
            'user': {
                'id': str(user.id),
                'name': user.username,
                'email': user.email,
            }
        }), 200

    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed'}), 500

@bp.route('/api/auth/logout', methods=['POST'])
@token_required
def logout(current_user) -> Tuple[Dict[str, str], int]:
    """Production-grade logout endpoint with token invalidation"""
    try:
        token = request.headers.get('Authorization', '').split(" ")[-1]

        cache.set(
            f'blacklisted_token_{token}',
            1,
            timeout=TOKEN_EXPIRY * 3600
        )

        cache.decr(f'user_tokens_{current_user.id}')

        logger.info(f"User logged out: {current_user.email}")
        return jsonify({'message': 'Successfully logged out'}), 200

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'message': 'Logout failed'}), 500

@bp.route('/api/auth/refresh', methods=['POST'])
def refresh_token() -> Tuple[Dict[str, Any], int]:
    """Endpoint to refresh access token using refresh token"""
    try:
        refresh_token = request.headers.get('Authorization', '').split(" ")[-1]
        if not refresh_token:
            return jsonify({'message': 'Refresh token is missing'}), 401

        if cache.get(f'blacklisted_token_{refresh_token}'):
            return jsonify({'message': 'Refresh token has been revoked'}), 401

        data = jwt.decode(
            refresh_token,
            current_app.config['SECRET_KEY'],
            algorithms=["HS256"]
        )

        if data.get('type') != 'refresh':
            return jsonify({'message': 'Invalid token type'}), 401

        user_id = data['id']
        new_tokens = generate_tokens(user_id)

        cache.set(
            f'blacklisted_token_{refresh_token}',
            1,
            timeout=REFRESH_TOKEN_EXPIRY * 86400
        )

        return jsonify({'tokens': new_tokens}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Refresh token has expired'}), 401
    except jwt.InvalidTokenError as e:
        return jsonify({'message': str(e)}), 401
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({'message': 'Token refresh failed'}), 500

@bp.route('/api/auth/verify', methods=['GET'])
@token_required
def verify_auth(current_user) -> Tuple[Dict[str, Any], int]:
    """Verify user authentication and return user details

    This endpoint uses the @token_required decorator to verify the access token
    and returns the current user's details if authentication is successful.

    Returns:
        tuple: Contains user details dictionary and HTTP status code
    """
    try:
        return jsonify({
            'user': {
                'id': str(current_user.id),
                'name': current_user.username,
                'email': current_user.email
            }
        }), 200
    except Exception as e:
        logger.error(f"Auth verification error: {str(e)}")
        return jsonify({'message': 'Verification failed'}), 500
