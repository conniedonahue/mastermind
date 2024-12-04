from flask import Flask

def create_app():
    app = Flask(__name__)

    from .routes import game_routes
    app.register_blueprint(game_routes)

    return app