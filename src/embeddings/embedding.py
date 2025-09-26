import os
import json
import time
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# ------------------ Load .env ------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Please set GOOGLE_API_KEY in .env file!")

# ------------------ Paths ------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
chunk_json_path = os.path.join(BASE_DIR, "data", "processed", "chunks", "chunks.json")
output_json_path = os.path.join(BASE_DIR, "data", "embedded", "chunks_embedded.json")
knl_json_path = os.path.join(BASE_DIR, "data", "khung_nang_luc.json")
output_knl_json_path = os.path.join(BASE_DIR, "data", "embedded", "knl_embedded.json")

# ------------------ Load data ------------------
with open(chunk_json_path, "r", encoding="utf-8") as f:
    chunks = json.load(f)

with open(knl_json_path, "r", encoding="utf-8") as f:
    knls = json.load(f)

# ------------------ Init embeddings ------------------
embeddings_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    api_key=api_key
)

# ------------------ Helper batch function ------------------
def batch_list(lst, batch_size=50):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i+batch_size]

def embed_with_retry(batch, max_retries=5):
    """Embed batch với retry khi bị quota"""
    for attempt in range(max_retries):
        try:
            return embeddings_model.embed_documents(batch)
        except Exception as e:
            if "429" in str(e):
                wait_time = 65  # chờ 65s cho chắc
                print(f"[WARN] Quota exceeded. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                raise e
    raise RuntimeError("Max retries exceeded!")

# ------------------ Embed chunks ------------------
embedded_chunks = []
chunk_texts = [c["text"] for c in chunks]

print(f"[INFO] Start embedding {len(chunk_texts)} chunks...")

for i, batch in enumerate(batch_list(chunk_texts, batch_size=50), start=1):
    vectors = embed_with_retry(batch)
    for j, vector in enumerate(vectors):
        idx = (i-1)*50 + j
        chunk = chunks[idx]
        embedded_chunks.append({
            "unit_id": chunk["unit_id"],
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "embedding": vector
        })
        print(f"[INFO] Embedded Unit {chunk['unit_id']} Chunk {chunk['chunk_id']}")
    print(f"[INFO] ✅ Batch {i} done.")

with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(embedded_chunks, f, ensure_ascii=False, indent=2)

# ------------------ Embed KNL ------------------
embedded_knl = []
knl_texts, meta_info = [], []

for framework_item in knls["framework"]:
    for sub in framework_item.get("sub_competencies", []):
        text_to_embed = f"{sub['name']}. {sub['description']}"
        knl_texts.append(text_to_embed)
        meta_info.append({
            "id": sub["id"],
            "name": sub["name"],
            "description": sub["description"]
        })

print(f"[INFO] Start embedding {len(knl_texts)} sub-competencies...")

for i, batch in enumerate(batch_list(knl_texts, batch_size=50), start=1):
    vectors = embed_with_retry(batch)
    for j, vector in enumerate(vectors):
        idx = (i-1)*50 + j
        info = meta_info[idx]
        embedded_knl.append({
            "id": info["id"],
            "name": info["name"],
            "description": info["description"],
            "embedding": vector
        })
        print(f"[INFO] Embedded Sub-competency {info['id']} - {info['name']}")
    print(f"[INFO] ✅ Batch {i} done.")

with open(output_knl_json_path, "w", encoding="utf-8") as f:
    json.dump(embedded_knl, f, ensure_ascii=False, indent=2)

print(f"[INFO] ✅ All chunks and KNL embedded. Saved to {output_json_path} and {output_knl_json_path}")
