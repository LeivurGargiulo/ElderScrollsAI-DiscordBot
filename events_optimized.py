"""
Optimized Events Module for Elder Scrolls Lore Bot
Enhanced with error handling, performance monitoring, and event debouncing.
"""

import discord
from discord.ext import commands, tasks
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Set
from functools import wraps
from collections import defaultdict, deque
import hashlib

from config import Config

logger = logging.getLogger(__name__)

def retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0):
    """Decorator to retry async functions with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"Final attempt failed for {func.__name__}: {e}")
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
            
            raise last_exception
        return wrapper
    return decorator

class EventDebouncer:
    """Debouncer for frequent events to prevent spam"""
    
    def __init__(self, delay_seconds: float = 2.0):
        self.delay_seconds = delay_seconds
        self.pending_tasks: Dict[str, asyncio.Task] = {}
    
    async def debounce(self, key: str, coro_func, *args, **kwargs):
        """Debounce a coroutine function"""
        # Cancel existing task if it exists
        if key in self.pending_tasks:
            self.pending_tasks[key].cancel()
        
        # Create new task
        task = asyncio.create_task(self._delayed_execution(key, coro_func, *args, **kwargs))
        self.pending_tasks[key] = task
        
        try:
            return await task
        except asyncio.CancelledError:
            logger.debug(f"Debounced task cancelled: {key}")
            raise
        finally:
            if key in self.pending_tasks:
                del self.pending_tasks[key]
    
    async def _delayed_execution(self, key: str, coro_func, *args, **kwargs):
        """Execute the coroutine after delay"""
        await asyncio.sleep(self.delay_seconds)
        return await coro_func(*args, **kwargs)

class ElderScrollsEvents(commands.Cog):
    """Optimized cog containing all Elder Scrolls Lore Bot event handlers"""
    
    def __init__(self, bot):
        self.bot = bot
        self.message_history = deque(maxlen=1000)  # Track recent messages
        self.user_activity = defaultdict(lambda: {'last_activity': 0, 'message_count': 0})
        self.guild_activity = defaultdict(lambda: {'last_activity': 0, 'message_count': 0})
        
        # Event debouncing
        self.debouncer = EventDebouncer(delay_seconds=1.0)
        
        # Performance tracking
        self.event_count = 0
        self.event_times = deque(maxlen=100)
        
        # Connection monitoring
        self.last_heartbeat = time.time()
        self.heartbeat_interval = 45.0  # Discord heartbeat interval
        
        logger.info("ElderScrollsEvents cog initialized")
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the bot is ready - optimized for performance"""
        logger.info(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
        logger.info(f'Connected to {len(self.bot.guilds)} guilds')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Elder Scrolls lore | !help"
        )
        await self.bot.change_presence(activity=activity)
        
        # Start background tasks
        if hasattr(self.bot, 'background_manager'):
            self.bot.background_manager.start_all_tasks()
        
        # Start monitoring tasks
        self.monitor_connection.start()
        self.cleanup_activity_data.start()
        
        logger.info("Bot is ready and all tasks started")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle incoming messages with optimized processing"""
        # Track event performance
        start_time = time.time()
        self.event_count += 1
        
        try:
            # Ignore messages from the bot itself
            if message.author == self.bot.user:
                return
            
            # Update activity tracking
            self._update_activity_tracking(message)
            
            # Process commands first
            await self.bot.process_commands(message)
            
            # If it's not a command and the bot is initialized, treat as a question
            if not message.content.startswith('!') and self.bot.initialized:
                # Debounce question processing to prevent spam
                question_key = f"question_{message.author.id}_{message.guild.id if message.guild else 'dm'}"
                await self.debouncer.debounce(
                    question_key,
                    self.handle_question,
                    message
                )
            
            # Track message in history
            self.message_history.append({
                'id': message.id,
                'author': message.author.id,
                'guild': message.guild.id if message.guild else None,
                'content': message.content[:100],  # Truncate for memory efficiency
                'timestamp': time.time()
            })
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.bot.log_error(f"Message processing error: {e}", {
                'message_id': message.id,
                'author': str(message.author),
                'guild': message.guild.name if message.guild else 'DM',
                'content_length': len(message.content)
            })
        finally:
            # Record event processing time
            processing_time = time.time() - start_time
            self.event_times.append(processing_time)
    
    async def handle_question(self, message):
        """Handle regular messages as questions with optimized processing"""
        if not self.bot.initialized:
            await self.safe_send_message(
                message.channel,
                "⚠️ Bot is still initializing. Please wait a moment and try again."
            )
            return
        
        question = message.content.strip()
        
        # Skip very short or very long questions
        if len(question) < 3:
            return
        if len(question) > 500:
            await self.safe_send_message(
                message.channel,
                "❌ Question is too long. Please keep it under 500 characters."
            )
            return
        
        # Check cache first
        cache_key = self._generate_cache_key(question)
        cached_response = self.bot.cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for question: {question[:50]}...")
            await self.safe_send_message(message.channel, cached_response)
            return
        
        # Show typing indicator
        async with message.channel.typing():
            try:
                # Search for relevant passages with timeout
                context_passages = await asyncio.wait_for(
                    self.bot.search_engine.search(question),
                    timeout=Config.SEARCH_TIMEOUT
                )
                
                if not context_passages:
                    response = "🤔 I searched multiple online sources but couldn't find specific information about that in the Elder Scrolls lore. Could you try rephrasing your question or ask about something else?"
                else:
                    # Process question using RAG with timeout
                    response = await asyncio.wait_for(
                        self.bot.rag_processor.process_question(question, context_passages),
                        timeout=Config.LLM_TIMEOUT
                    )
                
                # Cache the response
                self.bot.cache.set(cache_key, response, ttl=1800)  # 30 minutes
                
                # Send response with retry logic
                await self.safe_send_message(message.channel, response)
                
            except asyncio.TimeoutError:
                logger.error(f"Timeout processing question '{question}'")
                await self.safe_send_message(
                    message.channel,
                    "⏰ Sorry, the request took too long to process. Please try again with a simpler question or try later."
                )
            except Exception as e:
                logger.error(f"Error processing question '{question}': {e}")
                self.bot.log_error(f"Question processing error: {e}", {
                    'question': question,
                    'user': str(message.author),
                    'guild': message.guild.name if message.guild else 'DM'
                })
                await self.safe_send_message(
                    message.channel,
                    "❌ Sorry, I encountered an error while processing your question. Please try again later."
                )
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Global error handler for commands with enhanced logging"""
        # Track error performance
        start_time = time.time()
        
        try:
            # Log the error with context
            error_msg = f"Command error in {ctx.guild.name if ctx.guild else 'DM'} by {ctx.author}: {error}"
            logger.error(error_msg)
            
            # Add to error log with enhanced context
            self.bot.error_log.append({
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'error': str(error),
                'user': str(ctx.author),
                'guild': ctx.guild.name if ctx.guild else 'DM',
                'command': ctx.command.name if ctx.command else 'Unknown',
                'message_content': ctx.message.content[:100],
                'channel': str(ctx.channel)
            })
            
            # Keep only last 100 errors
            if len(self.bot.error_log) > 100:
                self.bot.error_log = self.bot.error_log[-100:]
            
            # Send user-friendly error message based on error type
            await self._handle_command_error(ctx, error)
            
        except Exception as e:
            logger.error(f"Error in command error handler: {e}")
        finally:
            # Record error handling time
            processing_time = time.time() - start_time
            self.event_times.append(processing_time)
    
    async def _handle_command_error(self, ctx, error):
        """Handle specific command errors with appropriate responses"""
        if isinstance(error, commands.CommandNotFound):
            await self.safe_send_message(
                ctx.channel,
                "❓ Command not found. Use `!help` to see available commands."
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await self.safe_send_message(
                ctx.channel,
                f"❌ Missing required argument: {error.param.name}\nUse `!help {ctx.command.name}` for usage information."
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await self.safe_send_message(
                ctx.channel,
                f"⏰ Command is on cooldown. Try again in {error.retry_after:.1f} seconds."
            )
        elif isinstance(error, commands.MissingPermissions):
            await self.safe_send_message(
                ctx.channel,
                "❌ You don't have permission to use this command."
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await self.safe_send_message(
                ctx.channel,
                "❌ I don't have the required permissions to execute this command."
            )
        else:
            await self.safe_send_message(
                ctx.channel,
                "❌ An error occurred while processing your command. Please try again later."
            )
    
    @retry_with_backoff(max_retries=Config.MAX_RETRY_ATTEMPTS, base_delay=Config.RETRY_BASE_DELAY, max_delay=Config.RETRY_MAX_DELAY)
    async def safe_send_message(self, channel, content, **kwargs):
        """Safely send a message with retry logic"""
        return await channel.send(content, **kwargs)
    
    @retry_with_backoff(max_retries=Config.MAX_RETRY_ATTEMPTS, base_delay=Config.RETRY_BASE_DELAY, max_delay=Config.RETRY_MAX_DELAY)
    async def safe_edit_message(self, message, content, **kwargs):
        """Safely edit a message with retry logic"""
        return await message.edit(content=content, **kwargs)
    
    def _update_activity_tracking(self, message):
        """Update user and guild activity tracking"""
        current_time = time.time()
        
        # Update user activity
        user_id = message.author.id
        self.user_activity[user_id]['last_activity'] = current_time
        self.user_activity[user_id]['message_count'] += 1
        
        # Update guild activity
        if message.guild:
            guild_id = message.guild.id
            self.guild_activity[guild_id]['last_activity'] = current_time
            self.guild_activity[guild_id]['message_count'] += 1
    
    def _generate_cache_key(self, question: str) -> str:
        """Generate a cache key for a question"""
        normalized = question.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    @tasks.loop(seconds=30)
    async def monitor_connection(self):
        """Monitor bot connection health"""
        try:
            current_time = time.time()
            
            # Check if we're still connected
            if not self.bot.is_ready():
                logger.warning("Bot is not ready during connection monitoring")
                self.bot.connection_issues += 1
                return
            
            # Check latency
            latency = self.bot.latency * 1000
            if latency > 1000:  # More than 1 second
                logger.warning(f"High latency detected: {latency:.0f}ms")
                self.bot.connection_issues += 1
            
            # Check memory usage
            try:
                import psutil
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                self.bot.memory_usage_history.append(memory_mb)
                
                if memory_mb > 500:  # More than 500MB
                    logger.warning(f"High memory usage: {memory_mb:.1f}MB")
            except ImportError:
                pass
            
            # Update last heartbeat
            self.last_heartbeat = current_time
            
        except Exception as e:
            logger.error(f"Error during connection monitoring: {e}")
    
    @monitor_connection.before_loop
    async def before_monitor_connection(self):
        """Wait until the bot is ready before starting monitoring"""
        await self.bot.wait_until_ready()
    
    @tasks.loop(minutes=5)
    async def cleanup_activity_data(self):
        """Clean up old activity data to prevent memory bloat"""
        try:
            current_time = time.time()
            cutoff_time = current_time - 3600  # 1 hour ago
            
            # Clean up user activity
            expired_users = [
                user_id for user_id, data in self.user_activity.items()
                if data['last_activity'] < cutoff_time
            ]
            for user_id in expired_users:
                del self.user_activity[user_id]
            
            # Clean up guild activity
            expired_guilds = [
                guild_id for guild_id, data in self.guild_activity.items()
                if data['last_activity'] < cutoff_time
            ]
            for guild_id in expired_guilds:
                del self.guild_activity[guild_id]
            
            # Clean up old messages from history
            cutoff_timestamp = current_time - 1800  # 30 minutes ago
            self.message_history = deque(
                [msg for msg in self.message_history if msg['timestamp'] > cutoff_timestamp],
                maxlen=1000
            )
            
            logger.debug(f"Cleaned up activity data: {len(expired_users)} users, {len(expired_guilds)} guilds")
            
        except Exception as e:
            logger.error(f"Error during activity cleanup: {e}")
    
    @cleanup_activity_data.before_loop
    async def before_cleanup_activity_data(self):
        """Wait until the bot is ready before starting cleanup"""
        await self.bot.wait_until_ready()
    
    def get_activity_stats(self) -> Dict[str, Any]:
        """Get activity statistics"""
        current_time = time.time()
        
        # Calculate active users (active in last 10 minutes)
        active_users = sum(
            1 for data in self.user_activity.values()
            if current_time - data['last_activity'] < 600
        )
        
        # Calculate active guilds (active in last 10 minutes)
        active_guilds = sum(
            1 for data in self.guild_activity.values()
            if current_time - data['last_activity'] < 600
        )
        
        return {
            'total_users_tracked': len(self.user_activity),
            'total_guilds_tracked': len(self.guild_activity),
            'active_users': active_users,
            'active_guilds': active_guilds,
            'total_events_processed': self.event_count,
            'avg_event_processing_time': sum(self.event_times) / len(self.event_times) if self.event_times else 0,
            'message_history_size': len(self.message_history)
        }

async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(ElderScrollsEvents(bot))