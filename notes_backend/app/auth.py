import os
import datetime
import hashlib
import hmac
import jwt
from flask import request, abort, g
from app.models import User

def hash_password(password: str) -> str:
    """Hash the password with a simple salted SHA256 hashing."""
    salt = os.getenv('SECRET_KEY', 'somesalt')
    pwd_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return pwd_hash

def check_password(hash: str, password: str) -> bool:
    """Check if password matches hash."""
    return hmac.compare_digest(hash, hash_password(password))

def generate_token(user_id: int):
    """Generate JWT for a user."""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3)
    }
    token = jwt.encode(payload, os.getenv('JWT_SECRET', 'change_me'), algorithm='HS256')
    return token

def verify_token(token: str):
    """Verify JWT and return payload."""
    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET', 'change_me'), algorithms=['HS256'])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

# PUBLIC_INTERFACE
def get_current_user():
    """Get current user from JWT in Authorization header."""
    auth_hdr = request.headers.get('Authorization')
    if not auth_hdr or not auth_hdr.startswith('Bearer '):
        abort(401, description="Missing or invalid Authorization header.")
    token = auth_hdr.split(' ', 1)[1]
    payload = verify_token(token)
    if not payload:
        abort(401, description="Invalid or expired token.")
    user = User.query.get(payload['user_id'])
    if not user:
        abort(401, description="User not found.")
    g.current_user = user
    return user
