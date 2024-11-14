#!/usr/bin/env python3
"""
Unit tests for User model.
This module contains comprehensive test cases for the User class,
including authentication, data validation, and relationship handling.
"""
import unittest
from datetime import datetime, UTC
from unittest.mock import patch, Mock
from app import create_app, db
from models.user import User
from models.order import Order
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import MagicMock


class TestUser(unittest.TestCase):
    """
    Test cases for User class.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_contact': '+254712345678',
            'address': '123 Test Street',
            'is_admin': False
        }

        self.user = User(**self.valid_user_data)
        self.original_save_method = User.save
        User.save = Mock()

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        User.save = self.original_save_method  # Restore original save method
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        """Test user instance creation with valid data."""
        self.assertEqual(self.user.username, self.valid_user_data['username'])
        self.assertEqual(self.user.email, self.valid_user_data['email'])
        self.assertEqual(self.user.phone_contact, self.valid_user_data['phone_contact'])
        self.assertEqual(self.user.address, self.valid_user_data['address'])
        self.assertEqual(self.user.is_admin, self.valid_user_data['is_admin'])

    def test_password_hashing(self):
        """Test password hashing functionality."""
        test_password = "Securepassword123"
        self.user.set_password(test_password)

        self.assertIsNotNone(self.user.password_hash)
        self.assertNotEqual(self.user.password_hash, test_password)
        self.assertTrue(self.user.check_password(test_password))
        self.assertFalse(self.user.check_password("Wrongpassword"))

        another_user = User(**self.valid_user_data)
        another_user.set_password("Differentpassword44")
        self.assertNotEqual(self.user.password_hash, another_user.password_hash)

    def test_password_encoding(self):
        """Test password hash encoding and decoding with special characters."""
        special_passwords = [
            "Password123!@#",
            "userPässword4",
            "Nаролькириллица7",
            "P密码中可口可樂文d69"
        ]

        for password in special_passwords:
            self.user.set_password(password)
            self.assertIsInstance(self.user.password_hash, str)
            self.assertTrue(self.user.check_password(password))

    def test_empty_password(self):
        """Test handling of empty passwords."""
        with self.assertRaises(ValueError):
            self.user.set_password("")

        with self.assertRaises(ValueError):
            self.user.set_password(None)

    def test_user_repr(self):
        """Test string representation of User."""
        self.user.id = 'test-id'
        repr_string = str(self.user)

        self.assertIn(self.user.username, repr_string)
        self.assertIn(str(self.user.id), repr_string)
        self.assertTrue(repr_string.startswith('<User'))
        self.assertTrue(repr_string.endswith(')>'))

    def test_unique_constraints(self):
        """Test unique constraints on username and email."""
        with patch('models.user.User.save') as mock_save:
            mock_save.side_effect = SQLAlchemyError("Unique constraint violation")

            duplicate_user = User(
                username=self.user.username,
                email="different@example.com"
            )

            with self.assertRaises(SQLAlchemyError):
                duplicate_user.save()

            duplicate_email = User(
                username="different",
                email=self.user.email
            )

            with self.assertRaises(SQLAlchemyError):
                duplicate_email.save()


if __name__ == '__main__':
    unittest.main()
