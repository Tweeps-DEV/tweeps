# Project Tweeps - Test Report

## Overview

This document provides a detailed report of the tests conducted for the Project Tweeps application. It includes the status of the application, the tests performed, and best practices for maintaining and writing tests.

## Application State

The Project Tweeps application is a web-based platform that allows users to manage orders, menu items, and carts. The application is built using Flask and SQLAlchemy, and it includes models for users, menu items, orders, and carts.

## Tests Conducted

### Test Setup

The tests are written using the `pytest` framework and are located in the `backend/tests` directory. The tests use fixtures to set up the application and database for testing.

#### Fixtures

- `test_app`: Sets up the Flask application for testing.
- `session`: Provides a database session for testing.
- `client`: Provides a Flask test client for testing routes.

### Test Cases

#### BaseModel Unit Tests

- **Test Object Initialization**: Tests object initialization with and without keyword arguments.
- **Test Save Method**: Tests the `save()` method to ensure objects are correctly stored.
- **Test Delete Method**: Tests the `delete()` method for proper instance removal from storage.
- **Test to_dict Method**: Verifies the `to_dict()` method returns accurate dictionaries.

#### Orders Model Unit Tests

- **Test Order Creation**: Tests order creation with valid and invalid data.
- **Test Multiple Items**: Ensures orders can store multiple items (list of items).
- **Test Adding Items Without Toppings**: Validates the behavior when adding items without toppings (since toppings are free).
- **Test Unique Order ID Generation**: Tests unique order ID generation logic.

#### Users Model Unit Tests

- **Test User Creation**: Validates User creation with correct data inputs.
- **Test User Linkage**: Tests that Users are linked to required models.
- **Test User Storage**: Verifies correct storage behavior of User objects.

#### Cart Model Unit Tests

- **Test Add Item to Cart**: Tests adding an item to a cart.
- **Test Update Cart Quantity**: Tests updating the quantity of an item in the cart.
- **Test Delete Cart Item**: Tests deleting an item from the cart.

#### MenuItem Model Unit Tests

- **Test MenuItem Creation**: Tests the creation of a menu item.
- **Test MenuItem Storage**: Verifies correct storage behavior of MenuItem objects.

#### Auth Route Unit Tests

- **Test User Signup**: Tests the user signup route.
- **Test User Login**: Tests the user login route.

### Test Log

The following is an excerpt from the `pytest.log` file, which contains the log for the tests conducted:

```log
========================================== test session starts ===========================================
platform linux -- Python 3.10.12, pytest-8.3.3, pluggy-1.5.0
rootdir: /home/ivan/project/tweeps
plugins: mock-3.14.0
collected 18 items                                                                                        

backend/tests/test_models.py::test_create_order PASSED                                             [  5%]
backend/tests/test_models.py::test_update_order_status PASSED                                      [ 11%]
backend/tests/test_models.py::test_delete_order PASSED                                             [ 16%]
backend/tests/test_models.py::test_add_item_to_cart PASSED                                         [ 22%]
backend/tests/test_models.py::test_update_cart_quantity PASSED                                     [ 27%]
backend/tests/test_models.py::test_delete_cart_item PASSED                                         [ 33%]
backend/tests/test_models.py::test_base_model_initialization PASSED                                [ 38%]
backend/tests/test_models.py::test_base_model_save PASSED                                          [ 44%]
backend/tests/test_models.py::test_base_model_delete PASSED                                        [ 50%]
backend/tests/test_models.py::test_base_model_to_dict PASSED                                       [ 55%]
backend/tests/test_models.py::test_order_multiple_items PASSED                                     [ 61%]
backend/tests/test_models.py::test_order_items_without_toppings PASSED                             [ 66%]
backend/tests/test_models.py::test_unique_order_id PASSED                                          [ 72%]
backend/tests/test_models.py::test_create_user PASSED                                              [ 77%]
backend/tests/test_models.py::test_user_linkage PASSED                                             [ 83%]
backend/tests/test_models.py::test_user_storage PASSED                                             [ 88%]
backend/tests/test_models.py::test_create_menu_item PASSED                                         [ 94%]
backend/tests/test_models.py::test_menu_item_storage PASSED                                        [100%]

============================================ warnings summary ============================================
backend/tests/test_models.py::test_create_order
  /home/ivan/project/tweeps/.venv/lib/python3.10/site-packages/flask_limiter/extension.py:333: UserWarning: Using the in-memory storage for tracking rate limits as no storage was explicitly specified. This is not recommended for production use. See: https://flask-limiter.readthedocs.io#configuring-a-storage-backend for documentation about configuring the storage backend.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
===================================== 18 passed, 1 warning in 3.09s ======================================