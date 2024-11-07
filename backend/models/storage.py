# backend/models/storage.py
from backend.models.base import db

class Storage(db.Model):
    __tablename__ = 'storage'
    id = db.Column(db.Integer, primary_key=True)
    # Add other columns here

def save(obj):
    db.session.add(obj)
    db.session.commit()

def delete(obj):
    db.session.delete(obj)
    db.session.commit()