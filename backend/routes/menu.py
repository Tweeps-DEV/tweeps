from flask import Blueprint, jsonify, request
from backend.models.menu_item import MenuItem
from backend.extensions import db

bp = Blueprint('menu', __name__)

@bp.route('/api/menu', methods=['GET'])
def get_menu():
    deal_of_the_day = MenuItem.get_deal_of_the_day()
    menu_items = MenuItem.get_menu_items()
    return jsonify({
        'dealOfTheDay': deal_of_the_day,
        'menuItems': menu_items
    })

@bp.route('/api/categories', methods=['GET'])
def get_categories():
    categories = [
        {'id': '1', 'name': 'Deal of the Day'},
        {'id': '2', 'name': 'Popular Picks'},
        {'id': '3', 'name': 'New Arrivals'},
        {'id': '4', 'name': "Chef's Favorites"},
    ]
    return jsonify({'categories': categories})

@bp.route('/api/admin/deal', methods=['POST'])
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