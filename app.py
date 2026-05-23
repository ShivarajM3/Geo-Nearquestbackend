import os
from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import Blueprints
from routes.auth import auth_bp
from routes.preferences import preferences_bp
from routes.history import history_bp
from routes.recommendations import recommendations_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # ─── Configuration ────────────────────────────────────────────────────────
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret-for-dev-only")
    
    # Enable session lifetime setting (e.g. 7 days)
    app.permanent_session_lifetime = timedelta(days=7)
    
    # Configure CORS origins dynamically (allowing local Vitetdev servers and Vercel URL)
    frontend_origins = [
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ]
    env_origins = os.environ.get("FRONTEND_URL")
    if env_origins:
        for origin in env_origins.split(","):
            frontend_origins.append(origin.strip().rstrip("/"))
            
    CORS(
        app, 
        resources={r"/api/*": {"origins": frontend_origins}},
        supports_credentials=True
    )
    
    # Session Cookie Security for Production (Cross-Origin session cookies)
    is_prod = os.environ.get("FLASK_ENV") == "production" or os.environ.get("RENDER") == "true"
    if is_prod:
        app.config.update(
            SESSION_COOKIE_SAMESITE="None",
            SESSION_COOKIE_SECURE=True
        )
    
    # ─── Register Blueprints ──────────────────────────────────────────────────
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(preferences_bp, url_prefix="/api/preferences")
    app.register_blueprint(history_bp, url_prefix="/api/history")
    app.register_blueprint(recommendations_bp, url_prefix="/api/recommendations")
    
    # Health Check API
    @app.route("/api/health", methods=["GET"])
    def health_check():
        from database import is_supabase_configured
        return jsonify({
            "status": "healthy",
            "database": "Supabase PostgreSQL" if is_supabase_configured else "Local SQLite Fallback",
            "message": "Geo-Nearquest Backend API is online!"
        }), 200

    # Global Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"error": "Internal server error"}), 500
        
    return app

app = create_app()

if __name__ == "__main__":
    # Bind to host 0.0.0.0 and dynamic port for hosting providers like Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=(os.environ.get("FLASK_ENV") != "production"))
