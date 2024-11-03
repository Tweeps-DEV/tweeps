# backend/models/storage.py
from backend.extensions import db

def save(obj):
    db.session.add(obj)
    db.session.commit()

def delete(obj):
    db.session.delete(obj)
    db.session.commit()