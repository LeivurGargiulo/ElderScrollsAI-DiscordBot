# Elder Scrolls Lore Discord Bot

A comprehensive Discord bot that provides detailed information about The Elder Scrolls universe using AI-powered search and response generation. This bot is a conversion from the original Telegram bot, maintaining all functionality while adapting to Discord's API and conventions.

## 🌟 Features

- **🔍 Multi-Source Search**: Searches Elder Scrolls Wiki, Hugging Face datasets, and Wikipedia
- **🤖 AI-Powered Responses**: Uses advanced language models (OpenRouter, Ollama, or LM Studio)
- **⚡ Real-time Information**: Gets the latest information from online sources
- **🎯 Smart Context**: Uses RAG (Retrieval-Augmented Generation) for accurate responses
- **🛡️ Robust Error Handling**: Comprehensive error handling with retry logic
- **📊 Debug & Monitoring**: Built-in debug commands and health monitoring
- **⚙️ Modular Architecture**: Clean, maintainable code structure with cogs

## 📋 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!start` | Welcome message and introduction | `!start` |
| `!help` | Show help and command information | `!help` |
| `!ask <question>` | Ask a question about Elder Scrolls lore | `!ask Who is Tiber Septim?` |
| `!debug` | Show bot status and debug information | `!debug` |

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
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   # Discord Bot Configuration
   DISCORD_TOKEN=your_discord_bot_token_here
   
   # LLM Backend Configuration (choose one)
   LLM_BACKEND=openrouter
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
   
   # Optional: Alternative LLM backends
   # OLLAMA_BASE_URL=http://localhost:11434
   # OLLAMA_MODEL=llama2
   # LM_STUDIO_BASE_URL=http://localhost:1234
   # LM_STUDIO_MODEL=default
   
   # Optional: Customize timeouts and retries
   SEARCH_TIMEOUT=45.0
   LLM_TIMEOUT=30.0
   MAX_RETRY_ATTEMPTS=2
   ```

4. **Create a Discord Bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the "Bot" section
   - Create a bot and copy the token
   - Add the bot to your server with appropriate permissions

5. **Run the bot**
   ```bash
   python discord_bot.py
   ```

## 🏗️ Architecture

The bot uses a modular architecture with the following components:

### Core Files

- **`discord_bot.py`**: Main bot class and entry point
- **`commands.py`**: Command handlers (cog)
- **`events.py`**: Event handlers (cog)
- **`background_tasks.py`**: Background task management
- **`config.py`**: Configuration management
- **`online_search.py`**: Multi-source search engine
- **`llm_client.py`**: LLM client implementations

### Key Components

1. **Search Engine**: Multi-tier search strategy
   - Hugging Face datasets
   - Elder Scrolls Wiki API
   - Wikipedia API

2. **RAG Processor**: Retrieval-Augmented Generation
   - Context retrieval from search results
   - AI-powered response generation
   - Multiple LLM backend support

3. **Background Tasks**: Automated maintenance
   - Error log cleanup
   - Health monitoring
   - Search engine maintenance

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Discord bot token | Required |
| `LLM_BACKEND` | LLM backend to use | `openrouter` |
| `OPENROUTER_API_KEY` | OpenRouter API key | Required for OpenRouter |
| `OPENROUTER_MODEL` | OpenRouter model | `anthropic/claude-3.5-sonnet` |
| `SEARCH_TIMEOUT` | Search operation timeout | `45.0` seconds |
| `LLM_TIMEOUT` | LLM response timeout | `30.0` seconds |
| `MAX_RETRY_ATTEMPTS` | Number of retry attempts | `2` |

### LLM Backends

The bot supports multiple LLM backends:

1. **OpenRouter** (Recommended)
   - Access to multiple AI models
   - Reliable and fast
   - Requires API key

2. **Ollama** (Local)
   - Run locally for privacy
   - No API costs
   - Requires local Ollama installation

3. **LM Studio** (Local)
   - Local model hosting
   - Custom model support
   - Requires LM Studio installation

## 🛡️ Error Handling & Resilience

The bot includes comprehensive error handling:

- **Retry Logic**: Exponential backoff for failed requests
- **Timeout Protection**: Configurable timeouts for all operations
- **Graceful Degradation**: Continues operation even if some components fail
- **Error Logging**: Detailed error tracking with context
- **User-Friendly Messages**: Clear error messages for users

## 📊 Monitoring & Debugging

### Debug Command

Use `!debug` to view:
- Bot uptime and status
- Connected guilds and latency
- LLM backend configuration
- Search engine status
- Recent error logs
- Memory usage

### Health Monitoring

The bot includes automatic health checks:
- Connection status monitoring
- Latency tracking
- Memory usage monitoring
- Search engine health checks

## 🔄 Background Tasks

The bot runs several background tasks:

1. **Error Cleanup** (Hourly)
   - Removes old error logs
   - Maintains performance

2. **Health Checks** (Every 30 minutes)
   - Monitors bot health
   - Detects issues early

3. **Search Engine Maintenance** (Every 6 hours)
   - Maintains search functionality
   - Updates cached data

## 🚀 Deployment

### Local Development

```bash
python discord_bot.py
```

### Production Deployment

1. **VPS/Cloud Deployment**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Set environment variables
   export DISCORD_TOKEN=your_token
   export OPENROUTER_API_KEY=your_key
   
   # Run with process manager (e.g., systemd, PM2)
   python discord_bot.py
   ```

2. **Docker Deployment**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   CMD ["python", "discord_bot.py"]
   ```

3. **Environment Variables for Production**
   ```env
   DISCORD_TOKEN=your_production_token
   OPENROUTER_API_KEY=your_production_key
   SEARCH_TIMEOUT=60.0
   LLM_TIMEOUT=45.0
   MAX_RETRY_ATTEMPTS=3
   ```

## 🔒 Security Considerations

- **Token Security**: Never commit Discord tokens to version control
- **API Key Protection**: Use environment variables for all sensitive data
- **Rate Limiting**: Built-in cooldowns prevent abuse
- **Input Validation**: All user input is validated and sanitized

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if `DISCORD_TOKEN` is set correctly
   - Verify bot has proper permissions
   - Check logs for error messages

2. **Search not working**
   - Verify internet connection
   - Check API keys are valid
   - Review timeout settings

3. **High memory usage**
   - Monitor with `!debug` command
   - Check for memory leaks in logs
   - Consider increasing server resources

### Logs

The bot provides detailed logging:
- Error tracking with stack traces
- Performance monitoring
- User interaction logs
- Background task status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Elder Scrolls Wiki for lore content
- Hugging Face for dataset hosting
- Discord.py community for the excellent library
- OpenRouter for AI model access

---

**Happy exploring, traveler!** 🗡️⚔️

For support or questions, please open an issue on the repository.