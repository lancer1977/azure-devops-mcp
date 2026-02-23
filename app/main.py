"""Main application entry point."""
import os

from flask import Flask

from .config import get_settings
from .logging_config import setup_logging
from .routes import api_bp


def create_app() -> Flask:
    """Create and configure the Flask application."""
    # Setup logging first
    setup_logging()

    # Create Flask app
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(api_bp)

    return app


# Create the app instance
app = create_app()


def main():
    """Run the application."""
    settings = get_settings()
    port = settings.port

    print(f"Starting ADO MCP server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
