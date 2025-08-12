#!/usr/bin/env python3
"""
Test script to verify async fixes for the Elder Scrolls Lore Bot
"""

import asyncio
import logging
from telegram_bot import ElderScrollsLoreBot
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_async_operations():
    """Test that async operations work correctly"""
    print("🧪 Testing Async Operations...")
    
    try:
        # Create bot instance
        bot = ElderScrollsLoreBot()
        
        # Initialize bot components
        print("   Initializing bot components...")
        if not await bot.initialize():
            print("❌ Bot initialization failed")
            return False
        
        print("✅ Bot initialization successful")
        
        # Test search operation
        print("   Testing search operation...")
        test_question = "Who is the Dragonborn?"
        
        try:
            context_passages = await asyncio.wait_for(
                bot.search_engine.search(test_question),
                timeout=Config.SEARCH_TIMEOUT
            )
            print(f"✅ Search operation successful - found {len(context_passages)} passages")
        except asyncio.TimeoutError:
            print("❌ Search operation timed out")
            return False
        except Exception as e:
            print(f"❌ Search operation failed: {e}")
            return False
        
        # Test RAG processing
        if context_passages:
            print("   Testing RAG processing...")
            try:
                response = await asyncio.wait_for(
                    bot.rag_processor.process_question(test_question, context_passages),
                    timeout=Config.LLM_TIMEOUT
                )
                print(f"✅ RAG processing successful - response length: {len(response)}")
            except asyncio.TimeoutError:
                print("❌ RAG processing timed out")
                return False
            except Exception as e:
                print(f"❌ RAG processing failed: {e}")
                return False
        
        # Cleanup
        await bot.cleanup()
        print("✅ Cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_timeout_handling():
    """Test that timeout handling works correctly"""
    print("\n⏰ Testing Timeout Handling...")
    
    try:
        # Create bot instance
        bot = ElderScrollsLoreBot()
        
        # Initialize bot components
        if not await bot.initialize():
            print("❌ Bot initialization failed")
            return False
        
        # Test with a very short timeout
        print("   Testing with short timeout...")
        test_question = "What is the history of Tamriel?"
        
        try:
            context_passages = await asyncio.wait_for(
                bot.search_engine.search(test_question),
                timeout=0.1  # Very short timeout to trigger timeout error
            )
            print("❌ Expected timeout but operation completed")
            return False
        except asyncio.TimeoutError:
            print("✅ Timeout handling working correctly")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        
        # Cleanup
        await bot.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ Timeout test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing Async Fixes for Elder Scrolls Lore Bot...\n")
    
    # Check configuration
    config_errors = Config.validate_config()
    if config_errors:
        print("❌ Configuration errors found:")
        for error in config_errors:
            print(f"   - {error}")
        return
    
    print("✅ Configuration validated")
    
    # Run tests
    test1_passed = await test_async_operations()
    test2_passed = await test_timeout_handling()
    
    print("\n📊 Test Results:")
    print(f"   Async Operations: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Timeout Handling: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The async fixes are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    asyncio.run(main())