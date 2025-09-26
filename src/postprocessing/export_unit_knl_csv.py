import os
import json
import csv

# ------------------ Paths ------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
mapping_path = os.path.join(BASE_DIR, "data", "embedded", "knl_unit_mapping.json")
units_dir = os.path.join(BASE_DIR, "data", "processed", "units")
output_csv_path = os.path.join(BASE_DIR, "results","unit_to_nangluc.csv")

# ------------------ Load mapping ------------------
with open(mapping_path, "r", encoding="utf-8") as f:
    knl_mappings = json.load(f)

# ------------------ Lấy thông tin unit_name từ folder ------------------
unit_info = {}
for filename in os.listdir(units_dir):
    if filename.endswith(".txt"):
        unit_id = filename.split("_", 1)[0]  # lấy số trước dấu _
        unit_name = filename.split("_", 1)[1].replace(".txt", "").replace("_", " ")
        unit_info[unit_id] = unit_name

# ------------------ Gom knl theo unit ------------------
unit_to_knls = {}

for knl in knl_mappings:
    for uid in knl["assigned_units"]:
        uid = str(uid)  # đảm bảo là string để so với unit_info keys
        if uid not in unit_to_knls:
            unit_to_knls[uid] = []
        unit_to_knls[uid].append(knl["knl_id"])

# ------------------ Lưu ra CSV ------------------
with open(output_csv_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["unit_id", "unit_name", "knl_ids"])

    for uid, knls in unit_to_knls.items():
        unit_name = unit_info.get(uid, "Unknown")
        knl_ids = ", ".join(knls)
        writer.writerow([uid, unit_name, knl_ids])

print(f"[INFO] ✅ Saved CSV to {output_csv_path}")
