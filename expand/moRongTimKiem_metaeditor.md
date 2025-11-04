Tôi thấy các agent ai hiện nay có một số công cụ tìm kiếm khá hay trên từ khóa. Kiểu khi sửa code, lọc riêng các file py, md hoặc tìm  file có tên bao gồm *abc* hoặc tìm hàm trong các file source code. Tôi định làm agentai, tôi có nên phát triển tool đó không hay có bm25 và VectorDB là đủ rồi? 

---

Bạn đang đặt câu hỏi rất hay — thực ra **BM25 + VectorDB** là hai trụ cột phổ biến cho retrieval, nhưng chưa chắc đã đủ nếu bạn muốn agent AI của mình hỗ trợ tốt cho các use case lập trình thực tế như bạn mô tả (tìm file `.py`, tìm hàm trong source code, lọc docs `.md`,…).

---

## 1. BM25 và VectorDB

* **BM25 (keyword search)**: mạnh trong việc tìm kiếm từ khóa chính xác, hữu ích khi người dùng nhớ một tên hàm, tên file, hoặc đoạn text.
* **VectorDB (semantic search)**: mạnh ở ngữ nghĩa, khi người dùng không nhớ chính xác nhưng mô tả bằng từ tự nhiên. Ví dụ: "hàm tạo database connection" → vẫn tìm ra `init_db()`.

Tuy nhiên:

* BM25 không giỏi với synonym, paraphrase.
* VectorDB thì dễ bị “false positive” nếu chỉ cần tìm chính xác tên file/hàm.

---

## 2. Tại sao nên phát triển thêm tool lọc & tìm chuyên biệt

Agent AI dùng trong dev workflow thường cần:

* **Lọc theo file type**: chỉ quan tâm `.py`, `.js`, `.md`,…
* **Glob pattern / regex search**: tìm file có tên chứa `*abc*` hoặc `config.*.yml`.
* **Code-aware search**: không chỉ text search, mà parse AST để tìm **định nghĩa hàm, class, biến**.
  Ví dụ: "tìm function connect_db" → parse AST, trả ra định nghĩa và vị trí trong file.

Các tool này bổ sung rất tốt cho BM25/Vector search:

* Tránh noise (không phải lúc nào cũng muốn semantic search).
* Tăng tốc độ: lọc trước bằng file type, sau đó mới apply BM25/Vector.
* Đáp ứng thói quen dev (nhiều dev quen grep, ripgrep, ag, hoặc IDE search).

---

## 3. Gợi ý hướng phát triển

Nếu bạn muốn agent AI thực sự hữu ích cho coder:

* **Kết hợp hybrid search**:

  * bước 1: lọc file theo extension/pattern.
  * bước 2: BM25 để match keyword.
  * bước 3: VectorDB để bổ sung semantic.
* **Code indexing**: parse AST → lưu metadata (function name, class name, docstring). Cho phép query kiểu “tìm class kế thừa từ BaseModel”.
* **Fallback**: nếu semantic trả về mơ hồ → cho phép user switch sang exact grep.
* **UI/UX**: expose query kiểu `"search function=abc file=*.py"` hoặc `"grep: abc in *.md"`.

---

## 4. Kết luận

👉 Nếu bạn chỉ cần demo/PoC, **BM25 + VectorDB** là đủ.
👉 Nếu mục tiêu là **agent AI dùng thực sự cho lập trình**, thì **nên phát triển thêm tool filter + code-aware search**. Nó vừa tăng hiệu quả, vừa tạo khác biệt so với các hệ thống retrieval chung chung.

---

Bạn có muốn mình phác thảo kiến trúc pipeline (BM25 + VectorDB + file filter + AST index) để bạn thấy cách tích hợp chúng lại trong agent không?
Tôi cần agentai xử lý tài liệu tiếng Việt. Phần bm25 và VectorDB đã ổn rồi, nhưng tôi vẫn thấy thiếu thiếu. 

Mình hiểu rồi 👍 — bạn đã có **BM25 + VectorDB** để tìm kiếm tài liệu tiếng Việt, nhưng vẫn cảm giác "thiếu thiếu". Đó là điều rất nhiều anh em gặp khi triển khai retrieval cho nội dung tiếng Việt, vì ngôn ngữ này có một số đặc thù khiến BM25/Vector chưa tối ưu 100%.

---

## 1. Những hạn chế khi chỉ dùng BM25 + VectorDB cho tiếng Việt

* **Tokenization**: BM25 dựa vào tách từ. Tiếng Việt có dấu cách giữa âm tiết chứ không phải từ. Ví dụ: "công nghệ thông tin" → nếu tokenizer cắt sai thì việc match sẽ kém.
* **Hình thái (morphology)**: Tiếng Việt có nhiều biến thể: "học sinh", "học-sinh", "học-sịnh (lỗi chính tả)" → BM25 khó xử lý, VectorDB thì cần augmentation.
* **Tìm kiếm chính xác (exact match)**: nhiều khi bạn chỉ cần tìm cụm "Điều 5" trong văn bản pháp luật, BM25 + VectorDB dễ noise vì semantic lẫn vào.
* **Cấu trúc tài liệu**: nhiều tài liệu tiếng Việt dạng văn bản dài (PDF, nghị định, báo cáo). Nếu chỉ cắt chunk và embed thì dễ mất ngữ cảnh.

---

## 2. Các thành phần bổ sung bạn nên xem xét

Để agent AI "xử lý tài liệu tiếng Việt" hiệu quả hơn, bạn có thể thêm:

### 🔹 **Tìm kiếm chính xác / Regex / Pattern search**

* Cho phép user tìm **số điều luật, mã sản phẩm, số công văn** chính xác.
* Dùng regex hoặc trie-based search → tránh noise của embedding.

### 🔹 **Synonym & normalization**

* Thêm lớp chuẩn hóa: "CNTT" ↔ "công nghệ thông tin", "HĐ" ↔ "hợp đồng".
* Xây dựng synonym dictionary hoặc dùng model Vietnamese synonym expansion.

### 🔹 **Rank fusion / Hybrid reranker**

* Kết hợp BM25 + VectorDB + reranker (cross-encoder tiếng Việt).
* Ví dụ: sắp xếp lại top 50 kết quả bằng mô hình `PhoBERT` hoặc `MiniLM đa ngôn ngữ`.

### 🔹 **Xử lý văn bản dài**

* Chunk theo **cấu trúc tài liệu** (theo heading/mục lục/điều khoản) thay vì fixed-size.
* Cho phép agent trả lời kèm **mốc tham chiếu** ("Điều 15, Khoản 2, Luật A...").

### 🔹 **Lọc metadata**

* Ngoài text, nên cho phép filter theo: tác giả, ngày ban hành, loại văn bản (pdf, docx).
* Rất quan trọng khi xử lý tài liệu hành chính/luật.

---

## 3. Kiến trúc gợi ý

Một pipeline agent AI cho tài liệu tiếng Việt có thể như sau:

1. **Preprocessing**

   * Chuẩn hóa Unicode, bỏ dấu / giữ dấu tuỳ use case.
   * Tokenize bằng `VnCoreNLP` hoặc `underthesea`.
   * Gắn nhãn metadata (ngày, tiêu đề, loại văn bản).

2. **Indexing**

   * BM25 cho keyword search.
   * VectorDB (e5-large, PhoBERT embeddings, multilingual MPNet).
   * AST/regex index nếu có code hoặc tài liệu có cấu trúc.

3. **Query handling**

   * Nếu query là **mẫu số/regex** → search trực tiếp.
   * Nếu query là **natural language** → VectorDB + reranker.
   * Nếu query là **cụm chính xác** → BM25 boost.

4. **Reranking + Aggregation**

   * Hợp nhất kết quả BM25 & VectorDB.
   * Dùng cross-encoder reranker (fine-tuned trên tiếng Việt nếu có).

---

## 4. Kết luận

👉 BM25 + VectorDB là nền tảng tốt, nhưng với tài liệu tiếng Việt thì bạn **nên bổ sung thêm**:

* exact/regex search,
* synonym & normalization,
* reranker đa ngôn ngữ,
* chunk theo cấu trúc tài liệu.

Khi có đủ, agent AI mới thực sự mạnh trong **tìm luật, báo cáo, tài liệu nội bộ** tiếng Việt.

---

Bạn có muốn mình liệt kê luôn **các model/middleware open-source tốt cho tiếng Việt** (ví dụ: tokenizer, embedding, reranker) để bạn build nhanh không?
Một số kỹ thuật bạn giới thiệu rất hay nhưng tôi chưa hiểu. Các kỹ thuật ấy cần database để triển khai không? Tôi đang có sẵn PostgreSQL cho bm25 và chromadb cho VectorDB và redis để cached rồi. 
Câu hỏi của bạn rất thực tế 👌. Mình sẽ giải thích rõ: **các kỹ thuật bổ sung** mình gợi ý có cái cần database backend, có cái chỉ là “middleware” thêm vào pipeline, không yêu cầu DB mới. Bạn đang có **PostgreSQL (BM25), ChromaDB (VectorDB), Redis (cache)** thì đã đủ để triển khai.

---

## 1. Những kỹ thuật KHÔNG cần DB riêng

Các lớp này có thể đặt ngay trên pipeline tìm kiếm hiện tại:

* **Regex / exact match search**
  → Chạy trực tiếp trên file raw text hoặc trong PostgreSQL (dùng `LIKE`, `~` hoặc `pg_trgm`).
  → Không cần DB mới, chỉ cần thêm module query handler.

* **Synonym & normalization**
  → Ví dụ: trước khi query, map “CNTT” → “công nghệ thông tin”.
  → Chỉ cần dictionary (file JSON, bảng nhỏ trong Postgres).
  → Không đòi hỏi DB mới, chỉ xử lý query + text preprocessing.

* **Chunk theo cấu trúc tài liệu**
  → Là bước **indexing** trước khi nạp vào PostgreSQL / ChromaDB.
  → Bạn vẫn lưu trong DB cũ, chỉ khác là document được cắt smart hơn (theo heading/mục lục).

---

## 2. Những kỹ thuật cần DB hỗ trợ hoặc data structure thêm

Không nhất thiết phải cài DB mới, nhưng bạn có thể tận dụng Postgres/Chroma hiện có:

* **Hybrid reranker (BM25 + VectorDB + rerank)**

  * Postgres trả về top-k BM25.
  * Chroma trả về top-k semantic.
  * Bạn merge hai danh sách → rerank bằng cross-encoder.
  * Không cần DB mới, chỉ cần compute model (PhoBERT, MiniLM).

* **Metadata filter**

  * Nếu tài liệu có thuộc tính (ngày ban hành, loại văn bản…) thì nên lưu trong schema Postgres hoặc collection metadata của Chroma.
  * Truy vấn sau đó sẽ kết hợp: `WHERE doc_type='law' AND date > 2020`.

* **Index AST / code-aware search** (nếu muốn hỗ trợ code/document đặc thù)

  * Parse code → lưu function name, class, line number vào Postgres table riêng.
  * Query: `"SELECT * FROM function_index WHERE name ILIKE '%connect_db%'"`.
  * Đây chỉ là thêm 1 bảng index, không phải DB mới.

---

## 3. Vai trò của Redis

Redis bạn có thể tận dụng cho:

* Cache kết quả query (BM25 / VectorDB top-k).
* Cache embedding vector của những đoạn text hay truy vấn lặp lại.
* Cache synonym mapping để query nhanh hơn.

Không cần thay đổi gì, chỉ cần thêm logic cache hit/miss.

---

## 4. Tổng kết

👉 Các kỹ thuật bổ sung **không bắt buộc DB mới**.
Bạn hoàn toàn có thể build trên stack hiện tại: **Postgres (BM25) + Chroma (Vector) + Redis (cache)**.
Chỉ cần:

* thêm module preprocessing (regex, synonym),
* thêm reranker (model inference),
* và có thể mở rộng schema (AST index, metadata) trong Postgres/Chroma.

---

Bạn có muốn mình vẽ cho bạn **sơ đồ pipeline kiến trúc** (từng bước: query → filter/regex → BM25/Vector → reranker → answer) để dễ hình dung hơn không?

Như thế việc triển khai cũng rất độc lập mà không ảng hưởng gì đến những module đang chạy đúng không. Sẽ cần một metadata editor để sửa, update thông tin cho các dữ liệu đã có cho tương thích các kỹ thuật mới. Rồi triển khai dần các module, kỹ thuật còn lại? 

Đúng rồi 👍, bạn nắm ý rất chuẩn. Mình giải thích chi tiết hơn để bạn yên tâm:

---

## 1. Triển khai độc lập, không ảnh hưởng module đang chạy

* **BM25 (Postgres)** và **VectorDB (Chroma)** hiện tại của bạn cứ để nguyên, không phải đổi.
* Các kỹ thuật mới (regex, synonym, reranker, metadata filter…) đều có thể thêm vào dưới dạng **middleware** hoặc **service riêng**, không cần đụng vào core DB.
* Cách làm: bạn viết thêm một lớp **retrieval orchestrator** (kiểu router) để nhận query, rồi:

  1. Quyết định loại query (regex? semantic? exact?).
  2. Gọi Postgres hoặc Chroma hoặc cả hai.
  3. Áp dụng reranker / filter nếu có.

→ Như vậy hệ thống cũ vẫn chạy ổn định, chỉ là có thêm đường xử lý “cao cấp” hơn.

---

## 2. Metadata editor là cần thiết

* Vì muốn dùng được **metadata filter / synonym mapping / document type filtering**, bạn phải enrich dữ liệu đã index.
* Một **metadata editor** (UI đơn giản hoặc tool CLI) sẽ giúp:

  * Thêm / sửa / xoá field metadata: ví dụ `doc_type = "nghị định"`, `ngày_ban_hành = 2023-10-12`.
  * Quản lý synonym dictionary: `"CNTT" ↔ "công nghệ thông tin"`.
  * Update label cho dữ liệu cũ để tương thích với module mới.

Bạn có thể lưu metadata này trực tiếp trong:

* **Postgres**: thêm cột hoặc bảng liên kết.
* **Chroma**: dùng metadata field của document/embedding.

---

## 3. Triển khai dần từng module

Không nhất thiết phải build tất cả cùng lúc. Một lộ trình hợp lý:

1. **Phase 1 – Quick win**

   * Thêm regex/exact match vào Postgres.
   * Thêm dictionary-based synonym expansion.

2. **Phase 2 – Enrichment**

   * Xây metadata editor để enrich tài liệu.
   * Lưu metadata vào Postgres/Chroma.
   * Cho phép filter theo metadata.

3. **Phase 3 – Intelligence**

   * Tích hợp reranker (PhoBERT / multilingual MiniLM).
   * Hợp nhất BM25 + VectorDB + reranker.

4. **Phase 4 – Specialized search**

   * Index code AST (nếu cần hỗ trợ code).
   * Chunk tài liệu theo cấu trúc (heading/mục lục).

→ Triển khai kiểu “modular incremental”, không ảnh hưởng tới các module cũ, mà vẫn cải thiện trải nghiệm liên tục.

---

✅ Tóm lại:

* Bạn hoàn toàn có thể phát triển độc lập, không phá vỡ hệ thống cũ.
* Cần **metadata editor** để đồng bộ dữ liệu cho các kỹ thuật mới.
* Có thể triển khai từng bước nhỏ, mỗi bước đem lại giá trị rõ rệt.

---

Bạn có muốn mình gợi ý luôn **công cụ / framework để build metadata editor** (ví dụ: admin UI open-source hoặc tích hợp ngay với Postgres/Chroma) để tiết kiệm thời gian dev không?

tổng hợp lại những gì đã thảo luận thành một tài liệu thiết kế để dev phát triển. Yêu cầu thực hiện theo từng bước như. step1: kiểm tra databases hiện tại, kết nối, schema. step2: cập nhật schema của database theo thiết kế mới. kiểm tra đảm bảo schema mới đã triển khai đúng. step3: hiệu chỉnh các module nạp dữ liệu nếu cần thiết và nạp dữ liệu vào databases mới, kiểm tra đảm bảo dữ liệu nạp đúng. step4. phát triển và kiểm tra các module mở rộng từng module 1, kiểm tra sau khi phát triển xong mối module, đảm bảo phải độc lập với các module đã có, lặp lại step4 cho đến khi các module đã hoàn thiện. tất cả đều phải có log ra terminal để theo dõi và debug xem lỗi ở module nào, lúc nào.



Mình đã soạn xong **tài liệu thiết kế** với lộ trình triển khai theo từng bước (step1 → step4), có đầy đủ schema gợi ý, module mở rộng, logging chuẩn JSON ra terminal, tiêu chí test/rollback… Bạn xem ở khung bên cạnh nhé. Nếu muốn chỉnh sửa hay thêm chi tiết (ví dụ mẫu migration “down”, hoặc DSL bộ lọc metadata cụ thể), nói mình cập nhật ngay.

---

# Thiết kế Agent AI Retrieval tiếng Việt – Kế hoạch triển khai theo bước

> Mục tiêu: mở rộng hệ thống tìm kiếm hiện tại (PostgreSQL cho keyword/BM25, ChromaDB cho semantic/Vector, Redis cho cache) bằng các kỹ thuật bổ sung (regex/exact search, synonym & normalization, metadata filter, rank fusion + reranker, chunking theo cấu trúc, tùy chọn code-aware/AST) theo lộ trình từng bước, đảm bảo độc lập với hệ thống đang chạy.

---

## 0) Phạm vi & nguyên tắc

* **Không phá vỡ** hệ thống hiện có. Tất cả mở rộng dưới dạng module độc lập + feature flag.
* **Observability trước:** mọi bước phải có log ra terminal (structured log) để theo dõi, debug, và audit.
* **Triển khai tăng dần:** mỗi module hoàn thiện → kiểm thử → bật cờ.
* **Tối ưu cho tiếng Việt:** normalization, synonym, chunking có cấu trúc.

---

## 1) Kiến trúc tổng quan (high-level)

```
[Client/Agent]
   │
   ├─► [Retrieval Orchestrator]
   │       ├─ Preprocess (normalization, synonym expansion, intent detection)
   │       ├─ Router (regex/exact? keyword? semantic?)
   │       ├─ Query BM25 (Postgres) + Filters (metadata)
   │       ├─ Query Semantic (Chroma) + Filters (metadata)
   │       ├─ Merge Top-K → Reranker (cross-encoder)
   │       └─ Compose Answer + Citations
   │
   ├─► [Ingestion Pipeline]
   │       ├─ Parsing (PDF/DOCX/HTML)
   │       ├─ VN normalization (unicode/unaccent/tokenize)
   │       ├─ Structural Chunking (heading/mục/điều)
   │       ├─ Embedding → Chroma
   │       └─ Keyword/TS index + Metadata → Postgres
   │
   ├─► [Optional: Code-Aware Index]
   │       ├─ AST parser → function/class index → Postgres
   │       └─ File filters/globs
   │
   └─► [Redis Cache]
           ├─ Query cache (BM25/Vector top-k)
           ├─ Embedding cache
           └─ Synonym dictionary cache
```

---

## 2) Thiết kế dữ liệu & metadata

### 2.1 Bảng/tập dữ liệu cốt lõi (Postgres)

* **documents**: (doc_id PK, title, source, lang, doc_type, issued_date, version, url, checksum, raw_text, normalized_text, metadata JSONB, created_at, updated_at)
* **chunks**: (chunk_id PK, doc_id FK, idx, text, normalized_text, headings JSONB, page_from, page_to, metadata JSONB)
* **synonyms**: (key TEXT, variants TEXT[], normalized BOOLEAN, updated_at)
* **function_index (optional)**: (id PK, repo, file_path, symbol, kind, signature, line_no, docstring, metadata JSONB)

Chỉ mục khuyến nghị:

* `CREATE EXTENSION IF NOT EXISTS pg_trgm;`
* `CREATE EXTENSION IF NOT EXISTS unaccent;`
* GIN/GIN_trgm trên `title`, `raw_text`/`normalized_text`, và `metadata` (JSONB path ops).

### 2.2 ChromaDB (vector store)

* **collection: vi_documents**

  * id = chunk_id
  * embedding
  * metadata: { doc_id, title, doc_type, issued_date, headings, page, source, url, lang }

### 2.3 Redis (cache)

* Key scheme gợi ý:

  * `retrieval:bm25:{q_hash}` → list(doc_id/chunk_id, score)
  * `retrieval:vec:{q_hash}` → list(chunk_id, score)
  * `embedding:{text_hash}` → vector
  * `synonyms:v1` → JSON dictionary
  * TTL theo nhu cầu; có invalidation khi reindex.

---

## 3) Module mở rộng (độc lập, bật/tắt bằng feature flag)

1. **Regex / Exact Search**

   * Xử lý truy vấn chứa pattern (mã văn bản, “Điều \d+”, số công văn…).
   * Ưu tiên chạy trước semantic khi phát hiện pattern.

2. **Synonym & Normalization**

   * Map viết tắt: CNTT ↔ công nghệ thông tin, HĐ ↔ hợp đồng…
   * Chuẩn hóa: unicode NFC, lowercasing theo ngữ cảnh, unaccent (tùy chọn), chuẩn lỗi gõ dấu phổ biến.

3. **Metadata Filter**

   * Filter theo `doc_type`, `issued_date`, `source`…
   * Thêm UI/query DSL: `type:law date>=2020 source:gov`.

4. **Rank Fusion + Reranker**

   * Lấy top-K từ BM25 + top-K từ Vector → union → rerank (cross-encoder đa ngôn ngữ).
   * Cho phép weight điều chỉnh.

5. **Structural Chunking**

   * Cắt theo heading/mục/điều khoản để giữ ngữ cảnh đúng.
   * Lưu `headings` và `page` vào metadata chunk.

6. **Code-Aware / AST (tùy chọn)**

   * Parse AST, lưu bảng `function_index` để truy vấn nhanh theo symbol/ký hiệu.

---

## 4) Quy ước logging (bắt buộc)

* **Structured logs** (JSON từng dòng) ra terminal. Trường khuyến nghị:

  * `ts`, `level`, `step`, `module`, `action`, `status`, `duration_ms`, `records`, `doc_id/chunk_id`, `error`
* Ví dụ:

```json
{"ts":"2025-10-08T09:12:03.456Z","level":"INFO","step":"step3","module":"ingest","action":"upsert_chunks","status":"ok","records":128,"duration_ms":842}
{"ts":"2025-10-08T09:12:05.110Z","level":"ERROR","step":"step4","module":"reranker","action":"score","status":"fail","error":"cuda out of memory","records":50}
```

* Mức log: `INFO` (luồng chuẩn), `WARN` (bất thường), `ERROR` (lỗi), `DEBUG` (chi tiết khi bật).
* Kèm `trace_id` để liên kết các log của cùng một truy vấn.

---

## 5) Kế hoạch triển khai theo bước

### **Step 1: Kiểm tra databases hiện tại, kết nối, schema**

**Mục tiêu:** xác nhận trạng thái Postgres/Chroma/Redis đang chạy tốt và nắm rõ schema.

Checklist

* [ ] Kiểm tra kết nối Postgres/Chroma/Redis (healthcheck + quyền).
* [ ] Dump/ghi nhận schema hiện tại (Postgres) và collections/metadata của Chroma.
* [ ] Kiểm thử truy vấn mẫu (BM25, vector) để baseline latency/accuracy.
* [ ] Ghi log: environment, version, endpoint, params.

Gợi ý lệnh (minh họa)

```sql
-- Postgres
SELECT version();
\dt+ -- liệt kê bảng
-- Kiểm tra extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
```

```bash
# Chroma (pseudo)
chromactl collections list
chromactl health

# Redis
redis-cli PING
redis-cli INFO server
```

Kết quả mong đợi

* Có báo cáo ngắn: kết nối OK, schema hiện tại, extensions/collections hỗ trợ.
* Log INFO chi tiết từng bài test.

---

### **Step 2: Cập nhật schema theo thiết kế mới**

**Mục tiêu:** thêm bảng/cột/indices để hỗ trợ metadata, chunking, synonym, và optional AST.

Migration (minh họa Postgres)

```sql
BEGIN;

-- documents
ALTER TABLE documents
  ADD COLUMN IF NOT EXISTS doc_type TEXT,
  ADD COLUMN IF NOT EXISTS issued_date DATE,
  ADD COLUMN IF NOT EXISTS lang TEXT DEFAULT 'vi',
  ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb,
  ADD COLUMN IF NOT EXISTS normalized_text TEXT;

-- chunks
CREATE TABLE IF NOT EXISTS chunks (
  chunk_id TEXT PRIMARY KEY,
  doc_id   TEXT REFERENCES documents(doc_id) ON DELETE CASCADE,
  idx      INT,
  text     TEXT,
  normalized_text TEXT,
  headings JSONB,
  page_from INT,
  page_to   INT,
  metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_chunks_text_trgm ON chunks USING GIN (normalized_text gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_chunks_meta ON chunks USING GIN (metadata);

-- synonyms
CREATE TABLE IF NOT EXISTS synonyms (
  key TEXT PRIMARY KEY,
  variants TEXT[],
  normalized BOOLEAN DEFAULT true,
  updated_at TIMESTAMP DEFAULT now()
);

-- optional AST index
CREATE TABLE IF NOT EXISTS function_index (
  id SERIAL PRIMARY KEY,
  repo TEXT,
  file_path TEXT,
  symbol TEXT,
  kind TEXT,
  signature TEXT,
  line_no INT,
  docstring TEXT,
  metadata JSONB
);
CREATE INDEX IF NOT EXISTS idx_function_symbol_trgm ON function_index USING GIN (symbol gin_trgm_ops);

COMMIT;
```

Indices & extensions (nhắc lại)

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
```

ChromaDB

* Xác nhận metadata fields cần có trong collection `vi_documents` (doc_id, title, doc_type, issued_date, headings, page, source, url, lang).

Kiểm tra sau triển khai

* [ ] `EXPLAIN ANALYZE` truy vấn thử trên bảng/bộ chỉ mục mới.
* [ ] API layer có thể đọc/ghi trường metadata mới.
* [ ] Log INFO: thời gian migration, số bảng/cột/indices tạo mới; ERROR nếu fail.

Rollback plan

* Mọi migration gói trong `BEGIN/COMMIT`; nếu lỗi → `ROLLBACK`.
* Bảng mới có thể xóa độc lập nếu chưa dùng.

---

### **Step 3: Hiệu chỉnh module nạp dữ liệu & nạp lại dữ liệu**

**Mục tiêu:** ingestion pipeline cập nhật normalization tiếng Việt, structural chunking, và ghi metadata.

Việc cần làm

* [ ] Parser cập nhật: chuẩn hóa Unicode, (tùy chọn) unaccent, lowercasing theo ngữ cảnh.
* [ ] Structural chunking: cắt theo heading/mục/điều; lưu `headings`, `page_*`.
* [ ] Ghi `doc_type`, `issued_date`, `source`, `lang`… vào `documents.metadata` hoặc cột riêng.
* [ ] Tạo embeddings mới cho `chunks.normalized_text` → upsert vào Chroma.
* [ ] Upsert `chunks` + chỉ mục trgm.

Kiểm thử & xác nhận

* [ ] So khớp tổng số chunk với kỳ vọng.
* [ ] Lấy mẫu 20 doc → kiểm tra thủ công metadata/chunking đúng.
* [ ] Benchmark thời gian nạp, ghi log `records`, `duration_ms`.
* [ ] Cache invalidation: xóa cache Redis liên quan.

Ví dụ log

```json
{"level":"INFO","step":"step3","module":"ingest","action":"parse_chunk","records":512,"duration_ms":3210}
{"level":"INFO","step":"step3","module":"embed","action":"upsert_chroma","records":512,"duration_ms":8421}
```

---

### **Step 4: Phát triển & kiểm tra các module mở rộng (lặp lại cho từng module)**

**Mục tiêu:** triển khai độc lập từng module, có unit/integration test và log rõ ràng.

Khuôn mẫu lặp lại cho mỗi module

1. **Thiết kế & cấu hình**

   * Thêm feature flag: `features.regex_search=true` (ví dụ).
   * DSL/param API rõ ràng (vd: `type:law`, `date>=2020`).
2. **Phát triển**

   * Viết service/module riêng (không chạm core path cũ).
   * Thêm metric counters & timing.
3. **Kiểm thử**

   * Unit test: logic nội bộ.
   * Integration: end-to-end với Postgres/Chroma/Redis giả lập.
4. **Xác nhận độc lập**

   * Bật flag chỉ cho canary/QA.
   * Đảm bảo tắt module không ảnh hưởng đường cũ.
5. **Quan sát & log**

   * Log structured theo quy ước.
   * Alert cơ bản trên ERROR rate/latency.

Ví dụ các vòng lặp:

* **Vòng 4.1 – Regex/Exact**: phát hiện pattern, chạy truy vấn trgm/regex trước; so sánh precision với baseline.
* **Vòng 4.2 – Synonym/Normalization**: mở rộng truy vấn bằng từ đồng nghĩa; cache dictionary trên Redis.
* **Vòng 4.3 – Metadata Filter**: bổ sung cú pháp filter; kiểm thử recall/precision theo mốc thời gian/loại văn bản.
* **Vòng 4.4 – Rank Fusion + Reranker**: hợp nhất BM25 + Vector; rerank bằng cross-encoder đa ngữ; benchmark chất lượng.
* **Vòng 4.5 – Structural Chunking**: so latency/quality trước vs sau chunking có cấu trúc.
* **Vòng 4.6 – (Optional) AST/Code**: build chỉ mục hàm/class; test truy vấn symbol.

Mỗi vòng phải có:

* Báo cáo ngắn: **mục tiêu, thay đổi, số liệu**, và cách rollback.
* Kết quả PASS/FAIL với tiêu chí chấp nhận (dưới đây).

---

## 6) Tiêu chí chấp nhận & bộ kiểm thử

* **Đúng chức năng:** truy vấn có pattern trả về exact match; filter theo metadata chính xác.
* **Chất lượng truy hồi:** nDCG/MRR@10 cải thiện ≥ X% so baseline (đặt mục tiêu nội bộ).
* **Hiệu năng:** P95 latency không tăng quá ngưỡng cho phép (đặt ngân sách ms).
* **Ổn định:** ERROR rate < Y% trong canary.
* **Khả dụng:** tắt module (flag off) → hệ thống quay lại hành vi cũ.

Bộ test gợi ý

* Query luật/pháp lý: “Điều 15”, “Nghị định 13/2023/NĐ-CP”, filter `date>=2023`.
* Từ đồng nghĩa/viết tắt: “CNTT” vs “công nghệ thông tin”.
* Exact codes/IDs: số công văn, mã sản phẩm.
* Văn bản dài: truy vấn mục con theo heading.

---

## 7) Vận hành, an toàn & rollback

* **Feature flags** cho từng module; canary deploy.
* **Migration an toàn:** BEGIN/COMMIT + kiểm tra tương thích schema.
* **Sao lưu**: snapshot Postgres/Chroma trước step2/step3.
* **Rollback**: tắt flag module; revert migration nếu cần (script down);
* **Giám sát**: dashboard latency, ERROR rate, cache hit, size embeddings.

---

## 8) Phụ lục

### 8.1. Pseudo config (YAML)

```yaml
features:
  regex_search: true
  synonym_expansion: true
  metadata_filter: true
  rank_fusion: true
  reranker: true
  structural_chunking: true
  ast_index: false

orchestrator:
  bm25_topk: 50
  vector_topk: 50
  fusion_weight:
    bm25: 0.5
    vector: 0.5
  reranker_topk: 50
  timeouts_ms:
    bm25: 800
    vector: 800
    reranker: 1200

redis:
  ttl_seconds:
    query_cache: 600
    embedding_cache: 86400
```

### 8.2. Pseudo code logging (Python)

```python
import json, time, logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def log(level, **kwargs):
    kwargs.setdefault('ts', time.strftime('%Y-%m-%dT%H:%M:%S%z'))
    print(json.dumps({"level": level, **kwargs}))

log("INFO", step="step3", module="ingest", action="upsert_chunks", records=512, duration_ms=842)
```

### 8.3. Gợi ý kiểm tra hiệu năng

* Benchmark trước/sau mỗi vòng step4.
* So sánh cache hit Redis, thời gian truy vấn Postgres/Chroma, và thời gian reranker.

---

**Kết luận:** Lộ trình trên cho phép mở rộng khả năng xử lý tài liệu tiếng Việt một cách an toàn, có thể kiểm soát, không ảnh hưởng hệ thống đang chạy. Mỗi bước đều có tiêu chí kiểm thử rõ ràng và log chi tiết để truy vết khi có sự cố.

