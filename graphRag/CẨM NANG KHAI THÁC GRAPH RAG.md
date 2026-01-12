# CẨM NANG KHAI THÁC GRAPH RAG (THỰC HÀNH & VẬN HÀNH)

*Tài liệu này được viết dựa trên toàn bộ quá trình triển khai, debug và test GraphRAG trong hệ thống FR03.3. Mục tiêu là giúp bạn (và dev sau này) **hiểu – vận hành – khai thác GraphRAG đúng cách**, không nhầm lẫn giữa graph traversal và nghiệp vụ.*

---

## 1. GraphRAG là gì trong hệ thống của bạn?

Trong hệ thống này, **GraphRAG không thay thế semantic search**, mà **mở rộng nó bằng quan hệ đã được con người/logic hệ thống xác định trước**.

Pipeline chuẩn:

```
User Query
   ↓
Semantic Search (vector / keyword)
   ↓
Graph Expansion (mở rộng theo graph_edges)
   ↓
(Lineage Attach – tùy chọn)
   ↓
Context cho LLM / API response
```

GraphRAG trả lời tốt các câu hỏi dạng:

* *Tại sao văn bản này phải tuân thủ văn bản kia?*
* *Văn bản này dựa trên những căn cứ nào?*
* *Từ luật này triển khai xuống các tài liệu nào?*

---

## 2. Hai khái niệm cốt lõi: Graph Expansion & Lineage Attach

### 2.1. Graph Expansion (Mở rộng đồ thị)

**Định nghĩa**
Graph expansion là quá trình **lấy thêm tài liệu liên quan bằng cách đi theo các cạnh trong graph**, bắt đầu từ các tài liệu semantic search tìm được.

**Nó làm gì?**

* Lấy thêm tài liệu *không giống nội dung*, nhưng *liên quan logic*
* Bổ sung đầy đủ bối cảnh nghiệp vụ / pháp lý

**Ví dụ thực tế**

* Semantic search tìm thấy: `Báo cáo ĐTCT Q1/2025`
* Graph expansion lấy thêm:

  * Dự án DTCT
  * Quy trình DTCT
  * Quyết định phê duyệt
  * Quy chế
  * Thông tư
  * Luật

**Thông số quan trọng**

* `expand_graph: true`
* `max_hops`: đi tối đa bao nhiêu bước trong graph
* `expand_per_doc`: mỗi node mở rộng tối đa bao nhiêu hàng xóm
* `relation_types`: loại quan hệ được phép đi (`BASED_ON`, `REFERENCES`, ...)

---

### 2.2. Lineage Attach (Gắn phả hệ / chuỗi căn cứ)

**Định nghĩa**
Lineage attach là việc **gắn thêm đường đi trong graph** để trả lời câu hỏi:

> “Vì sao tài liệu A lại liên quan tới tài liệu B?”

**Nó KHÔNG**

* Không lấy thêm tài liệu mới
* Không thay đổi kết quả semantic / expansion

**Nó CÓ**

* Chuỗi node + edge giải thích quan hệ
* Hướng đi (upstream / downstream)

**Ví dụ lineage**

```
Báo cáo Q1/2025
 → Dự án DTCT
 → Quy trình DTCT
 → Quyết định phê duyệt
 → Quy chế
 → Thông tư
 → Luật KHCN
```

**Khi nào bật?**

* Debug / audit
* Explainability cho người dùng
* Legal reasoning

---

## 3. Hiểu đúng các bài test standalone

### 3.1. `standalone_lineage_test.py`

**Mục đích**

* Kiểm tra graph traversal có chạy được không
* Không kiểm tra đúng/sai nghiệp vụ

**Ý nghĩa output**

* Upstream lineage: đi ngược lên căn cứ
* Downstream lineage: đi xuôi xuống triển khai
* WARNING về hierarchy: **không phải lỗi**, mà là dấu hiệu graph đã có nhánh ngang

**Kết luận cần nhớ**

> Test này chứng minh graph **đủ phức tạp để cần policy**, không phải graph sai.

---

### 3.2. `standalone_rag_test.py`

**Mục đích**

* Test pipeline GraphRAG end-to-end
* Không dùng FastAPI
* Không dùng semantic engine thật

**Semantic trong test này là gì?**

* DummySemanticEngine
* Chỉ để tạo *initial matches*
* Không phản ánh độ đúng nội dung

**Đọc output như thế nào?**

* `semantic`: tài liệu mồi
* `graph_expanded`: tài liệu lấy thêm từ graph
* `graph_dist`: khoảng cách graph (số hop)

---

## 4. Đọc kết quả GraphRAG đúng cách

### 4.1. Phân biệt 2 loại tài liệu trong context

| Loại            | Ý nghĩa                         |
| --------------- | ------------------------------- |
| semantic        | Tài liệu giống nội dung câu hỏi |
| graph_expansion | Tài liệu liên quan logic        |

Không nên mong **semantic = đúng hết**, vì sức mạnh nằm ở **graph_expansion**.

---

### 4.2. Hiểu `graph_dist`

* `0`: tài liệu mồi (semantic)
* `1`: hàng xóm trực tiếp
* `2+`: tài liệu nền / căn cứ xa hơn

GraphRAG tốt khi:

* `graph_dist` tăng dần theo logic nghiệp vụ
* Context phủ được nhiều level (L0–L6)

---

## 5. Các pattern sử dụng GraphRAG hiệu quả

### 5.1. Câu hỏi "Tại sao / căn cứ"

**Chiến lược**

* Semantic top_k nhỏ (1–2)
* Graph expansion ưu tiên `BASED_ON`
* Bật lineage attach

---

### 5.2. Câu hỏi "Liên quan / triển khai"

**Chiến lược**

* Cho phép cả `REFERENCES`
* Có thể bật downstream lineage
* Không nhất thiết bật lineage attach

---

### 5.3. Tránh nhiễu (Audit / Project khác)

* Giảm `top_k` semantic
* Chỉ expand từ doc có score cao nhất
* Filter theo category / project_code nếu có

---

## 6. Những hiểu lầm thường gặp (RẤT QUAN TRỌNG)

❌ *GraphRAG phải trả về 1 chuỗi thẳng*
→ Sai. Graph có thể có nhánh, đó là bình thường.

❌ *WARNING lineage là lỗi*
→ Không. Nó là tín hiệu graph đã có quan hệ ngang.

❌ *Graph expansion lấy tài liệu không liên quan*
→ Đúng về nội dung, nhưng **đúng về logic**.

---

## 7. Khi nào KHÔNG nên dùng GraphRAG?

* Câu hỏi thuần factual (1 văn bản cụ thể)
* Search nhanh, không cần giải thích
* Dataset chưa có graph_edges đủ chất lượng

---

## 8. Kết luận cuối cùng

> **GraphRAG không phải để “tìm cho giống”, mà để “hiểu cho đúng”.**

Khi bạn:

* Chấp nhận graph là graph (không phải cây)
* Dùng semantic để tìm điểm bắt đầu
* Dùng graph để mở rộng và giải thích

thì GraphRAG sẽ trở thành **công cụ suy luận tài liệu**, không chỉ là search.

---

*(Tài liệu này nên được lưu cùng repo để onboarding dev & làm chuẩn vận hành.)*
