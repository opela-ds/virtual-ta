import faiss
import json
import numpy as np

# Only import SentenceTransformer and avoid auto-importing everything
from sentence_transformers.SentenceTransformer import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index
index = faiss.read_index("faiss_index.bin")

# Load metadata
with open("index_to_data.json", "r") as f:
    metadata = json.load(f)

