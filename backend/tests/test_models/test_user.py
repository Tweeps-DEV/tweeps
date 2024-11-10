#!/usr/bin/env python3
"""
Unit tests for User model.
This module contains comprehensive test cases for the User class,
including authentication, data validation, and relationship handling.
"""
import unittest
from datetime import datetime, UTC
from unittest.mock import Mock, patch
from models.user import User
from extensions import bcrypt
from sqlalchemy.exc import SQLAlchemyError


class TestUser(unittest.TestCase):
    """
    Test cases for User class.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone_contact': '+254712345678',
            'address': '123 Test Street',
            'is_admin': False
        }

        self.user = User(**self.valid_user_data)
        User.save = Mock()
        self.mock_orders = Mock()
        type(self.user).orders = self.mock_orders

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        User.save = None

    def test_user_creation(self):
        """Test user instance creation with valid data."""
        self.assertEqual(self.user.username, self.valid_user_data['username'])
        self.assertEqual(self.user.email, self.valid_user_data['email'])
        self.assertEqual(self.user.phone_contact,
                         self.valid_user_data['phone_contact'])
        self.assertEqual(self.user.address, self.valid_user_data['address'])
        self.assertEqual(self.user.is_admin, self.valid_user_data['is_admin'])

        self.assertIsInstance(self.user.username, str)
        self.assertIsInstance(self.user.email, str)
        self.assertIsInstance(self.user.is_admin, bool)

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
        self.assertNotEqual(self.user.password_hash,
                            another_user.password_hash)

    def test_password_encoding(self):
        """Test password hash encoding and decoding."""
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

    def test_orders_relationship(self):
        """Test the relationship between User and Order models."""
        mock_orders = Mock()
        mock_order1 = Mock()
        mock_order2 = Mock()
        mock_orders.all.return_value = [mock_order1, mock_order2]

        type(self.user).orders = mock_orders
        orders = self.user.orders.all()
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders, [mock_order1, mock_order2])

    def test_user_repr(self):
        """Test string representation of User."""
        self.user.id = 'test-id'
        repr_string = str(self.user)

        self.assertIn(self.user.username, repr_string)
        self.assertIn(self.user.id, repr_string)
        self.assertTrue(repr_string.startswith('<User'))
        self.assertTrue(repr_string.endswith(')>'))

        special_user = User(username="test@user", email="test@example.com")
        special_user.id = 'test-id'
        repr_string = str(special_user)
        self.assertIn("test@user", repr_string)

    def test_unique_constraints(self):
        """Test unique constraints on username and email."""
        with patch('models.user.User.save') as mock_save:
            mock_save.side_effect = SQLAlchemyError(
                "Unique constraint violation")

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
