#!/usr/bin/env python3
"""
Test script for Elder Scrolls Lore Bot components
Run this to verify everything works before starting the Telegram bot
"""

import asyncio
import logging
import nest_asyncio

# Patch asyncio to allow nested event loops
nest_asyncio.apply()

from config import Config
from online_search import OnlineSearchEngine
from llm_client import LLMClientFactory, RAGProcessor

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_online_search_engine():
    """Test the online search engine component"""
    print("🧪 Testing Online Search Engine...")
    
    try:
        search_engine = OnlineSearchEngine()
        success = await search_engine.initialize()
        
        if success:
            print("✅ Online search engine initialized successfully")
            
            # Test search functionality
            test_query = "Dragonborn"
            print(f"   Testing search for: '{test_query}'")
            results = await search_engine.search(test_query)
            
            if results:
                print(f"✅ Search test successful - found {len(results)} results for '{test_query}'")
                for i, (text, score) in enumerate(results):
                    print(f"   Result {i+1} (score: {score:.3f}): {text[:100]}...")
            else:
                print("⚠️  Search returned no results")
            
            # Cleanup
            await search_engine.close()
                
        else:
            print("❌ Online search engine initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Online search engine test failed: {e}")
        return False
    
    return True

async def test_llm_client():
    """Test the LLM client component"""
    print("\n🧪 Testing LLM Client...")
    
    try:
        # Validate configuration first
        config_errors = Config.validate_config()
        if config_errors:
            print("❌ Configuration errors:")
            for error in config_errors:
                print(f"   - {error}")
            return False
        
        # Create LLM client
        llm_client = LLMClientFactory.create_client()
        backend = Config.get_llm_backend()
        print(f"✅ LLM client created successfully for backend: {backend.value}")
        
        # Test simple generation
        test_prompt = "Hello, this is a test message. Please respond with 'Test successful' if you can read this."
        
        print("   Testing LLM response generation...")
        response = llm_client.generate_response(test_prompt)
        
        if response and len(response) > 0:
            print(f"✅ LLM response test successful")
            print(f"   Response: {response[:200]}...")
        else:
            print("❌ LLM response test failed - empty response")
            return False
            
    except Exception as e:
        print(f"❌ LLM client test failed: {e}")
        return False
    
    return True

async def test_rag_processor():
    """Test the RAG processor component"""
    print("\n🧪 Testing RAG Processor...")
    
    try:
        # Create LLM client
        llm_client = LLMClientFactory.create_client()
        rag_processor = RAGProcessor(llm_client)
        
        # Test RAG processing
        test_question = "Who is the Dragonborn?"
        test_context = [
            ("The Dragonborn is a legendary figure in Elder Scrolls lore who can absorb dragon souls and use the Thu'um.", 0.9),
            ("Dragonborn individuals have the ability to shout like dragons and are destined to face great challenges.", 0.8)
        ]
        
        print(f"   Testing RAG processing for: '{test_question}'")
        response = await rag_processor.process_question(test_question, test_context)
        
        if response and len(response) > 0:
            print(f"✅ RAG processing test successful")
            print(f"   Response: {response[:200]}...")
        else:
            print("❌ RAG processing test failed - empty response")
            return False
            
    except Exception as e:
        print(f"❌ RAG processor test failed: {e}")
        return False
    
    return True

async def test_full_pipeline():
    """Test the complete pipeline from search to response"""
    print("\n🧪 Testing Full Pipeline...")
    
    try:
        # Initialize components
        search_engine = OnlineSearchEngine()
        await search_engine.initialize()
        
        llm_client = LLMClientFactory.create_client()
        rag_processor = RAGProcessor(llm_client)
        
        # Test complete pipeline
        test_question = "What is the history of the Dark Elves?"
        print(f"   Testing full pipeline for: '{test_question}'")
        
        # Search for context
        context_passages = await search_engine.search(test_question)
        
        if context_passages:
            print(f"   Found {len(context_passages)} context passages")
            
            # Process with RAG
            response = await rag_processor.process_question(test_question, context_passages)
            
            if response and len(response) > 0:
                print(f"✅ Full pipeline test successful")
                print(f"   Response: {response[:300]}...")
            else:
                print("❌ Full pipeline test failed - empty response")
                return False
        else:
            print("⚠️  No context found for test question")
            print("   This might be normal if the search sources are unavailable")
        
        # Cleanup
        await search_engine.close()
            
    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        return False
    
    return True

async def test_configuration():
    """Test configuration validation"""
    print("🧪 Testing Configuration...")
    
    try:
        config_errors = Config.validate_config()
        
        if not config_errors:
            print("✅ Configuration validation passed")
            print(f"   LLM Backend: {Config.get_llm_backend().value}")
            print(f"   Telegram Token: {'Set' if Config.TELEGRAM_TOKEN else 'Missing'}")
            
            backend = Config.get_llm_backend()
            if backend.value == "openrouter":
                print(f"   OpenRouter API Key: {'Set' if Config.OPENROUTER_API_KEY else 'Missing'}")
            elif backend.value == "ollama":
                print(f"   Ollama URL: {Config.OLLAMA_BASE_URL}")
            elif backend.value == "lm_studio":
                print(f"   LM Studio URL: {Config.LM_STUDIO_BASE_URL}")
                
        else:
            print("❌ Configuration validation failed:")
            for error in config_errors:
                print(f"   - {error}")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting Elder Scrolls Lore Bot Tests...\n")
    
    tests = [
        ("Configuration", test_configuration),
        ("Online Search Engine", test_online_search_engine),
        ("LLM Client", test_llm_client),
        ("RAG Processor", test_rag_processor),
        ("Full Pipeline", test_full_pipeline),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your bot should work correctly.")
    else:
        print("⚠️  Some tests failed. Please check the configuration and try again.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)