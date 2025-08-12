import discord
from discord.ext import commands
import asyncio
import logging
import os
from datetime import datetime

from config import Config
from online_search import OnlineSearchEngine
from llm_client import LLMClientFactory, RAGProcessor
from background_tasks import BackgroundTaskManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ElderScrollsLoreBot(commands.Bot):
    """Discord bot for Elder Scrolls Lore with online search capabilities"""
    
    def __init__(self):
        # Initialize bot with command prefix '!'
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None  # We'll create our own help command
        )
        
        # Bot state
        self.search_engine = None
        self.rag_processor = None
        self.initialized = False
        self.start_time = None
        self.error_log = []
        
        # Initialize background task manager
        self.background_manager = BackgroundTaskManager(self)
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Setting up Elder Scrolls Lore Discord Bot...")
        
        # Load cogs
        await self.load_extension('commands')
        await self.load_extension('events')
        
        # Initialize bot components
        if not await self.initialize():
            logger.error("Failed to initialize bot components")
            raise RuntimeError("Bot initialization failed")
    
    async def initialize(self):
        """Initialize the bot components"""
        try:
            logger.info("Initializing Elder Scrolls Lore Bot with online search...")
            
            # Initialize online search engine
            self.search_engine = OnlineSearchEngine()
            if not await self.search_engine.initialize():
                logger.error("Failed to initialize online search engine")
                return False
            
            # Initialize LLM client and RAG processor
            llm_client = LLMClientFactory.create_client()
            self.rag_processor = RAGProcessor(llm_client)
            
            self.initialized = True
            self.start_time = datetime.now()
            logger.info("Bot initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Bot initialization failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources when bot shuts down"""
        # Stop background tasks
        if hasattr(self, 'background_manager'):
            self.background_manager.stop_all_tasks()
        
        # Cleanup search engine
        if self.search_engine:
            await self.search_engine.close()

async def main():
    """Main function to run the bot"""
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
        # Start the bot
        logger.info("Starting Elder Scrolls Lore Discord Bot...")
        await bot.start(discord_token)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested...")
    except Exception as e:
        logger.error(f"Bot startup failed: {e}")
    finally:
        # Cleanup resources
        await bot.cleanup()
        logger.info("Bot shutdown complete.")

if __name__ == "__main__":
    asyncio.run(main())