from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    ENV_NAME = "development"
    DEBUG = True
