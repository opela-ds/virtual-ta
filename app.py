# app.py
from flask import Flask, request, jsonify
import os
import base64

try:
    from runner import generate_answer, generate_answer_with_image, search_faiss
except ImportError as e:
    def generate_answer(question, contexts):
        return {"answer": "System initializing...", "links": []}
    
    def generate_answer_with_image(question, image_bytes):
        return {"answer": "Image processing unavailable", "links": []}
    
    def search_faiss(query):
        return []
    
    print(f"⚠️ Failed to import modules: {e}. Using fallback functions.")
    
app = Flask(__name__)

@app.route('/api/', methods=['POST'])
def virtual_ta():
    try:
        data = request.get_json()
        question = data.get('question', '')
        image_b64 = data.get('image', None)
        
        if image_b64:
            image_bytes = base64.b64decode(image_b64)
            response = generate_answer_with_image(question, image_bytes)
        else:
            contexts = search_faiss(question)
            response = generate_answer(question, contexts)
            
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            "answer": f"Error processing request: {str(e)}",
            "links": []
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
