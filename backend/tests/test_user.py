# backend/tests/test_user.py
import unittest
from backend.app import create_app
from backend.models.user import User

class TestUser(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_user_creation(self):
        user = User(username='testuser', email='test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')

    def test_user_storage(self):
        user = User(username='testuser', email='test@example.com')
        user.save()
        self.assertIsNotNone(user.id)

if __name__ == '__main__':
    unittest.main()