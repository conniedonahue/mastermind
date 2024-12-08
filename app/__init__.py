from flask import Flask
import os
from .config import DevelopmentConfig, ProductionConfig, TestingConfig


def create_app():
    app = Flask(__name__)

    if os.getenv("ENV") == "production":
        app.config.from_object(ProductionConfig)
        from app.db.session_manager import RedisSessionManager as Session_Manager
    elif os.getenv("ENV") == "testing":
        app.config.from_object(TestingConfig)
        from app.db.session_manager import InMemorySessionManager as Session_Manager
    else:
        app.config.from_object(DevelopmentConfig)
        from app.db.session_manager import InMemorySessionManager as Session_Manager
        
    app.session_manager = Session_Manager

    from .routes import game_routes
    app.register_blueprint(game_routes)

    return app