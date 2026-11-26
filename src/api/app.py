"""
Flask Application Factory for Memora.

Initializes the Flask app, registers blueprints, configures CORS,
and establishes consistent JSON error handlers.
"""

import os
from flask import Flask, jsonify, request, render_template
from src.api.routes import api_bp

try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False


def create_app(test_config=None):
    """
    Create and configure the Flask application.

    Args:
        test_config (dict, optional): Configuration dictionary for testing.

    Returns:
        Flask: Configured Flask application instance.
    """
    # Configure template and static directories relative to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    template_dir = os.path.join(project_root, "templates")
    static_dir = os.path.join(project_root, "static")

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
        static_url_path="/static",
    )

    # Default configuration
    app.config["JSON_SORT_KEYS"] = False

    if test_config:
        app.config.update(test_config)

    # Enable Cross-Origin Resource Sharing (CORS) for future frontend integration
    if HAS_CORS:
        CORS(app)
    else:
        @app.after_request
        def add_cors_headers(response):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
            return response

    # Register API blueprint under /api
    app.register_blueprint(api_bp, url_prefix="/api")

    # Root route: serves interactive HTML frontend to browsers, JSON API info to API clients
    @app.route("/", methods=["GET"])
    def index():
        accept = request.headers.get("Accept", "")
        if "text/html" in accept:
            return render_template("index.html")
        return jsonify({
            "application": "Memora",
            "version": "1.0.0",
            "description": "Virtual Memory Simulator for Page Replacement Algorithm Analysis",
            "endpoints": [
                {"method": "GET",  "path": "/api/health",   "description": "Health check"},
                {"method": "POST", "path": "/api/simulate", "description": "Run single algorithm"},
                {"method": "POST", "path": "/api/compare",  "description": "Compare all algorithms"},
            ],
        }), 200

    @app.route("/dashboard", methods=["GET"])
    @app.route("/index.html", methods=["GET"])
    def dashboard():
        return render_template("index.html")

    # Consistent HTTP error handlers
    @app.errorhandler(400)
    def bad_request(error):
        details = getattr(error, "description", "Bad request.")
        return jsonify({
            "error": {
                "message": "Bad request",
                "details": details,
            }
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        details = getattr(error, "description", "The requested resource was not found on the server.")
        return jsonify({
            "error": {
                "message": "Resource not found",
                "details": details,
            }
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        details = getattr(error, "description", "The method is not allowed for the requested URL.")
        return jsonify({
            "error": {
                "message": "Method not allowed",
                "details": details,
            }
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {error}")
        return jsonify({
            "error": {
                "message": "Internal server error",
                "details": "An unexpected server error occurred.",
            }
        }), 500

    return app
