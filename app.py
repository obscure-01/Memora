"""
Memora Flask Backend Server Entry Point.

Usage:
    python app.py

Starts the Flask development server on http://127.0.0.1:5000.
"""

from src.api.app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 60)
    print("  Starting Memora Flask API Backend")
    print("  Server running on http://127.0.0.1:5000")
    print("  Endpoints:")
    print("    GET  http://127.0.0.1:5000/api/health")
    print("    POST http://127.0.0.1:5000/api/simulate")
    print("    POST http://127.0.0.1:5000/api/compare")
    print("    POST http://127.0.0.1:5000/api/cpu/schedule")
    print("    POST http://127.0.0.1:5000/api/deadlock/safety")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)
