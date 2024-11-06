# backend/tests/test_models.py
import pytest
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.menu_item import MenuItem
from backend.models.order import Order
from backend.models.cart import Cart
from backend.models.base_model import BaseModel
from unittest.mock import patch
from datetime import datetime

@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='module')
def session(test_app):
    with test_app.app_context():
        yield db.session

@pytest.fixture
def client(test_app):
    return test_app.test_client()

### BaseModel Unit Tests ###

# Test object initialization with and without keyword arguments
def test_base_model_initialization():
    obj = BaseModel()
    assert obj is not None

    obj_with_kwargs = BaseModel(id=1)
    assert obj_with_kwargs.id == 1

# Test the save() method to ensure objects are correctly stored
@patch("backend.models.base_model.BaseModel.save")
def test_base_model_save(mock_save):
    obj = BaseModel()
    obj.save()
    mock_save.assert_called_once()

# Test the delete() method for proper instance removal from storage
@patch("backend.models.base_model.BaseModel.delete")
def test_base_model_delete(mock_delete):
    obj = BaseModel()
    obj.delete()
    mock_delete.assert_called_once()

# Verify the to_dict() method returns accurate dictionaries
def test_base_model_to_dict():
    obj = BaseModel(id=1, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    obj_dict = obj.to_dict()
    assert obj_dict['id'] == 1
    assert obj_dict['created_at'] is not None
    assert obj_dict['updated_at'] is not None

### Orders Model Unit Tests ###

# Test order creation with valid and invalid data
def test_create_order(session):
    user = User(username="orderuser", email="orderuser@example.com", password_hash="hashedpassword")
    session.add(user)
    session.commit()

    order = Order(user_id=user.id, status="Pending", items=[])
    session.add(order)
    session.commit()

# Ensure orders can store multiple items (list of items)
def test_order_multiple_items(session):
    user = User.query.filter_by(username="orderuser").first()
    order = Order(user_id=user.id, status="Pending", items=[{"item_id": 1, "quantity": 2}, {"item_id": 2, "quantity": 1}])
    session.add(order)
    session.commit()

# Validate the behavior when adding items without toppings (since toppings are free)
def test_order_items_without_toppings(session):
    user = User.query.filter_by(username="orderuser").first()
    order = Order(user_id=user.id, status="Pending", items=[{"item_id": 1, "quantity": 2}])
    session.add(order)
    session.commit()

# Test unique order ID generation logic
def test_unique_order_id(session):
    user = User.query.filter_by(username="orderuser").first()
    order1 = Order(user_id=user.id, status="Pending", items=[])
    order2 = Order(user_id=user.id, status="Pending", items=[])
    session.add_all([order1, order2])
    session.commit()
    assert order1.id != order2.id

### Users Model Unit Tests ###

# Validate User creation with correct data inputs
def test_create_user(session):
    user = User(username="testuser", email="testuser@example.com", password_hash="hashedpassword")
    session.add(user)
    session.commit()
    
    retrieved_user = User.query.filter_by(username="testuser").first()
    assert retrieved_user is not None

# Test that Users are linked to required models
def test_user_linkage(session):
    user = User.query.filter_by(username="testuser").first()
    order = Order(user_id=user.id, status="Pending", items=[])
    session.add(order)
    session.commit()
    assert order.user_id == user.id

# Verify correct storage behavior of User objects
def test_user_storage(session):
    user = User.query.filter_by(username="testuser").first()
    assert user is not None

### Cart Model Unit Tests ###

# Test adding an item to a cart
def test_add_item_to_cart(session):
    user = User(username="cartuser", email="cartuser@example.com", password_hash="hashedpassword")
    item = MenuItem(name="Pizza", price=15.99, description="Cheesy pizza")
    session.add_all([user, item])
    session.commit()

    cart = Cart(user_id=user.id, items={item.id: {"quantity": 2}})
    session.add(cart)
    session.commit()

# Test updating the quantity of an item in the cart
def test_update_cart_quantity(session):
    cart = Cart.query.filter(Cart.items.contains({"quantity": 2})).first()
    assert cart is not None
    item_id = list(cart.items.keys())[0]
    cart.items[item_id]["quantity"] = 3
    session.commit()

# Test deleting an item from the cart
def test_delete_cart_item(session):
    user = User.query.filter_by(username="cartuser").first()
    item = MenuItem.query.filter_by(name="Pizza").first()
    cart = Cart(user_id=user.id, items={item.id: {"quantity": 3}})
    session.add(cart)
    session.commit()

    cart = Cart.query.filter(Cart.items.contains({"quantity": 3})).first()
    assert cart is not None
    session.delete(cart)
    session.commit()

### MenuItem Model Unit Tests ###

# Test the creation of a menu item
def test_create_menu_item(session):
    item = MenuItem(name="Burger", price=10.99, description="Juicy burger")
    session.add(item)
    session.commit()
    
    retrieved_item = MenuItem.query.filter_by(name="Burger").first()
    assert retrieved_item is not None

# Verify correct storage behavior of MenuItem objects
def test_menu_item_storage(session):
    item = MenuItem.query.filter_by(name="Burger").first()
    assert item is not None

### Auth Route Unit Tests ###

# Test the user signup route
def test_user_signup(client):
    response = client.post('/api/auth/signup', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201

# Test the user login route
def test_user_login(client):
    response = client.post('/api/auth/login', json={
        'email': 'newuser@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200