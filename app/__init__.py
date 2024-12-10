from flask import Flask
from redis import Redis, RedisError
from dotenv import load_dotenv
import os
from .config import DevelopmentConfig, ProductionConfig, TestingConfig
from .db.user_db.manager import DatabaseManager
from .db.user_db.update_queue import UserStatUpdateQueue
from .db.user_db.models import Base
import logging
import asyncio

logger = logging.getLogger(__name__)

def init_async_components(app):
    """Initialize async database components"""
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    
    # Set up the event loop
    if asyncio.get_event_loop().is_closed():
        asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    
    # Initialize database manager
    db_manager = DatabaseManager(db_url)
    loop.run_until_complete(db_manager.init_db())
    
    # Create queue manager (but don't start workers yet)
    update_queue = UserStatUpdateQueue(db_manager)
    
    # Store components in app context
    app.db_manager = db_manager
    app.update_queue = update_queue
    
    logger.info("Async database components initialized successfully")

def cleanup_async_components(app):
    """Cleanup async components on shutdown"""
    if hasattr(app, 'update_queue'):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            # Stop any running workers
            loop.run_until_complete(app.update_queue.stop())
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    logger.info("Async components cleaned up successfully")


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

    # Initialize async components
    init_async_components(app)

    # Register cleanup
    @app.teardown_appcontext
    def shutdown_async(exception=None):
        cleanup_async_components(app)

    @app.shell_context_processor
    def make_shell_context():
        return {
            'app': app,
            'db_manager': app.db_manager,
            'update_queue': app.update_queue
        }

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