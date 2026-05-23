from flask import Blueprint, request, jsonify, session
from database import db_get_preferences, db_save_preferences

preferences_bp = Blueprint("preferences", __name__)

@preferences_bp.route("", methods=["GET"])
def get_preferences():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    prefs = db_get_preferences(user_id)
    return jsonify(prefs), 200

@preferences_bp.route("", methods=["POST"])
def save_preferences():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json() or {}
    mood = data.get("mood", "")
    purpose = data.get("purpose", "")

    saved = db_save_preferences(user_id, mood, purpose)
    if not saved:
        return jsonify({"error": "Failed to save preferences"}), 500

    return jsonify({
        "message": "Preferences saved successfully",
        "mood": mood,
        "purpose": purpose
    }), 200
