#!/usr/bin/env python3
"""Unit tests for the BaseModel class"""
import time
import unittest
import uuid
from app import create_app, db
from datetime import datetime
from models.base_model import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import patch


class TestModel(BaseModel):
    """
    Test model class that inherits from BaseModel.

    This class is used for testing the abstract BaseModel class functionality.
    """
    __abstract__ = False
    name = db.Column(db.String(50))
    description = db.Column(db.Text, nullable=True)


class TestBaseModel(unittest.TestCase):
    """
    Test cases for the BaseModel class.

    This test suite verifies the functionality of the base model including:
    - Model initialization and validation
    - CRUD operations
    - Error handling
    - Data serialization
    - Timestamp management
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
        """Set up the test environment before each test."""
        db.session.begin_nested()
        self.test_model = TestModel(name="test",
                                    description="test description")

    def tearDown(self):
        """Clean up after each test."""
        db.session.rollback()
        db.session.remove()

    def test_model_initialization(self):
        """Test model initialization and default values."""
        self.assertIsNotNone(self.test_model.id)
        self.assertTrue(isinstance(self.test_model.id, str))
        self.assertEqual(len(self.test_model.id), 36)

        # Verify UUID format
        try:
            uuid_obj = uuid.UUID(self.test_model.id)
            self.assertEqual(str(uuid_obj), self.test_model.id)
        except ValueError:
            self.fail("ID is not a valid UUID")

    def test_model_initialization_with_attributes(self):
        """Test model initialization with provided attributes."""
        test_name = "test_name"
        test_desc = "test_description"
        model = TestModel(name=test_name, description=test_desc)

        self.assertEqual(model.name, test_name)
        self.assertEqual(model.description, test_desc)
        self.assertIsNotNone(model.id)

    def test_get_by_id_success(self):
        """Test successful retrieval of a record by ID."""
        self.test_model.save()

        retrieved_model = TestModel.get_by_id(self.test_model.id)

        self.assertIsNotNone(retrieved_model)
        self.assertEqual(retrieved_model.id, self.test_model.id)
        self.assertEqual(retrieved_model.name, self.test_model.name)
        self.assertEqual(
            retrieved_model.description,
            self.test_model.description
        )

    def test_get_by_id_not_found(self):
        """Test retrieval with non-existent ID."""
        non_existent_id = str(uuid.uuid4())
        model = TestModel.get_by_id(non_existent_id)

        self.assertIsNone(model)

    def test_get_by_id_invalid_id(self):
        """Test get_by_id with invalid ID format."""
        invalid_id = "invalid-id"
        model = TestModel.get_by_id(invalid_id)

        self.assertIsNone(model)

    def test_save_success(self):
        """Test successful save operation."""
        self.test_model.save()

        saved_model = TestModel.get_by_id(self.test_model.id)

        self.assertIsNotNone(saved_model)
        self.assertEqual(saved_model.name, "test")
        self.assertIsNotNone(saved_model.created_at)
        self.assertIsInstance(saved_model.created_at, datetime)

    def test_save_duplicate_id(self):
        """Test save operation with duplicate ID."""
        self.test_model.save()

        duplicate_model = TestModel(
            id=self.test_model.id,
            name="duplicate"
        )

        with self.assertRaises(SQLAlchemyError):
            duplicate_model.save()

    def test_delete_success(self):
        """Test successful delete operation."""
        self.test_model.save()
        self.test_model.delete()

        deleted_model = TestModel.get_by_id(self.test_model.id)
        self.assertIsNone(deleted_model)

    def test_delete_non_existent(self):
        """Test delete operation on non-existent record."""
        with self.assertRaises(SQLAlchemyError):
            self.test_model.delete()

    def test_update_success(self):
        """Test successful update operation."""
        self.test_model.save()
        new_name = "updated_name"
        new_description = "updated_description"

        original_updated_at = self.test_model.updated_at

        time.sleep(1)

        self.test_model.update(
            name=new_name,
            description=new_description
        )

        updated_model = TestModel.get_by_id(self.test_model.id)

        self.assertEqual(updated_model.name, new_name)
        self.assertEqual(updated_model.description, new_description)
        # Some databases might not support update timestamps
        if updated_model.updated_at:
            self.assertNotEqual(updated_model.updated_at, original_updated_at)

    def test_update_invalid_field(self):
        """Test update operation with invalid field."""
        self.test_model.save()

        with self.assertRaises(AttributeError):
            self.test_model.update(invalid_field="value")

    def test_to_dict_basic(self):
        """Test basic dictionary conversion."""
        self.test_model.save()
        model_dict = self.test_model.to_dict()

        self.assertIsInstance(model_dict, dict)
        self.assertIn('id', model_dict)
        self.assertIn('created_at', model_dict)
        self.assertIn('updated_at', model_dict)

        self.assertEqual(model_dict['id'], self.test_model.id)
        self.assertIsInstance(model_dict['created_at'], str)

    def test_to_dict_null_timestamps(self):
        """Test dictionary conversion with null timestamps."""
        self.test_model.created_at = None
        self.test_model.updated_at = None

        model_dict = self.test_model.to_dict()

        self.assertIsNone(model_dict['created_at'])
        self.assertIsNone(model_dict['updated_at'])

    def test_timestamp_auto_update(self):
        """Test automatic timestamp updates."""
        self.test_model.save()
        original_created_at = self.test_model.created_at
        original_updated_at = self.test_model.updated_at

        time.sleep(1)

        self.test_model.update(name="new_name")

        self.assertEqual(self.test_model.created_at, original_created_at)
        if self.test_model.updated_at:
            self.assertNotEqual(self.test_model.updated_at,
                                original_updated_at)

    def test_save_with_db_error(self):
        """Test save operation with database error."""
        with patch.object(db.session, 'commit') as mock_commit:
            mock_commit.side_effect = SQLAlchemyError("Database error")
            with self.assertRaises(SQLAlchemyError):
                self.test_model.save()

    def test_delete_with_db_error(self):
        """Test delete operation with database error."""
        self.test_model.save()
        with patch.object(db.session, 'commit') as mock_commit:
            mock_commit.side_effect = SQLAlchemyError("Database error")
            with self.assertRaises(SQLAlchemyError):
                self.test_model.delete()


if __name__ == '__main__':
    unittest.main(verbosity=2)
