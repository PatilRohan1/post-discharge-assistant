import os
from enum import Enum


class EnvironmentConstants(Enum):
    # Application
    APP_MODE = os.getenv("APP_MODE", "development")
    PORT = int(os.getenv("PORT", 8000))
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    
    # Paths
    LOG_FOLDER_PATH = os.getenv("LOG_FOLDER_PATH", "src/logs")
    DATA_FOLDER_PATH = os.getenv("DATA_FOLDER_PATH", "src/data")
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "src/vector_db")
    
    # Database Files
    PATIENTS_JSON_PATH = os.getenv("PATIENTS_JSON_PATH", "src/data/patients.json")
    NEPHROLOGY_PDF_PATH = os.getenv("NEPHROLOGY_PDF_PATH", "src/data/nephrology_book.pdf")
    
    # LLM Models (Groq - Free)
    RECEPTIONIST_MODEL = os.getenv("RECEPTIONIST_MODEL", "llama-3.1-70b")
    CLINICAL_MODEL = os.getenv("CLINICAL_MODEL", "lllama-3.1-70b")
    
    # Vector DB
    VECTOR_COLLECTION_NAME = os.getenv("VECTOR_COLLECTION_NAME", "nephrology_docs")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # RAG Settings
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", 3))
    
    # Web Search
    WEB_SEARCH_RESULTS = int(os.getenv("WEB_SEARCH_RESULTS", 3))