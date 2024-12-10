import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import Optional

class UserStatUpdateQueue:
    def __init__(self, database_url: str, max_workers: Optional[int] = None):
        self.database_url = database_url
        self.database_manager = DatabaseManager(database_url)
        self.queue = asyncio.Queue()
        self.max_workers = max_workers or 5  # Default to 5 concurrent workers

    async def worker(self):
        """
        Worker to process updates from the queue
        """
        while True:
            # Get username and won status from queue
            username, won = await self.queue.get()
            
            try:
                # Update user stats
                await self.database_manager.update_user_stats(username, won)
            except Exception as e:
                print(f"Queue worker error: {e}")
            finally:
                # Mark task as done
                self.queue.task_done()

    async def start_workers(self):
        """
        Start multiple worker tasks
        """
        workers = [
            asyncio.create_task(self.worker()) 
            for _ in range(self.max_workers)
        ]
        return workers

    async def enqueue_user_update(self, username: str, won: bool):
        """
        Add a user stats update to the queue
        """
        await self.queue.put((username, won))