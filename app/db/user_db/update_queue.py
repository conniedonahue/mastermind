from queue import Queue
from threading import Thread
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
        self.queue = Queue()
        self.max_workers = max_workers
        self._running = False
        self._workers = []

    def worker(self):
        """Process updates from the queue"""
        self._active_workers += 1
        
        while self._running:
            try:
                username, won = self.queue.get(timeout=1)
                self.db_manager.update_user_game_stats(username, won)
                self.queue.task_done()
            except Exception as e:
                logger.error(f"Error processing queue item: {e}")
            except Queue.Empty:
                continue

    def start_workers(self):
        """Start worker pool if not already running"""
        if not self._running:
            self._running = True
            self._workers = [
                Thread(target=self.worker, daemon=True)
                for _ in range(self.max_workers)
            ]
            for worker in self._workers:
                worker.start()
            logger.info(f"Started {self.max_workers} worker(s)")

    def stop(self):
        """Stop workers gracefully"""
        self._running = False
        for worker in self._workers:
            worker.join()
        self._workers = []
        logger.info("All workers stopped")

    def enqueue_update(self, username: str, won: bool):
        """Add update to queue and ensure workers are running"""
        try:
            self.queue.put((username, won))
            logger.debug(f"Queued stats update for user {username}")
            
            # Start workers if they're not running
            self.start_workers()
            
        except RuntimeError as e:
            logger.error(f"Failed to enqueue update: {e}")