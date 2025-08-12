#!/usr/bin/env python3
"""
Example usage of Elder Scrolls Lore Bot components
This script demonstrates how to use the bot's search and LLM capabilities programmatically
"""

import asyncio
import logging
from config import Config
from online_search import OnlineSearchEngine
from llm_client import LLMClientFactory, RAGProcessor

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def example_search_and_answer():
    """Example of searching for lore and generating an answer"""
    
    print("🔍 Elder Scrolls Lore Bot - Example Usage")
    print("="*50)
    
    try:
        # Initialize components
        print("Initializing components...")
        search_engine = OnlineSearchEngine()
        await search_engine.initialize()
        
        llm_client = LLMClientFactory.create_client()
        rag_processor = RAGProcessor(llm_client)
        
        print("✅ Components initialized successfully")
        
        # Example questions
        questions = [
            "Who is the Dragonborn?",
            "What is the history of the Dark Elves?",
            "Tell me about the Thalmor",
            "What are the Nine Divines?",
            "Explain the events of the Great War"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n{'='*60}")
            print(f"Question {i}: {question}")
            print(f"{'='*60}")
            
            # Search for relevant context
            print("🔍 Searching for relevant information...")
            context_passages = await search_engine.search(question)
            
            if context_passages:
                print(f"✅ Found {len(context_passages)} relevant passages")
                
                # Show context sources
                for j, (passage, score) in enumerate(context_passages):
                    source = "Unknown"
                    if score > 0.7:
                        source = "Elder Scrolls Wiki API"
                    elif score > 0.5:
                        source = "Hugging Face Dataset"
                    elif score > 0.4:
                        source = "Wikipedia"
                    else:
                        source = "Web Search"
                    
                    print(f"   Source {j+1} ({source}, score: {score:.2f}):")
                    print(f"   {passage[:200]}...")
                
                # Generate answer
                print("\n🤖 Generating answer...")
                answer = rag_processor.process_question(question, context_passages)
                
                print(f"📝 Answer:")
                print(f"{answer}")
                
            else:
                print("❌ No relevant information found")
                print("   This might happen if:")
                print("   - The search sources are unavailable")
                print("   - The question is too specific or obscure")
                print("   - Network connectivity issues")
            
            # Add delay between questions to be polite
            if i < len(questions):
                print("\n⏳ Waiting 2 seconds before next question...")
                await asyncio.sleep(2)
        
        # Cleanup
        await search_engine.close()
        print("\n✅ Example completed successfully")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        logger.error(f"Example failed: {e}")

async def example_custom_search():
    """Example of custom search functionality"""
    
    print("\n🔍 Custom Search Example")
    print("="*30)
    
    try:
        search_engine = OnlineSearchEngine()
        await search_engine.initialize()
        
        # Custom search query
        query = "Dwemer technology"
        print(f"Searching for: {query}")
        
        # Search with custom parameters
        results = await search_engine.search(query)
        
        if results:
            print(f"Found {len(results)} results:")
            for i, (text, score) in enumerate(results):
                print(f"\nResult {i+1} (relevance: {score:.2f}):")
                print(f"{text[:300]}...")
        else:
            print("No results found")
        
        await search_engine.close()
        
    except Exception as e:
        print(f"❌ Custom search failed: {e}")

def example_llm_only():
    """Example of using LLM client directly"""
    
    print("\n🤖 LLM Client Example")
    print("="*25)
    
    try:
        llm_client = LLMClientFactory.create_client()
        
        # Direct LLM prompt
        prompt = """You are an expert on The Elder Scrolls universe. 
        Please provide a brief overview of the different races in Tamriel."""
        
        print("Sending prompt to LLM...")
        response = llm_client.generate_response(prompt)
        
        print("Response:")
        print(response)
        
    except Exception as e:
        print(f"❌ LLM example failed: {e}")

async def main():
    """Run all examples"""
    
    # Check configuration first
    config_errors = Config.validate_config()
    if config_errors:
        print("❌ Configuration errors found:")
        for error in config_errors:
            print(f"   - {error}")
        print("\nPlease fix these issues in your .env file before running examples")
        return
    
    print("✅ Configuration validated")
    
    # Run examples
    await example_search_and_answer()
    await example_custom_search()
    example_llm_only()
    
    print("\n🎉 All examples completed!")
    print("\nYou can now integrate these components into your own applications.")

if __name__ == "__main__":
    asyncio.run(main())