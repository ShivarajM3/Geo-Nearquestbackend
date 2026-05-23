from flask import Blueprint, request, jsonify, session
from database import db_get_recommendations, db_save_recommendation

recommendations_bp = Blueprint("recommendations", __name__)

@recommendations_bp.route("", methods=["GET"])
def get_recommendations():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    recs = db_get_recommendations(user_id)
    return jsonify(recs), 200

@recommendations_bp.route("", methods=["POST"])
def save_recommendation():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json() or {}
    place_name = data.get("place_name")
    category = data.get("category", "General")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    rating = data.get("rating")
    mood = data.get("mood")

    if not place_name or latitude is None or longitude is None or not mood:
        return jsonify({"error": "Missing required fields (place_name, latitude, longitude, mood)"}), 400

    # Ensure coordinates are floats
    try:
        latitude = float(latitude)
        longitude = float(longitude)
        if rating is not None:
            rating = float(rating)
    except ValueError:
        return jsonify({"error": "Latitude, longitude, and rating must be numeric"}), 400

    saved = db_save_recommendation(user_id, place_name, category, latitude, longitude, rating, mood)
    if not saved:
        return jsonify({"error": "Failed to save recommendation"}), 500

    return jsonify({
        "message": "Recommendation saved successfully",
        "recommendation": saved
    }), 201
