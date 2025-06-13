import os
import json
from bs4 import BeautifulSoup

SOURCE_DIR = "discourse_json"
OUTPUT_FILE = "cleaned_posts.json"

def clean_html(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(separator="\n").strip()

def extract_posts_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    posts = data.get("post_stream", {}).get("posts", [])
    cleaned_posts = []

    for post in posts:
        cooked = post.get("cooked", "")
        clean_text = clean_html(cooked)

        cleaned_posts.append({
            "post_id": post.get("id"),
            "topic_id": post.get("topic_id"),
            "post_number": post.get("post_number"),
            "created_at": post.get("created_at"),
            "author": post.get("username"),
            "url": f"https://discourse.onlinedegree.iitm.ac.in{post.get('post_url')}",
            "text": clean_text
        })

    return cleaned_posts

def main():
    all_cleaned_posts = []
    for filename in os.listdir(SOURCE_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(SOURCE_DIR, filename)
            posts = extract_posts_from_file(filepath)
            all_cleaned_posts.extend(posts)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_cleaned_posts, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(all_cleaned_posts)} cleaned posts to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
