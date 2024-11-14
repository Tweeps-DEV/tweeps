#!/usr/bin/env python3
"""Initializes application extensions"""
import os
import redis
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
bcrypt = Bcrypt()

pool = redis.connection.BlockingConnectionPool.from_url(REDIS_URL)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=REDIS_URL,
    strategy='fixed-window',
    headers_enabled=True,
    storage_options={'connection_pool': pool},
)
