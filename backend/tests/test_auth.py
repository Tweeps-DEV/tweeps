# backend/tests/test_auth.py
import unittest
from backend.app import app
from unittest.mock import patch

class TestAuth(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_signup(self):
        response = self.app.post('/api/auth/signup', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        response = self.app.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()