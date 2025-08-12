"""
Optimized Configuration Module for Elder Scrolls Lore Bot
Enhanced with better security, validation, and environment variable handling.
"""

import os
import logging
from dotenv import load_dotenv
from enum import Enum
from typing import List, Dict, Any, Optional
import json
import hashlib
from pathlib import Path

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LLMBackend(Enum):
    """Supported LLM backends"""
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"

class SecurityLevel(Enum):
    """Security levels for the bot"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Config:
    """Optimized configuration class for Elder Scrolls Lore Bot"""
    
    # Bot Configuration
    BOT_NAME = "Elder Scrolls Lore Bot"
    BOT_VERSION = "2.0.0"
    BOT_DESCRIPTION = "An AI-powered Discord bot for Elder Scrolls lore with online search capabilities"
    
    # Discord Bot Configuration
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    DISCORD_APPLICATION_ID = os.getenv("DISCORD_APPLICATION_ID")
    
    # Security Configuration
    SECURITY_LEVEL = SecurityLevel(os.getenv("SECURITY_LEVEL", "medium").lower())
    ALLOWED_GUILDS = os.getenv("ALLOWED_GUILDS", "").split(",") if os.getenv("ALLOWED_GUILDS") else []
    BLOCKED_USERS = os.getenv("BLOCKED_USERS", "").split(",") if os.getenv("BLOCKED_USERS") else []
    
    # LLM Backend Configuration
    LLM_BACKEND = os.getenv("LLM_BACKEND", "openrouter").lower()
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
    OPENROUTER_MAX_TOKENS = int(os.getenv("OPENROUTER_MAX_TOKENS", "1000"))
    OPENROUTER_TEMPERATURE = float(os.getenv("OPENROUTER_TEMPERATURE", "0.7"))
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "60"))
    
    # LM Studio Configuration
    LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234")
    LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "default")
    LM_STUDIO_TIMEOUT = int(os.getenv("LM_STUDIO_TIMEOUT", "60"))
    
    # Dataset Configuration
    DATASET_NAME = os.getenv("DATASET_NAME", "RoyalCities/Elder_Scrolls_Wiki_Dataset")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "3"))
    
    # Vector Search Configuration
    FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "elder_scrolls_index.faiss")
    EMBEDDINGS_PATH = os.getenv("EMBEDDINGS_PATH", "elder_scrolls_embeddings.npy")
    TEXTS_PATH = os.getenv("TEXTS_PATH", "elder_scrolls_texts.json")
    
    # Online Search Configuration
    UESP_API_BASE_URL = os.getenv("UESP_API_BASE_URL", "https://en.uesp.net/api.php")
    UESP_SEARCH_URL = os.getenv("UESP_SEARCH_URL", "https://en.uesp.net/wiki")
    WIKIPEDIA_API_BASE_URL = os.getenv("WIKIPEDIA_API_BASE_URL", "https://en.wikipedia.org/api/rest_v1")
    
    # Rate Limiting Configuration
    REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.0"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # User Rate Limiting
    USER_RATE_LIMIT = int(os.getenv("USER_RATE_LIMIT", "5"))
    USER_RATE_WINDOW = float(os.getenv("USER_RATE_WINDOW", "60.0"))
    
    # Guild Rate Limiting
    GUILD_RATE_LIMIT = int(os.getenv("GUILD_RATE_LIMIT", "20"))
    GUILD_RATE_WINDOW = float(os.getenv("GUILD_RATE_WINDOW", "60.0"))
    
    # Bot Timeout Settings
    SEARCH_TIMEOUT = float(os.getenv("SEARCH_TIMEOUT", "45.0"))
    LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "30.0"))
    BOT_STARTUP_TIMEOUT = float(os.getenv("BOT_STARTUP_TIMEOUT", "60.0"))
    
    # Retry Settings
    MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "2"))
    RETRY_BASE_DELAY = float(os.getenv("RETRY_BASE_DELAY", "1.0"))
    RETRY_MAX_DELAY = float(os.getenv("RETRY_MAX_DELAY", "10.0"))
    
    # Search Configuration
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    MIN_CONTENT_LENGTH = int(os.getenv("MIN_CONTENT_LENGTH", "100"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "2000"))
    MAX_QUESTION_LENGTH = int(os.getenv("MAX_QUESTION_LENGTH", "500"))
    
    # Cache Configuration
    CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "500"))
    CACHE_DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", "600"))
    CACHE_RESPONSE_TTL = int(os.getenv("CACHE_RESPONSE_TTL", "1800"))
    
    # Performance Configuration
    MAX_MESSAGE_HISTORY = int(os.getenv("MAX_MESSAGE_HISTORY", "1000"))
    MAX_ERROR_LOG_SIZE = int(os.getenv("MAX_ERROR_LOG_SIZE", "100"))
    MAX_PERFORMANCE_METRICS = int(os.getenv("MAX_PERFORMANCE_METRICS", "100"))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE = os.getenv("LOG_FILE", "discord_bot.log")
    LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # User Agent for polite scraping
    USER_AGENT = os.getenv("USER_AGENT", "ElderScrollsLoreBot/2.0 (Educational Bot; +https://github.com/elder-scrolls-lore-bot)")
    
    # File paths
    CONFIG_DIR = Path(os.getenv("CONFIG_DIR", "./config"))
    DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
    LOGS_DIR = Path(os.getenv("LOGS_DIR", "./logs"))
    
    @classmethod
    def initialize_directories(cls):
        """Initialize necessary directories"""
        directories = [cls.CONFIG_DIR, cls.DATA_DIR, cls.LOGS_DIR]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {directory}")
    
    @classmethod
    def get_llm_backend(cls) -> LLMBackend:
        """Get the configured LLM backend with validation"""
        try:
            return LLMBackend(cls.LLM_BACKEND)
        except ValueError:
            logger.warning(f"Invalid LLM backend: {cls.LLM_BACKEND}. Defaulting to OpenRouter.")
            return LLMBackend.OPENROUTER
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate that all required configuration is present"""
        errors = []
        
        # Required Discord configuration
        if not cls.DISCORD_TOKEN:
            errors.append("DISCORD_TOKEN is required")
        
        # Validate LLM backend configuration
        backend = cls.get_llm_backend()
        if backend == LLMBackend.OPENROUTER:
            if not cls.OPENROUTER_API_KEY:
                errors.append("OPENROUTER_API_KEY is required when using OpenRouter backend")
        elif backend == LLMBackend.OLLAMA:
            # Check if Ollama is accessible
            import aiohttp
            import asyncio
            try:
                async def test_ollama():
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{cls.OLLAMA_BASE_URL}/api/tags", timeout=5) as response:
                            return response.status == 200
                
                if not asyncio.run(test_ollama()):
                    errors.append("Ollama server is not accessible")
            except Exception:
                errors.append("Cannot connect to Ollama server")
        
        # Validate security configuration
        if cls.SECURITY_LEVEL == SecurityLevel.HIGH:
            if not cls.ALLOWED_GUILDS:
                errors.append("ALLOWED_GUILDS must be specified for HIGH security level")
        
        # Validate numeric configurations
        numeric_configs = [
            ("REQUEST_DELAY", cls.REQUEST_DELAY, 0.1, 10.0),
            ("REQUEST_TIMEOUT", cls.REQUEST_TIMEOUT, 5, 300),
            ("SEARCH_TIMEOUT", cls.SEARCH_TIMEOUT, 10.0, 300.0),
            ("LLM_TIMEOUT", cls.LLM_TIMEOUT, 10.0, 300.0),
            ("USER_RATE_LIMIT", cls.USER_RATE_LIMIT, 1, 100),
            ("GUILD_RATE_LIMIT", cls.GUILD_RATE_LIMIT, 1, 1000),
        ]
        
        for name, value, min_val, max_val in numeric_configs:
            if not min_val <= value <= max_val:
                errors.append(f"{name} must be between {min_val} and {max_val}")
        
        return errors
    
    @classmethod
    def get_backend_config(cls) -> Dict[str, Any]:
        """Get configuration for the current LLM backend"""
        backend = cls.get_llm_backend()
        
        if backend == LLMBackend.OPENROUTER:
            return {
                'api_key': cls.OPENROUTER_API_KEY,
                'base_url': cls.OPENROUTER_BASE_URL,
                'model': cls.OPENROUTER_MODEL,
                'max_tokens': cls.OPENROUTER_MAX_TOKENS,
                'temperature': cls.OPENROUTER_TEMPERATURE,
                'timeout': cls.REQUEST_TIMEOUT
            }
        elif backend == LLMBackend.OLLAMA:
            return {
                'base_url': cls.OLLAMA_BASE_URL,
                'model': cls.OLLAMA_MODEL,
                'timeout': cls.OLLAMA_TIMEOUT
            }
        elif backend == LLMBackend.LM_STUDIO:
            return {
                'base_url': cls.LM_STUDIO_BASE_URL,
                'model': cls.LM_STUDIO_MODEL,
                'timeout': cls.LM_STUDIO_TIMEOUT
            }
        else:
            raise ValueError(f"Unsupported backend: {backend}")
    
    @classmethod
    def is_guild_allowed(cls, guild_id: str) -> bool:
        """Check if a guild is allowed based on security configuration"""
        if cls.SECURITY_LEVEL == SecurityLevel.LOW:
            return True
        elif cls.SECURITY_LEVEL == SecurityLevel.MEDIUM:
            return True  # Medium security allows all guilds but logs
        elif cls.SECURITY_LEVEL == SecurityLevel.HIGH:
            return str(guild_id) in cls.ALLOWED_GUILDS
        return False
    
    @classmethod
    def is_user_blocked(cls, user_id: str) -> bool:
        """Check if a user is blocked"""
        return str(user_id) in cls.BLOCKED_USERS
    
    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Get cache configuration"""
        return {
            'max_size': cls.CACHE_MAX_SIZE,
            'default_ttl': cls.CACHE_DEFAULT_TTL,
            'response_ttl': cls.CACHE_RESPONSE_TTL
        }
    
    @classmethod
    def get_rate_limit_config(cls) -> Dict[str, Any]:
        """Get rate limiting configuration"""
        return {
            'user_limit': cls.USER_RATE_LIMIT,
            'user_window': cls.USER_RATE_WINDOW,
            'guild_limit': cls.GUILD_RATE_LIMIT,
            'guild_window': cls.GUILD_RATE_WINDOW,
            'request_delay': cls.REQUEST_DELAY
        }
    
    @classmethod
    def export_config(cls, filepath: str = None) -> str:
        """Export configuration to JSON file (excluding sensitive data)"""
        if filepath is None:
            filepath = cls.CONFIG_DIR / "config_export.json"
        
        # Create safe config for export (exclude sensitive data)
        safe_config = {
            'bot_name': cls.BOT_NAME,
            'bot_version': cls.BOT_VERSION,
            'llm_backend': cls.LLM_BACKEND,
            'security_level': cls.SECURITY_LEVEL.value,
            'allowed_guilds': cls.ALLOWED_GUILDS,
            'rate_limits': cls.get_rate_limit_config(),
            'cache_config': cls.get_cache_config(),
            'timeouts': {
                'search_timeout': cls.SEARCH_TIMEOUT,
                'llm_timeout': cls.LLM_TIMEOUT,
                'request_timeout': cls.REQUEST_TIMEOUT
            },
            'search_config': {
                'max_results': cls.MAX_SEARCH_RESULTS,
                'min_content_length': cls.MIN_CONTENT_LENGTH,
                'max_content_length': cls.MAX_CONTENT_LENGTH
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(safe_config, f, indent=2)
        
        logger.info(f"Configuration exported to {filepath}")
        return str(filepath)
    
    @classmethod
    def get_config_hash(cls) -> str:
        """Get a hash of the current configuration for change detection"""
        config_string = json.dumps({
            'llm_backend': cls.LLM_BACKEND,
            'security_level': cls.SECURITY_LEVEL.value,
            'allowed_guilds': cls.ALLOWED_GUILDS,
            'rate_limits': cls.get_rate_limit_config(),
            'timeouts': {
                'search_timeout': cls.SEARCH_TIMEOUT,
                'llm_timeout': cls.LLM_TIMEOUT
            }
        }, sort_keys=True)
        
        return hashlib.md5(config_string.encode()).hexdigest()
    
    @classmethod
    def log_config_summary(cls):
        """Log a summary of the current configuration"""
        logger.info("Configuration Summary:")
        logger.info(f"  Bot: {cls.BOT_NAME} v{cls.BOT_VERSION}")
        logger.info(f"  LLM Backend: {cls.get_llm_backend().value}")
        logger.info(f"  Security Level: {cls.SECURITY_LEVEL.value}")
        logger.info(f"  Allowed Guilds: {len(cls.ALLOWED_GUILDS)}")
        logger.info(f"  Blocked Users: {len(cls.BLOCKED_USERS)}")
        logger.info(f"  Rate Limits: {cls.USER_RATE_LIMIT} req/{cls.USER_RATE_WINDOW}s per user")
        logger.info(f"  Cache: {cls.CACHE_MAX_SIZE} entries, {cls.CACHE_DEFAULT_TTL}s TTL")
        logger.info(f"  Timeouts: Search={cls.SEARCH_TIMEOUT}s, LLM={cls.LLM_TIMEOUT}s")

# Initialize directories on import
Config.initialize_directories()