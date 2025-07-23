import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from flask_smorest import Api

load_dotenv()

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuration from .env
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///notes.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "somesalt")
app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "change_me")

# CORS and API docs
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["API_TITLE"] = "Notes Backend API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config['OPENAPI_URL_PREFIX'] = '/docs'
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

from .models import db
from .db_init import init_db
from .routes.health import blp as health_blp
from .routes.auth import blp as auth_blp
from .routes.notes import blp as notes_blp

api = Api(app)
api.register_blueprint(health_blp)
api.register_blueprint(auth_blp)
api.register_blueprint(notes_blp)

init_db(app)
