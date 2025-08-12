import discord
from discord.ext import commands, tasks
import asyncio
import logging
from datetime import datetime, timedelta
from functools import wraps

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

class ElderScrollsEvents(commands.Cog):
    """Cog containing all Elder Scrolls Lore Bot event handlers"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
        logger.info(f'Connected to {len(self.bot.guilds)} guilds')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Elder Scrolls lore | !help"
        )
        await self.bot.change_presence(activity=activity)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return
        
        # Process commands first
        await self.bot.process_commands(message)
        
        # If it's not a command and the bot is initialized, treat as a question
        if not message.content.startswith('!') and self.bot.initialized:
            await self.handle_question(message)
    
    async def handle_question(self, message):
        """Handle regular messages as questions"""
        if not self.bot.initialized:
            await self.safe_send_message(
                message.channel,
                "⚠️ Bot is still initializing. Please wait a moment and try again."
            )
            return
        
        question = message.content
        
        # Show typing indicator
        async with message.channel.typing():
            try:
                # Search for relevant passages using online search engine with timeout
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
                await self.safe_send_message(
                    message.channel,
                    "❌ Sorry, I encountered an error while processing your question. Please try again later."
                )
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Global error handler for commands"""
        # Log the error
        error_msg = f"Command error in {ctx.guild.name if ctx.guild else 'DM'} by {ctx.author}: {error}"
        logger.error(error_msg)
        
        # Add to error log
        self.bot.error_log.append({
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(error),
            'user': str(ctx.author),
            'guild': ctx.guild.name if ctx.guild else 'DM',
            'command': ctx.command.name if ctx.command else 'Unknown'
        })
        
        # Keep only last 100 errors
        if len(self.bot.error_log) > 100:
            self.bot.error_log = self.bot.error_log[-100:]
        
        # Send user-friendly error message
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
    
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the bot is ready"""
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

async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(ElderScrollsEvents(bot))