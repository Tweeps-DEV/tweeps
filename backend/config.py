#!/usr/bin/env python3
"""Defines the config for the backend"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Base configuration class.

    This class contains configuration settings common to all environments.

    Attributes:
        SECRET_KEY (str): The secret key for the application.
        SQLALCHEMY_DATABASE_URI (str): The URI for the database connection.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Flag to track modifications.
        ALLOWED_ORIGINS (list): List of allowed origins for CORS.

    """
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '').split(',')


class DevelopmentConfig(Config):
    """
    Development configuration.

    This class contains configuration settings
    specific to the development environment.

    Attributes:
        DEBUG (bool): Flag to enable debug mode.

    """
    DEBUG = True


class ProductionConfig(Config):
    """
    Production configuration.

    This class contains configuration settings
    specific to the production environment.

    Attributes:
        DEBUG (bool): Flag to disable debug mode.

    """
    DEBUG = False


class TestingConfig(Config):
    """
    Testing configuration.

    This class contains configuration settings
    specific to the testing environment.

    Attributes:
        TESTING (bool): Flag to enable testing mode.
        SQLALCHEMY_DATABASE_URI (str): The URI for the testing database.

    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
