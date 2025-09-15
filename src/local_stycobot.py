import chromadb
import requests

class RAGBot:
    def __init__(self, vector_store_path="RAG/vector_store", collection_name="document_chunks"):
        # Connect to vector store
        self.client = chromadb.PersistentClient(path=vector_store_path)
        self.collection = self.client.get_collection(collection_name)
        
    def get_embedding(self, text, model="mxbai-embed-large"):
        """Convert text to embedding using Ollama"""
        response = requests.post("http://localhost:11434/api/embeddings", json={
            "model": model,
            "prompt": text
        })
        return response.json()["embedding"]
    
    def retrieve_context(self, query, n_results=3):
        """Retrieve relevant document chunks"""
        # Convert user query to embedding
        query_embedding = self.get_embedding(query)
        
        # Search vector store for similar chunks
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Extract the text chunks
        context_chunks = results['documents'][0]
        return context_chunks
    
    def generate_response(self, query, context_chunks, model="llama2"):
        """Generate answer using LLM with context"""
        # Combine context chunks
        context = "\n\n".join(context_chunks)
        
        # Create prompt with context
        prompt = f"""Based on the following context, answer the user's question:

Context:
{context}

Question: {query}

Answer:"""
        
        # Send to Ollama LLM
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": False
        })
        
        return response.json()["response"]
    
    def chat(self, query):
        """Complete RAG workflow"""
        print(f"🔍 Searching for relevant information...")
        
        # Step 1: Retrieve relevant chunks
        context_chunks = self.retrieve_context(query)
        
        print(f"📄 Found {len(context_chunks)} relevant chunks")
        
        # Step 2: Generate response with context
        print(f"🤖 Generating response...")
        response = self.generate_response(query, context_chunks)
        
        return response

# Initialize the RAG bot
bot = RAGBot()

# Chat loop
print("RAG Bot ready! Ask questions about your documents (type 'quit' to exit)")
while True:
    user_query = input("\nYou: ")
    if user_query.lower() in ['quit', 'exit']:
        break
        
    try:
        answer = bot.chat(user_query)
        print(f"\nBot: {answer}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Ollama is running and models are available")