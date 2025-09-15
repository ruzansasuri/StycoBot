import json
import os
from openai import OpenAI
import requests
import chromadb

from RAG.libs.common import save_to_json

# Ollama API endpoint
OLLAMA_URL = "http://localhost:11434/api/embeddings"

def get_embedding_local(text, model="mxbai-embed-large"):
    """Get embedding from Ollama"""
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": text
    })
    result = response.json()
    # print("API Response:", result)
    return result["embedding"]

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
    embeddings_data = []
    for i, chunk in enumerate(chunks_data):
        text = chunk["text"]
        
        # Get embedding from Ollama
        embedding = get_embedding_openai(text)
        
        # Store chunk with its embedding
        embeddings_data.append({
            "id": i,
            "text": text,
            "metadata": chunk["metadata"],
            "embedding": embedding
        })
        
        print(f"Processed chunk {i+1}/{len(chunks_data)}")
    return embeddings_data



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