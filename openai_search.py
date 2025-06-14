import os
import json
import numpy as np
from openai import OpenAI

client = OpenAI(
    api_key="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE3NTBAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.v85lE2a1QBW-INTFrcyVHeiDHA5bHBqxf9cxwVlLtqE",
    base_url="https://aipipe.org/openai/v1"
)

# Load metadata and precomputed OpenAI embeddings
with open("index_to_data.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

with open("openai_embeddings.npy", "rb") as f:
    vectors = np.load(f)

texts = [metadata[str(i)] for i in range(len(metadata))]

def cosine_similarity(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b, axis=1, keepdims=True)
    return np.dot(b, a)

def search_openai_embeddings(query, top_k=5):
    # Get query embedding from OpenAI
    response = client.embeddings.create(
        model="text-embedding-3-small",  # or text-embedding-ada-002
        input=query
    )
    query_vec = np.array(response.data[0].embedding)

    # Compute cosine similarity
    sims = cosine_similarity(query_vec, vectors)
    top_indices = sims.argsort()[-top_k:][::-1]

    return [texts[i] for i in top_indices]
