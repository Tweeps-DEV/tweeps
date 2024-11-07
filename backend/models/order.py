from backend.base import db

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_items = db.relationship('OrderItem', backref='parent_order', lazy=True)

    def __repr__(self):
        return f'<Order {self.id}>'