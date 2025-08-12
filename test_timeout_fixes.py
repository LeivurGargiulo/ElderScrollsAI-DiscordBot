#!/usr/bin/env python3
"""
Test script to verify timeout and retry improvements for the Telegram bot.
This script tests the retry logic and timeout configurations without actually
connecting to Telegram API.
"""

import asyncio
import logging
from unittest.mock import AsyncMock, patch
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import ElderScrollsLoreBot, retry_with_backoff
from config import Config

# Configure logging for testing
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TestTimeoutFixes:
    """Test class for timeout and retry improvements"""
    
    def __init__(self):
        self.bot = None
    
    async def setup(self):
        """Setup test environment"""
        logger.info("Setting up test environment...")
        self.bot = ElderScrollsLoreBot()
        
        # Mock the initialization to avoid actual API calls
        with patch.object(self.bot, 'initialize', return_value=True):
            await self.bot.initialize()
    
    async def test_retry_decorator(self):
        """Test the retry decorator with exponential backoff"""
        logger.info("Testing retry decorator...")
        
        call_count = 0
        
        @retry_with_backoff(max_retries=2, base_delay=0.1, max_delay=1.0)
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Fail first 2 times, succeed on 3rd
                raise Exception(f"Simulated failure {call_count}")
            return "Success!"
        
        # Test successful retry
        result = await failing_function()
        assert result == "Success!"
        assert call_count == 3
        logger.info("✅ Retry decorator test passed - function succeeded after retries")
        
        # Test max retries exceeded
        call_count = 0
        
        @retry_with_backoff(max_retries=1, base_delay=0.1)
        async def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Always fails")
        
        try:
            await always_failing_function()
            assert False, "Should have raised an exception"
        except Exception as e:
            assert call_count == 2  # Initial attempt + 1 retry
            logger.info("✅ Retry decorator test passed - max retries exceeded correctly")
    
    async def test_safe_reply_method(self):
        """Test the safe_reply method with retry logic"""
        logger.info("Testing safe_reply method...")
        
        # Create a mock message
        mock_message = AsyncMock()
        mock_message.reply_text = AsyncMock()
        
        # Test successful reply
        await self.bot.safe_reply(mock_message, "Test message")
        mock_message.reply_text.assert_called_once_with("Test message")
        logger.info("✅ Safe reply test passed - successful reply")
        
        # Test retry on failure
        mock_message.reply_text.reset_mock()
        mock_message.reply_text.side_effect = [
            Exception("Network error"),  # First call fails
            "Success"  # Second call succeeds
        ]
        
        await self.bot.safe_reply(mock_message, "Test message with retry")
        assert mock_message.reply_text.call_count == 2
        logger.info("✅ Safe reply test passed - retry on failure")
    
    async def test_safe_send_chat_action(self):
        """Test the safe_send_chat_action method with retry logic"""
        logger.info("Testing safe_send_chat_action method...")
        
        # Create mock bot and parameters
        mock_bot = AsyncMock()
        mock_bot.send_chat_action = AsyncMock()
        
        # Test successful chat action
        await self.bot.safe_send_chat_action(mock_bot, 12345, "typing")
        mock_bot.send_chat_action.assert_called_once_with(chat_id=12345, action="typing")
        logger.info("✅ Safe send chat action test passed - successful action")
        
        # Test retry on failure
        mock_bot.send_chat_action.reset_mock()
        mock_bot.send_chat_action.side_effect = [
            Exception("Network error"),  # First call fails
            "Success"  # Second call succeeds
        ]
        
        await self.bot.safe_send_chat_action(mock_bot, 12345, "typing")
        assert mock_bot.send_chat_action.call_count == 2
        logger.info("✅ Safe send chat action test passed - retry on failure")
    
    async def test_error_handler_resilience(self):
        """Test that the error handler doesn't cause cascading failures"""
        logger.info("Testing error handler resilience...")
        
        # Create mock update and context
        mock_update = AsyncMock()
        mock_context = AsyncMock()
        mock_context.error = Exception("Test error")
        
        # Mock the safe_reply method to fail
        with patch.object(self.bot, 'safe_reply', side_effect=Exception("Error handler failed")):
            # This should not raise an exception
            await self.bot.error_handler(mock_update, mock_context)
            logger.info("✅ Error handler resilience test passed - no cascading failure")
    
    async def test_configuration_values(self):
        """Test that configuration values are properly set"""
        logger.info("Testing configuration values...")
        
        # Test timeout configurations
        assert Config.TELEGRAM_READ_TIMEOUT >= 30
        assert Config.TELEGRAM_WRITE_TIMEOUT >= 30
        assert Config.TELEGRAM_CONNECT_TIMEOUT >= 30
        assert Config.TELEGRAM_POOL_TIMEOUT >= 30
        
        # Test retry configurations
        assert Config.MAX_RETRY_ATTEMPTS >= 1
        assert Config.RETRY_BASE_DELAY > 0
        assert Config.RETRY_MAX_DELAY > Config.RETRY_BASE_DELAY
        
        logger.info("✅ Configuration values test passed")
        logger.info(f"  - Read timeout: {Config.TELEGRAM_READ_TIMEOUT}s")
        logger.info(f"  - Write timeout: {Config.TELEGRAM_WRITE_TIMEOUT}s")
        logger.info(f"  - Connect timeout: {Config.TELEGRAM_CONNECT_TIMEOUT}s")
        logger.info(f"  - Pool timeout: {Config.TELEGRAM_POOL_TIMEOUT}s")
        logger.info(f"  - Max retry attempts: {Config.MAX_RETRY_ATTEMPTS}")
        logger.info(f"  - Retry base delay: {Config.RETRY_BASE_DELAY}s")
        logger.info(f"  - Retry max delay: {Config.RETRY_MAX_DELAY}s")
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting timeout and retry tests...")
        
        try:
            await self.setup()
            await self.test_retry_decorator()
            await self.test_safe_reply_method()
            await self.test_safe_send_chat_action()
            await self.test_error_handler_resilience()
            await self.test_configuration_values()
            
            logger.info("🎉 All tests passed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            return False

async def main():
    """Main test function"""
    tester = TestTimeoutFixes()
    success = await tester.run_all_tests()
    
    if success:
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("The timeout and retry improvements are working correctly!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ SOME TESTS FAILED")
        print("Please check the logs above for details.")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())