# Elder Scrolls Lore Bot

A sophisticated Telegram bot that answers questions about The Elder Scrolls universe using online data retrieval and AI-powered responses.

## 🌟 Features

- **🔍 Multi-Source Online Search**: Searches multiple sources including:
  - Hugging Face Elder Scrolls Wiki Dataset
  - Elder Scrolls Wiki (UESP) API
  - Wikipedia for Elder Scrolls content
  - Polite web scraping as fallback
- **🤖 AI-Powered Responses**: Uses advanced language models (OpenRouter, Ollama, or LM Studio)
- **⚡ Real-time Information**: Gets the latest information from online sources
- **🎯 Smart Context Retrieval**: Implements three-tier search strategy for optimal results
- **🛡️ Rate Limiting**: Polite scraping with configurable delays
- **📱 Telegram Integration**: Full Telegram bot functionality with commands

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- LLM API access (OpenRouter, Ollama, or LM Studio)

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
   # Required: Telegram Bot Token
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   
   # LLM Backend Configuration (choose one)
   LLM_BACKEND=openrouter  # or "ollama" or "lm_studio"
   
   # OpenRouter Configuration (if using OpenRouter)
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
   
   # Ollama Configuration (if using Ollama)
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama2
   
   # LM Studio Configuration (if using LM Studio)
   LM_STUDIO_BASE_URL=http://localhost:1234
   LM_STUDIO_MODEL=default
   
   # Optional: Rate limiting and search configuration
   REQUEST_DELAY=1.0
   MAX_RETRIES=3
   REQUEST_TIMEOUT=30
   MAX_SEARCH_RESULTS=5
   ```

4. **Run the bot**
   ```bash
   python telegram_bot.py
   ```

## 🔧 Configuration

### LLM Backend Options

#### 1. OpenRouter (Recommended)
- **Pros**: High-quality models, no local setup required
- **Cons**: Requires API key, usage costs
- **Setup**: Get API key from [OpenRouter](https://openrouter.ai/)

#### 2. Ollama (Local)
- **Pros**: Free, runs locally, privacy-focused
- **Cons**: Requires local setup, limited model quality
- **Setup**: Install [Ollama](https://ollama.ai/) and download a model

#### 3. LM Studio (Local)
- **Pros**: Free, runs locally, good model support
- **Cons**: Requires local setup
- **Setup**: Install [LM Studio](https://lmstudio.ai/) and load a model

### Search Configuration

The bot implements a three-tier search strategy:

1. **Tier 1**: Hugging Face Datasets API
   - Searches the Elder Scrolls Wiki dataset
   - Uses semantic similarity with embeddings
   - Fastest and most reliable

2. **Tier 2**: Elder Scrolls Wiki API
   - Searches UESP (Unofficial Elder Scrolls Pages)
   - Uses official API endpoints
   - Good for recent content

3. **Tier 3**: Wikipedia Integration
   - Searches for Elder Scrolls related content
   - Filters for relevant keywords
   - Extracts summaries from matching pages

### Web Scraping (Fallback)
- Polite scraping with rate limiting
- User-agent identification
- Content extraction and cleaning
- Respects robots.txt and site policies

## 📱 Bot Commands

- `/start` - Welcome message and introduction
- `/help` - Show help and available commands
- `/ask <question>` - Ask a question about Elder Scrolls lore

### Example Questions

- "Who is the Dragonborn?"
- "What is the history of the Dark Elves?"
- "Tell me about the Thalmor"
- "What are the Nine Divines?"
- "Explain the events of the Great War"
- "Who is Tiber Septim?"

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram Bot  │───▶│  Online Search   │───▶│  LLM Backend    │
│                 │    │     Engine       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Search Sources  │
                       │                  │
                       │ • Hugging Face   │
                       │ • UESP Wiki      │
                       │ • Wikipedia      │
                       │ • Web Scraping   │
                       └──────────────────┘
```

### Components

1. **`telegram_bot.py`** - Main bot application with command handlers
2. **`online_search.py`** - Multi-source search engine implementation
3. **`llm_client.py`** - LLM backend integration (OpenRouter/Ollama/LM Studio)
4. **`config.py`** - Configuration management and validation

## 🔍 Search Strategy Details

### Hugging Face Datasets API
- Loads Elder Scrolls Wiki dataset on-demand
- Uses sentence transformers for semantic search
- Returns top-k most relevant passages

### Elder Scrolls Wiki API
- Searches UESP using MediaWiki API
- Extracts relevant snippets from search results
- Handles HTML content cleaning

### Wikipedia Integration
- Searches for Elder Scrolls related content
- Filters for relevant keywords
- Extracts summaries from matching pages

### Web Scraping (Fallback)
- Polite scraping with rate limiting
- User-agent identification
- Content extraction and cleaning
- Respects robots.txt and site policies

## 🛡️ Error Handling

The bot includes comprehensive error handling:

- **API Failures**: Graceful fallback to alternative sources
- **Rate Limiting**: Configurable delays between requests
- **Network Issues**: Retry logic with exponential backoff
- **Content Validation**: Minimum/maximum content length checks
- **User Feedback**: Clear error messages for users

## 📊 Performance Considerations

- **Async Operations**: All network requests are asynchronous
- **Connection Pooling**: Reuses HTTP connections for efficiency
- **Caching**: Embedding model loaded once and reused
- **Rate Limiting**: Prevents overwhelming external APIs
- **Timeout Handling**: Prevents hanging requests

## 🧪 Testing

Run the test suite:
```bash
python test_bot.py
```

The test suite includes:
- Configuration validation
- Search engine functionality
- LLM client integration
- Error handling scenarios

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [UESP](https://en.uesp.net/) - Unofficial Elder Scrolls Pages
- [Hugging Face](https://huggingface.co/) - Datasets and models
- [OpenRouter](https://openrouter.ai/) - LLM API access
- [Ollama](https://ollama.ai/) - Local LLM hosting
- [LM Studio](https://lmstudio.ai/) - Local LLM interface

## 🆘 Support

If you encounter issues:

1. Check the configuration in your `.env` file
2. Ensure all dependencies are installed
3. Verify your API keys are valid
4. Check the logs for detailed error messages
5. Open an issue on GitHub with relevant details

---

**Happy exploring, traveler!** 🗡️⚔️