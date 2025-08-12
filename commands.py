import discord
from discord.ext import commands
import asyncio
import logging
from datetime import datetime
import traceback

from config import Config

logger = logging.getLogger(__name__)

class ElderScrollsCommands(commands.Cog):
    """Cog containing all Elder Scrolls Lore Bot commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.ask_cooldown = commands.CooldownMapping.from_cooldown(
            rate=3, per=60.0, type=commands.BucketType.user
        )
    
    @commands.command(name='start')
    async def start_command(self, ctx):
        """Handle !start command"""
        welcome_message = """
🌟 **Welcome to the Elder Scrolls Lore Bot!** 🌟

I'm your guide to the vast world of Tamriel and beyond. Ask me anything about:

• Characters and NPCs
• Locations and cities
• Historical events
• Magic and spells
• Races and cultures
• Artifacts and weapons
• And much more!

Use `!ask` followed by your question to get started.

**Example:** `!ask Who is Tiber Septim?`

Use `!help` for more information.
        """
        
        embed = discord.Embed(
            title="Welcome to Elder Scrolls Lore Bot!",
            description=welcome_message,
            color=discord.Color.blue()
        )
        embed.set_footer(text="May the Nine Divines guide your path!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Handle !help command"""
        help_message = """
📚 **Elder Scrolls Lore Bot Help** 📚

**Commands:**
• `!start` - Welcome message and introduction
• `!help` - Show this help message
• `!ask <question>` - Ask a question about Elder Scrolls lore
• `!debug` - Show bot status and debug information

**Examples:**
• `!ask Who is the Dragonborn?`
• `!ask What is the history of the Dark Elves?`
• `!ask Tell me about the Thalmor`
• `!ask What are the Nine Divines?`

**Features:**
• 🔍 **Online Search**: Searches multiple sources including Elder Scrolls Wiki, Hugging Face datasets, and Wikipedia
• 🤖 **AI-Powered**: Uses advanced language models for accurate and engaging responses
• ⚡ **Real-time**: Gets the latest information from online sources

**Tips:**
• Be specific in your questions for better answers
• I can answer questions about characters, locations, events, magic, and more
• If I don't have information on a topic, I'll let you know politely
• You can also just type your question without using `!ask`

**Current LLM Backend:** `{backend}`

Happy exploring, traveler! 🗡️⚔️
        """.format(backend=Config.get_llm_backend().value)
        
        embed = discord.Embed(
            title="Elder Scrolls Lore Bot Help",
            description=help_message,
            color=discord.Color.green()
        )
        embed.set_footer(text="Use !ask followed by your question to get started!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='ask')
    async def ask_command(self, ctx, *, question: str = None):
        """Handle !ask command"""
        # Check cooldown
        bucket = self.ask_cooldown.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await ctx.send(f"⏰ Please wait {retry_after:.1f} seconds before asking another question.")
            return
        
        if not self.bot.initialized:
            await ctx.send("⚠️ Bot is still initializing. Please wait a moment and try again.")
            return
        
        if not question:
            await ctx.send("❓ Please provide a question after `!ask`.\n\n**Example:** `!ask Who is Tiber Septim?`")
            return
        
        # Show typing indicator
        async with ctx.channel.typing():
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
                
                # Send response
                await ctx.send(response)
                
            except asyncio.TimeoutError:
                logger.error(f"Timeout processing question '{question}'")
                await ctx.send("⏰ Sorry, the request took too long to process. Please try again with a simpler question or try later.")
            except Exception as e:
                logger.error(f"Error processing question '{question}': {e}")
                await ctx.send("❌ Sorry, I encountered an error while processing your question. Please try again later.")
    
    @commands.command(name='debug')
    async def debug_command(self, ctx):
        """Handle !debug command - show bot status and debug information"""
        if not self.bot.start_time:
            uptime = "Unknown"
        else:
            uptime_delta = datetime.now() - self.bot.start_time
            uptime = str(uptime_delta).split('.')[0]  # Remove microseconds
        
        # Get recent errors (last 10)
        recent_errors = self.bot.error_log[-10:] if self.bot.error_log else []
        error_summary = "\n".join([f"• {error['time']}: {error['error']}" for error in recent_errors])
        if not error_summary:
            error_summary = "No recent errors"
        
        debug_info = f"""
🤖 **Bot Debug Information**

**Status:**
• **Initialized:** {'✅ Yes' if self.bot.initialized else '❌ No'}
• **Uptime:** {uptime}
• **Connected Guilds:** {len(self.bot.guilds)}
• **Latency:** {round(self.bot.latency * 1000)}ms

**Configuration:**
• **LLM Backend:** {Config.get_llm_backend().value}
• **Search Engine:** {'✅ Active' if self.bot.search_engine else '❌ Inactive'}
• **RAG Processor:** {'✅ Active' if self.bot.rag_processor else '❌ Inactive'}

**Recent Errors (Last 10):**
{error_summary}

**Memory Usage:** {self._get_memory_usage()}
        """
        
        embed = discord.Embed(
            title="Bot Debug Information",
            description=debug_info,
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    def _get_memory_usage(self):
        """Get approximate memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            return f"{memory_mb:.1f} MB"
        except ImportError:
            return "Unknown (psutil not available)"

async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(ElderScrollsCommands(bot))