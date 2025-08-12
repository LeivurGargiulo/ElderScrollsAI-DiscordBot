# Elder Scrolls Lore Bot

A Telegram bot that answers questions about The Elder Scrolls universe using Retrieval-Augmented Generation (RAG) from the Elder Scrolls Wiki dataset.

## Features

- 🤖 **Telegram Bot Integration**: Easy-to-use bot with `/start`, `/help`, and `/ask` commands
- 🔍 **Semantic Search**: Uses FAISS and sentence-transformers for efficient passage retrieval
- 🧠 **Multiple LLM Backends**: Support for OpenRouter API, Ollama, and LM Studio
- 📚 **Elder Scrolls Wiki Dataset**: Comprehensive knowledge base from HuggingFace
- ⚡ **RAG Processing**: Retrieval-Augmented Generation for accurate, context-aware answers
- 💾 **Caching**: Saves processed embeddings and index for faster startup

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))
- One of the following LLM backends:
  - **OpenRouter API**: API key from [OpenRouter](https://openrouter.ai/)
  - **Ollama**: Local installation with models
  - **LM Studio**: Local installation with models

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd elder-scrolls-lore-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Configure your bot**:
   - Copy `.env.example` to `.env`
   - Fill in your Telegram bot token
   - Choose and configure your preferred LLM backend

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required: Telegram Bot Token
TELEGRAM_TOKEN=your_telegram_bot_token_here

# Required: Choose LLM backend (openrouter, ollama, lm_studio)
LLM_BACKEND=openrouter

# OpenRouter Configuration (if using OpenRouter)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Ollama Configuration (if using Ollama)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# LM Studio Configuration (if using LM Studio)
LM_STUDIO_BASE_URL=http://localhost:1234
LM_STUDIO_MODEL=default
```

### LLM Backend Setup

#### Option 1: OpenRouter (Recommended for beginners)
1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Get your API key
3. Set `LLM_BACKEND=openrouter` and `OPENROUTER_API_KEY=your_key`

#### Option 2: Ollama (Local)
1. Install [Ollama](https://ollama.ai/)
2. Pull a model: `ollama pull llama2`
3. Set `LLM_BACKEND=ollama` and `OLLAMA_MODEL=llama2`

#### Option 3: LM Studio (Local)
1. Install [LM Studio](https://lmstudio.ai/)
2. Load a model and start the local server
3. Set `LLM_BACKEND=lm_studio` and configure the base URL

## Usage

1. **Start the bot**:
   ```bash
   python telegram_bot.py
   ```

2. **Interact with the bot**:
   - Send `/start` for welcome message
   - Send `/help` for usage instructions
   - Send `/ask <question>` or just type your question

### Example Questions

- "Who is the Dragonborn?"
- "What is the history of the Dark Elves?"
- "Tell me about the Thalmor"
- "What are the Nine Divines?"
- "How does magic work in Tamriel?"
- "What is the story of the Dwemer?"

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram Bot  │───▶│  Dataset Loader  │───▶│  FAISS Index    │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  RAG Processor  │◀───│  LLM Client      │    │  Embeddings     │
│                 │    │  (OpenRouter/    │    │  (sentence-     │
└─────────────────┘    │   Ollama/LM      │    │   transformers) │
                       │   Studio)        │    │                 │
                       └──────────────────┘    └─────────────────┘
```

## File Structure

```
elder-scrolls-lore-bot/
├── telegram_bot.py          # Main bot application
├── config.py               # Configuration management
├── dataset_loader.py       # Dataset loading and search
├── llm_client.py          # LLM backend clients
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
└── .env                  # Your environment variables (create this)
```

## Features in Detail

### Semantic Search
- Uses `all-MiniLM-L6-v2` for creating embeddings
- FAISS index for fast similarity search
- Retrieves top 3 most relevant passages for each question

### RAG Processing
- Combines retrieved passages with user questions
- Sends context-aware prompts to LLM
- Generates accurate, lore-based answers

### Error Handling
- Graceful handling of API failures
- User-friendly error messages
- Comprehensive logging

### Caching
- Saves processed embeddings and FAISS index
- Faster startup on subsequent runs
- Automatic regeneration if cache is corrupted

## Troubleshooting

### Common Issues

1. **"Bot is still initializing"**
   - Wait for the first startup to complete (may take several minutes)
   - Check logs for initialization errors

2. **"Couldn't find anything on that"**
   - Try rephrasing your question
   - Be more specific about characters, locations, or events

3. **LLM API errors**
   - Verify your API keys and endpoints
   - Check if your local LLM services are running
   - Ensure you have sufficient credits (for OpenRouter)

4. **Dataset loading issues**
   - Check your internet connection
   - Verify the dataset is accessible on HuggingFace
   - Clear cached files and restart

### Logs

The bot provides detailed logging. Check the console output for:
- Initialization progress
- Search results
- API errors
- Performance metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Elder Scrolls Wiki Dataset](https://huggingface.co/datasets/RoyalCities/Elder_Scrolls_Wiki_Dataset) on HuggingFace
- [python-telegram-bot](https://python-telegram-bot.org/) library
- [FAISS](https://github.com/facebookresearch/faiss) for vector search
- [sentence-transformers](https://www.sbert.net/) for embeddings

---

**Happy exploring, traveler!** 🗡️⚔️