import asyncio
import logging
from datetime import datetime, timedelta
from discord.ext import tasks

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Manages background tasks for the Elder Scrolls Lore Bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.tasks = {}
    
    def start_all_tasks(self):
        """Start all background tasks"""
        logger.info("Starting background tasks...")
        
        # Start the cleanup task
        self.cleanup_old_errors.start()
        
        # Start the health check task
        self.health_check.start()
        
        # Start the search engine maintenance task
        self.search_engine_maintenance.start()
        
        logger.info("All background tasks started")
    
    def stop_all_tasks(self):
        """Stop all background tasks"""
        logger.info("Stopping background tasks...")
        
        for task_name, task in self.tasks.items():
            if task.is_running():
                task.cancel()
                logger.info(f"Stopped task: {task_name}")
        
        logger.info("All background tasks stopped")
    
    @tasks.loop(hours=1)
    async def cleanup_old_errors(self):
        """Clean up old error logs every hour"""
        try:
            # Keep only errors from the last 24 hours
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.bot.error_log = [
                error for error in self.bot.error_log
                if datetime.strptime(error['time'], '%Y-%m-%d %H:%M:%S') > cutoff_time
            ]
            logger.info(f"Cleaned up error log. {len(self.bot.error_log)} errors remaining.")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    @cleanup_old_errors.before_loop
    async def before_cleanup_old_errors(self):
        """Wait until the bot is ready before starting the cleanup task"""
        await self.bot.wait_until_ready()
    
    @tasks.loop(minutes=30)
    async def health_check(self):
        """Perform health checks every 30 minutes"""
        try:
            # Check if bot is still connected
            if not self.bot.is_ready():
                logger.warning("Bot is not ready during health check")
                return
            
            # Check latency
            latency = self.bot.latency * 1000
            if latency > 1000:  # More than 1 second
                logger.warning(f"High latency detected: {latency:.0f}ms")
            
            # Check memory usage
            try:
                import psutil
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                if memory_mb > 500:  # More than 500MB
                    logger.warning(f"High memory usage: {memory_mb:.1f}MB")
            except ImportError:
                pass
            
            # Check if search engine is still working
            if self.bot.search_engine:
                try:
                    # Quick test search
                    test_results = await asyncio.wait_for(
                        self.bot.search_engine.search("test"),
                        timeout=10.0
                    )
                    logger.debug("Search engine health check passed")
                except Exception as e:
                    logger.error(f"Search engine health check failed: {e}")
            
            logger.debug("Health check completed successfully")
            
        except Exception as e:
            logger.error(f"Error during health check: {e}")
    
    @health_check.before_loop
    async def before_health_check(self):
        """Wait until the bot is ready before starting the health check task"""
        await self.bot.wait_until_ready()
    
    @tasks.loop(hours=6)
    async def search_engine_maintenance(self):
        """Perform maintenance on the search engine every 6 hours"""
        try:
            if not self.bot.search_engine:
                return
            
            logger.info("Starting search engine maintenance...")
            
            # This could include:
            # - Refreshing cached data
            # - Cleaning up temporary files
            # - Rebuilding indexes if needed
            # - Checking for updates to datasets
            
            # For now, just log that maintenance was performed
            logger.info("Search engine maintenance completed")
            
        except Exception as e:
            logger.error(f"Error during search engine maintenance: {e}")
    
    @search_engine_maintenance.before_loop
    async def before_search_engine_maintenance(self):
        """Wait until the bot is ready before starting the maintenance task"""
        await self.bot.wait_until_ready()
    
    async def run_heavy_computation(self, task_name, func, *args, **kwargs):
        """Run a heavy computation task in the background"""
        try:
            logger.info(f"Starting heavy computation task: {task_name}")
            
            # Create a task for the heavy computation
            task = asyncio.create_task(func(*args, **kwargs))
            self.tasks[task_name] = task
            
            # Wait for the task to complete
            result = await task
            
            logger.info(f"Completed heavy computation task: {task_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error in heavy computation task {task_name}: {e}")
            raise
        finally:
            # Clean up the task reference
            if task_name in self.tasks:
                del self.tasks[task_name]
    
    async def example_heavy_task(self, data):
        """Example of a heavy computation task"""
        logger.info("Starting example heavy computation...")
        
        # Simulate heavy computation
        await asyncio.sleep(5)
        
        # Process the data (this could be ML inference, data analysis, etc.)
        processed_data = f"Processed: {data}"
        
        logger.info("Completed example heavy computation")
        return processed_data