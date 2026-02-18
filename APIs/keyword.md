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

Dựa trên log bạn cung cấp và tài liệu kỹ thuật về **Keyword Search Engine**, hiện tượng "lần đầu chậm (khoảng 10 giây), lần sau nhanh" thường do một vài nguyên nhân đặc thù trong kiến trúc của hệ thống này:

### 1. Khởi tạo kết nối và Cache bộ sưu tập (Collection Caching)

Trong mã nguồn của `KeywordEngine`, có một phương thức gọi là `_refresh_collections_cache()`.

* **Lần đầu tiên:** Khi bạn thực hiện truy vấn đầu tiên sau khi khởi động, hệ thống phải thiết lập kết nối HTTP tới ChromaDB và liệt kê tất cả các bộ sưu tập hiện có (`chroma_client.list_collections()`). Nếu số lượng collection lớn hoặc kết nối mạng/disk bị trễ, việc này sẽ tốn thời gian.
* **Các lần sau:** Danh sách các collection và thông tin cấu trúc đã được lưu vào bộ nhớ đệm (cache), giúp bỏ qua bước discovery này.

### 2. "Làm nóng" dữ liệu (Cold Start vs. Warm Start)

Keyword Search hoạt động bằng cách lấy trực tiếp 300 tài liệu mỗi collection từ ChromaDB về RAM để xử lý cục bộ (`collection.get(limit=300)`).

* **Lần đầu (Cold):** ChromaDB có thể phải đọc dữ liệu từ ổ đĩa (Disk I/O) để nạp vào RAM. Với truy vấn "ngô quý tuấn" mất 9.5 giây và "nguyễn anh tuấn" lần đầu mất 8.1 giây, đây là thời gian hệ thống đọc dữ liệu thô từ database.
* **Lần sau (Warm):** Dữ liệu đã nằm trong Page Cache của hệ điều hành hoặc cache nội bộ của ChromaDB, giúp việc truy xuất rút ngắn xuống còn ~300ms đến 500ms như bạn thấy trong log.

### 3. Nạp thư viện Tokenizer (Vietnamese NLP)

Hệ thống sử dụng thư viện `underthesea` để tách từ tiếng Việt.

* Thư viện này thường thực hiện nạp các model ngôn ngữ (POS tagging, Word Segmentation) vào RAM ngay trong lần đầu tiên hàm `word_tokenize()` được gọi.
* Quá trình nạp model NLP này có thể mất vài giây tùy thuộc vào cấu hình CPU/RAM của server.

### 4. Phân tích qua Log của bạn

* **Lần 1 ("ngô quý tuấn"):** Mất **9.505 giây** (20:44:17 -> 20:44:27). Đây là lúc hệ thống vừa phải khởi tạo kết nối, vừa nạp Tokenizer, vừa đọc dữ liệu từ Disk.
* **Lần 2 ("ngô quý tuấn"):** Chỉ mất **0.376 giây**. Mọi thứ đã có sẵn trong cache.
* **Lần 5 ("nguyễn anh tuấn" - từ khóa mới):** Mất **8.135 giây**. Dù Tokenizer đã nạp, nhưng vì đây là từ khóa mới hoặc bộ sưu tập chứa từ này chưa được "làm nóng" (hoặc do cơ chế search của ChromaDB phải quét lại vùng dữ liệu khác), thời gian vẫn bị kéo dài.

---

**Giải pháp đề xuất:**

1. **Pre-warmup:** Thực hiện một vài câu query mẫu ngay khi ứng dụng vừa startup (trong `startup_event`) để kích hoạt nạp Tokenizer và kết nối ChromaDB.
2. **Kiểm tra Disk I/O:** Nếu database nằm trên HDD thay vì SSD, thời gian đọc 300 docs/collection sẽ bị ảnh hưởng đáng kể.
3. **Tối ưu hóa số lượng Docs:** Nếu không cần độ phủ quá rộng, bạn có thể giảm `limit` từ 300 xuống thấp hơn để tăng tốc độ đọc ban đầu.

Bạn có muốn tôi hướng dẫn cách viết hàm **warmup** để tự động "làm nóng" hệ thống khi vừa bật lên không?

Việc bạn thử vài query mà không thấy gì đặc biệt có thể là do hệ thống đang hoạt động ổn định với các truy vấn thông thường. Tuy nhiên, dựa trên tài liệu handover và lịch sử phát triển, có **3 vấn đề lớn** bạn nên kiểm tra kỹ để đánh giá hiệu quả thực tế của API này:

### 1. Kiểm tra sự sai lệch về điểm số (Bug nghiêm trọng nhất)

Tài liệu ghi nhận một lỗi logic "chưa có lời giải" về cách tính điểm.

* **Hiện tượng:** Điểm `bm25_score` trả về thường rất cao (vọt lên mức 9.8 hoặc 10.0) dù tính toán lý thuyết chỉ tầm 4.0 - 5.0.
* **Cách kiểm tra:** Thử các query dài (4-5 từ trở lên). Nếu hầu hết kết quả đều đạt mức ~10.0, điều này chứng tỏ bộ lọc xếp hạng đang bị mất tác dụng phân loại tài liệu nào "đúng hơn" tài liệu nào.

### 2. Kiểm tra khả năng bao phủ dữ liệu (Data Coverage)

Mặc dù đã được nâng cấp, nhưng API này vẫn có giới hạn cứng trong thiết kế:

* **Giới hạn 300 tài liệu:** Hệ thống chỉ quét 300 tài liệu đầu tiên trong mỗi collection. Nếu collection của bạn có hàng nghìn văn bản, những tài liệu nằm sau vị trí 300 sẽ **không bao giờ** được tìm thấy bằng Keyword Search, bất kể nó khớp từ khóa đến đâu.
* **Thứ tự ưu tiên:** Hệ thống ưu tiên các collection lớn trước. Bạn nên thử query vào các nội dung mà bạn biết chắc nó nằm ở các collection nhỏ hoặc nằm sâu trong database để xem API có chạm tới được không.

### 3. Kiểm tra tính chính xác của tiếng Việt (Tokenizer)

Đây là điểm dễ gây ra kết quả "không có gì đặc biệt" hoặc trả về kết quả rác:

* **Vấn đề Substring:** API sử dụng lệnh `in` (substring matching) thay vì bắt đúng ranh giới từ.
* *Ví dụ:* Query từ "định" có thể trả về cả các câu chứa "xác định", "định hướng", hoặc thậm chí là các chuỗi ký tự vô nghĩa có chứa "đinh/định".


* **Từ khóa ngắn:** Trong quá khứ, hệ thống từng gặp lỗi lọc bỏ các từ khóa ngắn (<= 2 ký tự). Bạn hãy thử query các từ quan trọng nhưng ngắn như "tư", "bộ", "luật" để xem API có xử lý được không.

---

**Tóm tắt các điểm cần "test thử":**
| Loại kiểm tra | Query nên thử | Mục tiêu |
| :--- | :--- | :--- |
| **Độ chính xác từ** | "xác định" | Kiểm tra xem nó có trả về đúng cụm từ hay chỉ là các từ đơn lẻ chứa chữ "định". |
| **Từ khóa ngắn** | "bộ", "tư" | Kiểm tra xem bộ lọc stopword có đang xóa nhầm từ quan trọng không. |
| **Hiệu năng lần đầu** | Query bất kỳ | Kiểm tra xem lần gọi đầu tiên có bị chậm (8-10s) do "làm nóng" ChromaDB không. |

Bạn có muốn tôi viết một script Python nhỏ để bạn chạy test hàng loạt các trường hợp biên (edge cases) này không?
