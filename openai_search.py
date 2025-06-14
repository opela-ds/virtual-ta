import os
import json
import numpy as np
from openai import OpenAI

client = OpenAI(
    api_key="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE3NTBAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.v85lE2a1QBW-INTFrcyVHeiDHA5bHBqxf9cxwVlLtqE",
    base_url="https://aipipe.org/openai/v1"
)

# Delay loading until first use
metadata = None
embeddings = None

def load_index():
    global metadata, embeddings

    if metadata is not None and embeddings is not None:
        return  # Already loaded

    print("🔄 Loading OpenAI embedding index...")
    with open("index_to_data.json", "r", encoding="utf-8") as f:
        metadata = json.load(f)
    embeddings = np.load("openai_embeddings.npy")

def cosine_similarity(query_vec, embedding_matrix):
    query_vec = query_vec / np.linalg.norm(query_vec)
    embedding_matrix = embedding_matrix / np.linalg.norm(embedding_matrix, axis=1, keepdims=True)
    return np.dot(embedding_matrix, query_vec)

def search_openai_embeddings(query, top_k=5):
    load_index()

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_vec = np.array(response.data[0].embedding)

    similarities = cosine_similarity(query_vec, embeddings)
    top_indices = similarities.argsort()[-top_k:][::-1]

    return [metadata[str(i)] for i in top_indices if str(i) in metadata]