# SGK_NangLuc

Dự án thử nghiệm áp dụng Machine Learning để **gán khung năng lực số cho từng Unit trong SGK Tin học 11**.

## 🎯 Mục tiêu
- Sử dụng OCR để trích xuất nội dung từ SGK (file PDF scan).
- Chunking nội dung thành từng Unit.
- Tạo embedding cho Unit và khung năng lực.
- Phân loại (KNN / Decision Tree) để gán năng lực cho từng Unit.

## 📂 Cấu trúc thư mục
```
BTVN_3/
│
├── data/                  # Dữ liệu gốc và đã xử lý
│   ├── raw/               # PDF SGK, PDF Khung_năng_lực, data gốc
│   ├── interim/           # Dữ liệu scan PDF, Dữ liệu OCR thô (txt từng trang), Dữ liệu chia unit_page_map.json
│   ├── processed/         # Dữ liệu sau khi tách theo unit (JSON)
│   ├── embedded/          # Dữ liệu embedding (Unit + Khung năng lực)
│   └── khung_nangluc.json # File khung năng lực số (mô tả từng năng lực)
│   
├── notebooks/             # Jupyter notebooks (dùng để thử nghiệm, test code nhanh)
│   ├── 01_ocr_demo.ipynb
│   ├── 02_embedding_test.ipynb
│   └── 03_knn_classification.ipynb
│
├── src/                   # Source code chính
│   ├── __init__.py
│   ├── ocr/               # OCR pipeline
│   │   ├── __init__.py
│   │   ├── pdf_to_image.py
│   │   └── easyocr_engine.py
│   │
│   ├── preprocessing/     # Tiền xử lý dữ liệu text
│   │   ├── __init__.py
│   │   ├── clean_text.py
│   │   └── split_units.py
│   │
│   ├── embeddings/        # Tạo embedding cho Unit + Khung năng lực
│   │   ├── __init__.py
│   │   └── embedding_openai.py
│   │
│   ├── models/            # ML models (KNN, Decision Tree,…)
│   │   ├── __init__.py
│   │   ├── knn_classifier.py
│   │   └── decision_tree.py
│   │
│   └── postprocessing/             # lưu kết quả cuối cùng ra file csv
│       ├── __init__.py
│       ├── export_unit_knl_csv.py
│
├── results/               # Lưu kết quả gán nhãn, biểu đồ
│   ├── unit_to_nangluc.csv
│   
│
├── requirements.txt       # Thư viện cần cài
├── README.md               # File hướng dẫn này 
├── requirements.txt       # Thư viện cần cài
└── main.py                # Script chạy chính (pipeline end-to-end)

```
## 📌 Workflow
### 1. Data Gathering
- Thu thập SGK Tin học 11 (file PDF scan).
- Thu thập khung năng lực số (file text).
### 2. OCR - Trích xuất văn bản từ PDF scan
- **Input:** PDF tài liệu gốc  
- **Chuyển đổi:** PDF → ảnh (JPEG/PNG) 
    - Dùng `pdf2image` để chuyển đổi từng trang PDF thành ảnh.
    - Cần cài Poppler (for Windows: https://github.com/oschwartz10612/poppler-windows/releases/tag/v25.07.0-0)
    - Lưu ảnh PNG/JPEG trong `data/interim/pdf_images/`
- **OCR:** Dùng EasyOCR để trích xuất text từ ảnh  
- **Output:** Văn bản thô (raw text)  
### 3. Preprocessing - Tiền xử lý văn bản
- **Input:** Văn bản thô (raw text)
- **Xử lý: (Chunking) Semi-automatic Chunking**
    - Chia SGK thành các units dựa trên mục lục, lưu vào `data/processed/units`, mỗi file(text) là 1 unit. 
    - Sau đó dùng langchain để chunking tự động từng unit thành các đoạn nhỏ hơn, lưu vào data/processed/chunks/chunks.json.
    - Mỗi chunk sẽ có định danh unit_id để biết nó thuộc unit nào.
- **Output:** Văn bản đã được chia thành các chunks nhỏ hơn (JSON)
### 4. Embedding - Tạo embedding cho văn bản
- **Input:** Văn bản đã được chia thành các chunks nhỏ hơn (JSON)
- **Tạo embedding:**
    - Dùng Gemini Embedding API (gemini-embedding-001) để tạo embedding cho từng chunk.
    - Tạo embedding cho từng năng lực trong khung năng lực số.
    - Lưu embedding vào `data/embedded/`
    - Lưu ý: bản free sẽ có giới hạn số lượng token/ngày, có RPM và TPM, cần theo dõi, chia batch hợp lý, đặt time-sleep theo mỗi batch để tránh giới hạn.
- **Output:** Embedding vectors cho từng chunk và từng năng lực (JSON/CSV)
### 5. Classification - Gán nhãn năng lực cho từng Unit
- **Input:** Embedding vectors cho từng chunk và từng năng lực (JSON/CSV)
- **Phân loại:**
    - Sử dụng KNN để phân loại. (Yêu cầu bài toán gán nhãn năng lực vào từng unit, data có sãn sẽ là các unit của SGK Tin học 11, cái data mình cần gán nhãn sẽ là các mục năng lực).
    - Tính khoảng cách giữa embedding của từng chunk với embedding của từng năng lực.
    - Hằng số k (số láng giềng gần nhất) = 5:
        - Lấy 5 chunk gần nhất với mỗi năng lực, mỗi chunk sẽ có một unitId chính là cái unit mà nó thuộc vào.
        - Tính tần số xuất hiện của từng unit trong 5 chunk gần nhất với mỗi năng lực và lấy ra max(tần số).
        - Nếu có nhiều unit có tần số max thì sẽ lấy tất cả các unit đó.
    - Tổng hợp kết quả gán nhãn từ các chunks về từng unit.
- **Output:** Kết quả gán nhãn năng lực cho từng unit (JSON) 
### 6. Postprocessing - Lưu kết quả cuối cùng
- **Input:** Kết quả gán nhãn năng lực cho từng unit (JSON)
- **Lưu kết quả:** Lưu kết quả vào `results/unit_to_nangluc.csv`

## 😊 Khuyến nghị
### 1. OCR
- EasyOCR hỗ trợ khá tốt Tiếng Việt, tuy nhiên vẫn có thể gặp lỗi với font chữ đặc biệt hoặc chất lượng ảnh kém.
- Cần kiểm tra và hiệu chỉnh thủ công nếu cần thiết.
- Recommend: thư viện dots_ocr (open_source, hỗ trợ tiếng Việt tốt hơn, nhưng cần GPU để chạy nhanh) hoặc Landing AI (dịch vụ trả phí, miễn phí 1 phần, hỗ trợ tiếng Việt tốt, không cần GPU).
- Nên có GPU để chạy OCR nhanh hơn (khuyến nghị RTX 4060 trở lên).
- Cần cài torch với các OCR hiện đại (như dots_ocr, easy_ocr) để có hiệu suất tốt nhất.
  - **CPU only**: 
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
  - **GPU (nếu có CUDA)**: 
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

### 2. Embedding
- Dùng langchain để quản lý API key và gọi API.
- Sử dụng Gemini Embedding API (gemini-embedding-001) để tạo embedding cho văn bản.
- Lưu ý: bản free sẽ có giới hạn số lượng token/ngày, có RPM và TPM, cần theo dõi, chia batch hợp lý, đặt time-sleep theo mỗi batch để tránh giới hạn.
- Lưu ý 2: Có thể sử dụng API của ProtoX để tạo embedding miễn phí, tìm hiểu thêm https://protonx.co/models.html?fbclid=IwY2xjawNC8gdleHRuA2FlbQIxMABicmlkETFGRnlCdlJzU2FCcTl2OTFGAR4yKU6h5sqjt2y48_29BjvGXNFjFs_sG5NabY8337BVasQ-FKpbHmAcZucmQQ_aem_aLaP1HQzuUB-RE_MtUdr7g

## 🛠️ Cài đặt
### Các thư viện cần thiết được liệt kê trong `requirements.txt`. Cài đặt bằng pip:
```pip install -r requirements.txt```