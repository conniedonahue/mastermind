from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    if os.getenv("ENV") == "production":
        from app.db.cache_prod import Cache
    else:
        from app.db.session_manager import ServerSideSessionManager
    app.cache = ServerSideSessionManager

    from .routes import game_routes
    app.register_blueprint(game_routes)

    return app