# Async Fixes for Elder Scrolls Lore Bot

## Problem
The bot was experiencing `telegram.error.TimedOut` errors when trying to getUpdates or handle user messages. This was happening because the bot's process was taking too long to respond, causing timeouts.

## Root Cause
The main issue was that the LLM clients were using synchronous `requests` library calls, which block the entire event loop. When these blocking operations took too long, it prevented the bot from responding to Telegram's polling requests, causing timeouts.

## Solution

### 1. Converted LLM Clients to Async
- **File**: `llm_client.py`
- **Changes**:
  - Replaced `requests` with `aiohttp` for all HTTP calls
  - Made all `generate_response` methods async
  - Updated `RAGProcessor.process_question` to be async
  - Added proper async error handling

### 2. Updated Bot Handlers
- **File**: `telegram_bot.py`
- **Changes**:
  - Updated `ask_command` and `handle_message` methods to use `await` with `process_question`
  - Added timeout handling with `asyncio.wait_for`
  - Added specific timeout error handling

### 3. Made Search Operations Non-Blocking
- **File**: `online_search.py`
- **Changes**:
  - Wrapped `SentenceTransformer` initialization in `asyncio.to_thread()`
  - Wrapped `load_dataset` calls in `asyncio.to_thread()`
  - Wrapped embedding model operations in `asyncio.to_thread()`
  - Removed unused `requests` import

### 4. Added Configurable Timeouts
- **File**: `config.py`
- **Changes**:
  - Added `SEARCH_TIMEOUT` (45 seconds default)
  - Added `LLM_TIMEOUT` (30 seconds default)
  - Made timeouts configurable via environment variables

### 5. Updated Supporting Files
- **Files**: `example_usage.py`, `test_bot.py`
- **Changes**:
  - Updated all calls to `process_question` to use `await`

## Key Benefits

1. **Non-blocking Operations**: All I/O operations now run asynchronously, preventing event loop blocking
2. **Better Timeout Handling**: Explicit timeout management with graceful error messages
3. **Improved Responsiveness**: Bot can handle multiple requests concurrently
4. **Configurable Timeouts**: Easy to adjust timeout values based on deployment environment
5. **Better Error Messages**: Users get clear feedback when operations timeout

## Configuration

You can adjust timeout values by setting these environment variables:

```bash
SEARCH_TIMEOUT=45.0    # Timeout for search operations (seconds)
LLM_TIMEOUT=30.0       # Timeout for LLM responses (seconds)
REQUEST_TIMEOUT=30     # Timeout for individual HTTP requests (seconds)
```

## Testing

A new test script `test_async_fixes.py` has been created to verify:
- Async operations work correctly
- Timeout handling functions properly
- Bot initialization and cleanup work as expected

Run the test with:
```bash
python test_async_fixes.py
```

## Migration Notes

- All existing functionality remains the same
- No changes to bot commands or user interface
- Backward compatible with existing configurations
- Performance should be significantly improved

## Files Modified

1. `llm_client.py` - Converted to async HTTP calls
2. `telegram_bot.py` - Added async handling and timeouts
3. `online_search.py` - Made operations non-blocking
4. `config.py` - Added timeout configurations
5. `example_usage.py` - Updated for async calls
6. `test_bot.py` - Updated for async calls
7. `test_async_fixes.py` - New test script (created)

## Dependencies

The bot now requires:
- `aiohttp>=3.9.1` (already in requirements.txt)
- All other dependencies remain the same

This fix should resolve the timeout issues and make the bot much more responsive and reliable.