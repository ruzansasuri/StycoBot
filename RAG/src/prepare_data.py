
from RAG.libs.chunk_documents import chunker, chunks_to_list, load_documents
from RAG.libs.common import save_to_json
from RAG.libs.create_embeddings import get_chunks, get_embeddings

RAG_DOCUMENTS_PATH = "RAG/source_docs"
RAG_CHUNKS_PATH = "RAG/chunks/chunks.json"
RAG_EMBEDDINGS_PATH = "RAG/embeddings/embeddings.json"
RAG_CHROMA_DB_PATH = "RAG/chroma_db"

def chunk_documents(documents_path=RAG_DOCUMENTS_PATH, chunks_path=RAG_CHUNKS_PATH):
    documents = load_documents(documents_path)
    nodes = chunker(documents)
    chunks_data = chunks_to_list(nodes)
    save_to_json(chunks_data, chunks_path)
    return chunks_data

def create_embeddings(chunks_path=RAG_CHUNKS_PATH, embeddings_path=RAG_EMBEDDINGS_PATH, chroma_db_path=RAG_CHROMA_DB_PATH):
    chunks_data = get_chunks(chunks_path)
    embeddings_data = get_embeddings(chunks_data)
    save_to_json(embeddings_data, embeddings_path)
    print(f"Created embeddings for {len(embeddings_data)} chunks")
    print(f"Embedding dimension: {len(embeddings_data[0]['embedding'])}")
    return embeddings_data

def prepare_data_for_rag():
    chunks_data = chunk_documents()
    print(f"Created {len(chunks_data)} chunks in {RAG_CHUNKS_PATH}.")
    embeddings_data = create_embeddings()
    print(f"Created embeddings for {len(embeddings_data)} chunks in {RAG_EMBEDDINGS_PATH}, stored in Chromadb vector store {RAG_CHROMA_DB_PATH}.")

if __name__ == "__main__":
    print("Preparing data for RAG...")
    prepare_data_for_rag()
    print("Data preparation complete.")