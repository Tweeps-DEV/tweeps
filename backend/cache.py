#!/usr/bin/env python3
"""Implements caching functionality using Redis"""
from functools import wraps
from redis import Redis
import json
from typing import Any, Optional, Union, Callable
import pickle

class Cache:
    """Redis cache wrapper with advanced features"""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        """Initialize Redis connection with fallback handling"""
        try:
            self._redis = Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,  # Automatically decode responses to strings
                socket_timeout=2,  # Add timeout to prevent hanging
                retry_on_timeout=True  # Auto-retry on timeout
            )
            self._redis.ping()  # Test connection
        except Exception as e:
            print(f"Warning: Redis connection failed - {str(e)}")
            self._redis = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with type preservation"""
        if not self._redis:
            return None

        try:
            value = self._redis.get(key)
            if value is None:
                return None

            # Try to decode JSON first
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # If not JSON, try to decode pickle
                try:
                    return pickle.loads(value.encode())
                except:
                    # If all else fails, return raw value
                    return value
        except Exception as e:
            print(f"Cache get error for key {key}: {str(e)}")
            return None

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache with automatic serialization"""
        if not self._redis:
            return False

        try:
            # Try to encode as JSON first
            try:
                encoded_value = json.dumps(value)
            except (TypeError, ValueError):
                # If JSON encoding fails, use pickle
                encoded_value = pickle.dumps(value).decode()

            return self._redis.set(key, encoded_value, ex=timeout)
        except Exception as e:
            print(f"Cache set error for key {key}: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._redis:
            return False

        try:
            return bool(self._redis.delete(key))
        except Exception as e:
            print(f"Cache delete error for key {key}: {str(e)}")
            return False

    def incr(self, key: str) -> Optional[int]:
        """Increment value"""
        if not self._redis:
            return None

        try:
            return self._redis.incr(key)
        except Exception as e:
            print(f"Cache increment error for key {key}: {str(e)}")
            return None

    def decr(self, key: str) -> Optional[int]:
        """Decrement value"""
        if not self._redis:
            return None

        try:
            return self._redis.decr(key)
        except Exception as e:
            print(f"Cache decrement error for key {key}: {str(e)}")
            return None

    def flush(self) -> bool:
        """Clear all keys from the current database"""
        if not self._redis:
            return False

        try:
            return self._redis.flushdb()
        except Exception as e:
            print(f"Cache flush error: {str(e)}")
            return False

def cached(timeout: int = 300):
    """Decorator for caching function results"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Generate a cache key based on function name and arguments
            key = f"cache_{f.__name__}_{str(args)}_{str(kwargs)}"

            # Try to get cached result
            result = cache.get(key)
            if result is not None:
                return result

            # If no cached result, execute function
            result = f(*args, **kwargs)

            # Cache the result
            cache.set(key, result, timeout=timeout)
            return result
        return wrapper
    return decorator

# Initialize global cache instance
cache = Cache()
