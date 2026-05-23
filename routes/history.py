from flask import Blueprint, request, jsonify, session
from database import db_get_history, db_save_history, db_clear_history

history_bp = Blueprint("history", __name__)

@history_bp.route("", methods=["GET"])
def get_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    history = db_get_history(user_id)
    return jsonify(history), 200

@history_bp.route("", methods=["POST"])
def save_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json() or {}
    query_text = data.get("query_text")

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    saved = db_save_history(user_id, query_text)
    if not saved:
        return jsonify({"error": "Failed to save history log"}), 500

    return jsonify({
        "message": "Search history logged",
        "search": saved
    }), 201

@history_bp.route("", methods=["DELETE"])
def clear_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401

    success = db_clear_history(user_id)
    if not success:
        return jsonify({"error": "Failed to clear search history"}), 500

    return jsonify({"message": "Search history cleared successfully"}), 200
