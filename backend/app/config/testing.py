import os

from .base import BaseConfig


class TestingConfig(BaseConfig):
    ENV_NAME = "testing"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
