from flask import Flask, request, jsonify
from flask_cors import CORS  # Enables CORS for all routes
import os
import base64
import logging

# Import with fallback
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

# App setup
app = Flask(__name__)
CORS(app)  # ✅ Allow all cross-origin requests (safe for demo)

logging.basicConfig(level=logging.DEBUG)
print("✅ Flask app initialized")

# Root route for Render status or test page CORS check
@app.route("/", methods=["GET", "OPTIONS"])
def index():
    return (
        jsonify({"message": "Virtual TA API is running. POST to /api/"}),
        200,
        {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )

# Main API endpoint
@app.route('/api/', methods=['POST', 'OPTIONS'])
def virtual_ta():
    if request.method == "OPTIONS":
        return "", 200, {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }

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

        return jsonify(response), 200, {
            "Access-Control-Allow-Origin": "*"
        }

    except Exception as e:
        logging.exception("Error handling request:")
        return jsonify({
            "answer": f"Error processing request: {str(e)}",
            "links": []
        }), 500


# Port binding for Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
