Dựa trên tài liệu bàn giao "Keyword Search Engine Handover" ngày 25/11/2025, nguyên lý hoạt động của công cụ này tập trung vào việc đối khớp thuật ngữ (term matching) trực tiếp trên văn bản mà không sử dụng embedding hay phân tích ngữ nghĩa.

Dưới đây là các bước vận hành chi tiết:

### 1. Quy trình xử lý truy vấn

Khi nhận được một yêu cầu tìm kiếm, hệ thống thực hiện theo các bước sau:

* **Xác định bộ sưu tập (Collection Discovery):** Liệt kê tất cả các bộ sưu tập trong ChromaDB, lọc bỏ các bộ sưu tập trống và sắp xếp chúng theo kích thước (lớn nhất trước) để tối ưu kết quả.
* **Truy xuất tài liệu (Document Retrieval):** Với mỗi bộ sưu tập, hệ thống lấy ra tối đa **300 tài liệu** (đã nâng cấp từ 100) để xử lý. Nếu có bộ lọc metadata (WHERE clause), chúng sẽ được áp dụng trực tiếp tại bước này.
* **Phân tách từ (Tokenization):** Sử dụng thư viện `underthesea` để tách từ tiếng Việt (ví dụ: "xác định" được hiểu là một cụm từ thay vì hai từ đơn). Nếu thư viện này không khả dụng, hệ thống sẽ dùng phương thức `split()` cơ bản.
* **Đối khớp văn bản cục bộ (Local Text Matching):** Hệ thống duyệt qua từng tài liệu đã lấy ra, chuyển nội dung về chữ thường và đếm số lần xuất hiện của từng thuật ngữ trong truy vấn (substring matching).

### 2. Cách tính điểm và xếp hạng

Điểm số được tính toán theo phương pháp đếm thuật ngữ đơn giản (không phải BM25 chuẩn):

* **Raw Score:** Là tổng số lần xuất hiện của tất cả các từ khóa trong tài liệu.
* **BM25-style Score:** Được chuẩn hóa theo công thức:



Điểm số này bị giới hạn tối đa là **10.0**.
* **Tổng hợp:** Kết quả từ tất cả các bộ sưu tập được gộp lại, sắp xếp theo điểm số từ cao xuống thấp và trả về `top_k` kết quả tốt nhất.

### 3. Đặc điểm kỹ thuật quan trọng

* **Công nghệ:** Sử dụng phương thức `.get()` của ChromaDB thay vì tìm kiếm vector, giúp tiết kiệm tài nguyên GPU.
* **Tốc độ:** Thời gian phản hồi điển hình dao động từ **100-150ms**.
* **Ưu điểm:** Hiệu quả nhất cho việc tìm kiếm cụm từ chính xác (exact phrase) hoặc các từ khóa đặc thù như mã số, tên riêng.

### 4. Những hạn chế hiện tại

* **Chưa có trọng số IDF:** Hệ thống coi mọi từ đều quan trọng như nhau, chưa phân biệt được từ hiếm và từ phổ biến (ví dụ: từ "nhà" và từ "phong thủy" có trọng số ngang nhau).
* **Đối khớp chuỗi con (Substring):** Có thể gây ra kết quả sai nếu một từ khóa là chuỗi con của một từ không liên quan (ví dụ: "định" có thể khớp với một từ ngẫu nhiên chứa chuỗi đó).
* **Giới hạn phạm vi:** Chỉ tìm kiếm trong tối đa 300 tài liệu đầu tiên của mỗi collection, có thể bỏ lỡ dữ liệu nếu collection quá lớn.

Bạn có muốn tôi làm rõ thêm về cách cấu hình các bộ lọc (filters) hoặc cách kết hợp nó vào hệ thống tìm kiếm Hybrid không?

Đúng vậy, dựa trên tài liệu bàn giao, hệ thống **Keyword Search** này hoạt động hoàn toàn độc lập trên **ChromaDB** và không truy cập vào **PostgreSQL**.

Dưới đây là các điểm xác nhận sự tách biệt này:

* **Lưu trữ và Truy xuất**: Keyword Engine sử dụng `chromadb.HttpClient` để kết nối và lấy dữ liệu trực tiếp từ các collection trong ChromaDB.
* **Phương thức hoạt động**: Thay vì dùng tìm kiếm vector (semantic search), nó sử dụng phương thức `.get()` của ChromaDB để truy xuất tài liệu thô dựa trên các bộ lọc, sau đó mới thực hiện đối khớp văn bản bằng Python.
* **Sự khác biệt với Metadata Search**: Trong khi **Metadata Search** chạy trên PostgreSQL để tra cứu các trường dữ liệu có cấu trúc (như `law_id`), thì **Keyword Search** chạy trên ChromaDB để tìm kiếm nội dung văn bản tự do.
* **Kiến trúc hệ thống**: Tài liệu khẳng định rõ Keyword Engine "không truy cập PostgreSQL", khác hoàn toàn với các engine substring hay BM25 truyền thống thường dựa vào SQL.

**Mối liên hệ duy nhất (nếu có)**:
Mặc dù không truy cập trực tiếp, nhưng hai hệ thống này thường được điều phối bởi `SearchOrchestrator`. Khi bạn thực hiện một truy vấn **Hybrid Search**, Orchestrator sẽ gọi đồng thời Keyword Search (từ ChromaDB), Semantic Search (từ ChromaDB) và có thể là Metadata Search (từ PostgreSQL) rồi gộp kết quả lại để trả về cho người dùng.

Bạn có muốn tôi làm rõ thêm về cách `SearchOrchestrator` phối hợp kết quả từ hai cơ sở dữ liệu này không?
