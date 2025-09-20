from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

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

# Set SQLAlchemy to use PyMySQL for MySQL connections
import sqlalchemy as sa
from sqlalchemy import create_engine
sa.dialects.registry.register("mysql", "pymysql", "pymysql.dialects.mysql")

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
