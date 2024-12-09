from flask import Flask
from redis import Redis, RedisError
from dotenv import load_dotenv
import os
from .config import DevelopmentConfig, ProductionConfig, TestingConfig

def create_app():
    app = Flask(__name__)
    environment = os.getenv("FLASK_ENV", "development")

    if environment == 'production':
        app.config.from_object(ProductionConfig)
        redis_client = Redis(
            host=app.config["REDIS_HOST"],
            port=app.config["REDIS_PORT"],
            decode_responses=True,
            password=app.config["REDIS_PASSWORD"],
            db=0
        )

        print('host: ', app.config["REDIS_HOST"])

        try:
            redis_client.ping()
            print("Successfully connected to Redis!")
        except RedisError as e:
            print(f"Error connecting to Redis: {e}")
            raise RuntimeError("Redis connection failed") from e

        from app.db.session_manager import RedisSessionManager as Session_Manager
        app.session_manager = Session_Manager(redis_client)
    elif environment == 'testing':
        app.config.from_object(TestingConfig)
        from app.db.session_manager import InMemorySessionManager as Session_Manager
        app.session_manager = Session_Manager
    else:
        app.config.from_object(DevelopmentConfig)
        from app.db.session_manager import InMemorySessionManager as Session_Manager
        app.session_manager = Session_Manager

    from .routes import game_routes
    app.register_blueprint(game_routes)

    return app