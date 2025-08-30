# thietKeHeThongchatbot
## 3. YÊU CẦU CHỨC NĂNG

### 3.1 Module Quản lý Dữ liệu và Embedding (FR-01)

**FR-01.1 - Lựa chọn và Tối ưu Embedding Model**
- Hệ thống phải hỗ trợ test và so sánh tối thiểu 5 embedding models khác nhau
- Cung cấp metrics đánh giá: Hit Rate, Mean Reciprocal Rank (MRR)
- Cho phép lựa chọn 2-3 models tốt nhất để sử dụng trong production
- Hỗ trợ fine-tuning model trên dữ liệu nội bộ

**FR-01.2 - Thiết kế Cấu trúc Metadata**
- Mỗi tài liệu phải có các trường metadata bắt buộc:
  - document_id (unique)
  - source_file (đường dẫn file gốc)
  - version (phiên bản tài liệu)
  - department_owner (phòng ban sở hữu)
  - author (người tạo)
  - last_updated (ngày cập nhật cuối)
  - access_level (public, employee_only, manager_only, director_only)
  - document_type (policy, procedure, technical_guide, report)
  - tags (từ khóa tìm kiếm)

### 3.2 Module Quản trị Cơ sở Dữ liệu (FR-02)

**FR-02.1 - Hệ thống CSDL kép**
- **Vector Database**: Lưu trữ embeddings và thực hiện tìm kiếm ngữ nghĩa
  - Hỗ trợ ít nhất một trong: FAISS, Chroma, Weaviate
  - Khả năng lưu trữ tối thiểu 100,000 document chunks
- **Relational Database**: Quản lý metadata và phân quyền
  - Hỗ trợ PostgreSQL hoặc MySQL
  - Lưu trữ thông tin người dùng, phân quyền, audit log

**FR-02.2 - API Quản trị Thống nhất**
- Cung cấp RESTful API cho các thao tác CRUD
- Endpoint chính:
  - `/api/documents` - Quản lý tài liệu
  - `/api/users` - Quản lý người dùng
  - `/api/search` - Tìm kiếm tài liệu
  - `/api/access-control` - Quản lý phân quyền

### 3.3 Module Xử lý Dữ liệu (FR-03)

**FR-03.1 - Công cụ Raw-to-Clean Data**
- Web form để nhập metadata cho tài liệu mới
- Template chuẩn cho các loại tài liệu khác nhau
- Validation dữ liệu đầu vào bắt buộc
- Export tài liệu đã xử lý theo format chuẩn

**FR-03.2 - Công cụ Đánh giá Chất lượng Dữ liệu**
- Phát hiện tài liệu trùng lặp (ngữ nghĩa và từ khóa)
- Xác định nội dung mơ hồ, mâu thuẫn
- Đánh giá độ hoàn chỉnh của metadata
- Báo cáo chất lượng trực quan

**FR-03.3 - Pipeline Nạp Dữ liệu (Data Ingestion)**
- Tự động chunking tài liệu (size: 500-1000 tokens)
- Tạo embeddings cho từng chunk
- Lưu trữ đồng bộ vào Vector DB và Relational DB
- Hỗ trợ batch processing và real-time ingestion

### 3.4 Module RAG Core Engine (FR-04)

**FR-04.1 - Retrieval (Truy xuất)**
- Semantic search với độ chính xác tối thiểu 80%
- Hybrid search (kết hợp semantic và keyword)
- Filtering theo access level của user
- Trả về top-K documents có liên quan (K configurable, default=5)

**FR-04.2 - Synthesis (Tổng hợp)**
- Xây dựng context từ các documents truy xuất được
- Template hóa prompt cho LLM
- Xử lý trường hợp không tìm thấy thông tin phù hợp

**FR-04.3 - Generation (Tạo sinh)**
- Tích hợp với LLM (OpenAI GPT, Anthropic Claude, hoặc local model)
- Sinh câu trả lời dựa trên context và câu hỏi
- Cung cấp citation/reference cho câu trả lời

**FR-04.4 - API Endpoint**
- `/api/ask` - Endpoint chính cho chatbot
- Input: user_query, user_id, session_id
- Output: answer, references, confidence_score

### 3.5 Module Giao diện Chatbot (FR-05)

**FR-05.1 - Giao diện Chat**
- Real-time messaging interface
- Hiển thị lịch sử hội thoại
- Upload file để hỏi về tài liệu cụ thể
- Export cuộc hội thoại

**FR-05.2 - Tính năng Tương tác**
- Auto-suggestion câu hỏi phổ biến
- Quick actions (tìm policy, procedure, technical guide)
- Feedback mechanism (thumbs up/down)
- Multi-language support (Tiếng Việt, English)

### 3.6 Module Bảo mật và Phân quyền (FR-06)

**FR-06.1 - Authentication & Authorization**
- Single Sign-On (SSO) integration ready
- Session management với timeout
- Role-based access control (RBAC)
- Audit logging cho mọi truy cập

**FR-06.2 - Access Control Matrix**

| User Level | Public | Employee_only | Manager_only | Director_only | System_admin |
|------------|--------|---------------|--------------|---------------|--------------|
| Guest | ✓ | ✗ | ✗ | ✗ | ✗ |
| Employee | ✓ | ✓ | ✗ | ✗ | ✗ |
| Manager | ✓ | ✓ | ✓ | ✗ | ✗ |
| Director | ✓ | ✓ | ✓ | ✓ | ✗ |
| System Admin | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## 4. YÊU CẦU PHI CHỨC NĂNG

### 4.1 Hiệu suất (Performance)
- **Thời gian phản hồi**: < 60 giây cho mọi truy vấn
- **Throughput**: Hỗ trợ tối thiểu 100 concurrent users
- **Availability**: 99.5% uptime trong giờ làm việc (8AM-6PM)
- **Scalability**: Có khả năng mở rộng lên 500 users và 1M documents

### 4.2 Bảo mật (Security)
- Mã hóa dữ liệu trong quá trình truyền (TLS 1.3)
- Mã hóa dữ liệu lưu trữ (AES-256)
- Không lưu trữ dữ liệu nhạy cảm trong log
- Regular security scanning và penetration testing

### 4.3 Khả năng sử dụng (Usability)
- Giao diện trực quan, không cần đào tạo phức tạp
- Thời gian học sử dụng cơ bản < 30 phút
- Hỗ trợ nhiều device (desktop, tablet, mobile)
- Responsive design cho mọi kích thước màn hình

### 4.4 Độ tin cậy (Reliability)
- Recovery time sau sự cố < 4 giờ
- Backup dữ liệu hàng ngày
- Error rate < 1% cho các truy vấn hợp lệ
- Graceful degradation khi một số component fail

### 4.5 Khả năng bảo trì (Maintainability)
- Modular architecture với loose coupling
- Comprehensive logging và monitoring
- API documentation đầy đủ
- Code coverage tối thiểu 80%

---
