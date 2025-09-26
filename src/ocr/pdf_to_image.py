# src/ocr/pdf_to_image.py
from pdf2image import convert_from_path
from PIL import Image, ImageOps
import os


def pdf_to_images(pdf_path,
                  output_dir,
                  dpi=300,
                  grayscale=True,
                  threshold=False):
    """
    Chuyển PDF scan sang ảnh PNG để OCR.
    - pdf_path: đường dẫn file PDF
    - output_dir: thư mục lưu ảnh
    - dpi: độ phân giải ảnh
    - grayscale: convert sang grayscale để OCR tốt hơn
    - threshold: nhấn nét chữ bằng threshold (optional)
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Không tìm thấy file PDF: {pdf_path}")

    os.makedirs(output_dir, exist_ok=True)

    # Đường dẫn đến thư mục chứa poppler (thay đổi nếu cần)
    poppler_path = r"D:\G\Learning Tools\Poppler (Dùng cho pdf2image)\poppler-25.07.0\Library\bin"

    # Convert PDF sang ảnh (thread_count tăng tốc nếu PDF nhiều trang)
    pages = convert_from_path(pdf_path, dpi=dpi, fmt="png", thread_count=4, poppler_path=poppler_path)

    image_paths = []
    for i, page in enumerate(pages):
        if grayscale:
            page = ImageOps.grayscale(page)

        if threshold:
            page = page.point(lambda x: 0 if x < 128 else 255)  # nhấn nét chữ

        img_path = os.path.join(output_dir, f"page_{i + 1}.png")
        page.save(img_path, "PNG")
        image_paths.append(img_path)

        print(f"Đã xuất page {i + 1}/{len(pages)} → {img_path}")

    print(f"✅ Hoàn tất xuất {len(image_paths)} ảnh tại {output_dir}")
    return image_paths


# Khi chạy file này standalone
if __name__ == "__main__":
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pdf_path = os.path.join(BASE_DIR, "data", "raw", "TIN HỌC 11.pdf")
    output_dir = os.path.join(BASE_DIR, "data", "interim", "pdf_images")
    images = pdf_to_images(pdf_path=pdf_path, output_dir=output_dir)


