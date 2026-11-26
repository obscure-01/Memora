"""
Memora REST API Package.

Provides Flask-based HTTP endpoints wrapping the virtual memory simulation engine.
"""

from src.api.app import create_app

__all__ = ["create_app"]
