import json
import os
from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer

from RAG.libs.common import save_to_json

# Ollama API endpoint
OLLAMA_URL = "http://localhost:11434/api/embeddings"

def get_embedding_local(texts):
    """Get embedding from python"""
    model = SentenceTransformer("all-MiniLM-L6-v2")  # small, fast, good enough for most RAG
    return model.encode(texts, batch_size=32).tolist()

def get_embedding_openai(text, model="text-embedding-3-small"):
    """Get embedding from OpenAI"""
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding


def get_chunks(file_path):
    """Load chunks from a JSON file"""
    with open(file_path, "r") as f:
        return json.load(f)


def get_embeddings(chunks_data):
    """Get embeddings for all chunks"""
    texts = [chunk["text"] for chunk in chunks_data]
    embeddings = get_embedding_local(texts)

    return [
        {
            "id": i,
            "text": chunk["text"],
            "metadata": chunk["metadata"],
            "embedding": emb
        }
        for i, (chunk, emb) in enumerate(zip(chunks_data, embeddings))
    ]



def save_to_chroma(file_path, embeddings_data):
    client = chromadb.PersistentClient(path=file_path)
    collection = client.get_or_create_collection(
    name="document_chunks",
    metadata={"description": "Document chunks with embeddings"}
)
    
    """Save embeddings to Chroma vector store"""# Prepare data for Chroma
    ids = [str(chunk["id"]) for chunk in embeddings_data]
    embeddings = [chunk["embedding"] for chunk in embeddings_data]
    documents = [chunk["text"] for chunk in embeddings_data]
    metadatas = [chunk["metadata"] for chunk in embeddings_data]
    # Add to vector store
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )
    print("Saved embeddings to Chroma vector store")

def test_chroma():
    chunks_data = get_chunks("RAG/chunks/chunks.json")
    embeddings_data = get_embeddings(chunks_data)
    save_to_json(embeddings_data, "RAG/embeddings/embeddings.json")
    print(f"Created embeddings for {len(embeddings_data)} chunks")
    print(f"Embedding dimension: {len(embeddings_data[0]['embedding'])}")
    save_to_chroma("RAG/chroma_db", embeddings_data)

if __name__ == "__main__":
    print("This is for testing purposes only. Please call lib files directly.")
    test_chroma()