import os
import json
import yaml
import base64
import numpy as np
from PIL import Image
from openai import OpenAI

from faiss_setup import load_resources

client = OpenAI(
    api_key="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjI0ZjEwMDE3NTBAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.v85lE2a1QBW-INTFrcyVHeiDHA5bHBqxf9cxwVlLtqE",
    base_url="https://aipipe.org/openai/v1"
)

model = index = metadata = None

def ensure_loaded():
    global model, index, metadata
    if model is None:
        model, index, metadata = load_resources()

# FAISS search (assumes model, index, and metadata are already loaded)
def search_faiss(query, top_k=5):
    ensure_loaded()
    query_vec = model.encode([query])
    scores, indices = index.search(np.array(query_vec).astype("float32"), top_k)
    results = []
    for i in indices[0]:
        if str(i) in metadata:
            results.append(metadata[str(i)])
    return results

# Answer generation for TEXT-ONLY (returns full JSON object)
def generate_answer(query, contexts):
    context_text = "\n\n".join([item['original_text'] for item in contexts])
    prompt = f"""You are an assistant that answers student queries based only on the verified context provided below.

Give your answer in 2–3 sentences. Do not mention the context or refer to it explicitly. Be factual and concise. Do not fabricate any sources. Make inferences from the context.

Question: {query}

Context:
{context_text}

Answer:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    
    # Construct valid output JSON manually
    answer_text = response.choices[0].message.content.strip()

    links = [{"url": item["url"], "text": item["original_text"]} for item in contexts]

    return {
        "answer": answer_text,
        "links": links
    }


# Answer generation for TEXT + IMAGE (returns minimal JSON)
def generate_answer_with_image(query, image_bytes):
    encoded_image = base64.b64encode(image_bytes).decode()
    image_input = {
        "type": "image_url",
        "image_url": {"url": f"data:image/webp;base64,{encoded_image}"}
    }

    prompt = """You are an assistant answering a question using the image input. 
Output your response as a JSON object with an 'answer' field. 
Use this format:

{
  "answer": "<your answer>",
  "links": []
}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": [{"type": "text", "text": prompt}, image_input]},
            {"role": "user", "content": query}
        ],
        temperature=0.2,
    )
    return json.loads(response.choices[0].message.content)

# Test runner
def evaluate_tests_with_images(test_cases):
    passed = 0

    for i, test in enumerate(test_cases):
        vars = test["vars"]
        question = vars["question"]
        image_path = vars.get("image", None)
        image_bytes = None
        output = None

        print(f"\n🧪 Test {i+1}: {question}")

        if image_path:
            image_path = image_path.replace("file://", "")
            try:
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                print(f"📷 Using image: {image_path}")
            except FileNotFoundError:
                print(f"⚠️ Image not found: {image_path}")
                output = {
                    "answer": "I couldn't find a definitive answer.",
                    "links": []
                }
                print(json.dumps(output, indent=2))
                continue

        try:
            if image_bytes:
                output = generate_answer_with_image(question, image_bytes)
            else:
                retrieved = search_faiss(question)
                output = generate_answer(question, retrieved)
        except Exception as e:
            print(f"❌ Error generating output: {e}")
            output = {
                "answer": "I couldn't find a definitive answer.",
                "links": []
            }

        print(json.dumps(output, indent=2))

        all_pass = True
        for assertion in test["assert"]:
            ttype = assertion["type"]
            value = assertion["value"]
            transform = assertion["transform"]

            # Apply transform
            if transform == "output.answer":
                result = output["answer"]
            elif transform == "JSON.stringify(output.links)":
                result = json.dumps(output["links"])
            else:
                print(f"❓ Unknown transform: {transform}")
                all_pass = False
                continue

            # Apply assertion
            if ttype == "contains":
                if value in result:
                    print(f"✅ contains OK: '{value}'")
                else:
                    print(f"❌ contains FAIL: expected '{value}'")
                    all_pass = False

            elif ttype == "llm-rubric":
                if value.lower() in result.lower():
                    print(f"✅ rubric OK: '{value}'")
                else:
                    print(f"❌ rubric FAIL: expected '{value}'")
                    all_pass = False

            else:
                print(f"❓ Unknown assert type: {ttype}")
                all_pass = False

        if all_pass:
            passed += 1

    print(f"\n🎯 {passed}/{len(test_cases)} tests passed.")

# Load test cases
with open("project-tds-virtual-ta-promptfoo.yaml", "r") as f:
    test_cases = yaml.safe_load(f)["tests"]

# Run tests
#evaluate_tests_with_images(test_cases)