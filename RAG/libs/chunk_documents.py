from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SimpleNodeParser 

from RAG.libs.common import save_to_json

def load_documents(file_path):
    """
    Load documents from a directory
    params:
    - file_path: path to the directory containing documents
    returns: list of Document
    """
    return SimpleDirectoryReader(file_path).load_data()

def chunker(documents):
    """
    Chunk documents into smaller pieces
    params:
    - documents: list of Document
    returns: list of DocumentNode
    """
    # Create a chunker
    parser = SimpleNodeParser.from_defaults()

    # Chunk it
    return parser.get_nodes_from_documents(documents)


def chunks_to_list(nodes):
    """
    Convert chunks to a list of dicts
    params:
    - nodes: list of DocumentNode
    returns: list of dicts with 'text' and 'metadata' keys
    """
    chunks_data = []
    for node in nodes:  
        chunks_data.append({
            "text": node.text,        
            "metadata": node.metadata 
        })
    return chunks_data

def test_chunker():
    documents = load_documents("RAG/documents")
    nodes = chunker(documents)
    chunks_data = chunks_to_list(nodes)
    save_to_json(chunks_data, "RAG/chunks/chunks.json")
    print(f"Created {len(chunks_data)} chunks")
    print(f"Example chunk: {chunks_data[0]['text'][:100]}...")
    print(f"Metadata: {chunks_data[0]['metadata']}")

if __name__ == "__main__":
    print("This is for testing purposes only. Please call lib files directly.")
    test_chunker()