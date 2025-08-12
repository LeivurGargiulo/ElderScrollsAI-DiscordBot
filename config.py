import os
from dotenv import load_dotenv
from enum import Enum

# Load environment variables
load_dotenv()

class LLMBackend(Enum):
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"

class Config:
    """Configuration class for Elder Scrolls Lore Bot"""
    
    # Telegram Bot Configuration
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    # LLM Backend Configuration
    LLM_BACKEND = os.getenv("LLM_BACKEND", "openrouter").lower()
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    
    # LM Studio Configuration
    LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234")
    LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "default")
    
    # Dataset Configuration (for Hugging Face Datasets API)
    DATASET_NAME = "RoyalCities/Elder_Scrolls_Wiki_Dataset"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    TOP_K_RESULTS = 3
    
    # Vector Search Configuration
    FAISS_INDEX_PATH = "elder_scrolls_index.faiss"
    EMBEDDINGS_PATH = "elder_scrolls_embeddings.npy"
    TEXTS_PATH = "elder_scrolls_texts.json"
    
    # Online Search Configuration
    # Elder Scrolls Wiki API endpoints
    UESP_API_BASE_URL = "https://en.uesp.net/api.php"
    UESP_SEARCH_URL = "https://en.uesp.net/wiki"
    
    # Wikipedia API for Elder Scrolls content
    WIKIPEDIA_API_BASE_URL = "https://en.wikipedia.org/api/rest_v1"
    
    # Rate limiting settings
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.0"))  # seconds between requests
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Bot timeout settings
    SEARCH_TIMEOUT = float(os.getenv("SEARCH_TIMEOUT", "45.0"))  # seconds for search operations
    LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "30.0"))  # seconds for LLM responses
    
    # Telegram API timeout settings
    TELEGRAM_READ_TIMEOUT = int(os.getenv("TELEGRAM_READ_TIMEOUT", "30"))  # seconds for read operations
    TELEGRAM_WRITE_TIMEOUT = int(os.getenv("TELEGRAM_WRITE_TIMEOUT", "30"))  # seconds for write operations
    TELEGRAM_CONNECT_TIMEOUT = int(os.getenv("TELEGRAM_CONNECT_TIMEOUT", "30"))  # seconds for connection
    TELEGRAM_POOL_TIMEOUT = int(os.getenv("TELEGRAM_POOL_TIMEOUT", "30"))  # seconds for pool operations
    
    # Retry settings
    MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "2"))  # number of retry attempts
    RETRY_BASE_DELAY = float(os.getenv("RETRY_BASE_DELAY", "1.0"))  # base delay for retries
    RETRY_MAX_DELAY = float(os.getenv("RETRY_MAX_DELAY", "10.0"))  # maximum delay for retries
    
    # Search configuration
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    MIN_CONTENT_LENGTH = int(os.getenv("MIN_CONTENT_LENGTH", "100"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "2000"))
    
    # User agent for polite scraping
    USER_AGENT = "ElderScrollsLoreBot/1.0 (Educational Bot; +https://github.com/elder-scrolls-lore-bot)"
    
    @classmethod
    def get_llm_backend(cls):
        """Get the configured LLM backend"""
        try:
            return LLMBackend(cls.LLM_BACKEND)
        except ValueError:
            print(f"Invalid LLM backend: {cls.LLM_BACKEND}. Defaulting to OpenRouter.")
            return LLMBackend.OPENROUTER
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        errors = []
        
        if not cls.TELEGRAM_TOKEN:
            errors.append("TELEGRAM_TOKEN is required")
        
        backend = cls.get_llm_backend()
        if backend == LLMBackend.OPENROUTER and not cls.OPENROUTER_API_KEY:
            errors.append("OPENROUTER_API_KEY is required when using OpenRouter backend")
        
        return errors