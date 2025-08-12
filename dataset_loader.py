import json
import numpy as np
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import faiss
import os
from typing import List, Tuple, Optional
import logging

from config import Config

logger = logging.getLogger(__name__)

class ElderScrollsDatasetLoader:
    """Handles loading and processing the Elder Scrolls Wiki dataset"""
    
    def __init__(self):
        self.embedding_model = None
        self.faiss_index = None
        self.texts = []
        self.embeddings = None
        
    def load_embedding_model(self):
        """Load the sentence transformer model for embeddings"""
        try:
            logger.info(f"Loading embedding model: {Config.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def load_dataset(self) -> List[str]:
        """Load the Elder Scrolls Wiki dataset from HuggingFace"""
        try:
            logger.info(f"Loading dataset: {Config.DATASET_NAME}")
            dataset = load_dataset(Config.DATASET_NAME)
            
            # Extract text passages from the dataset
            texts = []
            for split in dataset.keys():
                for item in dataset[split]:
                    # Handle different possible field names for text content
                    if 'text' in item:
                        texts.append(item['text'])
                    elif 'content' in item:
                        texts.append(item['content'])
                    elif 'passage' in item:
                        texts.append(item['passage'])
                    elif 'article' in item:
                        texts.append(item['article'])
                    else:
                        # If no standard field, try to find any text-like field
                        for key, value in item.items():
                            if isinstance(value, str) and len(value) > 50:
                                texts.append(value)
                                break
            
            logger.info(f"Loaded {len(texts)} text passages from dataset")
            return texts
            
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for the given texts"""
        if not self.embedding_model:
            self.load_embedding_model()
        
        try:
            logger.info("Creating embeddings for text passages...")
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
            logger.info(f"Created embeddings with shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            raise
    
    def build_faiss_index(self, embeddings: np.ndarray):
        """Build FAISS index for efficient similarity search"""
        try:
            logger.info("Building FAISS index...")
            dimension = embeddings.shape[1]
            
            # Create FAISS index
            self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            self.faiss_index.add(embeddings.astype('float32'))
            
            logger.info(f"FAISS index built with {self.faiss_index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Failed to build FAISS index: {e}")
            raise
    
    def save_to_disk(self, texts: List[str], embeddings: np.ndarray):
        """Save processed data to disk for faster loading"""
        try:
            logger.info("Saving processed data to disk...")
            
            # Save texts
            with open(Config.TEXTS_PATH, 'w', encoding='utf-8') as f:
                json.dump(texts, f, ensure_ascii=False, indent=2)
            
            # Save embeddings
            np.save(Config.EMBEDDINGS_PATH, embeddings)
            
            # Save FAISS index
            faiss.write_index(self.faiss_index, Config.FAISS_INDEX_PATH)
            
            logger.info("Data saved successfully")
        except Exception as e:
            logger.error(f"Failed to save data to disk: {e}")
            raise
    
    def load_from_disk(self) -> bool:
        """Load processed data from disk if available"""
        try:
            if (os.path.exists(Config.TEXTS_PATH) and 
                os.path.exists(Config.EMBEDDINGS_PATH) and 
                os.path.exists(Config.FAISS_INDEX_PATH)):
                
                logger.info("Loading processed data from disk...")
                
                # Load texts
                with open(Config.TEXTS_PATH, 'r', encoding='utf-8') as f:
                    self.texts = json.load(f)
                
                # Load embeddings
                self.embeddings = np.load(Config.EMBEDDINGS_PATH)
                
                # Load FAISS index
                self.faiss_index = faiss.read_index(Config.FAISS_INDEX_PATH)
                
                # Load embedding model
                self.load_embedding_model()
                
                logger.info(f"Loaded {len(self.texts)} texts and FAISS index with {self.faiss_index.ntotal} vectors")
                return True
            else:
                logger.info("No cached data found, will process dataset from scratch")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load from disk: {e}")
            return False
    
    def initialize(self) -> bool:
        """Initialize the dataset loader with embeddings and search index"""
        try:
            # Try to load from disk first
            if self.load_from_disk():
                return True
            
            # If not available on disk, process from scratch
            logger.info("Processing dataset from scratch...")
            
            # Load dataset
            texts = self.load_dataset()
            if not texts:
                logger.error("No texts found in dataset")
                return False
            
            # Create embeddings
            embeddings = self.create_embeddings(texts)
            
            # Build FAISS index
            self.build_faiss_index(embeddings)
            
            # Store data
            self.texts = texts
            self.embeddings = embeddings
            
            # Save to disk for future use
            self.save_to_disk(texts, embeddings)
            
            logger.info("Dataset initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize dataset: {e}")
            return False
    
    def search(self, query: str, top_k: int = None) -> List[Tuple[str, float]]:
        """Search for relevant passages given a query"""
        if not self.faiss_index or not self.embedding_model:
            logger.error("Dataset not initialized")
            return []
        
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        try:
            # Create query embedding
            query_embedding = self.embedding_model.encode([query])
            
            # Search in FAISS index
            scores, indices = self.faiss_index.search(
                query_embedding.astype('float32'), 
                min(top_k, len(self.texts))
            )
            
            # Return results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.texts):
                    results.append((self.texts[idx], float(score)))
            
            logger.info(f"Found {len(results)} relevant passages for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []