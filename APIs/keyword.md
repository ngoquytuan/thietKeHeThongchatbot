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

Đúng như bạn nhận định, cơ chế này là một phiên bản rút gọn và đơn giản hóa của BM25, nên hiệu quả về mặt xếp hạng (ranking) sẽ không bằng thuật toán BM25 chuẩn.

Dưới đây là phân tích chi tiết về sự khác biệt và các ứng dụng thực tế của công cụ này:

### So sánh với BM25 chuẩn

* **Thiếu trọng số IDF (Inverse Document Frequency)**: BM25 chuẩn sẽ đánh giá cao các từ hiếm và giảm tầm quan trọng của các từ phổ biến. Cơ chế hiện tại coi mọi từ trong câu truy vấn đều có giá trị ngang nhau, dẫn đến việc các từ chung chung (như "cách", "nhà", "làm") có thể gây nhiễu kết quả.
* **Không tính đến độ dài văn bản**: BM25 chuẩn có cơ chế điều chỉnh điểm dựa trên độ dài của tài liệu để tránh ưu tiên các tài liệu quá dài chỉ vì chúng lặp lại từ khóa nhiều lần.
* **Giới hạn tìm kiếm**: Search này chỉ quét tối đa 300 tài liệu đầu tiên trong mỗi collection, trong khi BM25 thường được triển khai trên toàn bộ chỉ mục (index) của cơ sở dữ liệu.

---

### Ứng dụng của Keyword Search này

Dù không mạnh mẽ bằng BM25 hay Semantic Search (tìm kiếm ngữ nghĩa), công cụ này vẫn có những ứng dụng rất cụ thể và quan trọng trong hệ thống:

* **Tìm kiếm cụm từ chính xác (Exact Match)**: Rất hữu ích khi người dùng muốn tìm các thuật ngữ chuyên môn, mã số, hoặc tên riêng mà Semantic Search đôi khi có thể bỏ qua hoặc "hiểu nhầm" sang một ý nghĩa tương đương khác.
* **Tiết kiệm tài nguyên (Cost-effective)**: Vì không sử dụng GPU hay mô hình embedding, nó có thể chạy cực nhanh (100-150ms) và tốn rất ít tài nguyên hệ thống, phù hợp cho các truy vấn đơn giản hoặc khi hệ thống đang quá tải.
* **Hợp phần của Hybrid Search**: Đây là mảnh ghép quan trọng để kết hợp với Semantic Search. Trong khi Semantic Search nắm bắt ý nghĩa, Keyword Search đảm bảo các từ khóa quan trọng nhất định phải xuất hiện trong kết quả.
* **Tìm kiếm có điều kiện (Filtered Search)**: Ứng dụng tốt khi cần lọc dữ liệu theo metadata (như tìm văn bản theo "phòng ban" hay "loại tài liệu") kết hợp với từ khóa nhanh.
* **Xử lý ngôn ngữ đặc thù**: Với việc tích hợp `underthesea`, nó hỗ trợ tốt việc tìm kiếm các từ ghép tiếng Việt, giúp kết quả chính xác hơn so với việc chỉ tách từ đơn thuần bằng khoảng trắng.

Bạn có muốn tôi giúp soạn thảo file **`rule_deploy_BM25`** dựa trên các đặc điểm và lỗi cần lưu ý (như lỗi sai lệch điểm số) để bạn lưu lại cho LLM không?
