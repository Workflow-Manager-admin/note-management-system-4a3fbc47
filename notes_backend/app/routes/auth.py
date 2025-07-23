from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import request

from app.auth import hash_password, check_password, generate_token
from app.models import User, db

blp = Blueprint("Auth", "auth", url_prefix="/auth", description="User authentication routes")

# PUBLIC_INTERFACE
@blp.route("/signup")
class Signup(MethodView):
    """Endpoint for user registration."""
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            abort(400, message="Username and password are required.")
        if User.query.filter_by(username=username).first():
            abort(409, message="Username already exists.")
        user = User(username=username, password_hash=hash_password(password))
        db.session.add(user)
        db.session.commit()
        return {"message": "User created successfully."}, 201

# PUBLIC_INTERFACE
@blp.route("/login")
class Login(MethodView):
    """Endpoint for user login and token retrieval."""
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        if not user or not check_password(user.password_hash, password):
            abort(401, message="Invalid credentials.")
        token = generate_token(user.id)
        return {"token": token}
