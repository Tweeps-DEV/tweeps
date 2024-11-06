# backend/tests/test_order.py
import unittest
from backend.app import create_app
from backend.models.order import Order

class TestOrder(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_order_creation(self):
        order = Order(items=['item1', 'item2'])
        self.assertEqual(len(order.items), 2)

    def test_empty_order_items(self):
        order = Order(items=[])
        self.assertEqual(len(order.items), 0)

    def test_unique_order_id(self):
        order1 = Order(items=['item1'])
        order2 = Order(items=['item2'])
        self.assertNotEqual(order1.id, order2.id)

if __name__ == '__main__':
    unittest.main()