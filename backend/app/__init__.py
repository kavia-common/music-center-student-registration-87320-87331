from flask import Flask, request
from flask_cors import CORS
from flask_smorest import Api
import logging

from .routes.health import blp as health_blp
from .routes.students import blp as students_blp
from .models import db, build_mysql_uri_from_env_or_file

app = Flask(__name__)
app.url_map.strict_slashes = False

# Enable CORS for all routes, allowing frontend to call the API
CORS(app, resources={r"/*": {"origins": "*"}})

# OpenAPI / Swagger configuration
app.config["API_TITLE"] = "Music Center Registration API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Database configuration (SQLAlchemy URI built from env or db_connection.txt)
app.config["SQLALCHEMY_DATABASE_URI"] = build_mysql_uri_from_env_or_file()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 280, "pool_pre_ping": True}

# Import PyMySQL and register it with MySQLdb name for SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.before_request
def log_request_info():
    logger.info('Request Headers: %s', dict(request.headers))
    logger.info('Request URL: %s %s', request.method, request.full_path)
    if request.is_json:
        logger.info('Request Body: %s', request.get_json())

# Initialize extensions
api = Api(app)
db.init_app(app)

# Register blueprints
api.register_blueprint(health_blp)
api.register_blueprint(students_blp)

# Create tables if they don't exist.
# In production, prefer migrations. For this demo, create_all is acceptable.
with app.app_context():
    db.create_all()
