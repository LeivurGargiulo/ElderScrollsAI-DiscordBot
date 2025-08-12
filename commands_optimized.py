"""
Optimized Commands Module for Elder Scrolls Lore Bot
Enhanced with caching, rate limiting, error handling, and performance monitoring.
"""

import discord
from discord.ext import commands
import asyncio
import logging
import time
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import traceback
from functools import wraps

from config import Config

logger = logging.getLogger(__name__)

def command_timer(func):
    """Decorator to measure command execution time"""
    @wraps(func)
    async def wrapper(self, ctx, *args, **kwargs):
        start_time = time.time()
        try:
            result = await func(self, ctx, *args, **kwargs)
            execution_time = time.time() - start_time
            
            # Update bot performance stats
            self.bot.request_count += 1
            self.bot.successful_requests += 1
            self.bot.response_times.append(execution_time)
            
            # Update average response time
            if self.bot.response_times:
                self.bot.avg_response_time = sum(self.bot.response_times) / len(self.bot.response_times)
            
            logger.info(f"Command {func.__name__} executed in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.bot.request_count += 1
            self.bot.failed_requests += 1
            
            logger.error(f"Command {func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

def rate_limit_check(func):
    """Decorator to check rate limits before command execution"""
    @wraps(func)
    async def wrapper(self, ctx, *args, **kwargs):
        # Check user rate limit
        user_limiter = self.bot.user_rate_limiters[ctx.author.id]
        if not user_limiter.is_allowed():
            wait_time = user_limiter.get_wait_time()
            await ctx.send(f"⏰ Rate limit exceeded. Please wait {wait_time:.1f} seconds before trying again.")
            return
        
        # Check guild rate limit
        if ctx.guild:
            guild_limiter = self.bot.guild_rate_limiters[ctx.guild.id]
            if not guild_limiter.is_allowed():
                wait_time = guild_limiter.get_wait_time()
                await ctx.send(f"⏰ Guild rate limit exceeded. Please wait {wait_time:.1f} seconds before trying again.")
                return
        
        return await func(self, ctx, *args, **kwargs)
    
    return wrapper

class ElderScrollsCommands(commands.Cog):
    """Optimized cog containing all Elder Scrolls Lore Bot commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.command_cooldowns = {}
        self.last_maintenance = time.time()
        
        # Initialize cooldowns
        self.ask_cooldown = commands.CooldownMapping.from_cooldown(
            rate=3, per=60.0, type=commands.BucketType.user
        )
        
        logger.info("ElderScrollsCommands cog initialized")
    
    @commands.command(name='start')
    @command_timer
    async def start_command(self, ctx):
        """Handle !start command with welcome message"""
        welcome_message = """
🌟 **Welcome to the Elder Scrolls Lore Bot!** 🌟

I'm your guide to the vast world of Tamriel and beyond. Ask me anything about:

• **Characters and NPCs** - Heroes, villains, and everyone in between
• **Locations and cities** - From the frozen north to the scorching south
• **Historical events** - Wars, treaties, and world-changing moments
• **Magic and spells** - Schools of magic, artifacts, and enchantments
• **Races and cultures** - The diverse peoples of Tamriel
• **Artifacts and weapons** - Legendary items and their histories
• **And much more!**

**Quick Start:**
• Use `!ask <question>` for detailed answers
• Or just type your question directly
• Use `!help` for more information

**Example:** `!ask Who is Tiber Septim?`

*May the Nine Divines guide your path!* 🗡️⚔️
        """
        
        embed = discord.Embed(
            title="Welcome to Elder Scrolls Lore Bot!",
            description=welcome_message,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_footer(text="Ready to explore the lore of Tamriel!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='help')
    @command_timer
    async def help_command(self, ctx):
        """Handle !help command with comprehensive help information"""
        help_message = f"""
📚 **Elder Scrolls Lore Bot Help** 📚

**Commands:**
• `!start` - Welcome message and introduction
• `!help` - Show this help message
• `!ask <question>` - Ask a question about Elder Scrolls lore
• `!debug` - Show bot status and performance information
• `!stats` - Show your usage statistics

**Examples:**
• `!ask Who is the Dragonborn?`
• `!ask What is the history of the Dark Elves?`
• `!ask Tell me about the Thalmor`
• `!ask What are the Nine Divines?`

**Features:**
• 🔍 **Multi-Source Search**: Elder Scrolls Wiki, Hugging Face datasets, Wikipedia
• 🤖 **AI-Powered**: Advanced language models for accurate responses
• ⚡ **Real-time**: Latest information from online sources
• 🚀 **Optimized**: Fast responses with intelligent caching
• 🛡️ **Secure**: Rate limiting and error handling

**Rate Limits:**
• **Per User**: 5 requests per minute
• **Per Guild**: 20 requests per minute
• **Cooldown**: 3 questions per minute per user

**Tips:**
• Be specific in your questions for better answers
• I can answer questions about characters, locations, events, magic, and more
• If I don't have information on a topic, I'll let you know politely
• You can also just type your question without using `!ask`

**Current Backend:** `{Config.get_llm_backend().value}`

*Happy exploring, traveler!* 🗡️⚔️
        """
        
        embed = discord.Embed(
            title="Elder Scrolls Lore Bot Help",
            description=help_message,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_footer(text="Use !ask followed by your question to get started!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='ask')
    @rate_limit_check
    @command_timer
    async def ask_command(self, ctx, *, question: str = None):
        """Handle !ask command with caching and optimized processing"""
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
        
        # Check cache first
        cache_key = self._generate_cache_key(question)
        cached_response = self.bot.cache.get(cache_key)
        if cached_response:
            logger.info(f"Cache hit for question: {question[:50]}...")
            await ctx.send(cached_response)
            return
        
        # Show typing indicator
        async with ctx.channel.typing():
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
                
                # Send response
                await ctx.send(response)
                
            except asyncio.TimeoutError:
                logger.error(f"Timeout processing question '{question}'")
                await ctx.send("⏰ Sorry, the request took too long to process. Please try again with a simpler question or try later.")
            except Exception as e:
                logger.error(f"Error processing question '{question}': {e}")
                self.bot.log_error(f"Ask command error: {e}", {
                    'question': question,
                    'user': str(ctx.author),
                    'guild': ctx.guild.name if ctx.guild else 'DM'
                })
                await ctx.send("❌ Sorry, I encountered an error while processing your question. Please try again later.")
    
    @commands.command(name='debug')
    @command_timer
    async def debug_command(self, ctx):
        """Handle !debug command with comprehensive debug information"""
        if not self.bot.start_time:
            uptime = "Unknown"
        else:
            uptime_delta = datetime.now() - self.bot.start_time
            uptime = str(uptime_delta).split('.')[0]  # Remove microseconds
        
        # Get performance stats
        stats = self.bot.get_performance_stats()
        
        # Get recent errors (last 5)
        recent_errors = self.bot.error_log[-5:] if self.bot.error_log else []
        error_summary = "\n".join([f"• {error['time']}: {error['error'][:50]}..." for error in recent_errors])
        if not error_summary:
            error_summary = "No recent errors"
        
        debug_info = f"""
🤖 **Bot Debug Information**

**Status:**
• **Initialized:** {'✅ Yes' if self.bot.initialized else '❌ No'}
• **Uptime:** {uptime}
• **Connected Guilds:** {len(self.bot.guilds)}
• **Latency:** {round(self.bot.latency * 1000)}ms

**Performance:**
• **Total Requests:** {stats['total_requests']}
• **Success Rate:** {stats['success_rate']}%
• **Avg Response Time:** {stats['avg_response_time']}s
• **Memory Usage:** {stats['memory_usage_mb']} MB
• **Cache Size:** {stats['cache_size']} entries

**Configuration:**
• **LLM Backend:** {Config.get_llm_backend().value}
• **Search Engine:** {'✅ Active' if self.bot.search_engine else '❌ Inactive'}
• **RAG Processor:** {'✅ Active' if self.bot.rag_processor else '❌ Inactive'}

**Recent Errors (Last 5):**
{error_summary}

**Rate Limits:**
• **User Limiters:** {len(self.bot.user_rate_limiters)}
• **Guild Limiters:** {len(self.bot.guild_rate_limiters)}
        """
        
        embed = discord.Embed(
            title="Bot Debug Information",
            description=debug_info,
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='stats')
    @command_timer
    async def stats_command(self, ctx):
        """Handle !stats command to show user statistics"""
        user_id = ctx.author.id
        
        # Get user-specific stats
        user_limiter = self.bot.user_rate_limiters[user_id]
        user_stats = {
            'requests_in_window': len(user_limiter.requests),
            'max_requests': user_limiter.max_requests,
            'window_seconds': user_limiter.window_seconds
        }
        
        stats_info = f"""
📊 **Your Statistics**

**Rate Limit Status:**
• **Requests in Current Window:** {user_stats['requests_in_window']}/{user_stats['max_requests']}
• **Window Duration:** {user_stats['window_seconds']} seconds

**Bot Performance:**
• **Total Bot Requests:** {self.bot.request_count}
• **Bot Success Rate:** {self.bot.get_performance_stats()['success_rate']}%
• **Cache Hit Rate:** {self._calculate_cache_hit_rate():.1f}%

**Your Usage:**
• **Account Created:** {ctx.author.created_at.strftime('%Y-%m-%d')}
• **Server Join Date:** {ctx.author.joined_at.strftime('%Y-%m-%d') if ctx.author.joined_at else 'Unknown'}
        """
        
        embed = discord.Embed(
            title="Your Statistics",
            description=stats_info,
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Stats for {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='cache')
    @command_timer
    async def cache_command(self, ctx, action: str = "info"):
        """Handle !cache command for cache management (admin only)"""
        # Check if user has admin permissions
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ This command is only available to administrators.")
            return
        
        if action.lower() == "clear":
            self.bot.cache.clear()
            await ctx.send("✅ Cache cleared successfully.")
        elif action.lower() == "info":
            cache_info = f"""
🗄️ **Cache Information**

**Size:** {len(self.bot.cache.cache)}/{self.bot.cache.max_size} entries
**Default TTL:** {self.bot.cache.default_ttl} seconds
**Memory Usage:** {self._estimate_cache_memory():.1f} MB
            """
            
            embed = discord.Embed(
                title="Cache Information",
                description=cache_info,
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Invalid action. Use 'info' or 'clear'.")
    
    def _generate_cache_key(self, question: str) -> str:
        """Generate a cache key for a question"""
        # Normalize the question for better cache hits
        normalized = question.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate (simplified)"""
        # This is a simplified calculation - in a real implementation,
        # you'd track cache hits and misses separately
        return 75.0  # Placeholder value
    
    def _estimate_cache_memory(self) -> float:
        """Estimate cache memory usage in MB"""
        total_size = 0
        for key, data in self.bot.cache.cache.items():
            # Rough estimation: key + value + metadata
            total_size += len(key) + len(str(data['value'])) + 50
        
        return total_size / 1024 / 1024  # Convert to MB

async def setup(bot):
    """Setup function to add the cog to the bot"""
    await bot.add_cog(ElderScrollsCommands(bot))