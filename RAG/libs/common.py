import json

def save_to_json(embeddings_data, file_path):
    """Save embeddings to a JSON file"""
    with open(file_path, "w") as f:
        json.dump(embeddings_data, f, indent=2)