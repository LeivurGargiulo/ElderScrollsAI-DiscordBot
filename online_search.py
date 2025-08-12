import asyncio
import aiohttp
import requests
import json
import time
import logging
from typing import List, Tuple, Optional, Dict, Any
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
import wikipediaapi
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
import numpy as np

from config import Config

logger = logging.getLogger(__name__)

class OnlineSearchEngine:
    """Online search engine for Elder Scrolls lore with three-tier search strategy"""
    
    def __init__(self):
        self.embedding_model = None
        self.session = None
        self.last_request_time = 0
        
    async def initialize(self):
        """Initialize the search engine"""
        try:
            # Initialize embedding model for similarity search
            logger.info(f"Loading embedding model: {Config.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
            
            # Initialize aiohttp session for async requests
            self.session = aiohttp.ClientSession(
                headers={"User-Agent": Config.USER_AGENT},
                timeout=aiohttp.ClientTimeout(total=Config.REQUEST_TIMEOUT)
            )
            
            logger.info("Online search engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize online search engine: {e}")
            return False
    
    async def close(self):
        """Close the search engine and cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def _rate_limit(self):
        """Implement rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < Config.REQUEST_DELAY:
            await asyncio.sleep(Config.REQUEST_DELAY - time_since_last)
        self.last_request_time = time.time()
    
    async def search_huggingface_datasets(self, query: str) -> List[Tuple[str, float]]:
        """Search the Elder Scrolls Wiki dataset via Hugging Face Datasets API"""
        try:
            await self._rate_limit()
            
            logger.info(f"Searching Hugging Face dataset for: {query}")
            
            # Load dataset from Hugging Face
            dataset = load_dataset(Config.DATASET_NAME)
            
            # Extract text passages
            texts = []
            for split in dataset.keys():
                for item in dataset[split]:
                    if 'text' in item:
                        texts.append(item['text'])
                    elif 'content' in item:
                        texts.append(item['content'])
                    elif 'passage' in item:
                        texts.append(item['passage'])
                    elif 'article' in item:
                        texts.append(item['article'])
                    else:
                        # Find any text-like field
                        for key, value in item.items():
                            if isinstance(value, str) and len(value) > 50:
                                texts.append(value)
                                break
            
            if not texts:
                logger.warning("No texts found in Hugging Face dataset")
                return []
            
            # Create embeddings for query and texts
            query_embedding = self.embedding_model.encode([query])
            text_embeddings = self.embedding_model.encode(texts)
            
            # Calculate similarities
            similarities = np.dot(text_embeddings, query_embedding.T).flatten()
            
            # Get top results
            top_indices = np.argsort(similarities)[::-1][:Config.TOP_K_RESULTS]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    results.append((texts[idx], float(similarities[idx])))
            
            logger.info(f"Found {len(results)} relevant passages from Hugging Face dataset")
            return results
            
        except Exception as e:
            logger.error(f"Error searching Hugging Face dataset: {e}")
            return []
    
    async def search_uesp_wiki(self, query: str) -> List[Tuple[str, float]]:
        """Search the Elder Scrolls Wiki (UESP) via API"""
        try:
            await self._rate_limit()
            
            logger.info(f"Searching UESP Wiki for: {query}")
            
            # Search UESP using their search API
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': Config.MAX_SEARCH_RESULTS,
                'srnamespace': 0  # Main namespace
            }
            
            async with self.session.get(Config.UESP_API_BASE_URL, params=search_params) as response:
                if response.status != 200:
                    logger.warning(f"UESP API returned status {response.status}")
                    return []
                
                data = await response.json()
                
                if 'query' not in data or 'search' not in data['query']:
                    logger.warning("No search results from UESP API")
                    return []
                
                results = []
                for item in data['query']['search']:
                    # Extract relevant content from search result
                    content = item.get('snippet', '')
                    if len(content) >= Config.MIN_CONTENT_LENGTH:
                        # Clean HTML tags
                        soup = BeautifulSoup(content, 'html.parser')
                        clean_content = soup.get_text()
                        if len(clean_content) >= Config.MIN_CONTENT_LENGTH:
                            results.append((clean_content, 0.8))  # Default score for API results
                
                logger.info(f"Found {len(results)} relevant passages from UESP Wiki")
                return results
                
        except Exception as e:
            logger.error(f"Error searching UESP Wiki: {e}")
            return []
    
    async def search_wikipedia_elder_scrolls(self, query: str) -> List[Tuple[str, float]]:
        """Search Wikipedia for Elder Scrolls related content"""
        try:
            await self._rate_limit()
            
            logger.info(f"Searching Wikipedia for Elder Scrolls content: {query}")
            
            # Use wikipedia-api to search for Elder Scrolls content
            wiki = wikipediaapi.Wikipedia(
                language='en',
                extract_format=wikipediaapi.ExtractFormat.WIKI,
                user_agent=Config.USER_AGENT
            )
            
            # Search for Elder Scrolls related pages
            search_query = f"Elder Scrolls {query}"
            search_results = wiki.search(search_query, results=Config.MAX_SEARCH_RESULTS)
            
            results = []
            for page_title in search_results:
                page = wiki.page(page_title)
                if page.exists() and page.summary:
                    # Check if content is Elder Scrolls related
                    if any(keyword in page.summary.lower() for keyword in 
                          ['elder scrolls', 'tamriel', 'skyrim', 'oblivion', 'morrowind', 'cyrodiil']):
                        content = page.summary[:Config.MAX_CONTENT_LENGTH]
                        if len(content) >= Config.MIN_CONTENT_LENGTH:
                            results.append((content, 0.7))  # Lower score than UESP
            
            logger.info(f"Found {len(results)} relevant passages from Wikipedia")
            return results
            
        except Exception as e:
            logger.error(f"Error searching Wikipedia: {e}")
            return []
    
    async def scrape_uesp_pages(self, query: str) -> List[Tuple[str, float]]:
        """Scrape UESP pages for relevant content (fallback method)"""
        try:
            await self._rate_limit()
            
            logger.info(f"Scraping UESP pages for: {query}")
            
            # First, search for relevant pages
            search_url = f"{Config.UESP_SEARCH_URL}?search={quote(query)}"
            
            async with self.session.get(search_url) as response:
                if response.status != 200:
                    logger.warning(f"UESP search page returned status {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find search result links
                search_results = soup.find_all('a', href=True)
                relevant_links = []
                
                for link in search_results:
                    href = link.get('href', '')
                    if href.startswith('/wiki/') and any(keyword in link.get_text().lower() 
                                                       for keyword in query.lower().split()):
                        relevant_links.append(href)
                        if len(relevant_links) >= 3:  # Limit to 3 pages
                            break
                
                results = []
                for link in relevant_links:
                    try:
                        await self._rate_limit()
                        
                        full_url = urljoin("https://en.uesp.net", link)
                        async with self.session.get(full_url) as page_response:
                            if page_response.status == 200:
                                page_html = await page_response.text()
                                page_soup = BeautifulSoup(page_html, 'html.parser')
                                
                                # Extract main content
                                content_div = page_soup.find('div', id='mw-content-text')
                                if content_div:
                                    # Remove navigation and other non-content elements
                                    for element in content_div.find_all(['script', 'style', 'nav', 'table']):
                                        element.decompose()
                                    
                                    content = content_div.get_text()
                                    # Clean up whitespace
                                    content = ' '.join(content.split())
                                    
                                    if len(content) >= Config.MIN_CONTENT_LENGTH:
                                        content = content[:Config.MAX_CONTENT_LENGTH]
                                        results.append((content, 0.6))  # Lower score for scraped content
                    
                    except Exception as e:
                        logger.warning(f"Error scraping page {link}: {e}")
                        continue
                
                logger.info(f"Found {len(results)} relevant passages from scraped UESP pages")
                return results
                
        except Exception as e:
            logger.error(f"Error scraping UESP pages: {e}")
            return []
    
    async def search(self, query: str) -> List[Tuple[str, float]]:
        """Main search method implementing three-tier strategy"""
        all_results = []
        
        # Tier 1: Try Hugging Face Datasets API
        logger.info("Tier 1: Searching Hugging Face Datasets API")
        hf_results = await self.search_huggingface_datasets(query)
        all_results.extend(hf_results)
        
        # If we have enough good results, return them
        if len([r for r in all_results if r[1] > 0.5]) >= Config.TOP_K_RESULTS:
            logger.info("Sufficient results found from Hugging Face dataset")
            return sorted(all_results, key=lambda x: x[1], reverse=True)[:Config.TOP_K_RESULTS]
        
        # Tier 2: Try Elder Scrolls Wiki API
        logger.info("Tier 2: Searching Elder Scrolls Wiki API")
        uesp_results = await self.search_uesp_wiki(query)
        all_results.extend(uesp_results)
        
        # Check if we have enough results
        if len([r for r in all_results if r[1] > 0.4]) >= Config.TOP_K_RESULTS:
            logger.info("Sufficient results found from API sources")
            return sorted(all_results, key=lambda x: x[1], reverse=True)[:Config.TOP_K_RESULTS]
        
        # Tier 3: Try Wikipedia for Elder Scrolls content
        logger.info("Tier 3: Searching Wikipedia for Elder Scrolls content")
        wiki_results = await self.search_wikipedia_elder_scrolls(query)
        all_results.extend(wiki_results)
        
        # Check if we have enough results
        if len([r for r in all_results if r[1] > 0.3]) >= Config.TOP_K_RESULTS:
            logger.info("Sufficient results found including Wikipedia")
            return sorted(all_results, key=lambda x: x[1], reverse=True)[:Config.TOP_K_RESULTS]
        
        # Tier 4: Fallback to polite scraping
        logger.info("Tier 4: Fallback to polite scraping")
        scrape_results = await self.scrape_uesp_pages(query)
        all_results.extend(scrape_results)
        
        # Return top results
        final_results = sorted(all_results, key=lambda x: x[1], reverse=True)[:Config.TOP_K_RESULTS]
        logger.info(f"Final search results: {len(final_results)} passages found")
        
        return final_results
    
    def extract_relevant_snippets(self, content: str, query: str, max_length: int = 500) -> str:
        """Extract the most relevant snippet from content based on query"""
        try:
            # Simple keyword-based snippet extraction
            query_words = query.lower().split()
            sentences = content.split('. ')
            
            best_sentence = ""
            best_score = 0
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                score = sum(1 for word in query_words if word in sentence_lower)
                if score > best_score:
                    best_score = score
                    best_sentence = sentence
            
            if best_sentence:
                # Truncate if too long
                if len(best_sentence) > max_length:
                    best_sentence = best_sentence[:max_length] + "..."
                return best_sentence
            
            # Fallback: return first part of content
            return content[:max_length] + "..." if len(content) > max_length else content
            
        except Exception as e:
            logger.error(f"Error extracting snippet: {e}")
            return content[:max_length] + "..." if len(content) > max_length else content