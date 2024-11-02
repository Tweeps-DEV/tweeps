# backend/tests/test_base_model.py
import unittest
from backend.models.base_model import BaseModel
from unittest.mock import patch

class TestBaseModel(unittest.TestCase):

    def test_initialization(self):
        obj = BaseModel()
        self.assertIsInstance(obj, BaseModel)

    def test_save_method(self):
        obj = BaseModel()
        with patch('backend.models.storage.save') as mock_save:
            obj.save()
            mock_save.assert_called_once()

    def test_delete_method(self):
        obj = BaseModel()
        with patch('backend.models.storage.delete') as mock_delete:
            obj.delete()
            mock_delete.assert_called_once()

    def test_to_dict_method(self):
        obj = BaseModel()
        obj_dict = obj.to_dict()
        self.assertIsInstance(obj_dict, dict)

if __name__ == '__main__':
    unittest.main()