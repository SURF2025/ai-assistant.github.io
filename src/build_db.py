from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter

# Load PDF and extract pages as documents
pdf_path = "example.pdf"  # Replace with your PDF file path
loader = PyPDFLoader(pdf_path)
pages = loader.load()

# Split documents into manageable chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
docs = text_splitter.split_documents(pages)

# Initialize Ollama embeddings
embedding_function = OllamaEmbeddings(
    base_url="http://localhost:11434",
    model="llama3.1"
)

# Create Chroma vector store and add the chunks
db = Chroma.from_documents(
    documents=docs,
    embedding=embedding_function,
    persist_directory="chroma_db"
)

print(f"Chroma DB created and {len(docs)} chunks from PDF added.")