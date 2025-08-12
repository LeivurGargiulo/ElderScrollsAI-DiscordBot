#!/usr/bin/env python3
"""
Test script for Elder Scrolls Lore Bot components
Run this to verify everything works before starting the Telegram bot
"""

import asyncio
import logging
from config import Config
from dataset_loader import ElderScrollsDatasetLoader
from llm_client import LLMClientFactory, RAGProcessor

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_dataset_loader():
    """Test the dataset loader component"""
    print("🧪 Testing Dataset Loader...")
    
    try:
        loader = ElderScrollsDatasetLoader()
        success = loader.initialize()
        
        if success:
            print("✅ Dataset loader initialized successfully")
            
            # Test search functionality
            test_query = "Dragonborn"
            results = loader.search(test_query, top_k=2)
            
            if results:
                print(f"✅ Search test successful - found {len(results)} results for '{test_query}'")
                for i, (text, score) in enumerate(results):
                    print(f"   Result {i+1} (score: {score:.3f}): {text[:100]}...")
            else:
                print("⚠️  Search returned no results")
                
        else:
            print("❌ Dataset loader initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Dataset loader test failed: {e}")
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
            ("The Dragonborn is a legendary hero in Elder Scrolls lore who can absorb dragon souls.", 0.9),
            ("Dragons are powerful creatures in Tamriel that can use Thu'um or dragon shouts.", 0.8)
        ]
        
        print("   Testing RAG processing...")
        response = rag_processor.process_question(test_question, test_context)
        
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
    """Test the full RAG pipeline"""
    print("\n🧪 Testing Full RAG Pipeline...")
    
    try:
        # Initialize components
        loader = ElderScrollsDatasetLoader()
        if not loader.initialize():
            print("❌ Failed to initialize dataset loader")
            return False
        
        llm_client = LLMClientFactory.create_client()
        rag_processor = RAGProcessor(llm_client)
        
        # Test full pipeline
        test_question = "What is the Dragonborn?"
        
        print(f"   Testing full pipeline with question: '{test_question}'")
        
        # Search for relevant passages
        context_passages = loader.search(test_question, top_k=2)
        
        if not context_passages:
            print("   ⚠️  No relevant passages found, but continuing test...")
        
        # Process with RAG
        response = rag_processor.process_question(test_question, context_passages)
        
        if response and len(response) > 0:
            print(f"✅ Full pipeline test successful")
            print(f"   Found {len(context_passages)} relevant passages")
            print(f"   Response: {response[:300]}...")
        else:
            print("❌ Full pipeline test failed - empty response")
            return False
            
    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting Elder Scrolls Lore Bot Tests\n")
    
    tests = [
        ("Dataset Loader", test_dataset_loader),
        ("LLM Client", test_llm_client),
        ("RAG Processor", test_rag_processor),
        ("Full Pipeline", test_full_pipeline)
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
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your bot is ready to run.")
        print("   Run 'python telegram_bot.py' to start the bot.")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration and try again.")
        print("   Make sure you have:")
        print("   - Valid Telegram bot token")
        print("   - Proper LLM backend configuration")
        print("   - Internet connection for dataset loading")

if __name__ == "__main__":
    asyncio.run(main())