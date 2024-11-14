#!/usr/bin/env python3
"""
Unit tests for Cart model.
This module contains comprehensive test cases for the Cart class,
validating all its methods and edge cases.
"""
import unittest
from app import create_app, db
from unittest.mock import Mock, patch
from models.cart import Cart
from models.menu_item import MenuItem


class TestCart(unittest.TestCase):
    """
    Test cases for Cart class.

    This test suite validates the functionality of the Cart model,
    including item management, price calculations, and data conversion.

    Attributes:
        cart (Cart): A Cart instance used for testing
        menu_item (Mock): A mocked MenuItem instance for testing
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

        Creates a new Cart instance and mocks necessary dependencies
        to isolate the tests from external systems.
        """
        self.cart = Cart()
        self.cart.user_id = "test-user-123"
        self.cart.save = Mock()

        self.menu_item = Mock(spec=MenuItem)
        self.menu_item.id = "item-123"
        self.menu_item.price = 10.0
        self.menu_item.is_available = True
        self.menu_item.to_dict.return_value = {
            "id": "item-123",
            "name": "Test Item",
            "price": 10.0,
            "description": "Test item description",
            "category": "Test Category",
            "is_available": True
        }

    def tearDown(self):
        """
        Clean up test fixtures after each test method.

        Ensures each test starts with a clean state.
        """
        self.cart = None
        self.menu_item = None

    def test_init(self):
        """
        Test Cart initialization.

        Validates that a new Cart instance is properly initialized
        with empty items and zero total price.
        """
        self.assertEqual(self.cart.items, {})
        self.assertEqual(self.cart.total_price, 0.0)
        self.assertEqual(self.cart.user_id, "test-user-123")
        self.assertIsInstance(self.cart.items, dict)
        self.assertIsInstance(self.cart.total_price, float)

    @patch('models.cart.MenuItem.get_by_id')
    def test_add_item_new(self, mock_get_by_id):
        """
        Test adding a new item to cart.

        Args:
            mock_get_by_id: Mocked MenuItem.get_by_id method

        Validates:
            - Correct quantity is set
            - Total price is updated
            - Save method is called
        """
        mock_get_by_id.return_value = self.menu_item

        self.cart.add_item("item-123", quantity=2)

        self.assertIn("item-123", self.cart.items)
        self.assertEqual(self.cart.items["item-123"]["quantity"], 2)
        self.assertEqual(self.cart.total_price, 20.0)
        self.cart.save.assert_called_once()

    @patch('models.cart.MenuItem.get_by_id')
    def test_add_item_existing(self, mock_get_by_id):
        """
        Test adding an existing item to cart.

        Args:
            mock_get_by_id: Mocked MenuItem.get_by_id method

        Validates:
            - Quantity is properly accumulated
            - Total price is correctly updated
        """
        mock_get_by_id.return_value = self.menu_item

        self.cart.add_item("item-123", quantity=1)
        self.cart.add_item("item-123", quantity=2)

        self.assertEqual(self.cart.items["item-123"]["quantity"], 3)
        self.assertEqual(self.cart.total_price, 30.0)
        self.assertEqual(self.cart.save.call_count, 2)

    @patch('models.cart.MenuItem.get_by_id')
    def test_add_item_with_toppings(self, mock_get_by_id):
        """
        Test adding item with custom toppings.

        Args:
            mock_get_by_id: Mocked MenuItem.get_by_id method

        Validates:
            - Toppings are properly stored
            - Item is added with correct attributes
        """
        self.menu_item.toppings = [
            {"name": "Cheese", "price": 1.0},
            {"name": "Pepperoni", "price": 2.0}
        ]
        mock_get_by_id.return_value = self.menu_item

        toppings = ["Cheese", "Pepperoni"]
        self.cart.add_item("item-123", quantity=1, selected_toppings=toppings)

        self.assertIn("item-123", self.cart.items)
        self.assertEqual(self.cart.items["item-123"]["quantity"], 1)
        self.assertEqual(self.cart.items["item-123"]["toppings"], toppings)

        expected_price = 13.0  # Base price (10.0) + Cheese (1.0) + Pepperoni (2.0)
        self.assertEqual(self.cart.total_price, expected_price)

    @patch('models.cart.MenuItem.get_by_id')
    def test_add_item_invalid_cases(self, mock_get_by_id):
        """
        Test adding items with invalid parameters.

        Args:
            mock_get_by_id: Mocked MenuItem.get_by_id method

        Validates various error cases:
            - Zero quantity
            - Negative quantity
            - Unavailable item
            - Non-existent item
        """
        mock_get_by_id.return_value = self.menu_item

        with self.assertRaises(ValueError) as context:
            self.cart.add_item("item-123", quantity=0)
        self.assertIn("Quantity must be between 1 and 99", str(context.exception))

        with self.assertRaises(ValueError) as context:
            self.cart.add_item("item-123", quantity=-1)
        self.assertIn("Quantity must be between 1 and 99", str(context.exception))

        self.menu_item.is_available = False
        with self.assertRaises(ValueError) as context:
            self.cart.add_item("item-123")
        self.assertIn("not available", str(context.exception))

        mock_get_by_id.return_value = None
        with self.assertRaises(ValueError) as context:
            self.cart.add_item("non-existent")
        self.assertIn("not found", str(context.exception))

    def test_remove_item_variations(self):
        """
        Test all variations of removing items from cart.

        Validates:
            - Complete item removal
            - Partial quantity removal
            - Removing non-existent item
            - Removing with quantity > available
        """
        self.cart.items = {
            "item-123": {"quantity": 3, "toppings": []},
            "item-456": {"quantity": 1, "toppings": ["cheese"]}
        }

        self.cart.remove_item("item-456")
        self.assertNotIn("item-456", self.cart.items)

        self.cart.remove_item("item-123", quantity=2)
        self.assertEqual(self.cart.items["item-123"]["quantity"], 1)

        with self.assertRaises(ValueError) as context:
            self.cart.remove_item("non-existent")
        self.assertIn("Item not in cart", str(context.exception))

    def test_clear_cart(self):
        """
        Test clearing the cart completely.

        Validates:
            - Items are removed
            - Total price is reset
            - Save is called
        """
        self.cart.items = {
            "item-123": {"quantity": 2, "toppings": []},
            "item-456": {"quantity": 1, "toppings": ["cheese"]}
        }
        self.cart.total_price = 30.0

        self.cart.clear()

        self.assertEqual(self.cart.items, {})
        self.assertEqual(self.cart.total_price, 0.0)
        self.cart.save.assert_called_once()

    @patch('models.cart.MenuItem.get_by_id')
    def test_to_dict(self, mock_get_by_id):
        """
        Test converting cart to dictionary representation.

        Args:
            mock_get_by_id: Mocked MenuItem.get_by_id method

        Validates:
            - All required fields are present
            - Nested item information is correct
            - Types are correct
        """
        mock_get_by_id.return_value = self.menu_item
        self.cart.items = {
            "item-123": {
                "quantity": 1,
                "toppings": ["cheese"]
            }
        }
        self.cart.total_price = 10.0

        cart_dict = self.cart.to_dict()

        self.assertIsInstance(cart_dict, dict)
        self.assertEqual(cart_dict["user_id"], "test-user-123")
        self.assertEqual(cart_dict["total_price"], 10.0)
        self.assertIsInstance(cart_dict["items"], dict)

        item_data = cart_dict["items"]["item-123"]
        self.assertEqual(item_data["quantity"], 1)
        self.assertEqual(item_data["toppings"], ["cheese"])
        self.assertEqual(item_data["item"], self.menu_item.to_dict())

    def test_update_total(self):
        """
        Test total price calculation.

        Validates:
            - Correct total calculation with multiple items
            - Handling of missing menu items
            - Precision of float calculations
        """
        with patch('models.cart.MenuItem.get_by_id') as mock_get_by_id:
            item1 = Mock(spec=MenuItem)
            item1.price = 10.0
            item2 = Mock(spec=MenuItem)
            item2.price = 15.0

            mock_get_by_id.side_effect = lambda x: {
                "item-123": item1,
                "item-456": item2
            }.get(x)

            self.cart.items = {
                "item-123": {"quantity": 2, "toppings": []},
                "item-456": {"quantity": 1, "toppings": []},
                "non-existent": {"quantity": 1, "toppings": []}
            }

            self.cart._update_total()

            # 2 * 10.0 + 1 * 15.0 = 35.0
            self.assertEqual(self.cart.total_price, 35.0)


if __name__ == '__main__':
    unittest.main()
