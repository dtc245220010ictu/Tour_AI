"""
TourAI Application Factory and Entry Point.
Hệ thống Quản lý Tour Du lịch Tích hợp Trí tuệ Nhân tạo (Đề tài 17).
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template

# Load environment variables
load_dotenv()

from database.db import init_db
from database.seeder import seed_all
from routes.auth_routes import auth_bp
from routes.tour_routes import tour_bp
from routes.booking_routes import booking_bp
from routes.feedback_routes import feedback_bp
from routes.admin_routes import admin_bp
from routes.chat_routes import chat_bp
from routes.ai_tools_routes import ai_tools_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "tour_ai_production_secret_key_2026")
    
    # Initialize and seed database if not already done
    try:
        init_db()
        seed_all()
    except Exception as e:
        app.logger.warning(f"Database initialization notice: {e}")

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(tour_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(ai_tools_bp)

    # Custom Jinja filters
    @app.template_filter("format_currency")
    def format_currency_filter(value):
        try:
            return f"{int(value):,}".replace(",", ".") + " ₫"
        except (ValueError, TypeError):
            return str(value)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html"), 500

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ["true", "1"]
    print(f"🚀 TourAI server is running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)

