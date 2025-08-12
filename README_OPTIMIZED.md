# Elder Scrolls Lore Bot - Optimized Version

A production-ready, scalable Discord bot for Elder Scrolls lore with AI-powered responses, online search capabilities, and comprehensive performance optimization.

## 🌟 Features

### Core Functionality
- **AI-Powered Responses**: Uses advanced language models (OpenRouter, Ollama, LM Studio) for accurate and engaging lore answers
- **Multi-Source Search**: Searches Elder Scrolls Wiki, Hugging Face datasets, and Wikipedia for comprehensive information
- **Real-time Information**: Gets the latest information from online sources
- **Natural Language Processing**: Understands questions in natural language

### Performance & Security
- **Efficient Async Handling**: Non-blocking event processing for smooth operation
- **Intelligent Caching**: Reduces redundant API calls with TTL-based caching
- **Rate Limiting**: Prevents abuse with user and guild-level rate limits
- **Error Handling**: Comprehensive error handling with retry logic
- **Security Levels**: Configurable security with guild/user allowlisting
- **Memory Management**: Automatic cleanup and optimization

### Monitoring & Maintenance
- **Performance Monitoring**: Real-time metrics and health checks
- **Background Tasks**: Automated maintenance and cleanup
- **Comprehensive Logging**: Structured logging with file rotation
- **Resource Optimization**: Memory and CPU usage monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- LLM API Key (OpenRouter recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd elder-scrolls-lore-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements_optimized.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the bot**
   ```bash
   python discord_bot_optimized.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required: Discord Bot Token
DISCORD_TOKEN=your_discord_bot_token_here

# Required: LLM Backend Configuration
LLM_BACKEND=openrouter  # openrouter, ollama, or lm_studio
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: Security Configuration
SECURITY_LEVEL=medium  # low, medium, high
ALLOWED_GUILDS=guild_id1,guild_id2  # Required for HIGH security
BLOCKED_USERS=user_id1,user_id2

# Optional: Rate Limiting
USER_RATE_LIMIT=5
USER_RATE_WINDOW=60.0
GUILD_RATE_LIMIT=20
GUILD_RATE_WINDOW=60.0

# Optional: Performance Tuning
CACHE_MAX_SIZE=500
CACHE_DEFAULT_TTL=600
SEARCH_TIMEOUT=45.0
LLM_TIMEOUT=30.0

# Optional: Logging
LOG_LEVEL=INFO
LOG_FILE=discord_bot.log
```

### Security Levels

- **LOW**: No restrictions, logs all activity
- **MEDIUM**: Standard rate limiting, logs suspicious activity
- **HIGH**: Guild allowlisting required, strict rate limiting

## 📚 Commands

### User Commands
- `!start` - Welcome message and introduction
- `!help` - Show help information
- `!ask <question>` - Ask a question about Elder Scrolls lore
- `!stats` - Show your usage statistics

### Admin Commands
- `!debug` - Show bot status and performance information
- `!cache info` - Show cache information
- `!cache clear` - Clear the cache (admin only)

### Natural Language
You can also ask questions directly without using `!ask`:
```
Who is Tiber Septim?
What is the history of the Dark Elves?
Tell me about the Thalmor
```

## 🏗️ Architecture

### Core Components

1. **Main Bot (`discord_bot_optimized.py`)**
   - Handles Discord connection and event routing
   - Manages rate limiting and caching
   - Coordinates all bot components

2. **Commands (`commands_optimized.py`)**
   - Implements all bot commands
   - Handles user interactions
   - Manages command cooldowns

3. **Events (`events_optimized.py`)**
   - Processes Discord events
   - Handles natural language questions
   - Manages error handling

4. **Background Tasks (`background_tasks_optimized.py`)**
   - Performs maintenance tasks
   - Monitors system health
   - Optimizes performance

5. **Configuration (`config_optimized.py`)**
   - Manages all bot settings
   - Validates configuration
   - Handles security policies

### Performance Features

- **Rate Limiting**: Sliding window rate limiting per user and guild
- **Caching**: LRU cache with TTL for responses and search results
- **Async Processing**: Non-blocking event handling
- **Resource Monitoring**: Memory and CPU usage tracking
- **Error Recovery**: Automatic retry with exponential backoff

## 🔧 Advanced Configuration

### LLM Backend Options

#### OpenRouter (Recommended)
```env
LLM_BACKEND=openrouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

#### Ollama (Local)
```env
LLM_BACKEND=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

#### LM Studio (Local)
```env
LLM_BACKEND=lm_studio
LM_STUDIO_BASE_URL=http://localhost:1234
LM_STUDIO_MODEL=default
```

### Performance Tuning

#### Cache Configuration
```env
CACHE_MAX_SIZE=1000        # Maximum cache entries
CACHE_DEFAULT_TTL=600      # Default TTL in seconds
CACHE_RESPONSE_TTL=1800    # Response cache TTL
```

#### Rate Limiting
```env
USER_RATE_LIMIT=10         # Requests per user per window
USER_RATE_WINDOW=60.0      # Window in seconds
GUILD_RATE_LIMIT=50        # Requests per guild per window
GUILD_RATE_WINDOW=60.0     # Window in seconds
```

#### Timeouts
```env
SEARCH_TIMEOUT=60.0        # Search operation timeout
LLM_TIMEOUT=45.0          # LLM response timeout
REQUEST_TIMEOUT=30        # HTTP request timeout
```

## 📊 Monitoring

### Performance Metrics

The bot tracks various performance metrics:
- Request count and success rate
- Average response times
- Memory and CPU usage
- Cache hit rates
- Error rates and types

### Health Checks

Automatic health checks run every 30 minutes:
- Bot connection status
- Search engine health
- Memory usage monitoring
- Latency tracking

### Logging

Structured logging with multiple levels:
- **INFO**: Normal operations
- **WARNING**: Performance issues
- **ERROR**: Errors and failures
- **DEBUG**: Detailed debugging information

Log files are automatically rotated when they reach 10MB.

## 🛡️ Security

### Rate Limiting
- Per-user rate limiting prevents spam
- Per-guild rate limiting prevents server abuse
- Configurable limits and windows

### Access Control
- Guild allowlisting for high security
- User blocking capabilities
- Admin-only commands

### Data Protection
- No sensitive data stored in logs
- Secure environment variable handling
- Configurable data retention

## 🔄 Maintenance

### Background Tasks

The bot runs several background tasks:
- **Error Cleanup**: Removes old error logs (hourly)
- **Health Checks**: Monitors system health (30 min)
- **Search Engine Maintenance**: Optimizes search (6 hours)
- **Performance Monitoring**: Tracks metrics (5 min)
- **Cache Optimization**: Manages cache (15 min)
- **Memory Cleanup**: Garbage collection (10 min)

### Manual Maintenance

Export performance data:
```python
# In your bot code
await bot.background_manager.export_performance_data("performance_report.json")
```

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check Discord token validity
   - Verify bot permissions
   - Check logs for errors

2. **Slow responses**
   - Monitor rate limits
   - Check LLM API status
   - Review cache configuration

3. **High memory usage**
   - Reduce cache size
   - Enable memory cleanup
   - Monitor background tasks

### Debug Commands

Use `!debug` to get comprehensive bot status:
- Connection status
- Performance metrics
- Recent errors
- Configuration summary

### Log Analysis

Check log files for detailed information:
```bash
tail -f discord_bot.log
grep "ERROR" discord_bot.log
```

## 📈 Scaling

### Horizontal Scaling
- Multiple bot instances can run simultaneously
- Use Redis for shared caching (optional)
- Load balancer for Discord connections

### Vertical Scaling
- Increase cache size for more memory
- Adjust rate limits for higher throughput
- Optimize LLM backend configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements_optimized.txt
pip install pytest pytest-asyncio

# Run tests
pytest tests/

# Run with debug logging
LOG_LEVEL=DEBUG python discord_bot_optimized.py
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Elder Scrolls Wiki for lore content
- Hugging Face for datasets and models
- Discord.py community for the excellent framework
- OpenRouter for AI model access

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting section

---

**May the Nine Divines guide your path!** 🗡️⚔️