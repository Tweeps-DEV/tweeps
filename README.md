# Tweeps Fastfoods Backend Unit Tests

## Description

Tests are important to prevent breaking the production environment. This document covers the creation of unit tests for the backend services of Tweeps Fastfoods. These tests ensure that individual components behave as expected, including the core models (like Orders, Users, and BaseModel). This helps maintain code quality by validating that each function, method, and class performs according to the expected logic.

## Steps Taken

1. **Set Up Testing Environment**:
    - Created a virtual environment and installed necessary packages:
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      pip install Flask pytest pytest-mock coverage
      ```

2. **Created Test Directory**:
    - Created a directory for tests:
      ```bash
      mkdir backend/tests
      ```

3. **Wrote Unit Tests for BaseModel**:
    - Created `backend/tests/test_base_model.py` and wrote tests for `BaseModel`.

4. **Wrote Unit Tests for Orders Model**:
    - Created `backend/tests/test_order.py` and wrote tests for `Order`.

5. **Wrote Unit Tests for User Model**:
    - Created `backend/tests/test_user.py` and wrote tests for `User`.

6. **Wrote Unit Tests for Auth Route**:
    - Created `backend/tests/test_auth.py` and wrote tests for authentication routes.

7. **Ran Tests with Coverage**:
    - Ran the tests and generated a coverage report:
      ```bash
      coverage run -m pytest backend/tests/
      coverage report -m
      ```

## Acceptance Criteria

- Unit tests cover all core models and their key methods.
- All tests must pass with appropriate assertions to verify correctness.
- Mock any external dependencies to ensure the unit tests remain isolated.
- Ensure 100% unit test coverage of critical logic.

## Commenting Conventions

- **Test Cases**: Use descriptive comments at the start of each test to explain what it validates.
- **Edge Case Handling**: Use `# Edge Case` comments to highlight special scenarios tested.
- **Mocked Dependencies**: Mock services or external dependencies to isolate the logic.

## Example

```python
# Test that save() method correctly stores the instance
def test_save_method(self):
  obj = BaseModel()
  obj.save()
  self.assertIn(obj, models.storage.all().values())

# Edge Case: Test creating an order with an empty item list
def test_empty_order_items(self):
  order = Orders(items=[])
  self.assertEqual(len(order.items), 0)

@patch("models.storage.save")
def test_save_calls_storage(self, mock_save):
  obj = BaseModel()
  obj.save()
  mock_save.assert_called_once()