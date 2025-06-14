import faiss
import json
import numpy as np

def load_resources():
    from sentence_transformers import SentenceTransformer

    # 🔄 Lighter model for lower memory usage
    model = SentenceTransformer("paraphrase-MiniLM-L3-v2")

    # Load FAISS index
    index = faiss.read_index("faiss_index.bin")

    # Load metadata
    with open("index_to_data.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)

    return model, index, metadata
