import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ocr_txt_path = os.path.join(BASE_DIR, "data", "interim", "ocr_result.txt")
unit_json_path = os.path.join(BASE_DIR, "data", "interim", "unit_page_map.json")
output_dir = os.path.join(BASE_DIR, "data", "processed", "units")
os.makedirs(output_dir, exist_ok=True)

# Đọc toàn bộ OCR text và tách thành list per page
with open(ocr_txt_path, "r", encoding="utf-8") as f:
    content = f.read()
pages = content.split("\n" + "="*50 + "\n\n")  # mỗi phần tương ứng 1 page

# Load JSON unit
with open(unit_json_path, "r", encoding="utf-8") as f:
    units = json.load(f)["units"]

for unit in units:
    pages_to_skip = 5
    start = unit["start_page"] - 1 - pages_to_skip
    end = unit["end_page"] - pages_to_skip
    unit_text = "\n".join(pages[start:end])

    safe_name = unit["unit_name"].replace(" ", "_").replace("/", "_")
    out_path = os.path.join(output_dir, f"{unit['unit_id']}_{safe_name}.txt")
    with open(out_path, "w", encoding="utf-8") as f_out:
        f_out.write(unit_text)
    print(f"[INFO] Unit {unit['unit_id']} - {unit['unit_name']} saved to {out_path}")
