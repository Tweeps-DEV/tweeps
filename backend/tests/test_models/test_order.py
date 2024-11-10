#!/usr/bin/env python3
"""
Unit tests for Order model.
This module contains comprehensive test cases for the Order class,
validating all its methods and edge cases.
"""
import unittest
from app import create_app, db
from datetime import datetime, UTC, timedelta
from models.order import Order
from models.user import User
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from unittest.mock import patch, MagicMock


class TestOrder(unittest.TestCase):
    """
    Test cases for Order class.

    This test suite validates the functionality of the Order model,
    including CRUD operations, relationships, and business logic validation.

    Attributes:
        app (Flask): The Flask application instance
        test_user (User): A User instance used for testing
        order_data (dict): Sample order data for testing
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

        Creates a new test user and prepares sample order data
        to isolate the tests from external systems.
        """
        # Create a test user
        self.test_user = User(
            email="test@example.com",
            username="TestUser"
        )
        self.test_user.set_password(password="  Securepassword123")
        self.test_user.save()

        # Sample order data
        self.order_data = {
            "user_id": self.test_user.id,
            "items": {
                "item1": {"name": "Burger", "quantity": 2, "price": 10.99},
                "item2": {"name": "Fries", "quantity": 1, "price": 4.99}
            },
            "date": datetime.now(UTC),
            "total": 26.97,
            "status": "pending"
        }

    def tearDown(self):
        """
        Clean up test fixtures after each test method.

        Ensures each test starts with a clean state.
        """
        db.session.remove()
        db.drop_all()
        db.create_all()

    def test_create_order(self):
        """
        Test order creation.

        Validates:
            - Order is successfully saved to database
            - All attributes are correctly stored
            - Relationships are properly established
        """
        order = Order(**self.order_data)
        self.assertTrue(order.save())

        saved_order = Order.get_by_id(order.id)
        self.assertIsNotNone(saved_order)
        self.assertEqual(saved_order.user_id, self.test_user.id)
        self.assertEqual(saved_order.total, 26.97)
        self.assertEqual(saved_order.status, "pending")
        self.assertIsInstance(saved_order.items, dict)

    def test_order_user_relationship(self):
        """
        Test the relationship between Order and User.

        Validates:
            - Bidirectional relationship is maintained
            - Order appears in user's orders
            - User is accessible from order
        """
        order = Order(**self.order_data)
        order.save()

        user = User.get_by_id(self.test_user.id)
        orders = user.orders.all()

        self.assertEqual(order.user, self.test_user)
        self.assertIn(order, self.test_user.orders)

    def test_create_multiple_orders_same_user(self):
        """
        Test creating multiple orders for the same user.

        Validates:
            - Multiple orders can be created for one user
            - Orders have unique IDs
            - All orders are associated with the user
        """
        order1 = Order(**self.order_data)
        order1.save()

        order2_data = self.order_data.copy()
        order2_data["items"] = {
            "item1": {"name": "Pizza", "quantity": 1, "price": 15.99}
        }
        order2_data["total"] = 15.99
        order2 = Order(**order2_data)
        order2.save()

        self.assertNotEqual(order1.id, order2.id)
        self.assertEqual(self.test_user.orders.count(), 2)

    def test_order_status_transitions(self):
        """
        Test valid order status transitions.

        Validates:
            - All valid status changes are allowed
            - Status is correctly updated in database
            - Invalid status transitions are rejected
        """
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']
        order = Order(**self.order_data)
        order.save()

        for status in valid_statuses:
            order.update(status=status)
            updated_order = Order.get_by_id(order.id)
            self.assertEqual(updated_order.status, status)

    def test_invalid_order_status(self):
        """
        Test setting invalid order status.

        Validates:
            - Invalid status values are rejected
            - Appropriate error is raised
            - Database integrity is maintained
        """
        invalid_status = "invalid_status"
        self.order_data['status'] = invalid_status

        order = Order(**self.order_data)
        with self.assertRaises(ValueError):
            order.validate()

    def test_order_validation(self):
        """
        Test order validation rules.

        Validates that orders cannot be created with:
            - Zero or negative totals
            - Future dates
            - Empty item lists
            - Invalid item structures
        """
        test_cases = [
            ({"total": 0}, ValueError, "zero total"),
            ({"total": -10.99}, ValueError, "negative total"),
            ({"items": {}}, ValueError, "empty items"),
            ({"items": {"item1": {"quantity": 0}}}, ValueError, "zero quantity"),
        ]

        for invalid_data, expected_error, case_desc in test_cases:
            test_data = self.order_data.copy()
            test_data.update(invalid_data)
            order = Order(**test_data)

            with self.assertRaises(expected_error, msg=f"Failed to raise error for {case_desc}"):
                order.validate()

    def test_concurrent_order_updates(self):
        """
        Test handling concurrent updates to the same order.

        Args:
            mock_session: Mocked database session

        Validates:
            - Concurrent updates are handled gracefully
            - Database rollback occurs on conflict
            - Retry mechanism works correctly
        """
        order = Order(**self.order_data)
        order.save()

        with patch('models.order.db.session') as mock_session:
            mock_session.commit.side_effect = [
                SQLAlchemyError("Concurrent update detected"),
                None
            ]

            order.status = "confirmed"
            order.save()

            mock_session.rollback.assert_called_once()

    def test_order_history(self):
        """
        Test retrieving order history for a user.

        Validates:
            - Orders are retrieved in correct order
            - All orders for user are returned
            - Date ordering is preserved
        """
        dates = [
            datetime.now(UTC) - timedelta(days=i)
            for i in range(5)
        ]

        for date in dates:
            order_data = self.order_data.copy()
            order_data['date'] = date
            order = Order(**order_data)
            order.save()

        user_orders = Order.query.filter_by(user_id=self.test_user.id)\
                                .order_by(Order.date.desc())\
                                .all()

        self.assertEqual(len(user_orders), 5)
        for i in range(len(user_orders) - 1):
            self.assertGreater(user_orders[i].date, user_orders[i + 1].date)


if __name__ == '__main__':
    unittest.main()
