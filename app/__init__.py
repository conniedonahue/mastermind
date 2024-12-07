from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    if os.getenv("ENV") == "production":
        from app.db.session_manager import RedisSessionManager as Session_Manager
    else:
        from app.db.session_manager import InMemorySessionManager as Session_Manager
    app.session_manager = Session_Manager

    from .routes import game_routes
    app.register_blueprint(game_routes)

    return app