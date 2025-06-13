import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

def create_embeddings():
    # Load cleaned posts
    with open('cleaned_posts.json', 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    # Initialize embedding model (same one we'll use for queries)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Prepare data structures
    texts = []
    metadata = []
    
    # Process each post
    for idx, post in enumerate(tqdm(posts, desc="Processing posts")):
        text = post['text']
        # Basic cleaning - remove images and newlines
        text = ' '.join(text.split('\n')).replace('image', '').strip()
        if len(text) < 10:  # Skip very short posts
            continue
            
        texts.append(text)
        metadata.append({
            "post_id": post["post_id"],
            "url": post["url"],
            "original_text": post["text"]
        })
    
    # Generate embeddings
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    index.add(embeddings)
    
    # Save artifacts
    faiss.write_index(index, "faiss_index.bin")
    with open("index_to_data.json", "w") as f:
        json.dump({str(i): meta for i, meta in enumerate(metadata)}, f)
    
    print(f"Created index with {len(texts)} posts and {dimension}-dim embeddings")

if __name__ == "__main__":
    create_embeddings()