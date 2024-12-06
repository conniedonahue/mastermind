from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    if os.getenv("ENV") == "production":
        from app.db.cache_prod import Cache
    else:
        from app.db.cache_dev import Cache
    app.cache = Cache

    from .routes import game_routes
    app.register_blueprint(game_routes)

    return app