import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import nest_asyncio
import time
from functools import wraps

# Patch asyncio to allow nested event loops
nest_asyncio.apply()

from config import Config
from online_search import OnlineSearchEngine
from llm_client import LLMClientFactory, RAGProcessor

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
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

class ElderScrollsLoreBot:
    """Main Telegram bot class for Elder Scrolls Lore Bot with online search capabilities"""
    
    def __init__(self):
        self.search_engine = None
        self.rag_processor = None
        self.initialized = False
        
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
            logger.info("Bot initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Bot initialization failed: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources when bot shuts down"""
        if self.search_engine:
            await self.search_engine.close()
    
    @retry_with_backoff(max_retries=Config.MAX_RETRY_ATTEMPTS, base_delay=Config.RETRY_BASE_DELAY, max_delay=Config.RETRY_MAX_DELAY)
    async def safe_reply(self, message, text, **kwargs):
        """Safely send a reply with retry logic"""
        return await message.reply_text(text, **kwargs)
    
    @retry_with_backoff(max_retries=Config.MAX_RETRY_ATTEMPTS, base_delay=Config.RETRY_BASE_DELAY, max_delay=Config.RETRY_MAX_DELAY)
    async def safe_send_chat_action(self, bot, chat_id, action):
        """Safely send chat action with retry logic"""
        return await bot.send_chat_action(chat_id=chat_id, action=action)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
🌟 Welcome to the Elder Scrolls Lore Bot! 🌟

I'm your guide to the vast world of Tamriel and beyond. Ask me anything about:

• Characters and NPCs
• Locations and cities
• Historical events
• Magic and spells
• Races and cultures
• Artifacts and weapons
• And much more!

Use /ask followed by your question to get started.

Example: `/ask Who is Tiber Septim?`

Use /help for more information.
        """
        
        await self.safe_reply(update.message, welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 **Elder Scrolls Lore Bot Help** 📚

**Commands:**
• `/start` - Welcome message and introduction
• `/help` - Show this help message
• `/ask <question>` - Ask a question about Elder Scrolls lore

**Examples:**
• `/ask Who is the Dragonborn?`
• `/ask What is the history of the Dark Elves?`
• `/ask Tell me about the Thalmor`
• `/ask What are the Nine Divines?`

**Features:**
• 🔍 **Online Search**: Searches multiple sources including Elder Scrolls Wiki, Hugging Face datasets, and Wikipedia
• 🤖 **AI-Powered**: Uses advanced language models for accurate and engaging responses
• ⚡ **Real-time**: Gets the latest information from online sources

**Tips:**
• Be specific in your questions for better answers
• I can answer questions about characters, locations, events, magic, and more
• If I don't have information on a topic, I'll let you know politely

**Current LLM Backend:** `{backend}`

Happy exploring, traveler! 🗡️⚔️
        """.format(backend=Config.get_llm_backend().value)
        
        await self.safe_reply(update.message, help_message, parse_mode='Markdown')
    
    async def ask_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ask command"""
        if not self.initialized:
            await self.safe_reply(
                update.message,
                "⚠️ Bot is still initializing. Please wait a moment and try again."
            )
            return
        
        # Extract question from command
        if not context.args:
            await self.safe_reply(
                update.message,
                "❓ Please provide a question after /ask.\n\nExample: `/ask Who is Tiber Septim?`",
                parse_mode='Markdown'
            )
            return
        
        question = " ".join(context.args)
        
        # Send typing indicator
        await self.safe_send_chat_action(context.bot, update.effective_chat.id, "typing")
        
        try:
            # Search for relevant passages using online search engine with timeout
            context_passages = await asyncio.wait_for(
                self.search_engine.search(question),
                timeout=Config.SEARCH_TIMEOUT
            )
            
            if not context_passages:
                response = "🤔 I searched multiple online sources but couldn't find specific information about that in the Elder Scrolls lore. Could you try rephrasing your question or ask about something else?"
            else:
                # Process question using RAG with timeout
                response = await asyncio.wait_for(
                    self.rag_processor.process_question(question, context_passages),
                    timeout=Config.LLM_TIMEOUT
                )
            
            # Send response with retry logic
            await self.safe_reply(update.message, response)
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout processing question '{question}'")
            await self.safe_reply(
                update.message,
                "⏰ Sorry, the request took too long to process. Please try again with a simpler question or try later."
            )
        except Exception as e:
            logger.error(f"Error processing question '{question}': {e}")
            await self.safe_reply(
                update.message,
                "❌ Sorry, I encountered an error while processing your question. Please try again later."
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages (treat as questions)"""
        if not self.initialized:
            await self.safe_reply(
                update.message,
                "⚠️ Bot is still initializing. Please wait a moment and try again."
            )
            return
        
        question = update.message.text
        
        # Send typing indicator
        await self.safe_send_chat_action(context.bot, update.effective_chat.id, "typing")
        
        try:
            # Search for relevant passages using online search engine with timeout
            context_passages = await asyncio.wait_for(
                self.search_engine.search(question),
                timeout=Config.SEARCH_TIMEOUT
            )
            
            if not context_passages:
                response = "🤔 I searched multiple online sources but couldn't find specific information about that in the Elder Scrolls lore. Could you try rephrasing your question or ask about something else?"
            else:
                # Process question using RAG with timeout
                response = await asyncio.wait_for(
                    self.rag_processor.process_question(question, context_passages),
                    timeout=Config.LLM_TIMEOUT
                )
            
            # Send response with retry logic
            await self.safe_reply(update.message, response)
            
        except asyncio.TimeoutError:
            logger.error(f"Timeout processing message '{question}'")
            await self.safe_reply(
                update.message,
                "⏰ Sorry, the request took too long to process. Please try again with a simpler question or try later."
            )
        except Exception as e:
            logger.error(f"Error processing message '{question}': {e}")
            await self.safe_reply(
                update.message,
                "❌ Sorry, I encountered an error while processing your question. Please try again later."
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors with improved resilience"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Only try to send error message if we have a valid update and message
        if update and update.effective_message:
            try:
                # Use retry logic for error message
                await self.safe_reply(
                    update.effective_message,
                    "❌ An error occurred while processing your request. Please try again later."
                )
            except Exception as error_handler_error:
                # If even the error handler fails, just log it and don't re-raise
                logger.error(f"Error handler itself failed: {error_handler_error}")
                # Don't re-raise to prevent cascading failures

async def main():
    """Main function to run the bot"""
    # Validate configuration
    config_errors = Config.validate_config()
    if config_errors:
        logger.error("Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        return
    
    # Create bot instance
    bot = ElderScrollsLoreBot()
    
    # Initialize bot components
    if not await bot.initialize():
        logger.error("Failed to initialize bot. Exiting.")
        return
    
    # Create application with increased timeout configuration
    application = (
        Application.builder()
        .token(Config.TELEGRAM_TOKEN)
        .read_timeout(Config.TELEGRAM_READ_TIMEOUT)
        .write_timeout(Config.TELEGRAM_WRITE_TIMEOUT)
        .connect_timeout(Config.TELEGRAM_CONNECT_TIMEOUT)
        .pool_timeout(Config.TELEGRAM_POOL_TIMEOUT)
        .build()
    )
    
    # Add command handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("ask", bot.ask_command))
    
    # Add message handler for regular messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Add error handler
    application.add_error_handler(bot.error_handler)
    
    try:
        # Start the bot
        logger.info("Starting Elder Scrolls Lore Bot with online search capabilities...")
        await application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested...")
    finally:
        # Cleanup resources
        await bot.cleanup()
        logger.info("Bot shutdown complete.")

if __name__ == "__main__":
    asyncio.run(main())
    