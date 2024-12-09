from flask import Flask
from redis import Redis, RedisError
from dotenv import load_dotenv
import os
from .config import DevelopmentConfig, ProductionConfig, TestingConfig
import logging

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    environment = os.getenv("FLASK_ENV", "development")

    if environment == 'production':
        app.config.from_object(ProductionConfig)
        redis_client = create_redis_client(app.config)
        from app.db.session_manager import RedisSessionManager
        app.session_manager = RedisSessionManager(redis_client)
    elif environment == 'testing':
        app.config.from_object(TestingConfig)
        from app.db.session_manager import InMemorySessionManager
        app.session_manager = InMemorySessionManager
        logger.info("Using InMemorySessionManager for testing environment")
    else:
        app.config.from_object(DevelopmentConfig)
        from app.db.session_manager import InMemorySessionManager
        app.session_manager = InMemorySessionManager
        logger.info("Using InMemorySessionManager for development environment")

    from .routes import game_routes
    app.register_blueprint(game_routes)

    return app

def create_redis_client(config):
    """
    Create and verify a Redis client connection.
    
    Args:
        config (dict): Configuration dictionary with Redis connection parameters
    
    Returns:
        Redis: A verified Redis client
    
    Raises:
        RuntimeError: If unable to establish a connection to Redis
    """
    # Temp boost is log level for this operation
    original_level = logging.getLogger().level

    try:
        logging.getLogger().setLevel(logging.INFO)
        
        redis_client = Redis(
            host=config["REDIS_HOST"],
            port=config["REDIS_PORT"],
            decode_responses=True,
            password=config["REDIS_PASSWORD"],
            db=0
        )
        
        redis_client.ping()
        logger.info("Successfully connected to Redis!")
        return redis_client
    
    except RedisError as e:
        logger.error("Error connecting to Redis: %s", e)
        raise RuntimeError("Redis connection failed") from e

    finally:
        # Restore original logging level
        logging.getLogger().setLevel(original_level)