# src/preprocessing/split_chunk_from_units.py
import os
import json
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

def sort_units_numerically(file_list):
    """
    Sắp xếp danh sách file theo số đầu tên file (unit index)
    """
    def get_unit_number(filename):
        m = re.match(r'(\d+)_', filename)
        return int(m.group(1)) if m else 0

    return sorted(file_list, key=get_unit_number)

def split_unit_text(unit_text, chunk_size=500, chunk_overlap=50):
    """
    Chia text của một Unit thành các chunk nhỏ bằng LangChain.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(unit_text)
    return chunks

def main():
    # Folder chứa text từng Unit
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    unit_dir = os.path.join(BASE_DIR,"data", "processed", "units")

    # Folder lưu chunk
    chunk_dir = os.path.join(BASE_DIR,"data", "processed", "chunks")
    os.makedirs(chunk_dir, exist_ok=True)

    # Lấy danh sách file unit, sắp xếp theo số unit
    unit_files = [f for f in os.listdir(unit_dir) if f.endswith(".txt")]
    unit_files = sort_units_numerically(unit_files)

    all_chunks = []

    for file in unit_files:
        unit_id = int(file.split("_")[0])  # Lấy unit_id từ tên file, ví dụ "1_Hệ_điều_hành.txt"
        unit_path = os.path.join(unit_dir, file)
        with open(unit_path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = split_unit_text(text)
        print(f"[INFO] Unit {file} chia thành {len(chunks)} chunk")

        for i, chunk_text in enumerate(chunks, start=1):
            all_chunks.append({
                "unit_id": unit_id,
                "chunk_id": i,
                "text": chunk_text
            })

    # Lưu tất cả chunk vào 1 file JSON duy nhất
    output_json = os.path.join(chunk_dir, "chunks.json")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"[INFO] ✅ Hoàn tất split tất cả Unit. Chunks lưu tại {output_json}")


if __name__ == "__main__":
    main()
