from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from typing import Optional
import logging
import asyncio
from .models import User, Base
from .service import UserService

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, database_url: str):
        """
        Initialize database manager with async engine and session factory
        
        Args:
            database_url (str): Database URL (should be async compatible, e.g., 
                              postgresql+asyncpg:// instead of postgresql://)
        """
        # Create async engine with echo for SQL logging
        self.engine = create_async_engine(
            database_url,
            echo=True,
            pool_size=20,
            max_overflow=10
        )
        
        # Create async session factory
        self.AsyncSessionLocal = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def init_db(self):
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")

    async def get_session(self) -> AsyncSession:
        """Get a new async session"""
        return self.AsyncSessionLocal()

class UserStatUpdateQueue:
    def __init__(self, db_manager: DatabaseManager, max_workers: Optional[int] = None):
        """
        Initialize update queue for user statistics
        
        Args:
            db_manager (DatabaseManager): Database manager instance
            max_workers (int, optional): Maximum number of concurrent workers
        """
        self.db_manager = db_manager
        self.queue = asyncio.Queue()
        self.max_workers = max_workers or 5
        self._workers = []

    async def worker(self):
        """Process updates from the queue"""
        while True:
            try:
                # Get username and won status from queue
                username, won = await self.queue.get()
                
                async with self.db_manager.get_session() as session:
                    try:
                        # Get user and update stats
                        user = await session.get(User, username)
                        if user:
                            user.update_game_stats(won)
                            await session.commit()
                            logger.info(f"Updated stats for user {username}")
                    except Exception as e:
                        await session.rollback()
                        logger.error(f"Error updating stats for user {username}: {e}")
                    finally:
                        self.queue.task_done()
            except Exception as e:
                logger.error(f"Worker error: {e}")
                continue

    async def start(self):
        """Start the worker pool"""
        self._workers = [
            asyncio.create_task(self.worker())
            for _ in range(self.max_workers)
        ]
        logger.info(f"Started {self.max_workers} worker(s)")

    async def stop(self):
        """Stop all workers"""
        for worker in self._workers:
            worker.cancel()
        self._workers = []
        logger.info("All workers stopped")

    async def enqueue_update(self, username: str, won: bool):
        """
        Add a user stats update to the queue
        
        Args:
            username (str): Username to update
            won (bool): Whether the game was won
        """
        await self.queue.put((username, won))
        logger.debug(f"Queued stats update for user {username}")

# Usage example:
"""
# In your Flask app initialization:
async def init_app(app):
    database_url = app.config['SQLALCHEMY_DATABASE_URL']
    db_manager = DatabaseManager(database_url)
    await db_manager.init_db()
    
    # Create and start update queue
    update_queue = UserStatUpdateQueue(db_manager)
    await update_queue.start()
    
    # Store in app context
    app.db_manager = db_manager
    app.update_queue = update_queue

# In your game route:
@app.route('/game/end', methods=['POST'])
async def game_end():
    username = current_user.username
    won = request.json['won']
    
    # Queue the update
    await app.update_queue.enqueue_update(username, won)
    return jsonify({'status': 'success'})

# In your app shutdown:
async def cleanup():
    await app.update_queue.stop()
"""