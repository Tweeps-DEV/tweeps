# backend/tests/test_base_model.py
import unittest
from unittest.mock import patch
from backend.app import create_app
from backend.models.base_model import BaseModel

class TestBaseModel(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_save_method(self):
        obj = BaseModel()
        with patch('backend.models.storage.save') as mock_save:
            obj.save()
            mock_save.assert_called_once_with(obj)

    def test_delete_method(self):
        obj = BaseModel()
        with patch('backend.models.storage.delete') as mock_delete:
            obj.delete()
            mock_delete.assert_called_once_with(obj)

    def test_to_dict_method(self):
        obj = BaseModel()
        obj_dict = obj.to_dict()
        self.assertIn('id', obj_dict)
        self.assertIn('created_at', obj_dict)
        self.assertIn('updated_at', obj_dict)

if __name__ == '__main__':
    unittest.main()