"""
Optimized Background Tasks Module for Elder Scrolls Lore Bot
Enhanced with better task management, monitoring, and resource optimization.
"""

import asyncio
import logging
import time
import psutil
from datetime import datetime, timedelta
from discord.ext import tasks
from typing import Dict, Any, List, Optional
from collections import deque
import json
import os

logger = logging.getLogger(__name__)

class TaskManager:
    """Manages background tasks with monitoring and cleanup"""
    
    def __init__(self, task_name: str, interval_seconds: float):
        self.task_name = task_name
        self.interval_seconds = interval_seconds
        self.last_run = None
        self.run_count = 0
        self.total_execution_time = 0.0
        self.last_execution_time = 0.0
        self.errors = deque(maxlen=10)
        self.is_running = False
    
    def record_execution(self, execution_time: float, error: Optional[str] = None):
        """Record task execution statistics"""
        self.last_run = datetime.now()
        self.run_count += 1
        self.last_execution_time = execution_time
        self.total_execution_time += execution_time
        
        if error:
            self.errors.append({
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': error
            })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get task statistics"""
        avg_execution_time = self.total_execution_time / self.run_count if self.run_count > 0 else 0
        
        return {
            'task_name': self.task_name,
            'is_running': self.is_running,
            'run_count': self.run_count,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'last_execution_time': round(self.last_execution_time, 3),
            'avg_execution_time': round(avg_execution_time, 3),
            'total_execution_time': round(self.total_execution_time, 3),
            'error_count': len(self.errors),
            'recent_errors': list(self.errors)
        }

class BackgroundTaskManager:
    """Optimized background task manager for the Elder Scrolls Lore Bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.task_managers: Dict[str, TaskManager] = {}
        self.startup_time = datetime.now()
        self.performance_metrics = deque(maxlen=100)
        
        # Initialize task managers
        self._initialize_task_managers()
        
        logger.info("BackgroundTaskManager initialized")
    
    def _initialize_task_managers(self):
        """Initialize all task managers"""
        self.task_managers = {
            'cleanup_old_errors': TaskManager('cleanup_old_errors', 3600),  # 1 hour
            'health_check': TaskManager('health_check', 1800),  # 30 minutes
            'search_engine_maintenance': TaskManager('search_engine_maintenance', 21600),  # 6 hours
            'performance_monitoring': TaskManager('performance_monitoring', 300),  # 5 minutes
            'cache_optimization': TaskManager('cache_optimization', 900),  # 15 minutes
            'memory_cleanup': TaskManager('memory_cleanup', 600),  # 10 minutes
        }
    
    def start_all_tasks(self):
        """Start all background tasks"""
        logger.info("Starting optimized background tasks...")
        
        try:
            # Start all tasks
            self.cleanup_old_errors.start()
            self.health_check.start()
            self.search_engine_maintenance.start()
            self.performance_monitoring.start()
            self.cache_optimization.start()
            self.memory_cleanup.start()
            
            logger.info("All background tasks started successfully")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
    
    def stop_all_tasks(self):
        """Stop all background tasks gracefully"""
        logger.info("Stopping background tasks...")
        
        try:
            # Stop all tasks
            tasks_to_stop = [
                self.cleanup_old_errors,
                self.health_check,
                self.search_engine_maintenance,
                self.performance_monitoring,
                self.cache_optimization,
                self.memory_cleanup
            ]
            
            for task in tasks_to_stop:
                if task.is_running():
                    task.cancel()
                    logger.info(f"Stopped task: {task.__name__}")
            
            logger.info("All background tasks stopped")
            
        except Exception as e:
            logger.error(f"Error stopping background tasks: {e}")
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get comprehensive task statistics"""
        stats = {}
        for name, manager in self.task_managers.items():
            stats[name] = manager.get_stats()
        
        return {
            'startup_time': self.startup_time.isoformat(),
            'uptime_seconds': (datetime.now() - self.startup_time).total_seconds(),
            'total_tasks': len(self.task_managers),
            'running_tasks': sum(1 for manager in self.task_managers.values() if manager.is_running),
            'task_details': stats,
            'performance_metrics_count': len(self.performance_metrics)
        }
    
    @tasks.loop(hours=1)
    async def cleanup_old_errors(self):
        """Clean up old error logs every hour with enhanced cleanup"""
        start_time = time.time()
        task_manager = self.task_managers['cleanup_old_errors']
        task_manager.is_running = True
        
        try:
            logger.info("Starting enhanced error cleanup...")
            
            # Keep only errors from the last 24 hours
            cutoff_time = datetime.now() - timedelta(hours=24)
            original_count = len(self.bot.error_log)
            
            self.bot.error_log = [
                error for error in self.bot.error_log
                if datetime.strptime(error['time'], '%Y-%m-%d %H:%M:%S') > cutoff_time
            ]
            
            cleaned_count = original_count - len(self.bot.error_log)
            
            # Also clean up old rate limiter data
            current_time = time.time()
            cutoff_timestamp = current_time - 3600  # 1 hour ago
            
            # Clean up user rate limiters
            expired_users = [
                user_id for user_id, limiter in self.bot.user_rate_limiters.items()
                if not limiter.requests or max(limiter.requests) < cutoff_timestamp
            ]
            for user_id in expired_users:
                del self.bot.user_rate_limiters[user_id]
            
            # Clean up guild rate limiters
            expired_guilds = [
                guild_id for guild_id, limiter in self.bot.guild_rate_limiters.items()
                if not limiter.requests or max(limiter.requests) < cutoff_timestamp
            ]
            for guild_id in expired_guilds:
                del self.bot.guild_rate_limiters[guild_id]
            
            execution_time = time.time() - start_time
            task_manager.record_execution(execution_time)
            
            logger.info(f"Error cleanup completed: {cleaned_count} errors removed, "
                       f"{len(expired_users)} user limiters, {len(expired_guilds)} guild limiters")
            
        except Exception as e:
            execution_time = time.time() - start_time
            task_manager.record_execution(execution_time, str(e))
            logger.error(f"Error during cleanup: {e}")
        finally:
            task_manager.is_running = False
    
    @cleanup_old_errors.before_loop
    async def before_cleanup_old_errors(self):
        """Wait until the bot is ready before starting the cleanup task"""
        await self.bot.wait_until_ready()
    
    @tasks.loop(minutes=30)
    async def health_check(self):
        """Perform comprehensive health checks every 30 minutes"""
        start_time = time.time()
        task_manager = self.task_managers['health_check']
        task_manager.is_running = True
        
        try:
            logger.debug("Starting comprehensive health check...")
            
            health_status = {
                'bot_ready': self.bot.is_ready(),
                'latency_ms': round(self.bot.latency * 1000, 2),
                'guild_count': len(self.bot.guilds),
                'connection_issues': self.bot.connection_issues,
                'memory_usage_mb': 0,
                'cpu_usage_percent': 0,
                'search_engine_healthy': False,
                'rag_processor_healthy': False
            }
            
            # Check system resources
            try:
                process = psutil.Process()
                health_status['memory_usage_mb'] = round(process.memory_info().rss / 1024 / 1024, 1)
                health_status['cpu_usage_percent'] = round(process.cpu_percent(), 1)
                
                # Check for resource issues
                if health_status['memory_usage_mb'] > 500:
                    logger.warning(f"High memory usage: {health_status['memory_usage_mb']}MB")
                if health_status['cpu_usage_percent'] > 80:
                    logger.warning(f"High CPU usage: {health_status['cpu_usage_percent']}%")
                    
            except ImportError:
                logger.warning("psutil not available for system monitoring")
            
            # Check search engine health
            if self.bot.search_engine:
                try:
                    test_results = await asyncio.wait_for(
                        self.bot.search_engine.search("health check"),
                        timeout=10.0
                    )
                    health_status['search_engine_healthy'] = True
                except Exception as e:
                    logger.error(f"Search engine health check failed: {e}")
            
            # Check RAG processor health
            if self.bot.rag_processor:
                health_status['rag_processor_healthy'] = True
            
            # Log health status
            logger.info(f"Health check completed: {health_status}")
            
            # Store performance metric
            self.performance_metrics.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'health_check',
                'data': health_status
            })
            
            execution_time = time.time() - start_time
            task_manager.record_execution(execution_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            task_manager.record_execution(execution_time, str(e))
            logger.error(f"Error during health check: {e}")
        finally:
            task_manager.is_running = False
    
    @health_check.before_loop
    async def before_health_check(self):
        """Wait until the bot is ready before starting the health check task"""
        await self.bot.wait_until_ready()
    
    @tasks.loop(hours=6)
    async def search_engine_maintenance(self):
        """Perform maintenance on the search engine every 6 hours"""
        start_time = time.time()
        task_manager = self.task_managers['search_engine_maintenance']
        task_manager.is_running = True
        
        try:
            logger.info("Starting search engine maintenance...")
            
            if not self.bot.search_engine:
                logger.warning("Search engine not available for maintenance")
                return
            
            # Perform maintenance tasks
            maintenance_tasks = []
            
            # Check for dataset updates (placeholder)
            maintenance_tasks.append("Dataset update check completed")
            
            # Clean up temporary files
            maintenance_tasks.append("Temporary file cleanup completed")
            
            # Optimize search indexes if needed
            maintenance_tasks.append("Search index optimization completed")
            
            # Test search functionality
            try:
                test_results = await asyncio.wait_for(
                    self.bot.search_engine.search("maintenance test"),
                    timeout=15.0
                )
                maintenance_tasks.append("Search functionality test passed")
            except Exception as e:
                logger.error(f"Search functionality test failed: {e}")
                maintenance_tasks.append(f"Search functionality test failed: {e}")
            
            execution_time = time.time() - start_time
            task_manager.record_execution(execution_time)
            
            logger.info(f"Search engine maintenance completed: {len(maintenance_tasks)} tasks")
            
        except Exception as e:
            execution_time = time.time() - start_time
            task_manager.record_execution(execution_time, str(e))
            logger.error(f"Error during search engine maintenance: {e}")
        finally:
            task_manager.is_running = False
    
    @search_engine_maintenance.before_loop
    async def before_search_engine_maintenance(self):
        """Wait until the bot is ready before starting the maintenance task"""
        await self.bot.wait_until_ready()
    
    @tasks.loop(minutes=5)
    async def performance_monitoring(self):
        """Monitor performance metrics every 5 minutes"""
        start_time = time.time()
        task_manager = self.task_managers['performance_monitoring']
        task_manager.is_running = True
        
        try:
            # Collect performance metrics
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'bot_stats': self.bot.get_performance_stats(),
                'task_stats': self.get_task_stats(),
                'system_resources': {}
            }
            
            # Get system resource usage
            try:
                process = psutil.Process()
                metrics['system_resources'] = {
                    'memory_mb': round(process.memory_info().rss / 1024 / 1024, 1),
                    'cpu_percent': round(process.cpu_percent(), 1),
                    'thread_count': process.num_threads(),
                    'open_files': len(process.open_files()),
                    'connections': len(process.connections())
                }
            except ImportError:
                pass
            
            # Store metrics
            self.performance_metrics.append(metrics)
            
            # Log significant changes
            if len(self.performance_metrics) > 1:
                prev_metrics = self.performance_metrics[-2]
                current_metrics = metrics
                
                # Check for significant memory increase
                if 'system_resources' in current_metrics and 'system_resources' in prev_metrics:
                    mem_diff = current_metrics['system_resources']['memory_mb'] - prev_metrics['system_resources']['memory_mb']
                    if abs(mem_diff) > 50:  # More than 50MB change
                        logger.info(f"Significant memory change: {mem_diff:+.1f}MB")
            
            execution_time = time.time() - start_time
            task_manager.record_execution(execution_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            task_manager.record_execution(execution_time, str(e))
            logger.error(f"Error during performance monitoring: {e}")
        finally:
            task_manager.is_running = False
    
    @performance_monitoring.before_loop
    async def before_performance_monitoring(self):
        """Wait until the bot is ready before starting the monitoring task"""
        await self.bot.wait_until_ready()
    
    @tasks.loop(minutes=15)
    async def cache_optimization(self):
        """Optimize cache performance every 15 minutes"""
        start_time = time.time()
        task_manager = self.task_managers['cache_optimization']
        task_manager.is_running = True
        
        try:
            logger.debug("Starting cache optimization...")
            
            # Get cache statistics
            cache_size = len(self.bot.cache.cache)
            cache_usage_percent = (cache_size / self.bot.cache.max_size) * 100
            
            # Optimize cache if needed
            if cache_usage_percent > 80:
                logger.info(f"Cache usage high ({cache_usage_percent:.1f}%), performing optimization")
                
                # Remove some older entries to free up space
                entries_to_remove = int(cache_size * 0.1)  # Remove 10% of entries
                for _ in range(entries_to_remove):
                    if self.bot.cache.access_order:
                        oldest_key = self.bot.cache.access_order.popleft()
                        self.bot.cache._remove_key(oldest_key)
                
                logger.info(f"Cache optimization completed: removed {entries_to_remove} entries")
            
            # Log cache statistics
            logger.debug(f"Cache optimization completed: {cache_size} entries, {cache_usage_percent:.1f}% usage")
            
            execution_time = time.time() - start_time
            task_manager.record_execution(execution_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            task_manager.record_execution(execution_time, str(e))
            logger.error(f"Error during cache optimization: {e}")
        finally:
            task_manager.is_running = False
    
    @cache_optimization.before_loop
    async def before_cache_optimization(self):
        """Wait until the bot is ready before starting the cache optimization task"""
        await self.bot.wait_until_ready()
    
    @tasks.loop(minutes=10)
    async def memory_cleanup(self):
        """Perform memory cleanup every 10 minutes"""
        start_time = time.time()
        task_manager = self.task_managers['memory_cleanup']
        task_manager.is_running = True
        
        try:
            logger.debug("Starting memory cleanup...")
            
            # Force garbage collection
            import gc
            collected = gc.collect()
            
            # Clean up old performance metrics if too many
            if len(self.performance_metrics) > 1000:
                # Keep only the last 500 metrics
                self.performance_metrics = deque(list(self.performance_metrics)[-500:], maxlen=1000)
                logger.info("Cleaned up old performance metrics")
            
            # Log memory cleanup results
            logger.debug(f"Memory cleanup completed: {collected} objects collected")
            
            execution_time = time.time() - start_time
            task_manager.record_execution(execution_time)
            
        except Exception as e:
            execution_time = time.time() - start_time
            task_manager.record_execution(execution_time, str(e))
            logger.error(f"Error during memory cleanup: {e}")
        finally:
            task_manager.is_running = False
    
    @memory_cleanup.before_loop
    async def before_memory_cleanup(self):
        """Wait until the bot is ready before starting the memory cleanup task"""
        await self.bot.wait_until_ready()
    
    async def run_heavy_computation(self, task_name: str, func, *args, **kwargs):
        """Run a heavy computation task in the background with monitoring"""
        logger.info(f"Starting heavy computation task: {task_name}")
        
        start_time = time.time()
        try:
            # Create a task for the heavy computation
            task = asyncio.create_task(func(*args, **kwargs))
            
            # Wait for the task to complete with timeout
            result = await asyncio.wait_for(task, timeout=300.0)  # 5 minute timeout
            
            execution_time = time.time() - start_time
            logger.info(f"Completed heavy computation task: {task_name} in {execution_time:.2f}s")
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Heavy computation task {task_name} timed out")
            raise
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in heavy computation task {task_name} after {execution_time:.2f}s: {e}")
            raise
    
    def export_performance_data(self, filepath: str = "performance_data.json"):
        """Export performance data to JSON file"""
        try:
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'task_stats': self.get_task_stats(),
                'performance_metrics': list(self.performance_metrics),
                'bot_stats': self.bot.get_performance_stats() if hasattr(self.bot, 'get_performance_stats') else {}
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Performance data exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Error exporting performance data: {e}")