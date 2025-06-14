import json
import numpy as np
from openai import OpenAI
import os

client = OpenAI(
    api_key="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE3NTBAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.v85lE2a1QBW-INTFrcyVHeiDHA5bHBqxf9cxwVlLtqE",
    base_url="https://aipipe.org/openai/v1"
)
# Load the metadata
with open("index_to_data.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

texts = [metadata[str(i)]["original_text"] for i in range(len(metadata))]

embeddings = []

print("🔄 Creating embeddings for", len(texts), "posts...")

for i, text in enumerate(texts):
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",  # or "text-embedding-ada-002"
            input=text
        )
        vec = response.data[0].embedding
        embeddings.append(vec)
        print(f"✅ {i}: Embedded")
    except Exception as e:
        print(f"❌ {i}: Failed - {e}")
        embeddings.append([0.0] * 1536)  # dummy vector

# Save embeddings
np.save("openai_embeddings.npy", np.array(embeddings))
print("💾 Saved to openai_embeddings.npy")
