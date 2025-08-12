import aiohttp
import json
import subprocess
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from config import Config, LLMBackend

logger = logging.getLogger(__name__)

class LLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        """Generate a response for the given prompt"""
        pass

class OpenRouterClient(LLMClient):
    """Client for OpenRouter API"""
    
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.base_url = Config.OPENROUTER_BASE_URL
        self.model = Config.OPENROUTER_MODEL
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using OpenRouter API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/elder-scrolls-lore-bot",
                "X-Title": "Elder Scrolls Lore Bot"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert on The Elder Scrolls universe. Answer questions based on the provided lore context. Be accurate, concise, and engaging. If the context doesn't contain relevant information, politely say so."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                        return "Sorry, I'm having trouble connecting to my knowledge base right now."
                
        except aiohttp.ClientError as e:
            logger.error(f"OpenRouter API request failed: {e}")
            return "Sorry, I'm having trouble connecting to my knowledge base right now."
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return "Sorry, I encountered an error while processing your request."

class OllamaClient(LLMClient):
    """Client for Ollama local LLM"""
    
    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using Ollama API"""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "prompt": f"""You are an expert on The Elder Scrolls universe. Answer questions based on the provided lore context. Be accurate, concise, and engaging. If the context doesn't contain relevant information, politely say so.

Context: {prompt}

Answer:""",
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1000
                }
            }
            
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["response"]
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {response.status} - {error_text}")
                        return "Sorry, I'm having trouble connecting to my local knowledge base right now."
                
        except aiohttp.ClientError as e:
            logger.error(f"Ollama API request failed: {e}")
            return "Sorry, I'm having trouble connecting to my local knowledge base right now."
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return "Sorry, I encountered an error while processing your request."

class LMStudioClient(LLMClient):
    """Client for LM Studio local LLM"""
    
    def __init__(self):
        self.base_url = Config.LM_STUDIO_BASE_URL
        self.model = Config.LM_STUDIO_MODEL
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using LM Studio API"""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert on The Elder Scrolls universe. Answer questions based on the provided lore context. Be accurate, concise, and engaging. If the context doesn't contain relevant information, politely say so."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }
            
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"LM Studio API error: {response.status} - {error_text}")
                        return "Sorry, I'm having trouble connecting to my local knowledge base right now."
                
        except aiohttp.ClientError as e:
            logger.error(f"LM Studio API request failed: {e}")
            return "Sorry, I'm having trouble connecting to my local knowledge base right now."
        except Exception as e:
            logger.error(f"LM Studio API error: {e}")
            return "Sorry, I encountered an error while processing your request."

class LLMClientFactory:
    """Factory for creating LLM clients based on configuration"""
    
    @staticmethod
    def create_client() -> LLMClient:
        """Create and return the appropriate LLM client based on configuration"""
        backend = Config.get_llm_backend()
        
        if backend == LLMBackend.OPENROUTER:
            return OpenRouterClient()
        elif backend == LLMBackend.OLLAMA:
            return OllamaClient()
        elif backend == LLMBackend.LM_STUDIO:
            return LMStudioClient()
        else:
            raise ValueError(f"Unsupported LLM backend: {backend}")

class RAGProcessor:
    """Handles RAG (Retrieval-Augmented Generation) processing with online search results"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def create_rag_prompt(self, question: str, context_passages: list) -> str:
        """Create a RAG prompt with question and retrieved context from online sources"""
        if not context_passages:
            return f"""Question: {question}

I don't have any relevant information about this in my Elder Scrolls knowledge base. I searched multiple online sources including the Elder Scrolls Wiki, Hugging Face datasets, and Wikipedia, but couldn't find specific information about your query. Please try rephrasing your question or ask about a different aspect of Elder Scrolls lore."""
        
        # Format context with source information
        context_parts = []
        for i, (passage, score) in enumerate(context_passages):
            # Determine source based on score
            if score > 0.7:
                source = "Elder Scrolls Wiki API"
            elif score > 0.5:
                source = "Hugging Face Dataset"
            elif score > 0.4:
                source = "Wikipedia"
            else:
                source = "Web Search"
            
            context_parts.append(f"Context {i+1} (Source: {source}, Relevance: {score:.2f}):\n{passage}")
        
        context_text = "\n\n".join(context_parts)
        
        prompt = f"""You are an expert on The Elder Scrolls universe. Based on the following context retrieved from online Elder Scrolls lore sources, please answer the question accurately and engagingly.

{context_text}

Question: {question}

Please provide a clear, accurate, and engaging answer based on the Elder Scrolls lore. If the context doesn't contain sufficient information to answer the question completely, acknowledge what you know and what might be missing. Always maintain the rich, immersive tone of Elder Scrolls lore."""
        
        return prompt
    
    async def process_question(self, question: str, context_passages: list) -> str:
        """Process a question using RAG with online search results"""
        try:
            # Create RAG prompt
            prompt = self.create_rag_prompt(question, context_passages)
            
            # Generate response using LLM
            response = await self.llm_client.generate_response(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"RAG processing failed: {e}")
            return "Sorry, I encountered an error while processing your question. Please try again."