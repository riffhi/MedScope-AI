from flask import request, g
from jose import JWTError, jwt
from functools import wraps
from datetime import datetime, timedelta
from app.core.config import settings
from app.models import User
from app.schemas.user import TokenData
from app.core.database import db

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def get_current_user():
    """Get current authenticated user from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        token_data = TokenData(email=email)
    except JWTError:
        return None

    user = db.session.query(User).filter(User.email == token_data.email).first()
    return user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.current_user = get_current_user()
        if g.current_user is None:
            return {"message": "Unauthorized"}, 401
        return f(*args, **kwargs)
    return decorated_function