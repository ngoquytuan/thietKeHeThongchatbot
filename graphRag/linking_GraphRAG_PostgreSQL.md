Chào bạn, việc triển khai GraphRAG trên PostgreSQL gặp khó khăn khi tạo linking là vấn đề rất phổ biến. Dựa trên tài liệu hệ thống của bạn, tôi xin đưa ra các gợi ý và giải pháp cụ thể để giải quyết vấn đề này.

Vấn đề chính thường nằm ở chỗ các liên kết (linking) đang nằm rải rác trong `metadata JSONB` hoặc chỉ tồn tại dưới dạng văn bản thô, khiến việc truy vấn graph (như dùng Recursive CTE) trở nên chậm và phức tạp.

Dưới đây là lộ trình 3 giai đoạn để tối ưu hóa việc tạo linking:

### 1. Chuyển đổi từ "Soft Links" sang "Hard Links" (Bảng Edges)

Thay vì chỉ để thông tin liên quan trong JSONB, bạn nên tạo một bảng chuyên dụng để lưu trữ các quan hệ (edges). Điều này giúp PostgreSQL tối ưu hóa việc duyệt cây (traversal).

* **Tạo bảng `document_edges**`: Lưu trữ `source_doc_id`, `target_doc_id` và quan trọng nhất là `relation_type` (như `BASED_ON`, `AMENDS`, `SUPERSEDES`).
* **Sử dụng Index**: Tạo các index Bidirectional trên `source_doc_id` và `target_doc_id` để tăng tốc độ truy vấn graph 2 chiều.

### 2. Chiến lược tự động hóa tạo Linking (Extraction Strategy)

Bạn có thể áp dụng 3 chiến lược từ mạnh đến yếu để tự động tạo liên kết:

* **Chiến lược 1: Hard Linking (Độ tin cậy > 90%)**:
* Sử dụng Regex để bóc tách các mã văn bản (ví dụ: `265/2025/NĐ-CP`) từ phần "Căn cứ" của tài liệu.
* Tự động nối link nếu `law_id` mục tiêu đã tồn tại trong database.


* **Chiến lược 2: Semantic Linking (Độ tin cậy 50-80%)**:
* Tính toán độ tương đồng (Jaccard Similarity) giữa các `keywords` trong metadata của hai tài liệu.
* Nếu độ tương đồng > 0.6, tự động tạo quan hệ `RELATED_BY_KEYWORDS`.


* **Chiến lược 3: Hierarchy Linking (Theo cấp bậc)**:
* Phân loại tài liệu thành 4 cấp (0: Luật/Điều lệ, 1: Quy chế, 2: Kế hoạch, 3: Quyết định cụ thể).
* Văn bản cấp thấp hơn thường sẽ tự động link đến các văn bản cấp cao hơn mà nó "Căn cứ" vào.



### 3. Quy trình "Human-in-the-loop" cho các link khó

Với những tài liệu chỉ có 5% metadata đầy đủ, bạn nên triển khai một workflow **Semi-Auto Suggestion**:

1. **Gợi ý**: Khi import tài liệu mới, hệ thống tự động tìm các tài liệu "cha" tiềm năng dựa trên từ khóa và phòng ban.
2. **Xác nhận**: Hiển thị danh sách gợi ý cho người dùng chọn và xác nhận qua giao diện (UI) trước khi chính thức tạo edge.

### Ví dụ về cấu trúc SQL tối ưu để lưu trữ link:

```sql
CREATE TABLE document_edges (
    edge_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_doc_id UUID REFERENCES documents_metadata_v2(document_id),
    target_doc_id UUID REFERENCES documents_metadata_v2(document_id),
    relation_type VARCHAR(50), -- 'BASED_ON', 'AMENDS', etc.
    confidence DECIMAL(3,2),   -- Độ tin cậy của link (0-1)
    verified BOOLEAN DEFAULT false -- Đã được con người kiểm tra chưa?
);

```

**Gợi ý tiếp theo:** Bạn nên bắt đầu bằng việc chạy một script bóc tách Regex trên phần "Căn cứ" của 21 tài liệu hiện tại để tạo ra bộ khung quan hệ đầu tiên. Nếu bạn cần, tôi có thể cung cấp mẫu script Python để thực hiện việc này dựa trên database hiện có của bạn.
