Dưới đây là câu trả lời đầy đủ, gọn và có hệ thống cho câu hỏi của bạn:

# ❓ *Trong RAG, ngoài việc dùng vector DB + embedding, còn kỹ thuật nào đáng chú ý không?*

Câu trả lời: **Có rất nhiều kỹ thuật quan trọng khác** ngoài vector search. Hầu hết các kỹ thuật này **đang được sử dụng trong hệ thống FR05-RAG-Simple của bạn** như thấy trong mã nguồn và tài liệu dự án. Dưới đây là tổng hợp đầy đủ (có dẫn chiếu đến code khi phù hợp).

---

# ✅ 1. **Hybrid Retrieval (Semantic + BM25 + Substring)**

Đây là kỹ thuật mạnh nhất hiện nay, kết hợp ưu điểm của embedding và keyword search:

* **BM25** giúp bắt các từ khoá chính xác, đặc biệt với tài liệu kỹ thuật.
* **Semantic search** tìm các đoạn nghĩa tương đồng.
* **Substring search** xử lý acronym, mã hiệu (ATFM, AIS, AMHS…).

Trong project của bạn, cả 3 kỹ thuật được chạy song song và hợp nhất điểm số (hybrid scoring):
→ Được triển khai trong `SearchClient.triple_search()` 
→ Và được dùng trong orchestrator RAG.

---

# ✅ 2. **Keyword / Pattern-based Retrieval**

Một số câu hỏi chứa thuật ngữ đặc thù (AMHS, ATS, AIS…) mà semantic search khó xử lý.
Trong hệ thống của bạn có **SimpleKeywordExtractor** để nhận diện các pattern:
Ví dụ: “X là gì?”, “Thông tin về X”, acronym viết hoa.
→ File: `simple_keyword_extractor.py` 

Khi phát hiện acronym, hệ thống **auto-run substring search**, tăng độ chính xác.

---

# ✅ 3. **Query Decomposition (Multi-Query RAG)**

Thay vì dùng một câu hỏi lớn, hệ thống chia thành nhiều câu hỏi con → tìm kiếm độc lập → tổng hợp lại.

Ví dụ:

> “Ai ký chi tiền KHCN?”
> → tách thành 3 sub-queries.

Được triển khai trong MultiQuery RAG:
→ File `multi_query_orchestrator.py` và `query_decomposer.py`  

---

# ✅ 4. **Iterative Retrieval (Multi-step refinement)**

Kỹ thuật này lặp đi lặp lại 2–3 vòng:

* LLM phân tích kết quả iteration trước
* Sinh câu truy vấn tinh chỉnh
* Tìm tài liệu vòng tiếp theo

Hệ thống của bạn có module:
→ `IterativeRAGOrchestrator` với 3-step refinement loop 

---

# ✅ 5. **Context Ranking & Smart Context Building**

Ngoài việc “tìm đúng tài liệu”, còn phải “chọn đúng đoạn” để đưa vào LLM:

Trong hệ thống của bạn có:

* **Chunk quality scoring** (độ dài tối ưu, nhiều cấu trúc, chứa bảng/list)
* **Hybrid score normalization**
* **Sentence boundary preservation** (không cắt câu khi truncate)
* **Context utilization 95–99%**

→ Mô tả chi tiết trong tài liệu dự án (HANDOVER) 

---

# ✅ 6. **Prompt Strategies / Adaptive Prompting**

Không phải câu nào cũng xử lý giống nhau. Hệ thống của bạn có **6 chiến lược prompt**:

* technical
* hr
* sales
* balanced
* conservative
* comparison

Điều này là một kỹ thuật rất mạnh trong RAG hiện đại – gọi là **Prompt Orchestration**, giúp tùy chỉnh cách suy luận của LLM tùy theo nội dung.
→ `prompt_manager.py`, `strategy_interface.py`, các file strategy khác  

---

# ✅ 7. **Reranking / Duplicate Boosting**

Để cải thiện độ chính xác, kết quả từ semantic + BM25 + substring được:

* chuẩn hóa điểm về [0,1]
* tăng điểm nếu xuất hiện ở nhiều search engines
* xử lý trùng lặp theo `document_id + chunk_position`

→ `SearchClient` & RAG Orchestrator.

---

# ✅ 8. **SSE Streaming Retrieval**

Thay vì đợi 10–30s, hệ thống stream từng bước:

* decomposition
* search progress
* result aggregation
* token generation

→ `StreamingMultiQueryOrchestrator` 

Đây là kỹ thuật trải nghiệm người dùng hiện đại.

---

# ✅ 9. **Caching & Deduplication**

Cần cache kết quả search (Redis), deduplicate theo chunk & doc ID.
Trong FR05-RAG-Simple:

* Redis được tích hợp trong search-client layer (như mô tả kiến trúc).

---

# ✅ 10. **Hybrid Early Stopping**

Trong multi-query RAG:

* Nếu đã có đủ thông tin (confidence ≥ 0.85),
  → thì dừng tìm kiếm các sub-queries còn lại để tăng tốc.

→ Code trong `_parallel_search_with_early_stop()` của `multi_query_orchestrator.py` 

---

# 🔥 Kỹ thuật nâng cao (rất đáng học thêm, chưa dùng trong project)

Nếu muốn nâng RAG lên cấp độ “state-of-the-art”:

### ⭐ **1. RAG Fusion / Reciprocal Rank Fusion (RRF)**

Kết hợp nhiều engine: vector + BM25 + dense + sparse → dùng phép hợp rank.

### ⭐ **2. ColBERT / Late Interaction Retrieval**

embedding cấp token → tương quan tốt hơn so với embedding văn bản.

### ⭐ **3. Query Rewriting**

Tối ưu câu hỏi trước khi retrieval (Self-RAG, HyDE, Rewriter RAG).

### ⭐ **4. Memory-augmented RAG**

Giữ lại context từ các lần hỏi trước → tạo session knowledge.

---

# 📌 Tóm tắt

**RAG không chỉ là vector DB + embedding.**
Một hệ thống RAG mạnh cần:

* hybrid search
* keyword/pattern detection
* query decomposition
* iterative refinement
* context optimization
* strategy-based prompting
* reranking
* streaming và caching

Và dự án FR05-RAG-Simple của bạn **đã triển khai gần như toàn bộ các kỹ thuật tiên tiến nhất hiện nay**.

---

Nếu bạn muốn, mình có thể:
✅ Vẽ sơ đồ pipeline RAG nâng cao
✅ Đề xuất cách nâng cấp FR05-RAG lên chuẩn SOTA
✅ So sánh từng kỹ thuật và mức ảnh hưởng tới độ chính xác

Chỉ cần nói: **“giải thích sâu hơn phần X”**.
