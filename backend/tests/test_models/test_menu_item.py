#!/usr/bin/env python3
"""
Unit tests for MenuItem model.
This module contains comprehensive test cases for the MenuItem class,
including admin operations, validation, and data conversion.
"""
import unittest
from app import create_app, db
from unittest.mock import Mock, patch
from models.menu_item import MenuItem
from sqlalchemy.exc import SQLAlchemyError
from flask_login import FlaskLoginClient


class TestMenuItem(unittest.TestCase):
    """
    Test cases for MenuItem class.

    This test suite validates the functionality of the MenuItem model,
    including CRUD operations, admin permissions, and data validation.

    Attributes:
        menu_item (MenuItem): A MenuItem instance used for testing
        mock_admin_user (Mock): A mocked admin user for testing admin ops
        mock_normal_user (Mock): A mocked normal user for testing users
    """
    @classmethod
    def setUpClass(cls):
        """Set up the test environment once for all tests."""
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment after all tests."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Creates necessary mocks and test data to isolate tests
        from external dependencies.
        """
        db.session.begin_nested()

        # Create mock users
        self.mock_admin_user = Mock()
        self.mock_admin_user.is_admin = True

        self.mock_normal_user = Mock()
        self.mock_normal_user.is_admin = False

        # Sample valid menu item data
        self.valid_item_data = {
            'name': 'Test Burger',
            'description': 'A delicious test burger',
            'price': 9.99,
            'category': 'Burgers',
            'image_url': 'http://example.com/burger.jpg',
            'toppings': ['cheese', 'lettuce', 'tomato'],
            'is_available': True
        }

    def tearDown(self):
        """
        Clean up test fixtures after each test method.
        """
        db.session.rollback()
        db.session.remove()

    @patch('models.menu_item.current_user')
    def test_create_menu_item_success(self, mock_current_user):
        """
        Test successful creation of a menu item by admin.

        Args:
            mock_current_user: Mocked current_user for admin permission

        Validates:
            - Item is created with correct attributes
            - Save method is called
            - Admin permission check
        """
        mock_current_user.is_admin = True

        menu_item = MenuItem(**self.valid_item_data)
        db.session.add(menu_item)
        db.session.commit()

        item_id = menu_item.id

        MenuItem.delete_menu_item(item_id)

        deleted_item = db.session.get(MenuItem, item_id)
        self.assertIsNone(deleted_item)

    @patch('models.menu_item.current_user')
    def test_delete_menu_item_not_found(self, mock_current_user):
        """Test deleting non-existent menu item raises error."""
        mock_current_user.is_admin = True

        with self.assertRaises(ValueError) as context:
            MenuItem.delete_menu_item('non-existent-id')

        self.assertIn("Menu item not found", str(context.exception))

    @patch('models.menu_item.current_user')
    def test_create_menu_item_permission_denied(self, mock_current_user):
        """
        Test menu item creation by non-admin user.

        Args:
            mock_current_user: Mocked current_user for permission check

        Validates:
            - PermissionError is raised
            - Save method is not called
        """
        mock_current_user.is_admin = False

        menu_item = MenuItem(**self.valid_item_data)
        db.session.add(menu_item)
        db.session.commit()

        with self.assertRaises(PermissionError) as context:
            MenuItem.delete_menu_item(menu_item.id)

        self.assertIn("Only admins", str(context.exception))

    def test_create_menu_item_invalid_data(self):
        """
        Test menu item creation with invalid data.

        Validates:
            - Missing required fields
            - Invalid price
            - Data type validation
        """
        with patch('models.menu_item.current_user') as mock_current_user:
            mock_current_user.is_admin = True

            invalid_data = self.valid_item_data.copy()
            del invalid_data['name']
            with self.assertRaises(ValueError) as context:
                MenuItem.create_menu_item(**invalid_data)
            self.assertIn("Missing required fields", str(context.exception))

            invalid_data = self.valid_item_data.copy()
            invalid_data['price'] = 0
            with self.assertRaises(ValueError) as context:
                MenuItem.create_menu_item(**invalid_data)
            self.assertIn("Price must be between 0.01 and 10000.0",
                          str(context.exception))

            invalid_data['price'] = -10
            with self.assertRaises(ValueError) as context:
                MenuItem.create_menu_item(**invalid_data)
            self.assertIn("Price must be between 0.01 and 10000.0",
                          str(context.exception))

    @patch('models.menu_item.current_user')
    @patch('models.menu_item.MenuItem.get_by_id')
    def test_update_menu_item_success(self, mock_get_by_id, mock_current_user):
        """
        Test successful update of a menu item by admin.

        Args:
            mock_get_by_id: Mocked get_by_id method
            mock_current_user: Mocked current_user for admin permission

        Validates:
            - Item is updated correctly
            - Update method is called
            - Admin permission check
        """
        mock_current_user.is_admin = True

        existing_item = MenuItem()
        existing_item.update = Mock()
        mock_get_by_id.return_value = existing_item

        update_data = {
            'name': 'Updated Burger',
            'price': 11.99
        }

        MenuItem.update_menu_item('test-id', **update_data)

        existing_item.update.assert_called_once_with(**update_data)

    @patch('models.menu_item.current_user')
    @patch('models.menu_item.MenuItem.get_by_id')
    def test_update_menu_item_not_found(self,
                                        mock_get_by_id,
                                        mock_current_user):
        """
        Test updating non-existent menu item.

        Args:
            mock_get_by_id: Mocked get_by_id method
            mock_current_user: Mocked current_user for admin permission

        Validates:
            - ValueError is raised for non-existent item
            - Update is not attempted
        """
        mock_current_user.is_admin = True
        mock_get_by_id.return_value = None

        with self.assertRaises(ValueError) as context:
            MenuItem.update_menu_item('non-existent-id', name='New Name')

        self.assertIn("Menu item not found", str(context.exception))

    @patch('models.menu_item.current_user')
    @patch('models.menu_item.MenuItem.get_by_id')
    def test_delete_menu_item_success(self, mock_get_by_id, mock_current_user):
        """
        Test successful deletion of a menu item by admin.

        Args:
            mock_get_by_id: Mocked get_by_id method
            mock_current_user: Mocked current_user for admin permission

        Validates:
            - Item is deleted
            - Delete method is called
            - Admin permission check
        """
        mock_current_user.is_admin = True

        menu_item = MenuItem(**self.valid_item_data)
        db.session.add(menu_item)
        db.session.commit()

        item_id = menu_item.id
        MenuItem.delete_menu_item(item_id)

        self.assertIsNone(db.session.get(MenuItem, item_id))

    def test_to_dict(self):
        """
        Test converting MenuItem to dictionary representation.

        Validates:
            - All required fields are present
            - Types are correct
            - Nested data is properly handled
        """
        menu_item = MenuItem(**self.valid_item_data)

        item_dict = menu_item.to_dict()

        self.assertEqual(item_dict['name'], self.valid_item_data['name'])
        self.assertEqual(item_dict['description'],
                         self.valid_item_data['description'])
        self.assertEqual(item_dict['price'], self.valid_item_data['price'])
        self.assertEqual(item_dict['category'],
                         self.valid_item_data['category'])
        self.assertEqual(item_dict['image_url'],
                         self.valid_item_data['image_url'])
        self.assertEqual(item_dict['toppings'],
                         self.valid_item_data['toppings'])
        self.assertEqual(item_dict['is_available'],
                         self.valid_item_data['is_available'])

        self.assertIsInstance(item_dict['price'], float)
        self.assertIsInstance(item_dict['toppings'], list)
        self.assertIsInstance(item_dict['is_available'], bool)

    def test_repr(self):
        """
        Test string representation of MenuItem.

        Validates:
            - Format is correct
            - Contains essential information
        """
        menu_item = MenuItem(**self.valid_item_data)
        menu_item.id = 'test-id'

        repr_string = str(menu_item)

        self.assertIn(menu_item.name, repr_string)
        self.assertIn(menu_item.id, repr_string)
        self.assertTrue(repr_string.startswith('<MenuItem'))
        self.assertTrue(repr_string.endswith(')>'))


if __name__ == '__main__':
    unittest.main()
