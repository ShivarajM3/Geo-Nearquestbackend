from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import db_register_user, db_get_user_by_email, db_get_user_by_id

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    hashed_pw = generate_password_hash(password)
    user = db_register_user(name, email, hashed_pw)

    if not user:
        return jsonify({"error": "Email address already registered"}), 409

    return jsonify({
        "message": "User registered successfully",
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"]
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = db_get_user_by_email(email)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = user["user_id"]
    session.permanent = True  # Respect session lifetime parameters

    return jsonify({
        "message": "Login successful",
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"]
    }), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    session.pop("user_id", None)
    return jsonify({"message": "Logout successful"}), 200

@auth_bp.route("/me", methods=["GET"])
def get_me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    user = db_get_user_by_id(user_id)
    if not user:
        session.pop("user_id", None)  # Clean stale session
        return jsonify({"error": "User not found"}), 401

    return jsonify({
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"]
    }), 200
