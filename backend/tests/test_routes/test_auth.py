#!/usr/bin/env python3
"""Unit tests for authentication routes"""
import json
import jwt
import unittest
from app import create_app, db
from datetime import datetime, timedelta, UTC
from flask import current_app
from unittest.mock import patch, MagicMock
from models.user import User
from routes.auth import token_required


class TestAuthRoutes(unittest.TestCase):
    """Test cases for authentication routes"""

    def setUp(self):
        """Set up test client and test database"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Test user data
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123'
        }
        self.invalid_user_data = {
            'username': 'te',  # Too short
            'email': 'invalid-email',
            'password': 'short'  # Too short
        }

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_signup_success(self):
        """Test successful user signup"""
        response = self.client.post(
            '/api/auth/signup',
            data=json.dumps(self.valid_user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            json.loads(response.data)['message'],
            'New user created!'
        )

    def test_signup_invalid_data(self):
        """Test signup with invalid data"""
        response = self.client.post(
            '/api/auth/signup',
            data=json.dumps(self.invalid_user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_signup_duplicate_email(self):
        """Test signup with existing email"""
        response = self.client.post(
            '/api/auth/signup',
            data=json.dumps(self.valid_user_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)

        response = self.client.post(
            '/api/auth/signup',
            data=json.dumps(self.valid_user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.data)['message'],
            'Email already exists'
        )

    def test_login_success(self):
        """Test successful login"""
        signup_response = self.client.post(
            '/api/auth/signup',
            data=json.dumps(self.valid_user_data),
            content_type='application/json'
        )

        login_data = {
            'email': self.valid_user_data['email'],
            'password': self.valid_user_data['password']
        }
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('token', json.loads(response.data))

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'wrong@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data)['message'],
            'Invalid credentials!'
        )

    def test_token_required_decorator(self):
        """Test the token_required decorator"""
        @self.app.route('/api/protected')
        @token_required
        def protected_route(current_user):
            return jsonify({'message': 'Access granted'})

        response = self.client.get('/api/protected')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data)['message'],
            'Token is missing!'
        )

        response = self.client.get(
            '/api/protected',
            headers={'Authorization': 'Bearer invalid-token'}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data)['message'],
            'Invalid token!'
        )

        expired_token = jwt.encode(
            {
                'user_id': 1,
                'exp': datetime.now(UTC) - timedelta(hours=1)
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        response = self.client.get(
            '/api/protected',
            headers={'Authorization': f'Bearer {expired_token}'}
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.data)['message'],
            'Token has expired!'
        )


if __name__ == '__main__':
    unittest.main()
