import faiss
import json
import numpy as np

def load_resources():
    from sentence_transformers import SentenceTransformer
    import faiss
    import json

    model = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index("faiss_index.bin")
    with open("index_to_data.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return model, index, metadata


