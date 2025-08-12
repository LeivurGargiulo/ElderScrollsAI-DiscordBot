#!/usr/bin/env python3
"""
Test script for Elder Scrolls Lore Discord Bot
This script tests the bot initialization and configuration without actually connecting to Discord.
"""

import asyncio
import logging
import os
import sys
from unittest.mock import Mock, patch

# Configure logging for testing
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    
    try:
        from config import Config
        
        # Test basic config loading
        backend = Config.get_llm_backend()
        print(f"✅ LLM Backend: {backend.value}")
        
        # Test config validation
        errors = Config.validate_config()
        if errors:
            print("❌ Configuration errors found:")
            for error in errors:
                print(f"   - {error}")
            return False
        else:
            print("✅ Configuration validation passed")
            return True
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def test_search_engine():
    """Test search engine initialization"""
    print("\n🔍 Testing search engine...")
    
    try:
        from online_search import OnlineSearchEngine
        
        # Create search engine instance
        search_engine = OnlineSearchEngine()
        
        # Test initialization
        success = await search_engine.initialize()
        if success:
            print("✅ Search engine initialized successfully")
            
            # Test basic search functionality
            try:
                results = await search_engine.search("test")
                print(f"✅ Search test completed, found {len(results) if results else 0} results")
            except Exception as e:
                print(f"⚠️ Search test failed (this is normal if no internet): {e}")
            
            # Cleanup
            await search_engine.close()
            return True
        else:
            print("❌ Search engine initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Search engine test failed: {e}")
        return False

async def test_llm_client():
    """Test LLM client initialization"""
    print("\n🤖 Testing LLM client...")
    
    try:
        from llm_client import LLMClientFactory
        
        # Test client creation
        client = LLMClientFactory.create_client()
        print(f"✅ LLM client created: {type(client).__name__}")
        
        # Test basic functionality (without actual API call)
        print("✅ LLM client test completed")
        return True
        
    except Exception as e:
        print(f"❌ LLM client test failed: {e}")
        return False

async def test_bot_initialization():
    """Test bot initialization (mocked)"""
    print("\n🤖 Testing bot initialization...")
    
    try:
        # Mock Discord bot to avoid actual connection
        with patch('discord.ext.commands.Bot') as mock_bot_class:
            mock_bot = Mock()
            mock_bot_class.return_value = mock_bot
            
            from discord_bot import ElderScrollsLoreBot
            
            # Create bot instance
            bot = ElderScrollsLoreBot()
            print("✅ Bot instance created")
            
            # Test initialization
            success = await bot.initialize()
            if success:
                print("✅ Bot initialization completed")
                
                # Test cleanup
                await bot.cleanup()
                print("✅ Bot cleanup completed")
                return True
            else:
                print("❌ Bot initialization failed")
                return False
                
    except Exception as e:
        print(f"❌ Bot initialization test failed: {e}")
        return False

async def test_commands():
    """Test command loading"""
    print("\n📝 Testing commands...")
    
    try:
        from commands import ElderScrollsCommands
        
        # Mock bot for command testing
        mock_bot = Mock()
        mock_bot.initialized = True
        mock_bot.search_engine = Mock()
        mock_bot.rag_processor = Mock()
        mock_bot.error_log = []
        mock_bot.start_time = None
        mock_bot.guilds = []
        mock_bot.latency = 0.1
        
        # Create commands instance
        commands = ElderScrollsCommands(mock_bot)
        print("✅ Commands loaded successfully")
        
        # Test command methods exist
        assert hasattr(commands, 'start_command')
        assert hasattr(commands, 'help_command')
        assert hasattr(commands, 'ask_command')
        assert hasattr(commands, 'debug_command')
        print("✅ All command methods present")
        
        return True
        
    except Exception as e:
        print(f"❌ Commands test failed: {e}")
        return False

async def test_events():
    """Test event handlers"""
    print("\n📡 Testing event handlers...")
    
    try:
        from events import ElderScrollsEvents
        
        # Mock bot for event testing
        mock_bot = Mock()
        mock_bot.initialized = True
        mock_bot.search_engine = Mock()
        mock_bot.rag_processor = Mock()
        mock_bot.error_log = []
        
        # Create events instance
        events = ElderScrollsEvents(mock_bot)
        print("✅ Event handlers loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Event handlers test failed: {e}")
        return False

async def test_background_tasks():
    """Test background task manager"""
    print("\n🔄 Testing background tasks...")
    
    try:
        from background_tasks import BackgroundTaskManager
        
        # Mock bot for background task testing
        mock_bot = Mock()
        mock_bot.error_log = []
        
        # Create background task manager
        task_manager = BackgroundTaskManager(mock_bot)
        print("✅ Background task manager created")
        
        # Test task methods exist
        assert hasattr(task_manager, 'cleanup_old_errors')
        assert hasattr(task_manager, 'health_check')
        assert hasattr(task_manager, 'search_engine_maintenance')
        print("✅ All background tasks present")
        
        return True
        
    except Exception as e:
        print(f"❌ Background tasks test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Elder Scrolls Lore Discord Bot - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Search Engine", test_search_engine),
        ("LLM Client", test_llm_client),
        ("Bot Initialization", test_bot_initialization),
        ("Commands", test_commands),
        ("Event Handlers", test_events),
        ("Background Tasks", test_background_tasks),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The bot is ready to run.")
        print("\nNext steps:")
        print("1. Set up your .env file with Discord token and API keys")
        print("2. Run: python discord_bot.py")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️ Warning: .env file not found. Some tests may fail.")
        print("   Copy .env.example to .env and fill in your values.")
        print()
    
    # Run tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)