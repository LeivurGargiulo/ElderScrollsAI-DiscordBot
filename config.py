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
    
    # Dataset Configuration
    DATASET_NAME = "RoyalCities/Elder_Scrolls_Wiki_Dataset"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    TOP_K_RESULTS = 3
    
    # Vector Search Configuration
    FAISS_INDEX_PATH = "elder_scrolls_index.faiss"
    EMBEDDINGS_PATH = "elder_scrolls_embeddings.npy"
    TEXTS_PATH = "elder_scrolls_texts.json"
    
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