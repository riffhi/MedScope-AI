from flask import Blueprint, request, jsonify, g
from passlib.context import CryptContext
from datetime import timedelta
from app.core.config import settings
from app.models import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.api.dependencies import create_access_token, login_required
from app.core.database import db

auth_bp = Blueprint('auth', __name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    user_data = UserCreate(**request.get_json())

    existing_user = db.session.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()

    if existing_user:
        return jsonify({"detail": "User with this email or username already exists"}), 400

    hashed_password = pwd_context.hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role
    )

    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)

    return jsonify(UserResponse.from_orm(user).dict())

@auth_bp.route("/login", methods=["POST"])
def login():
    """Login user and return access token"""
    form_data = request.form
    user = db.session.query(User).filter(
        (User.email == form_data['username']) | (User.username == form_data['username'])
    ).first()

    if not user or not pwd_context.verify(form_data['password'], user.hashed_password):
        return jsonify({"detail": "Incorrect email/username or password"}), 401

    if not user.is_active:
        return jsonify({"detail": "Inactive user"}), 401

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    user.last_login = user.updated_at
    db.session.commit()

    return jsonify(Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    ).dict())

@auth_bp.route("/me", methods=["GET"])
@login_required
def get_current_user_info():
    """Get current user information"""
    return jsonify(UserResponse.from_orm(g.current_user).dict())

@auth_bp.route("/refresh", methods=["POST"])
@login_required
def refresh_token():
    """Refresh access token"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": g.current_user.email}, expires_delta=access_token_expires
    )

    return jsonify(Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    ).dict())