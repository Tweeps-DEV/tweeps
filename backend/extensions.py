#!/usr/bin/env python3
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

bcrypt = Bcrypt()
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)
