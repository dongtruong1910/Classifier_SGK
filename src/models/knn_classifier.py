import json
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_distances
from collections import Counter

# ------------------ Paths ------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
chunks_path = os.path.join(BASE_DIR, "data", "embedded", "chunks_embedded.json")
knl_path = os.path.join(BASE_DIR, "data", "embedded", "knl_embedded.json")
output_path = os.path.join(BASE_DIR, "data", "embedded", "knl_unit_mapping.json")

# ------------------ Load data ------------------
with open(chunks_path, "r", encoding="utf-8") as f:
    chunks = json.load(f)

with open(knl_path, "r", encoding="utf-8") as f:
    knls = json.load(f)

# Convert embeddings sang numpy
chunk_embeddings = np.array([c["embedding"] for c in chunks])
chunk_units = [c["unit_id"] for c in chunks]

k = 5  # số hàng xóm gần nhất
results = []

for knl in knls:
    knl_vec = np.array(knl["embedding"]).reshape(1, -1)

    # Tính khoảng cách cosine
    distances = cosine_distances(knl_vec, chunk_embeddings)[0]

    # Lấy top-k chunks gần nhất
    topk_idx = np.argsort(distances)[:k]
    topk_units = [chunk_units[i] for i in topk_idx]

    # Đếm tần số xuất hiện unit
    counter = Counter(topk_units)
    max_freq = max(counter.values())
    selected_units = [u for u, freq in counter.items() if freq == max_freq]

    # Lưu kết quả
    results.append({
        "knl_id": knl["id"],
        "knl_name": knl["name"],
        "assigned_units": selected_units,
        "topk_units": topk_units,  # để debug xem 5 hàng xóm
    })

    print(f"[INFO] KNL {knl['id']} → Units {selected_units} (top-5: {topk_units})")

# Save kết quả
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"[INFO] ✅ Done. Saved mapping to {output_path}")
