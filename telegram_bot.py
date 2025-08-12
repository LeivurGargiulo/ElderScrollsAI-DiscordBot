import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

from config import Config
from dataset_loader import ElderScrollsDatasetLoader
from llm_client import LLMClientFactory, RAGProcessor

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ElderScrollsLoreBot:
    """Main Telegram bot class for Elder Scrolls Lore Bot"""
    
    def __init__(self):
        self.dataset_loader = None
        self.rag_processor = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the bot components"""
        try:
            logger.info("Initializing Elder Scrolls Lore Bot...")
            
            # Initialize dataset loader
            self.dataset_loader = ElderScrollsDatasetLoader()
            if not self.dataset_loader.initialize():
                logger.error("Failed to initialize dataset loader")
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
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
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

**Tips:**
• Be specific in your questions for better answers
• I can answer questions about characters, locations, events, magic, and more
• If I don't have information on a topic, I'll let you know politely

**Current LLM Backend:** `{backend}`

Happy exploring, traveler! 🗡️⚔️
        """.format(backend=Config.get_llm_backend().value)
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def ask_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ask command"""
        if not self.initialized:
            await update.message.reply_text(
                "⚠️ Bot is still initializing. Please wait a moment and try again."
            )
            return
        
        # Extract question from command
        if not context.args:
            await update.message.reply_text(
                "❓ Please provide a question after /ask.\n\nExample: `/ask Who is Tiber Septim?`",
                parse_mode='Markdown'
            )
            return
        
        question = " ".join(context.args)
        
        # Send typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Search for relevant passages
            context_passages = self.dataset_loader.search(question)
            
            if not context_passages:
                response = "🤔 Hmm, I couldn't find anything on that in the Elder Scrolls lore. Could you try rephrasing your question or ask about something else?"
            else:
                # Process question using RAG
                response = self.rag_processor.process_question(question, context_passages)
            
            # Send response
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error processing question '{question}': {e}")
            await update.message.reply_text(
                "❌ Sorry, I encountered an error while processing your question. Please try again later."
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages (treat as questions)"""
        if not self.initialized:
            await update.message.reply_text(
                "⚠️ Bot is still initializing. Please wait a moment and try again."
            )
            return
        
        question = update.message.text
        
        # Send typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Search for relevant passages
            context_passages = self.dataset_loader.search(question)
            
            if not context_passages:
                response = "🤔 Hmm, I couldn't find anything on that in the Elder Scrolls lore. Could you try rephrasing your question or ask about something else?"
            else:
                # Process question using RAG
                response = self.rag_processor.process_question(question, context_passages)
            
            # Send response
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error processing message '{question}': {e}")
            await update.message.reply_text(
                "❌ Sorry, I encountered an error while processing your question. Please try again later."
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred while processing your request. Please try again later."
            )

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
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("ask", bot.ask_command))
    
    # Add message handler for regular messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Add error handler
    application.add_error_handler(bot.error_handler)
    
    # Start the bot
    logger.info("Starting Elder Scrolls Lore Bot...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    asyncio.run(main())