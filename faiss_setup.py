import faiss
import json
import numpy as np

# Only import SentenceTransformer and avoid auto-importing everything
from sentence_transformers.SentenceTransformer import SentenceTransformer

print("Loading model and FAISS index...")
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("faiss_index.bin")
with open("index_to_data.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

print("Loaded model and FAISS index successfully.")


