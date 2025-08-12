#!/usr/bin/env python3
"""
Elder Scrolls Lore Bot - Startup Script
Provides an easy way to run the optimized bot with proper error handling.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "discord_bot.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["DISCORD_TOKEN"]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with the required variables.")
        print("See .env.example for a template.")
        return False
    
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import discord
        import aiohttp
        import numpy
        import torch
        import transformers
        import sentence_transformers
        import datasets
        import faiss
        import psutil
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements_optimized.txt")
        return False

def validate_configuration():
    """Validate bot configuration"""
    try:
        from config_optimized import Config
        
        # Log configuration summary
        Config.log_config_summary()
        
        # Validate configuration
        errors = Config.validate_config()
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        print("✅ Configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

async def main():
    """Main function to run the bot"""
    print("🚀 Starting Elder Scrolls Lore Bot...")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check environment
    print("📋 Checking environment...")
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # Validate configuration
    print("⚙️ Validating configuration...")
    if not validate_configuration():
        sys.exit(1)
    
    # Import bot after validation
    try:
        from discord_bot_optimized import main as run_bot
        print("✅ Bot imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import bot: {e}")
        sys.exit(1)
    
    # Run the bot
    print("🤖 Starting bot...")
    print("=" * 50)
    
    try:
        await run_bot()
    except KeyboardInterrupt:
        print("\n🛑 Bot shutdown requested by user")
    except Exception as e:
        print(f"❌ Bot startup failed: {e}")
        logger.error(f"Bot startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)