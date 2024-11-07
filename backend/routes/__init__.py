from flask import Blueprint, jsonify, request
from backend.models.menu_item import MenuItem
from backend.models.user import User
from backend.extensions import db, bcrypt, limiter
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError

bp = Blueprint('main', __name__)

# User schema for validation
class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=30))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda p: len(p) >= 8)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda p: len(p) >= 8)

# Registration route
@bp.route('/api/auth/signup', methods=['POST'])
@limiter.limit("5 per minute")
def signup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        UserSchema().load(data)

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(username=data['username'], email=data['email'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'New user created!'}), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500

# Login route
@bp.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    try:
        data = request.get_json()
        LoginSchema().load(data)

        user = User.query.filter_by(email=data['email']).first()
        if not user or not bcrypt.check_password_hash(user.password, data['password']):
            return jsonify({'message': 'Invalid credentials!'}), 401

        token = create_access_token(identity=user.id)
        return jsonify({'token': token})
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({'message': 'Something went wrong'}), 500

# Get menu route
@bp.route('/api/menu', methods=['GET'])
@jwt_required()
def get_menu():
    deal_of_the_day = MenuItem.get_deal_of_the_day()
    menu_items = MenuItem.get_menu_items()
    return jsonify({
        'dealOfTheDay': deal_of_the_day,
        'menuItems': menu_items
    })

# Update deal of the day route
@bp.route('/api/admin/deal', methods=['POST'])
@jwt_required()
def update_deal_of_the_day():
    data = request.get_json()
    deal_id = data.get('deal_id')
    MenuItem.query.update({MenuItem.is_deal_of_the_day: False})
    deal_item = MenuItem.query.get(deal_id)
    if deal_item:
        deal_item.is_deal_of_the_day = True
        db.session.commit()
        return jsonify({'message': 'Deal of the Day updated successfully'}), 200
    return jsonify({'error': 'Item not found'}), 404