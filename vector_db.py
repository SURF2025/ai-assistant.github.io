import chromadb
import os
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import streamlit as st
from typing import List, Dict, Tuple
import hashlib

class MeetingVectorDB:
    def __init__(self, persist_directory="./chroma_db"):
        """Initialize ChromaDB client and collection"""
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = "meeting_transcripts"
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Meeting transcript embeddings"}
            )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()
            return full_text.strip()
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Find the last sentence boundary within the chunk
            if end < len(text):
                last_period = text.rfind('.', start, end)
                last_exclamation = text.rfind('!', start, end)
                last_question = text.rfind('?', start, end)
                
                sentence_end = max(last_period, last_exclamation, last_question)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
        return chunks
    
    def get_file_hash(self, file_path: str) -> str:
        """Get hash of file for checking if it's already processed"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def is_file_processed(self, file_path: str) -> bool:
        """Check if file is already in the database"""
        filename = os.path.basename(file_path)
        file_hash = self.get_file_hash(file_path)
        
        try:
            results = self.collection.get(
                where={"filename": filename, "file_hash": file_hash},
                limit=1
            )
            return len(results['ids']) > 0
        except:
            return False
    
    def add_meeting_to_db(self, file_path: str) -> bool:
        """Add a meeting PDF to the vector database"""
        if self.is_file_processed(file_path):
            print(f"File {file_path} already processed. Skipping.")
            return True
        
        try:
            # Extract text
            text = self.extract_text_from_pdf(file_path)
            if not text:
                print(f"No text extracted from {file_path}")
                return False
            
            # Chunk text
            chunks = self.chunk_text(text)
            
            # Prepare data for ChromaDB
            filename = os.path.basename(file_path)
            file_hash = self.get_file_hash(file_path)
            
            ids = []
            documents = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{filename}_{file_hash}_{i}"
                ids.append(chunk_id)
                documents.append(chunk)
                metadatas.append({
                    "filename": filename,
                    "file_hash": file_hash,
                    "chunk_index": i,
                    "file_path": file_path
                })
            
            # Add to collection
            self.collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )
            
            print(f"Added {len(chunks)} chunks from {filename} to vector database")
            return True
            
        except Exception as e:
            print(f"Error adding {file_path} to database: {e}")
            return False
    
    def process_all_meetings(self, meetings_dir: str = "data/Meetings") -> Dict[str, bool]:
        """Process all PDF files in the meetings directory"""
        results = {}
        
        if not os.path.exists(meetings_dir):
            print(f"Meetings directory {meetings_dir} does not exist")
            return results
        
        pdf_files = [f for f in os.listdir(meetings_dir) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            file_path = os.path.join(meetings_dir, pdf_file)
            success = self.add_meeting_to_db(file_path)
            results[pdf_file] = success
        
        return results
    
    def query_meeting(self, query: str, filename: str, top_k: int = 5) -> List[str]:
        """Query the vector database for relevant chunks from a specific meeting"""
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where={"filename": filename}
            )
            
            if results['documents'] and len(results['documents'][0]) > 0:
                return results['documents'][0]
            else:
                return []
                
        except Exception as e:
            print(f"Error querying database: {e}")
            return []
    
    def get_all_filenames(self) -> List[str]:
        """Get all unique filenames in the database"""
        try:
            results = self.collection.get()
            filenames = set()
            for metadata in results['metadatas']:
                filenames.add(metadata['filename'])
            return list(filenames)
        except:
            return []
    
    def delete_meeting(self, filename: str) -> bool:
        """Delete all chunks for a specific meeting file"""
        try:
            # Get all IDs for the filename
            results = self.collection.get(
                where={"filename": filename}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"Deleted {len(results['ids'])} chunks for {filename}")
                return True
            else:
                print(f"No chunks found for {filename}")
                return False
                
        except Exception as e:
            print(f"Error deleting {filename}: {e}")
            return False

@st.cache_resource
def get_vector_db():
    """Get or create the vector database instance (cached)"""
    return MeetingVectorDB()

def initialize_vector_db_if_needed():
    """Initialize vector database and process meetings if needed"""
    try:
        vector_db = get_vector_db()
        
        # Check if we need to process any meetings
        meetings_dir = "data/Meetings"
        if os.path.exists(meetings_dir):
            pdf_files = [f for f in os.listdir(meetings_dir) if f.endswith('.pdf')]
            existing_files = vector_db.get_all_filenames()
            
            # Find files that need processing
            files_to_process = [f for f in pdf_files if f not in existing_files]
            
            if files_to_process:
                with st.spinner(f"Processing {len(files_to_process)} meeting files for vector search..."):
                    results = vector_db.process_all_meetings()
                    success_count = sum(1 for success in results.values() if success)
                    st.success(f"✅ Processed {success_count}/{len(files_to_process)} meeting files")
            
        return vector_db
        
    except Exception as e:
        st.error(f"Error initializing vector database: {e}")
        return None

def retrieve_relevant_context(query: str, filename: str, top_k: int = 3) -> str:
    """Retrieve relevant context for a query from a specific meeting file"""
    try:
        vector_db = get_vector_db()
        relevant_chunks = vector_db.query_meeting(query, filename, top_k)
        
        if relevant_chunks:
            return "\n\n".join(relevant_chunks)
        else:
            # Fallback to full transcript if no relevant chunks found
            file_path = os.path.join("data/Meetings", filename)
            return vector_db.extract_text_from_pdf(file_path)
            
    except Exception as e:
        print(f"Error retrieving context: {e}")
        # Fallback to full transcript
        file_path = os.path.join("data/Meetings", filename)
        vector_db = get_vector_db()
        return vector_db.extract_text_from_pdf(file_path)
