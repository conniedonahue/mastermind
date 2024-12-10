# queue_manager.py
import asyncio
from typing import Optional
import logging
from .models import User

logger = logging.getLogger(__name__)

class UserStatUpdateQueue:
    def __init__(self, db_manager, max_workers: Optional[int] = None, loop=None):
        """
        Initialize update queue for user statistics
        
        Args:
            db_manager: Database manager instance
            max_workers (int, optional): Maximum number of concurrent workers
        """
        self.db_manager = db_manager
        self.loop = loop or asyncio.get_event_loop()
        self.queue = asyncio.Queue()
        self.max_workers = max_workers or 5
        self._active_workers = 0 
        self._workers = []
        self._running = False

    async def worker(self):
        """Process updates from the queue"""
        self._active_workers += 1
        
        try:
            while self._running:
                try:
                    # Get item with shorter timeout since we'll stop when empty
                    username, won = await asyncio.wait_for(
                        self.queue.get(), 
                        timeout=0.1
                    )
                except asyncio.TimeoutError:
                    # If queue is empty, check if we should stop
                    if self.queue.empty() and self._running:
                        self._running = False
                    continue
                
                # Process the update
                async with self.db_manager.get_session() as session:
                    try:
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
        finally:
            self._active_workers -= 1
            if self._active_workers == 0:
                logger.info("All workers stopped - queue is empty")

    async def start_workers(self):
        """Start worker pool if not already running"""
        if not self._running and not self._active_workers:
            self._running = True
            self._workers = [
                asyncio.create_task(self.worker())
                for _ in range(self.max_workers)
            ]
            logger.info(f"Started {self.max_workers} worker(s)")

    async def stop(self):
        """Stop workers gracefully"""
        if self._running:
            logger.info("Stopping workers...")
            self._running = False
            if self._workers:
                await asyncio.gather(*self._workers, return_exceptions=True)
                self._workers = []
            logger.info("All workers stopped")

    async def enqueue_update(self, username: str, won: bool):
        """Add update to queue and ensure workers are running"""
        try:
            await self.queue.put((username, won))
            logger.debug(f"Queued stats update for user {username}")
            
            # Start workers if they're not running
            await self.start_workers()
            
        except RuntimeError as e:
            logger.error(f"Failed to enqueue update: {e}")