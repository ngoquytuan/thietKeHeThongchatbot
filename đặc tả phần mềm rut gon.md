Dưới đây là **phiên bản rút gọn (condensed spec)** cho đặc tả phần mềm **Chatbot AI/RAG** theo đúng nội dung bạn cung cấp trong YAML.

---

## 1) Tổng quan dự án

* **Tên hệ thống:** Vietnamese Legal Document Knowledge Assistant System
* **Mã dự án:** ATTECH-RAG-KA
* **Mục tiêu chính:** Xây dựng chatbot AI cấp doanh nghiệp tối ưu cho **xử lý văn bản pháp luật tiếng Việt** và **tri thức nội bộ** 
* **Mô hình triển khai:** **On-premise** (ưu tiên vì an toàn dữ liệu) 

## 2) Mục tiêu đo lường (Success metrics / KPI)

Các chỉ tiêu mục tiêu:

* **Retrieval Recall@10 > 90%**
* **Faithfulness > 85%**
* **Response time < 60s (p95)**
* **100 users đồng thời**
* **User satisfaction > 4.0/5**
* **Search success rate > 95%**
* **Cache hit rate > 60%** 

## 3) Phạm vi

**In-scope** (đã xác định):

* Văn bản pháp luật VN (trọng tâm), quy trình/chính sách nội bộ, tài liệu kỹ thuật, quy định ngành hàng không (CNS/ATM)
* Upload/xử lý/index tài liệu đa định dạng (PDF, DOCX, TXT, HTML)
* Chat UI realtime + auto-suggestions, analytics, authz/authn, audit log, hybrid retrieval (Vector + BM25 + Graph định hướng) 

**Out-of-scope**:

* Chatbot public, đa ngôn ngữ ngoài VI/EN, mobile native app, tích hợp CSDL pháp luật bên thứ 3, dịch tự động 

## 4) Use cases chính (tóm tắt)

Hệ thống phục vụ các tình huống điển hình:

* Tra cứu văn bản theo **mã văn bản** (ví dụ “76/2018/NĐ-CP”) – Critical
* Hỏi đáp **quy trình/chính sách nội bộ**
* Tra cứu thông tin kỹ thuật sản phẩm, truy cập tài liệu compliance theo phân quyền
* Admin: quản lý user, batch upload, xem analytics 

## 5) Dữ liệu & đặc thù tiếng Việt

* Dữ liệu quy mô: **100,000+ documents, mở rộng đến 1M**, giới hạn **100 concurrent users** 
* Tài liệu pháp luật có cấu trúc phân cấp **Nghị định → Chương → Điều → Khoản** và cần **giữ nguyên mã luật/số/ký tự đặc biệt** 
* Xử lý tiếng Việt:

  * Chuẩn hóa Unicode **NFC**, nhận input NFD và normalize nội bộ 
  * Tokenization: **underthesea** (primary), **pyvi** (backup) và ràng buộc Python 3.10.11 
  * Tối ưu tìm kiếm dấu: lưu bản gốc có dấu + sinh biến thể bỏ dấu cho BM25 
  * Luật về “legal code preservation”: **không được remove số** trước khi phát hiện mã luật; lưu mã gốc trong metadata 

## 6) Kiến trúc rút gọn

**Stack chính:**

* **Backend:** FastAPI (Python 3.10.11) 
* **Frontend/UI:** Streamlit (chat UI + admin dashboard) 
* **Data layer:**

  * PostgreSQL 15: metadata, RBAC, audit logs, BM25, xử lý tiếng Việt 
  * ChromaDB 1.0.0: lưu vector, semantic search, hybrid search 
  * Redis 7: cache, session, rate limit 
  * Neo4j: **Phase 2 (planned)** cho Graph RAG 

**Hạ tầng/observability:**

* Docker + Docker Compose (K8s future), Prometheus/Grafana/Loki 

## 7) RAG/AI thiết kế cốt lõi (rút gọn)

* **Retrieval approach:** Hybrid 
* **Embedding model:** Qwen/Qwen3-Embedding-0.6B, **1024 dim**, self-host GPU (8GB+ VRAM, CUDA 11.8) 
* **LLM generation:** Multi-provider (OpenAI/Anthropic/local), fallback GPT-3.5-turbo, context 8192 tokens 

**Pipeline retrieval (tóm tắt):**

1. Vector search (ChromaDB) top 20, cosine > 0.5, weight 0.7
2. BM25 (PostgreSQL) top 20, weight 0.3
3. Hybrid combine → top 10
4. Reranking (optional) 

**Query understanding & fallback:**

* Query expansion (từ điển domain), intent classification, entity extraction (mã luật/điều/khoản/ngày)
* Fallback: substring search khi phát hiện mã luật, lọc theo metadata, graph traversal (phase 2) 

## 8) Bảo mật & phân quyền (RBAC)

* Auth: **JWT local**, session timeout 30 phút, password policy + bcrypt 
* Authorization: RBAC 5 tầng (Guest/Employee/Manager/Director/System Admin) và enforcement ở API layer trước khi trả kết quả 
* Data protection: TLS 1.3; AES-256 planned; masking PII trong logs; retention policy (audit 2 năm, query logs 1 năm, session 30 ngày…) 
* PDPA: hiện **Partially Met**, cần bổ sung workflow consent (Phase 2) 

## 9) Non-functional (NFR) tối thiểu cần đạt

* **Response time:** search <2s (p50), <5s (p95); generation <30s (p50), <60s (p95); end-to-end <60s 
* **Throughput:** 10 QPS sustained (peak 50), 100 concurrent users 
* **Availability:** SLA 99.5% (8AM–6PM), RTO 4h, RPO 24h 
* **Fallback mechanisms:** LLM fail → trả context + message; VectorDB fail → BM25; DB fail → serve cached… 

## 10) Kiểm thử & nghiệm thu (Acceptance)

Acceptance criteria (tóm tắt):

* Functional: FR-01..FR-08 hoạt động; search “relevant” cho 95% test queries; RBAC đúng; audit log đủ; ingestion hỗ trợ format; UI đạt yêu cầu 
* AI: Recall@10 > 90%, faithfulness > 85%, legal code extraction accuracy > 95% 

## 11) Triển khai & vận hành (Ops)

* Strategy: hướng tới blue-green; hiện manual có rollback plan; release bi-weekly (Phase 1) / weekly (Phase 2) 
* Environments: Dev/Staging/Prod, prod phục vụ ~400 nhân sự theo role 
* Backup/retention/recovery: PostgreSQL daily full + hourly incremental; retention theo ngày/tuần/tháng/năm; test DR quarterly 

## 12) Rủi ro / TBD / câu hỏi mở

Một số câu hỏi còn mở cho Phase 2: ngân sách infra, timeline SSO (LDAP/AD), quyết định self-host LLM vs API, timeline K8s, DR site… 

---

Nếu bạn muốn, mình có thể tiếp tục tạo **bản rút gọn theo đúng format 1–2 trang** (giống “Product/Technical One-pager”) hoặc **bản rút gọn theo checklist nghiệm thu** (dễ ký duyệt UAT/Go-live) dựa trên đúng các mục ở trên.
