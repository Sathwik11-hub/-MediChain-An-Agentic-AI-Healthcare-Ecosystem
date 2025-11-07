"""
RAG (Retrieval-Augmented Generation) Service for medical knowledge retrieval.
"""
import os
from typing import List, Dict, Any, Optional
from loguru import logger
from sentence_transformers import SentenceTransformer
import numpy as np
from Bio import Entrez

from config.settings import settings

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone not available, using in-memory FAISS")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available")


class RAGService:
    """Service for RAG operations with vector search and document retrieval."""
    
    def __init__(self):
        """Initialize RAG service with vector database and embedding model."""
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize vector store
        self.use_pinecone = PINECONE_AVAILABLE and settings.pinecone_api_key
        
        if self.use_pinecone:
            self._init_pinecone()
        elif FAISS_AVAILABLE:
            self._init_faiss()
        else:
            logger.warning("No vector store available, RAG functionality limited")
            self.index = None
            self.documents = []
        
        # Initialize PubMed
        Entrez.email = settings.pubmed_email
        if settings.pubmed_api_key:
            Entrez.api_key = settings.pubmed_api_key
        
        logger.info("RAG Service initialized")
    
    def _init_pinecone(self) -> None:
        """Initialize Pinecone vector database."""
        try:
            pinecone.init(
                api_key=settings.pinecone_api_key,
                environment=settings.pinecone_environment
            )
            
            # Check if index exists, create if not
            if settings.pinecone_index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=settings.pinecone_index_name,
                    dimension=self.dimension,
                    metric="cosine"
                )
            
            self.index = pinecone.Index(settings.pinecone_index_name)
            logger.info(f"Connected to Pinecone index: {settings.pinecone_index_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            self.use_pinecone = False
            if FAISS_AVAILABLE:
                self._init_faiss()
    
    def _init_faiss(self) -> None:
        """Initialize FAISS in-memory vector store."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        logger.info("Initialized FAISS in-memory index")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector
        """
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding
    
    def embed_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Embed multiple documents and store in vector database.
        
        Args:
            documents: List of documents with 'id', 'text', and 'metadata'
            
        Returns:
            List of documents with embeddings
        """
        logger.info(f"Embedding {len(documents)} documents")
        
        embedded_docs = []
        for doc in documents:
            embedding = self.embed_text(doc['text'])
            doc['embedding'] = embedding.tolist()
            embedded_docs.append(doc)
        
        # Store in vector database
        if self.use_pinecone:
            self._store_pinecone(embedded_docs)
        elif FAISS_AVAILABLE and self.index is not None:
            self._store_faiss(embedded_docs)
        
        logger.info(f"Stored {len(embedded_docs)} documents")
        return embedded_docs
    
    def _store_pinecone(self, documents: List[Dict[str, Any]]) -> None:
        """Store documents in Pinecone."""
        vectors = [
            (doc['id'], doc['embedding'], doc.get('metadata', {}))
            for doc in documents
        ]
        self.index.upsert(vectors=vectors)
    
    def _store_faiss(self, documents: List[Dict[str, Any]]) -> None:
        """Store documents in FAISS."""
        embeddings = np.array([doc['embedding'] for doc in documents]).astype('float32')
        self.index.add(embeddings)
        self.documents.extend(documents)
    
    def semantic_search(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Metadata filters
            
        Returns:
            List of relevant documents with scores
        """
        top_k = top_k or settings.top_k_results
        
        query_embedding = self.embed_text(query)
        
        if self.use_pinecone:
            return self._search_pinecone(query_embedding, top_k, filter_metadata)
        elif FAISS_AVAILABLE and self.index is not None:
            return self._search_faiss(query_embedding, top_k)
        else:
            logger.warning("No vector store available for search")
            return []
    
    def _search_pinecone(
        self,
        query_embedding: np.ndarray,
        top_k: int,
        filter_metadata: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Search in Pinecone."""
        results = self.index.query(
            vector=query_embedding.tolist(),
            top_k=top_k,
            filter=filter_metadata,
            include_metadata=True
        )
        
        return [
            {
                'id': match.id,
                'score': match.score,
                'metadata': match.metadata
            }
            for match in results.matches
        ]
    
    def _search_faiss(
        self,
        query_embedding: np.ndarray,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Search in FAISS."""
        if not self.documents:
            return []
        
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['score'] = float(1 / (1 + distances[0][i]))  # Convert distance to similarity
                results.append(doc)
        
        return results
    
    def retrieve_pubmed_articles(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve medical articles from PubMed.
        
        Args:
            query: Search query
            max_results: Maximum number of articles to retrieve
            
        Returns:
            List of articles with metadata
        """
        logger.info(f"Searching PubMed for: {query}")
        
        try:
            # Search PubMed
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort="relevance"
            )
            record = Entrez.read(handle)
            handle.close()
            
            id_list = record["IdList"]
            
            if not id_list:
                logger.info("No PubMed articles found")
                return []
            
            # Fetch article details
            handle = Entrez.efetch(
                db="pubmed",
                id=id_list,
                rettype="medline",
                retmode="text"
            )
            articles_text = handle.read()
            handle.close()
            
            # Parse articles (simplified)
            articles = []
            for pmid in id_list:
                articles.append({
                    'pmid': pmid,
                    'title': f"PubMed Article {pmid}",
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    'source': 'PubMed'
                })
            
            logger.info(f"Retrieved {len(articles)} PubMed articles")
            return articles
            
        except Exception as e:
            logger.error(f"Error retrieving PubMed articles: {e}")
            return []
    
    def get_relevant_context(
        self,
        query: str,
        include_pubmed: bool = True,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Get relevant context from multiple sources.
        
        Args:
            query: Search query
            include_pubmed: Whether to include PubMed results
            top_k: Number of results from each source
            
        Returns:
            Combined context from all sources
        """
        context = {
            'query': query,
            'vector_search_results': [],
            'pubmed_articles': []
        }
        
        # Vector search
        vector_results = self.semantic_search(query, top_k=top_k)
        context['vector_search_results'] = vector_results
        
        # PubMed search
        if include_pubmed:
            pubmed_results = self.retrieve_pubmed_articles(query, max_results=top_k)
            context['pubmed_articles'] = pubmed_results
        
        return context


# Singleton instance
_rag_service = None


def get_rag_service() -> RAGService:
    """Get or create RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
