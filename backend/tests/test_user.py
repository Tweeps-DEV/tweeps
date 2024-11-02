# backend/tests/test_user.py
import unittest
from backend.models.user import User
from unittest.mock import patch

class TestUser(unittest.TestCase):

    def test_user_creation(self):
        user = User(username='testuser', email='test@example.com')
        self.assertEqual(user.username, 'testuser')

    def test_user_storage(self):
        user = User(username='testuser', email='test@example.com')
        with patch('backend.models.storage.save') as mock_save:
            user.save()
            mock_save.assert_called_once()

if __name__ == '__main__':
    unittest.main()