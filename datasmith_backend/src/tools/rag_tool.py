import os
import chromadb
from pathlib import Path
from typing import List, Dict
from chromadb.config import Settings
from src.utils.logger import Logger
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.constants.environment_constants import EnvironmentConstants

# Docling for PDF processing with OCR
from docling.document_converter import DocumentConverter


class RAGTool:
    def __init__(self):
        self.vector_db_path = Path(EnvironmentConstants.VECTOR_DB_PATH.value)
        self.pdf_path = Path(EnvironmentConstants.NEPHROLOGY_PDF_PATH.value)
        self.collection_name = EnvironmentConstants.VECTOR_COLLECTION_NAME.value
        
        # Initialize embedding model (local, free)
        Logger.log_info_message("Loading embedding model...")
        self.embedding_model = SentenceTransformer(EnvironmentConstants.EMBEDDING_MODEL.value)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.vector_db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize Docling converter
        self.doc_converter = DocumentConverter()
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        Logger.log_info_message(f"RAG Tool initialized. Collection size: {self.collection.count()}")
    
    def _get_or_create_collection(self):
        """Get existing collection or create new one"""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            Logger.log_info_message(f"Loaded existing collection: {self.collection_name}")
            return collection
        except:
            Logger.log_info_message(f"Creating new collection: {self.collection_name}")
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Process PDF if it exists
            if self.pdf_path.exists():
                self._process_pdf_with_docling(collection)
            else:
                Logger.log_error_message(
                    Exception("PDF not found"),
                    f"Nephrology PDF not found at: {self.pdf_path}"
                )
            
            return collection
    
    def _process_pdf_with_docling(self, collection):
        """Process PDF using Docling (handles text + OCR automatically)"""
        try:
            Logger.log_info_message(f"Processing PDF with Docling: {self.pdf_path}")
            Logger.log_info_message("Docling will automatically handle text extraction and OCR...")
            
            # Convert PDF using Docling
            result = self.doc_converter.convert(str(self.pdf_path))
            
            # Extract text from document
            full_text = result.document.export_to_markdown()
            
            if not full_text or len(full_text.strip()) < 100:
                Logger.log_error_message(
                    Exception("No text extracted"),
                    "Docling failed to extract meaningful text from PDF"
                )
                return
            
            Logger.log_info_message(f"Successfully extracted {len(full_text)} characters from PDF")
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=EnvironmentConstants.CHUNK_SIZE.value,
                chunk_overlap=EnvironmentConstants.CHUNK_OVERLAP.value,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            # Create document-like objects for splitting
            chunks = text_splitter.create_documents(
                texts=[full_text],
                metadatas=[{"source": "nephrology_book", "extraction_method": "docling"}]
            )
            
            Logger.log_info_message(f"Created {len(chunks)} chunks from PDF")
            
            # Process in batches
            batch_size = 100
            total_processed = 0
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                
                texts = [chunk.page_content for chunk in batch]
                
                # Generate embeddings
                Logger.log_info_message(f"Generating embeddings for batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}...")
                embeddings = self.embedding_model.encode(texts, show_progress_bar=False).tolist()
                
                # Create IDs and metadata
                ids = [f"doc_{i+j}" for j in range(len(batch))]
                metadatas = [
                    {
                        "chunk_index": i+j,
                        "source": "nephrology_book",
                        "extraction_method": "docling"
                    }
                    for j in range(len(batch))
                ]
                
                # Add to collection
                collection.add(
                    ids=ids,
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas
                )
                
                total_processed += len(batch)
                
                # Log progress every 500 chunks
                if total_processed % 500 == 0:
                    Logger.log_info_message(f"Processed {total_processed}/{len(chunks)} chunks...")
            
            Logger.log_info_message(f"✅ Successfully processed {len(chunks)} chunks into vector database")
            
        except Exception as e:
            Logger.log_error_message(e, "Error processing PDF with Docling")
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """Search for relevant documents"""
        if top_k is None:
            top_k = EnvironmentConstants.RAG_TOP_K.value
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "content": doc,
                        "chunk_index": results['metadatas'][0][i].get('chunk_index', 'Unknown'),
                        "source": results['metadatas'][0][i].get('source', 'Unknown'),
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    })
            
            Logger.log_info_message(f"RAG search returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            Logger.log_error_message(e, "Error in RAG search")
            return []