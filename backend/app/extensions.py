from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from app.core.database.base import metadata

db = SQLAlchemy(metadata=metadata)
jwt = JWTManager()
cors = CORS()