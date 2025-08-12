"""
Optimized Discord Bot for Elder Scrolls Lore
A production-ready, scalable Discord bot with efficient async handling, proper error management,
rate limiting, caching, and security best practices.
"""

import discord
from discord.ext import commands
import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import weakref
from collections import defaultdict, deque
import json
import hashlib

from config import Config
from online_search import OnlineSearchEngine
from llm_client import LLMClientFactory, RAGProcessor
from background_tasks import BackgroundTaskManager

# Configure structured logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('discord_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RateLimiter:
    """Efficient rate limiter with sliding window"""
    
    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
    
    def is_allowed(self) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Remove old requests outside the window
        while self.requests and self.requests[0] <= now - self.window_seconds:
            self.requests.popleft()
        
        # Check if we can make a new request
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        return False
    
    def get_wait_time(self) -> float:
        """Get time to wait before next allowed request"""
        if not self.requests:
            return 0.0
        
        oldest_request = self.requests[0]
        return max(0.0, oldest_request + self.window_seconds - time.time())

class Cache:
    """Simple in-memory cache with TTL and size limits"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_order = deque()
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        now = time.time()
        expired_keys = [
            key for key, data in self.cache.items()
            if data['expires_at'] <= now
        ]
        for key in expired_keys:
            self._remove_key(key)
    
    def _remove_key(self, key: str):
        """Remove a key from cache"""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
    
    def _evict_oldest(self):
        """Evict oldest entry when cache is full"""
        if self.access_order:
            oldest_key = self.access_order.popleft()
            self._remove_key(oldest_key)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        self._cleanup_expired()
        
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]['value']
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        self._cleanup_expired()
        
        # Evict if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        self.cache[key] = {
            'value': value,
            'expires_at': expires_at
        }
        
        # Add to access order
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.access_order.clear()

class ElderScrollsLoreBot(commands.Bot):
    """Optimized Discord bot for Elder Scrolls Lore with production-ready features"""
    
    def __init__(self):
        # Initialize bot with optimized settings
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True  # For better user tracking
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,  # Custom help command
            max_messages=10000,  # Increase message cache
            chunk_guilds_at_startup=False  # Disable for better startup performance
        )
        
        # Bot state and performance tracking
        self.search_engine: Optional[OnlineSearchEngine] = None
        self.rag_processor: Optional[RAGProcessor] = None
        self.initialized = False
        self.start_time: Optional[datetime] = None
        self.error_log: List[Dict[str, Any]] = []
        
        # Performance and monitoring
        self.request_count = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.avg_response_time = 0.0
        self.response_times = deque(maxlen=100)
        
        # Rate limiting and caching
        self.user_rate_limiters: Dict[int, RateLimiter] = defaultdict(
            lambda: RateLimiter(max_requests=5, window_seconds=60.0)
        )
        self.guild_rate_limiters: Dict[int, RateLimiter] = defaultdict(
            lambda: RateLimiter(max_requests=20, window_seconds=60.0)
        )
        self.cache = Cache(max_size=500, default_ttl=600)  # 10 minutes default TTL
        
        # Background task management
        self.background_manager = BackgroundTaskManager(self)
        
        # Connection health monitoring
        self.last_heartbeat = time.time()
        self.connection_issues = 0
        
        # Memory monitoring
        self.memory_usage_history = deque(maxlen=50)
        
        logger.info("ElderScrollsLoreBot initialized with optimized settings")
    
    async def setup_hook(self):
        """Called when the bot is starting up - optimized for speed"""
        logger.info("Setting up Elder Scrolls Lore Discord Bot...")
        
        try:
            # Load cogs asynchronously
            await asyncio.gather(
                self.load_extension('commands'),
                self.load_extension('events')
            )
            
            # Initialize bot components with timeout
            if not await asyncio.wait_for(self.initialize(), timeout=60.0):
                logger.error("Bot initialization timed out")
                raise RuntimeError("Bot initialization timed out")
                
        except asyncio.TimeoutError:
            logger.error("Bot setup timed out")
            raise RuntimeError("Bot setup timed out")
        except Exception as e:
            logger.error(f"Bot setup failed: {e}")
            raise
    
    async def initialize(self):
        """Initialize the bot components with proper error handling"""
        try:
            logger.info("Initializing Elder Scrolls Lore Bot components...")
            
            # Initialize online search engine with timeout
            self.search_engine = OnlineSearchEngine()
            if not await asyncio.wait_for(
                self.search_engine.initialize(), 
                timeout=30.0
            ):
                logger.error("Failed to initialize online search engine")
                return False
            
            # Initialize LLM client and RAG processor
            llm_client = LLMClientFactory.create_client()
            self.rag_processor = RAGProcessor(llm_client)
            
            # Test components
            await self._test_components()
            
            self.initialized = True
            self.start_time = datetime.now()
            
            logger.info("Bot initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Bot initialization failed: {e}")
            return False
    
    async def _test_components(self):
        """Test bot components to ensure they're working"""
        try:
            # Test search engine
            test_results = await asyncio.wait_for(
                self.search_engine.search("test"),
                timeout=10.0
            )
            logger.info("Search engine test passed")
            
            # Test RAG processor
            if test_results:
                test_response = await asyncio.wait_for(
                    self.rag_processor.process_question("test", test_results),
                    timeout=10.0
                )
                logger.info("RAG processor test passed")
            
        except Exception as e:
            logger.warning(f"Component test failed: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        total_requests = self.request_count
        success_rate = (self.successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate memory usage
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
        except ImportError:
            memory_mb = 0
        
        return {
            'total_requests': total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': round(success_rate, 2),
            'avg_response_time': round(self.avg_response_time, 3),
            'memory_usage_mb': round(memory_mb, 1),
            'cache_size': len(self.cache.cache),
            'connection_issues': self.connection_issues,
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        }
    
    def log_error(self, error: str, context: Dict[str, Any] = None):
        """Log error with context"""
        error_entry = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': error,
            'context': context or {}
        }
        
        self.error_log.append(error_entry)
        
        # Keep only last 100 errors
        if len(self.error_log) > 100:
            self.error_log = self.error_log[-100:]
        
        logger.error(f"Error logged: {error}")
    
    async def cleanup(self):
        """Cleanup resources when bot shuts down"""
        logger.info("Starting bot cleanup...")
        
        try:
            # Stop background tasks
            if hasattr(self, 'background_manager'):
                self.background_manager.stop_all_tasks()
            
            # Cleanup search engine
            if self.search_engine:
                await self.search_engine.close()
            
            # Clear caches
            self.cache.clear()
            
            # Close bot connection
            await self.close()
            
            logger.info("Bot cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

async def main():
    """Main function to run the bot with comprehensive error handling"""
    logger.info("Starting Elder Scrolls Lore Discord Bot...")
    
    # Validate configuration
    config_errors = Config.validate_config()
    if config_errors:
        logger.error("Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        return
    
    # Check for Discord token
    discord_token = os.getenv("DISCORD_TOKEN")
    if not discord_token:
        logger.error("DISCORD_TOKEN environment variable is required")
        return
    
    # Create bot instance
    bot = ElderScrollsLoreBot()
    
    try:
        # Start the bot with timeout
        logger.info("Connecting to Discord...")
        await asyncio.wait_for(bot.start(discord_token), timeout=30.0)
        
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user...")
    except asyncio.TimeoutError:
        logger.error("Bot startup timed out")
    except Exception as e:
        logger.error(f"Bot startup failed: {e}")
        bot.log_error(f"Startup failure: {e}")
    finally:
        # Cleanup resources
        await bot.cleanup()
        logger.info("Bot shutdown complete.")

if __name__ == "__main__":
    # Set up asyncio event loop with proper error handling
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)