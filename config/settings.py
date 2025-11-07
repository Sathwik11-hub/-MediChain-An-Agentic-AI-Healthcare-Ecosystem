"""
Application settings and configuration.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    pinecone_api_key: str = ""
    pinecone_environment: str = ""
    pinecone_index_name: str = "medichain"
    pubmed_api_key: str = ""
    pubmed_email: str = ""
    
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    # PostgreSQL
    postgres_uri: str = "postgresql://user:password@localhost:5432/medichain"
    postgres_user: str = "medichain"
    postgres_password: str = "password"
    postgres_db: str = "medichain"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Frontend
    frontend_port: int = 8501
    api_base_url: str = "http://localhost:8000"
    
    # Security
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    
    # Environment
    environment: str = "development"
    
    # LLM Settings
    llm_provider: str = "openai"  # openai or anthropic
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    
    # RAG Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    top_k_results: int = 5
    similarity_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
