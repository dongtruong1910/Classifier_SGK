# src/ocr/ocr_pipeline.py
import re
import easyocr
import os
import gc

def ocr_image(image_path, lang='vi', gpu=True):
    """
    Nhận diện text từ 1 ảnh bằng EasyOCR.
    - image_path: đường dẫn ảnh
    - lang: 'vi' hoặc ['vi','en']
    - gpu: True nếu có GPU
    """
    reader = easyocr.Reader([lang] if isinstance(lang, str) else lang, gpu=gpu)
    text = reader.readtext(image_path, detail=0)  # detail=0 chỉ lấy text
    return text

def sort_key(filename):
    # Lấy số trong tên file page_XXX.png
    m = re.search(r'page_(\d+)\.png', filename)
    return int(m.group(1)) if m else 0

def ocr_all_images(image_dir, output_txt="data/interim/ocr_result.txt", lang='vi', gpu=True):
    """
    OCR tất cả ảnh trong thư mục image_dir, ghi kết quả ra file text.
    - Xử lý 1 ảnh 1 lần để giảm RAM
    """
    image_paths = sorted(
        [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.lower().endswith('.png')],
        key=sort_key
    )

    os.makedirs(os.path.dirname(output_txt), exist_ok=True)

    with open(output_txt, "w", encoding="utf-8") as f:
        for i, img_path in enumerate(image_paths, start=1):
            print(f"[INFO] OCR page {i}/{len(image_paths)} → {img_path}")

            # OCR page
            text_lines = ocr_image(img_path, lang=lang, gpu=gpu)
            for line in text_lines:
                f.write(line + "\n")

            f.write("\n" + "="*50 + "\n\n")  # phân cách giữa các trang

            # Giải phóng RAM ngay sau khi xử lý 1 page
            del text_lines
            gc.collect()

    print(f"[INFO] OCR completed. Saved to {output_txt}")


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    image_dir = os.path.join(BASE_DIR, "data", "interim", "pdf_images")
    output_txt = os.path.join(BASE_DIR, "data", "interim", "ocr_result.txt")

    ocr_all_images(image_dir, output_txt, lang='vi', gpu=True)
