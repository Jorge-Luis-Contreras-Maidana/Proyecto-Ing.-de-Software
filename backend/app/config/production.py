from .base import BaseConfig


class ProductionConfig(BaseConfig):
    ENV_NAME = "production"
    DEBUG = False