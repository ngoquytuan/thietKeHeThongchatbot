# 📖 HƯỚNG DẪN TOÀN DIỆN: TỪ ĐẶC TẢ ĐẾN PRODUCTION

## HỆ THỐNG TRỢ LÝ TRI THỨC TÀI LIỆU PHÁP LUẬT ATTECH

> **Phiên bản:** 1.0  
> **Ngày:** 08/02/2026  
> **Mục đích:** Hướng dẫn chi tiết từng bước từ bản Đặc tả Phần mềm (Software Requirements Specification) đến khi hệ thống lên Production — dành cho team phát triển hiểu rõ "tại sao làm", "làm gì", và "làm thế nào"  

---

## MỤC LỤC

1. [Tổng quan Quy trình](#1-tổng-quan-quy-trình)
2. [Giai đoạn 1: Thiết kế Trải nghiệm (UX) & Luồng Logic](#2-giai-đoạn-1)
3. [Giai đoạn 2: Kiến trúc Hệ thống & Thiết kế API](#3-giai-đoạn-2)
4. [Giai đoạn 3: Xử lý Dữ liệu (Data Ingestion Pipeline)](#4-giai-đoạn-3)
5. [Giai đoạn 4: Coding & Phát triển (Implementation)](#5-giai-đoạn-4)
6. [Giai đoạn 5: Kiểm thử & Đánh giá (Testing & Evaluation)](#6-giai-đoạn-5)
7. [Giai đoạn 6: Triển khai & Vận hành (Production & DevOps)](#7-giai-đoạn-6)
8. [Phụ lục: Ma trận Truy vết Yêu cầu](#8-phụ-lục)

---

## 1. TỔNG QUAN QUY TRÌNH

### 1.1. Luồng Tổng thể: Từ Ý tưởng → Production

```mermaid
graph TD
    subgraph "📄 ĐẦU VÀO"
        SRS["📋 Đặc tả Phần mềm (SRS)<br/>Bài toán nghiệp vụ<br/>Yêu cầu chức năng<br/>Yêu cầu phi chức năng"]
    end

    subgraph "GĐ1: THIẾT KẾ UX & LUỒNG LOGIC"
        G1A["👤 Phân tích Stakeholder<br/>& Persona"]
        G1B["🔀 Thiết kế Use Case<br/>& Luồng xử lý"]
        G1C["🎨 Wireframe<br/>& Prototype"]
        G1D["📜 Tài liệu:<br/>Use Case Diagram<br/>Sequence Diagram<br/>Wireframes"]
    end

    subgraph "GĐ2: KIẾN TRÚC & API"
        G2A["🏗️ Chọn Technology Stack"]
        G2B["📊 Thiết kế Database<br/>ERD & Schema"]
        G2C["🔌 Thiết kế API<br/>Endpoints & Contracts"]
        G2D["📜 Tài liệu:<br/>Architecture Diagram<br/>ERD<br/>API Specification"]
    end

    subgraph "GĐ3: XỬ LÝ DỮ LIỆU"
        G3A["📥 Thu thập &<br/>Trích xuất tài liệu"]
        G3B["✂️ Chunking &<br/>Metadata tagging"]
        G3C["🧬 Embedding &<br/>Indexing vào Vector DB"]
        G3D["📜 Sản phẩm:<br/>Vector Database<br/>có dữ liệu sẵn sàng"]
    end

    subgraph "GĐ4: CODING & PHÁT TRIỂN"
        G4A["⚙️ Backend:<br/>RAG Pipeline"]
        G4B["🎨 Frontend:<br/>Chat UI"]
        G4C["🔐 Auth:<br/>RBAC & Security"]
        G4D["📜 Sản phẩm:<br/>Source code<br/>hoàn chỉnh"]
    end

    subgraph "GĐ5: KIỂM THỬ & ĐÁNH GIÁ"
        G5A["🧪 Unit Test &<br/>Integration Test"]
        G5B["📊 RAG Evaluation<br/>(RAGAS)"]
        G5C["🔥 Load Test &<br/>Security Test"]
        G5D["📜 Sản phẩm:<br/>Báo cáo kiểm định<br/>chất lượng"]
    end

    subgraph "GĐ6: TRIỂN KHAI & VẬN HÀNH"
        G6A["🐳 Docker &<br/>Containerization"]
        G6B["🔄 CI/CD<br/>Pipeline"]
        G6C["📈 Monitoring &<br/>Logging"]
        G6D["🚀 PRODUCTION<br/>Hệ thống chạy thực tế"]
    end

    SRS --> G1A --> G1B --> G1C --> G1D
    G1D --> G2A --> G2B --> G2C --> G2D
    G2D --> G3A --> G3B --> G3C --> G3D
    G3D --> G4A --> G4B --> G4C --> G4D
    G4D --> G5A --> G5B --> G5C --> G5D
    G5D --> G6A --> G6B --> G6C --> G6D

    style SRS fill:#E3F2FD,stroke:#1565C0,stroke-width:2px
    style G1D fill:#FFF3E0,stroke:#E65100
    style G2D fill:#FFF3E0,stroke:#E65100
    style G3D fill:#E8F5E9,stroke:#2E7D32
    style G4D fill:#E8F5E9,stroke:#2E7D32
    style G5D fill:#FCE4EC,stroke:#C62828
    style G6D fill:#E8F5E9,stroke:#2E7D32,stroke-width:3px
```

### 1.2. Nguyên tắc Cốt lõi

Mỗi giai đoạn đều tuân theo nguyên tắc **"Truy vết Yêu cầu" (Requirement Traceability)**:

> **Mỗi dòng code đều phải trả lời được: "Dòng code này phục vụ yêu cầu nào trong Đặc tả?"**

```mermaid
graph LR
    SRS["Đặc tả<br/>(SRS §3.4)"] --> UC["Use Case<br/>(UC-001)"]
    UC --> Design["Thiết kế<br/>(Sequence Diagram)"]
    Design --> Code["Code<br/>(api/chat.py)"]
    Code --> Test["Test Case<br/>(TC-001)"]
    Test --> Deploy["Deploy<br/>(docker-compose)"]

    style SRS fill:#E3F2FD,stroke:#1565C0
    style Deploy fill:#E8F5E9,stroke:#2E7D32
```

---

## 2. GIAI ĐOẠN 1: THIẾT KẾ TRẢI NGHIỆM (UX) & LUỒNG LOGIC

### 2.1. Điểm Xuất phát: Từ SRS → Tính năng UX

Tất cả tính năng UX đều **bắt nguồn từ Đặc tả Phần mềm (SRS)**. Không có tính năng nào "tự nghĩ ra" — mọi thứ đều có căn cứ.

#### 2.1.1. Truy vết: Persona Bot đến từ đâu?

```mermaid
graph LR
    subgraph "📋 SRS — Bài toán Nghiệp vụ"
        BT1["§1.3: NV R&D không biết<br/>quy trình mua hàng"]
        BT2["§1.3: NV kinh doanh thiếu<br/>thông tin sản phẩm"]
        BT3["§1.3: NV sản xuất không chắc<br/>tài liệu đang dùng có đúng"]
    end

    subgraph "🎯 Phân tích → Persona Bot"
        P1["Bot phải trả lời CHÍNH XÁC<br/>→ Không được bịa (Hallucination)"]
        P2["Bot phải TRÍCH DẪN NGUỒN<br/>→ NV cần kiểm chứng tài liệu gốc"]
        P3["Bot trả lời NGẮN GỌN<br/>→ NV bận, cần thông tin nhanh"]
    end

    BT1 --> P1
    BT2 --> P2
    BT3 --> P3

    style BT1 fill:#E3F2FD,stroke:#1565C0
    style BT2 fill:#E3F2FD,stroke:#1565C0
    style BT3 fill:#E3F2FD,stroke:#1565C0
    style P1 fill:#FFF3E0,stroke:#E65100
    style P2 fill:#FFF3E0,stroke:#E65100
    style P3 fill:#FFF3E0,stroke:#E65100
```

**Cách suy luận chi tiết:**

| # | Từ SRS (Bài toán) | Phân tích | → Quyết định Thiết kế UX |
|---|---|---|---|
| 1 | *"NV sản xuất không chắc tài liệu có đúng"* (§1.3) | Người dùng cần KIỂM CHỨNG câu trả lời → Bot phải cung cấp bằng chứng | **Citations (Trích dẫn nguồn):** Mỗi câu trả lời kèm link/trích dẫn đến tài liệu gốc, số trang, đoạn cụ thể |
| 2 | *"Hệ thống trả lời chính xác ≥80%"* (§8.1) | 20% có thể sai → Bot PHẢI thú nhận khi không biết | **Fallback:** "Tôi không tìm thấy thông tin về vấn đề này trong tài liệu nội bộ" thay vì trả lời bừa |
| 3 | *"4 loại người dùng: Guest, NV, Trưởng phòng, GĐ"* (§2.2) | Mỗi loại user thấy tài liệu khác nhau → Bot phải filter theo quyền | **Filter theo phòng ban/cấp độ:** UI cho phép chọn danh mục, phòng ban; backend filter theo `access_level` |
| 4 | *"API response time < 60 giây"* (§8.1) | 60 giây là lâu → cần giảm cảm giác chờ đợi | **Streaming Response:** Bot trả lời từng phần (streaming) thay vì đợi xong mới hiển thị |
| 5 | *"Lưu trữ thông tin phiên hội thoại"* (§3.2) | Cần tracking conversation → cần lưu lịch sử | **Chat History:** Sidebar hiển thị danh sách cuộc hội thoại cũ, có thể quay lại xem |
| 6 | *"Batch processing và real-time ingestion"* (§3.3) | Admin cần upload tài liệu mới vào hệ thống | **Upload tài liệu:** Giao diện cho Admin upload PDF/Docx, hệ thống tự xử lý |

#### 2.1.2. Truy vết: Tất cả Tính năng UX

```mermaid
graph TD
    subgraph "📋 SRS Sections"
        S1["§1.3 Bối cảnh nghiệp vụ"]
        S2["§2.2 Phân loại người dùng"]
        S3["§3.2 Module CSDL kép"]
        S4["§3.3 Module Xử lý Dữ liệu"]
        S5["§3.4 Module RAG Core"]
        S6["§8.1 Acceptance Criteria"]
    end

    subgraph "🎨 Tính năng UX"
        F1["🤖 Persona Bot<br/>(ngắn gọn, chính xác)"]
        F2["🚫 Fallback<br/>(thú nhận không biết)"]
        F3["📎 Citations<br/>(trích dẫn nguồn)"]
        F4["📁 Upload tài liệu"]
        F5["📜 Chat History"]
        F6["🔍 Filter<br/>(phòng ban/danh mục)"]
        F7["⚡ Streaming Response"]
        F8["👍 Feedback (Like/Dislike)"]
        F9["📤 Export Conversation"]
    end

    S1 --> F1
    S6 --> F2
    S1 --> F3
    S4 --> F4
    S3 --> F5
    S2 --> F6
    S6 --> F7
    S6 --> F8
    S3 --> F9

    style S1 fill:#E3F2FD,stroke:#1565C0
    style S2 fill:#E3F2FD,stroke:#1565C0
    style S3 fill:#E3F2FD,stroke:#1565C0
    style S4 fill:#E3F2FD,stroke:#1565C0
    style S5 fill:#E3F2FD,stroke:#1565C0
    style S6 fill:#E3F2FD,stroke:#1565C0
```

### 2.2. Bước 1: Vẽ Use Case Diagram

**Mục đích:** Trả lời câu hỏi "AI LÀM GÌ với hệ thống?"

Từ SRS §2.2 (4 loại người dùng) + §3.x (yêu cầu chức năng), ta vẽ Use Case Diagram:

```mermaid
graph TB
    Guest["👤 Guest"]
    Employee["👤 Nhân viên"]
    Manager["👤 Trưởng phòng"]
    Director["👤 Giám đốc"]
    Admin["👤 Admin"]

    subgraph "Hệ thống Trợ lý Tri thức"
        UC1["UC-001: Đặt câu hỏi<br/>(tài liệu public)"]
        UC2["UC-002: Đặt câu hỏi<br/>(tài liệu theo quyền)"]
        UC3["UC-003: Xem lịch sử chat"]
        UC4["UC-004: Upload tài liệu"]
        UC5["UC-005: Quản lý người dùng"]
        UC6["UC-006: Xem Analytics"]
        UC7["UC-007: Cấu hình hệ thống"]
    end

    Guest --> UC1
    Employee --> UC1
    Employee --> UC2
    Employee --> UC3
    Manager --> UC2
    Manager --> UC3
    Manager --> UC6
    Director --> UC2
    Director --> UC6
    Admin --> UC4
    Admin --> UC5
    Admin --> UC7

    style UC1 fill:#E8F5E9
    style UC2 fill:#FFF3E0
    style UC4 fill:#FCE4EC
    style UC5 fill:#FCE4EC
```

**Cách làm cụ thể:**

| Bước | Hành động | Kết quả |
|---|---|---|
| 1 | Đọc SRS §2.2 → Liệt kê tất cả **Actor** (loại người dùng) | Guest, NV, Trưởng phòng, GĐ, Admin |
| 2 | Đọc SRS §3.x → Liệt kê tất cả **Hành động** mỗi Actor có thể làm | Đặt câu hỏi, Xem lịch sử, Upload, Quản lý, ... |
| 3 | Gắn **quyền** cho mỗi Actor-Hành động dựa trên SRS §2.2 | Guest chỉ xem public, NV xem employee_only, ... |
| 4 | Vẽ diagram bằng Mermaid/PlantUML/Draw.io | Use Case Diagram hoàn chỉnh |

### 2.3. Bước 2: Viết Use Case Chi tiết

**Mục đích:** Mô tả CHÍNH XÁC từng bước user tương tác với hệ thống — đây là "kịch bản" để lập trình viên code theo.

**Ví dụ: UC-002 — Đặt Câu hỏi (Tài liệu theo Quyền)**

| Mục | Nội dung |
|---|---|
| **ID** | UC-002 |
| **Tên** | Đặt Câu hỏi về Tài liệu Nội bộ |
| **Actor** | Nhân viên (đã đăng nhập) |
| **Điều kiện tiên quyết** | User đã đăng nhập, có token JWT hợp lệ |
| **Luồng chính (Happy Path)** | Xem bên dưới |
| **Luồng ngoại lệ** | Xem bên dưới |
| **Điều kiện sau** | Câu hỏi và câu trả lời được lưu vào chat history |
| **Nguồn SRS** | §3.4 (RAG Core), §2.2 (Phân quyền) |

**Luồng chính (Happy Path):**

```mermaid
sequenceDiagram
    actor User as 👤 Nhân viên
    participant UI as 🖥️ Chat UI
    participant API as ⚙️ Backend API
    participant Auth as 🔐 Auth Service
    participant RAG as 🤖 RAG Engine
    participant VDB as 🧬 Vector DB
    participant LLM as 🧠 LLM

    User->>UI: 1. Gõ câu hỏi: "Quy trình mua hàng?"
    UI->>API: 2. POST /api/v1/query {question, session_id, token}
    API->>Auth: 3. Verify JWT token
    Auth-->>API: 4. OK: user_level=employee, department=R&D

    API->>RAG: 5. search(query, user_level, department)
    RAG->>VDB: 6. Tìm top-50 chunks tương tự (vector similarity)
    VDB-->>RAG: 7. Trả về 50 chunks + metadata

    Note over RAG: 8. LỌC theo quyền:<br/>Loại bỏ chunks có access_level<br/>> employee
    Note over RAG: 9. XẾP HẠNG: Hybrid scoring<br/>0.7×semantic + 0.3×keyword

    RAG->>LLM: 10. Gửi prompt: System + Context (top-10 chunks) + Question
    LLM-->>RAG: 11. Trả về câu trả lời (streaming)

    RAG-->>API: 12. Response + Citations + Metadata
    API-->>UI: 13. Streaming response về UI
    UI-->>User: 14. Hiển thị câu trả lời + trích dẫn nguồn

    Note over API: 15. Lưu vào chat_messages<br/>& search_analytics
```

**Luồng ngoại lệ (Fallback):**

```mermaid
sequenceDiagram
    actor User as 👤 Nhân viên
    participant UI as 🖥️ Chat UI
    participant RAG as 🤖 RAG Engine
    participant VDB as 🧬 Vector DB

    User->>UI: Hỏi: "Giá cổ phiếu ATTECH hôm nay?"
    UI->>RAG: POST /api/v1/query
    RAG->>VDB: Tìm kiếm vector similarity
    VDB-->>RAG: Kết quả: max_similarity = 0.25 (thấp)

    Note over RAG: similarity < 0.50 threshold<br/>→ KHÔNG ĐỦ CONTEXT<br/>→ Kích hoạt FALLBACK

    RAG-->>UI: Fallback Response
    UI-->>User: "Xin lỗi, tôi không tìm thấy<br/>thông tin về vấn đề này<br/>trong tài liệu nội bộ.<br/>Bạn có thể liên hệ<br/>Phòng Tài chính để được hỗ trợ."

    Note over RAG: Log câu hỏi vào<br/>"unanswered_queries"<br/>để cải thiện data sau
```

### 2.4. Bước 3: Thiết kế Wireframe / Prototype

**Mục đích:** Hình dung giao diện TRƯỚC KHI code — tiết kiệm thời gian sửa đổi.

**Từ Use Case → Layout:**

```
┌─────────────────────────────────────────────────────────┐
│  🔐 ATTECH Trợ lý Tri thức        👤 NV Nguyễn Văn A  │  ← SRS §2.2: Hiển thị user info
├──────────────┬──────────────────────────────────────────┤
│              │                                          │
│ 📜 Lịch sử  │  🤖 Xin chào! Tôi là trợ lý tri thức   │  ← SRS §1.3: Persona Bot
│              │     ATTECH. Tôi có thể giúp bạn tra     │
│ • Quy trình  │     cứu tài liệu nội bộ.                │
│   mua hàng   │                                          │
│              │  👤 Quy trình mua hàng trình GĐ?        │  ← UC-002: Đặt câu hỏi
│ • Chính sách │                                          │
│   nghỉ phép  │  🤖 Theo Quy trình QT-MH-001 [1],      │  ← SRS §1.3: Citations
│              │     quy trình mua hàng gồm 5 bước:      │
│              │     1. Lập phiếu đề xuất mua hàng...     │
│              │     2. Trưởng phòng phê duyệt...         │
│              │                                          │
│              │     📎 Nguồn: [1] QT-MH-001 trang 3-5   │  ← SRS §1.3: Trích dẫn cụ thể
│              │     👍 👎 Phản hồi hữu ích?              │  ← SRS §8.1: User feedback
│              │                                          │
├──────────────┤──────────────────────────────────────────┤
│ 🔍 Lọc theo: │  ┌─────────────────────────────────┐    │
│ □ Phòng R&D  │  │ Nhập câu hỏi...          📎 ➤  │    │  ← SRS §3.3: Upload + Query
│ □ Phòng KD   │  └─────────────────────────────────┘    │
│ □ Tất cả     │                                          │  ← SRS §2.2: Filter theo phòng ban
└──────────────┴──────────────────────────────────────────┘
```

**Mapping Wireframe → SRS:**

| Vùng giao diện | Vị trí | Nguồn SRS | Lý do |
|---|---|---|---|
| Header (user info) | Trên cùng | §2.2 Phân loại người dùng | Hiển thị tên, vai trò, phòng ban — user biết đang đăng nhập đúng |
| Sidebar (lịch sử) | Bên trái | §3.2 Lưu trữ phiên hội thoại | Cho phép quay lại cuộc trò chuyện cũ |
| Sidebar (bộ lọc) | Bên trái dưới | §2.2 Phân quyền + §3.4 Filtering | Chọn phạm vi tìm kiếm theo phòng ban/danh mục |
| Chat area (messages) | Chính giữa | §3.4 RAG Core Engine | Hiển thị hội thoại giữa user và bot |
| Citations block | Dưới mỗi câu trả lời | §1.3 Bối cảnh (cần kiểm chứng) | Trích dẫn trang, đoạn cụ thể trong tài liệu gốc |
| Feedback buttons | Dưới mỗi câu trả lời | §8.1 User satisfaction ≥ 4.0/5.0 | Thu thập phản hồi để cải thiện chất lượng |
| Input area (text + upload) | Dưới cùng | §3.3 Real-time ingestion + §3.4 Query | Nhập câu hỏi, đính kèm file nếu cần |

### 2.5. Sản phẩm Bàn giao Giai đoạn 1

| # | Tài liệu | Mô tả | Công cụ |
|---|---|---|---|
| 1 | **Use Case Diagram** | Tổng quan Actor ↔ System | Mermaid / Draw.io |
| 2 | **Use Case Chi tiết** (10-15 UC) | Mô tả từng bước cho mỗi tương tác | Markdown / Confluence |
| 3 | **Sequence Diagrams** | Luồng xử lý chính và ngoại lệ | Mermaid / PlantUML |
| 4 | **Wireframes / Mockups** | Bản vẽ giao diện cho từng màn hình | Figma / Excalidraw / ASCII |
| 5 | **Ma trận Truy vết** | Mapping: SRS → Use Case → Wireframe component | Bảng Excel/Markdown |

### 2.6. Checklist GĐ1: PASS/FAIL trước khi sang GĐ2

- [ ] Mỗi tính năng UX đều có truy vết ngược về SRS
- [ ] Mọi loại người dùng (4 vai trò) đều có Use Case tương ứng
- [ ] Luồng Fallback (bot không biết) đã được thiết kế
- [ ] Wireframe đã được review bởi ít nhất 1 stakeholder
- [ ] Không có tính năng "tự nghĩ ra" ngoài SRS

---

## 3. GIAI ĐOẠN 2: KIẾN TRÚC HỆ THỐNG & THIẾT KẾ API

### 3.1. Điểm Xuất phát: Từ Use Case → Quyết định Kiến trúc

Kiến trúc hệ thống **không phải tự chọn tùy thích** — nó được **suy ra từ yêu cầu**:

```mermaid
graph TD
    subgraph "📋 Yêu cầu từ SRS"
        R1["§3.4: Semantic search<br/>chính xác ≥80%"]
        R2["§3.2: CSDL kép<br/>(Vector + Relational)"]
        R3["§8.1: 100 concurrent users"]
        R4["§7.1: Bảo mật dữ liệu nội bộ"]
        R5["§3.4: Hybrid search<br/>(semantic + keyword)"]
        R6["§8.1: Response < 60 giây"]
    end

    subgraph "🏗️ Quyết định Kiến trúc"
        D1["→ Cần Vector Database<br/>(ChromaDB / pgvector)"]
        D2["→ Cần PostgreSQL<br/>(metadata + phân quyền)"]
        D3["→ Cần Cache Layer<br/>(Redis)"]
        D4["→ Cần On-premise<br/>(không dùng Cloud công cộng)"]
        D5["→ Cần Embedding Model<br/>(hỗ trợ tiếng Việt)"]
        D6["→ Cần Async API<br/>(FastAPI + Streaming)"]
    end

    R1 --> D1
    R2 --> D2
    R3 --> D3
    R4 --> D4
    R5 --> D5
    R6 --> D6

    style R1 fill:#E3F2FD,stroke:#1565C0
    style R2 fill:#E3F2FD,stroke:#1565C0
    style R3 fill:#E3F2FD,stroke:#1565C0
    style R4 fill:#E3F2FD,stroke:#1565C0
    style R5 fill:#E3F2FD,stroke:#1565C0
    style R6 fill:#E3F2FD,stroke:#1565C0
    style D1 fill:#FFF3E0,stroke:#E65100
    style D2 fill:#FFF3E0,stroke:#E65100
    style D3 fill:#FFF3E0,stroke:#E65100
    style D4 fill:#FFF3E0,stroke:#E65100
    style D5 fill:#FFF3E0,stroke:#E65100
    style D6 fill:#FFF3E0,stroke:#E65100
```

### 3.2. Bước 1: Chọn Technology Stack

**Quy trình quyết định (KHÔNG phải "tôi thích gì thì chọn nấy"):**

| Yêu cầu SRS | Các lựa chọn | Tiêu chí đánh giá | → Quyết định |
|---|---|---|---|
| Vector DB (§3.2) | ChromaDB / Milvus / pgvector / FAISS | Hỗ trợ metadata filter, dễ deploy Docker, Open Source | **ChromaDB 1.0.0** (đơn giản, đủ cho 100K chunks) |
| Relational DB (§3.2) | PostgreSQL / MySQL | Hỗ trợ JSONB, Full-text search tiếng Việt, Extension ecosystem | **PostgreSQL 15** (JSONB indexes, pg_trgm, pgvector extension) |
| Embedding Model (§3.1) | OpenAI / Cohere / Qwen / PhoBERT | Hỗ trợ tiếng Việt, chạy local (bảo mật), GPU RTX 2080 Ti fit | **Qwen3-Embedding-0.6B** (1024 dim, Apache 2.0, local deploy) |
| Backend Framework (§3.2) | FastAPI / Django / Express | Async support, auto OpenAPI docs, Python ML ecosystem | **FastAPI** (async + Pydantic + auto docs) |
| Cache (§8.1) | Redis / Memcached | TTL, pub/sub, data structures | **Redis 7** (session + cache + pub/sub) |
| Frontend (§3.5) | React / Vue / Streamlit | Tốc độ phát triển, real-time chat, prototype nhanh | **Streamlit** (prototype) → **NextJS 18** (production) |
| Bảo mật (§7) | On-premise / Cloud | Dữ liệu nội bộ ATTECH → không đưa lên cloud công cộng | **On-premise** (2 servers nội bộ) |

### 3.3. Bước 2: Thiết kế Database Schema (ERD)

**Từ Use Case → Xác định Entity:**

```mermaid
graph LR
    UC1["UC-001: Đặt câu hỏi"] --> E1["Entity: chat_sessions<br/>Entity: chat_messages"]
    UC2["UC-002: Truy vấn theo quyền"] --> E2["Entity: users<br/>Entity: user_permissions"]
    UC4["UC-004: Upload tài liệu"] --> E3["Entity: documents_metadata<br/>Entity: document_chunks"]
    UC6["UC-006: Xem Analytics"] --> E4["Entity: search_analytics<br/>Entity: system_metrics"]

    style UC1 fill:#E8F5E9
    style UC2 fill:#FFF3E0
    style UC4 fill:#FCE4EC
    style UC6 fill:#E3F2FD
```

**ERD (Entity Relationship Diagram):**

```mermaid
erDiagram
    users {
        uuid user_id PK
        varchar username UK
        varchar email UK
        varchar password_hash
        enum user_level "guest|employee|manager|director"
        varchar department
        boolean is_active
        timestamp created_at
    }

    documents_metadata {
        uuid document_id PK
        varchar title
        varchar source_file
        enum access_level "public|employee|manager|director"
        varchar department_owner
        varchar document_type "policy|procedure|technical"
        text[] tags
        uuid author_id FK
        integer chunk_count
        timestamp created_at
    }

    document_chunks {
        uuid chunk_id PK
        uuid document_id FK
        integer chunk_index
        text content
        varchar vector_id "ID trong ChromaDB"
        jsonb chunk_metadata
    }

    chat_sessions {
        uuid session_id PK
        uuid user_id FK
        varchar session_name
        timestamp created_at
        timestamp last_activity
    }

    chat_messages {
        uuid message_id PK
        uuid session_id FK
        enum role "user|assistant|system"
        text content
        jsonb citations "nguồn trích dẫn"
        float processing_time_ms
        timestamp created_at
    }

    search_analytics {
        uuid log_id PK
        uuid user_id FK
        text query_text
        varchar search_method
        integer results_count
        float processing_time_ms
        float top_similarity_score
        timestamp created_at
    }

    audit_logs {
        uuid log_id PK
        uuid user_id FK
        varchar action
        varchar resource_type
        jsonb action_details
        varchar ip_address
        timestamp created_at
    }

    users ||--o{ documents_metadata : "tạo"
    users ||--o{ chat_sessions : "sở hữu"
    users ||--o{ search_analytics : "tạo"
    users ||--o{ audit_logs : "tạo"
    documents_metadata ||--o{ document_chunks : "chứa"
    chat_sessions ||--o{ chat_messages : "chứa"
```

**Cách suy luận mỗi bảng:**

| Bảng | Suy ra từ | SRS Section | Giải thích |
|---|---|---|---|
| `users` | UC "Đăng nhập", 4 vai trò | §2.2 | Lưu thông tin 4 loại người dùng |
| `documents_metadata` | UC "Upload tài liệu" | §3.1, §3.3 | Metadata: ai tạo, phòng ban nào, cấp truy cập nào |
| `document_chunks` | UC "Tìm kiếm" | §3.3, §3.4 | Mỗi tài liệu chia thành chunks để search |
| `chat_sessions` | UC "Xem lịch sử" | §3.2 | Mỗi cuộc trò chuyện là 1 session |
| `chat_messages` | UC "Đặt câu hỏi" | §3.4 | Mỗi câu hỏi/trả lời là 1 message |
| `search_analytics` | UC "Xem Analytics" | §8.1 | Log mỗi lần tìm kiếm để phân tích |
| `audit_logs` | Yêu cầu bảo mật | §7 | Log mọi hành động để kiểm toán |

### 3.4. Bước 3: Thiết kế API Endpoints

**Từ Use Case → API Endpoint:**

| Use Case | HTTP Method | Endpoint | Request | Response | SRS |
|---|---|---|---|---|---|
| UC-001,002: Đặt câu hỏi | `POST` | `/api/v1/query` | `{question, session_id, filters}` | `{answer, citations[], sources[]}` (streaming) | §3.4 |
| UC-004: Upload tài liệu | `POST` | `/api/v1/ingest` | `multipart/form-data {file, metadata}` | `{document_id, chunk_count, status}` | §3.3 |
| UC-003: Xem lịch sử | `GET` | `/api/v1/sessions` | `?page=1&limit=20` | `{sessions[]}` | §3.2 |
| UC-003: Xem chi tiết | `GET` | `/api/v1/sessions/{id}/messages` | | `{messages[]}` | §3.2 |
| Đăng nhập | `POST` | `/api/v1/auth/login` | `{username, password}` | `{token, user_info}` | §2.2 |
| UC-006: Analytics | `GET` | `/api/v1/analytics/summary` | `?period=7d` | `{total_queries, avg_time, top_docs}` | §8.1 |
| UC-005: Quản lý users | `CRUD` | `/api/v1/admin/users` | Varies | Varies | §2.2 |
| Health check | `GET` | `/api/v1/health` | | `{status, services{}}` | §8.1 |

**API Contract chi tiết (ví dụ endpoint chính):**

```
POST /api/v1/query
Headers:
  Authorization: Bearer <jwt_token>
  Content-Type: application/json

Request Body:
{
  "question": "Quy trình mua hàng trình giám đốc?",
  "session_id": "uuid-optional",          // null = tạo session mới
  "filters": {
    "departments": ["Phòng R&D"],          // Lọc theo phòng ban (SRS §2.2)
    "document_types": ["procedure"],        // Lọc theo loại tài liệu (SRS §3.1)
    "date_range": null                      // Optional
  },
  "top_k": 10,                             // Số kết quả search (SRS §3.4)
  "stream": true                            // Streaming response (SRS §8.1: <60s)
}

Response (streaming):                       // Server-Sent Events
data: {"type": "token", "content": "Theo"}
data: {"type": "token", "content": " Quy"}
data: {"type": "token", "content": " trình"}
...
data: {"type": "citations", "content": [
  {
    "document_id": "uuid",
    "title": "QT-MH-001 Quy trình Mua hàng",
    "page": 3,
    "section": "Mục 2.1",
    "excerpt": "Bước 1: Lập phiếu đề xuất...",
    "similarity_score": 0.92
  }
]}
data: {"type": "metadata", "content": {
  "processing_time_ms": 3500,
  "search_method": "hybrid",
  "chunks_retrieved": 10,
  "chunks_after_filter": 7
}}
data: {"type": "done"}
```

### 3.5. Bước 4: Vẽ Architecture Diagram

**Tổng hợp tất cả quyết định thành 1 sơ đồ:**

```mermaid
graph TB
    subgraph "🖥️ Client Layer"
        WebUI["🌐 Chat UI<br/>(Streamlit → NextJS 18)"]
        AdminUI["⚙️ Admin Panel<br/>(Streamlit)"]
    end

    subgraph "⚙️ API Layer (FastAPI)"
        Gateway["🔀 API Gateway<br/>Rate Limiting<br/>JWT Validation"]
        QueryAPI["📝 /api/v1/query<br/>Xử lý câu hỏi"]
        IngestAPI["📥 /api/v1/ingest<br/>Upload tài liệu"]
        AuthAPI["🔐 /api/v1/auth<br/>Đăng nhập/Đăng ký"]
        AnalyticsAPI["📊 /api/v1/analytics<br/>Báo cáo"]
    end

    subgraph "🤖 RAG Engine"
        QueryProc["🔍 Query Processor<br/>- Vietnamese NLP<br/>- Entity extraction<br/>- Intent classify"]
        Retrieval["📚 Retrieval Engine<br/>- Vector search<br/>- BM25 keyword<br/>- Hybrid scoring"]
        Synthesis["📋 Synthesis<br/>- Context assembly<br/>- Prompt template<br/>- Token management"]
        Generation["✨ Generation<br/>- LLM call<br/>- Citation extract<br/>- Fallback logic"]
    end

    subgraph "💾 Data Layer"
        PG["🐘 PostgreSQL 15<br/>- Metadata<br/>- Users & RBAC<br/>- Chat history<br/>- Analytics<br/>- BM25 search"]
        Chroma["🧬 ChromaDB 1.0.0<br/>- Vector embeddings<br/>- Similarity search"]
        Redis["⚡ Redis 7<br/>- Session cache<br/>- Query cache<br/>- Rate limiting"]
    end

    subgraph "🧠 AI Models (GPU Server)"
        Embed["📐 Qwen3-Embedding-0.6B<br/>1024 dimensions<br/>~2.2 GB VRAM"]
    end

    subgraph "📈 Monitoring"
        Prometheus["📊 Prometheus"]
        Grafana["📈 Grafana"]
    end

    WebUI --> Gateway
    AdminUI --> Gateway
    Gateway --> QueryAPI
    Gateway --> IngestAPI
    Gateway --> AuthAPI
    Gateway --> AnalyticsAPI

    QueryAPI --> QueryProc --> Retrieval
    Retrieval --> Chroma
    Retrieval --> PG
    Retrieval --> Synthesis --> Generation

    IngestAPI --> Embed
    Embed --> Chroma

    AuthAPI --> PG
    AnalyticsAPI --> PG
    QueryAPI --> Redis
    Generation --> Redis

    Gateway --> Prometheus --> Grafana
```

### 3.6. Sản phẩm Bàn giao Giai đoạn 2

| # | Tài liệu | Mô tả |
|---|---|---|
| 1 | **Architecture Diagram** | Sơ đồ kiến trúc tổng thể |
| 2 | **Technology Decision Record** | Bảng giải thích lý do chọn từng công nghệ |
| 3 | **ERD (Entity Relationship Diagram)** | Schema database đầy đủ |
| 4 | **SQL Migration Scripts** | File `.sql` tạo tất cả bảng |
| 5 | **API Specification** | OpenAPI/Swagger cho tất cả endpoints |
| 6 | **Network Diagram** | Sơ đồ server, port, firewall |

### 3.7. Checklist GĐ2: PASS/FAIL trước khi sang GĐ3

- [ ] Mỗi quyết định công nghệ có lý do từ SRS
- [ ] ERD cover tất cả Use Case đã thiết kế ở GĐ1
- [ ] API endpoints cover tất cả Use Case
- [ ] Architecture diagram được review bởi team lead
- [ ] SQL scripts chạy được, tạo đủ bảng
- [ ] Không có "over-engineering" (không chọn công nghệ vượt nhu cầu)

---

## 4. GIAI ĐOẠN 3: XỬ LÝ DỮ LIỆU (DATA INGESTION PIPELINE)

### 4.1. Tại sao Giai đoạn này Quan trọng nhất?

> **"Dữ liệu đầu vào rác → AI trả ra rác" (Garbage in, Garbage out)**

Theo Gemini và kinh nghiệm thực tế: **Giai đoạn xử lý dữ liệu chiếm 70% sự thành công** của chatbot RAG. Không có dữ liệu tốt thì dù kiến trúc hoàn hảo cũng vô nghĩa.

### 4.2. Luồng Xử lý Dữ liệu

```mermaid
graph TD
    subgraph "📁 ĐẦU VÀO: Tài liệu Gốc"
        PDF["📄 PDF<br/>(Nghị định, Thông tư)"]
        DOCX["📝 Docx<br/>(Quy trình nội bộ)"]
        JSONL["📋 JSONL<br/>(Dữ liệu có cấu trúc)"]
    end

    subgraph "Bước 1: TRÍCH XUẤT (Extract)"
        OCR["🔍 OCR<br/>(nếu PDF dạng ảnh)"]
        TextExtract["📝 Text Extraction<br/>(nếu PDF/Docx có text)"]
        Parse["📊 Parse JSONL"]
    end

    subgraph "Bước 2: LÀM SẠCH (Clean)"
        Unicode["🔤 Chuẩn hóa Unicode<br/>(NFC normalization)"]
        Diacritics["🇻🇳 Xử lý dấu tiếng Việt<br/>(hòa vs hoà)"]
        Legal["⚖️ Bảo toàn mã pháp luật<br/>(Điều 15, Khoản 3)"]
        Dedup["🔄 Loại bỏ trùng lặp"]
    end

    subgraph "Bước 3: CHIA NHỎ (Chunk)"
        Chunk["✂️ Chunking<br/>500-1000 tokens<br/>Overlap 100 tokens"]
        Boundary["📏 Tôn trọng ranh giới<br/>Điều/Khoản/Mục"]
        Metadata["🏷️ Gắn Metadata<br/>document_id, chunk_index<br/>page, section"]
    end

    subgraph "Bước 4: VECTOR HÓA (Embed)"
        Embed["🧬 Qwen3-Embedding<br/>Text → Vector 1024-dim"]
        QualCheck["✅ Kiểm tra chất lượng<br/>- Vector không null<br/>- Dimension = 1024"]
    end

    subgraph "Bước 5: LƯU TRỮ (Index)"
        ChromaStore["🧬 ChromaDB<br/>Lưu vector + metadata"]
        PGStore["🐘 PostgreSQL<br/>Lưu metadata + text"]
    end

    PDF --> OCR --> Unicode
    PDF --> TextExtract --> Unicode
    DOCX --> TextExtract
    JSONL --> Parse --> Unicode

    Unicode --> Diacritics --> Legal --> Dedup
    Dedup --> Chunk --> Boundary --> Metadata
    Metadata --> Embed --> QualCheck
    QualCheck --> ChromaStore
    QualCheck --> PGStore

    style Chunk fill:#FFF3E0,stroke:#E65100,stroke-width:2px
    style Legal fill:#FCE4EC,stroke:#C62828,stroke-width:2px
```

### 4.3. Chi tiết Từng Bước

#### Bước 1: Trích xuất (Extract)

| Loại file | Công cụ | Xử lý đặc biệt |
|---|---|---|
| PDF (có text) | `PyMuPDF` / `pdfplumber` | Giữ nguyên bảng biểu, header/footer |
| PDF (dạng ảnh) | `Marker` / `Tesseract OCR` | Cần OCR trước, chất lượng phụ thuộc scan |
| Docx | `python-docx` | Giữ nguyên format heading, list |
| JSONL | `json.loads()` | Mỗi dòng = 1 document, validate schema |

#### Bước 2: Làm sạch (Clean) — ĐẶC BIỆT QUAN TRỌNG CHO TIẾNG VIỆT

| Xử lý | Ví dụ | Tại sao quan trọng |
|---|---|---|
| **Unicode NFC** | `"hoà"` (2 ký tự) → `"hòa"` (1 ký tự) | Tìm kiếm nhất quán, tránh miss kết quả |
| **Dấu tiếng Việt** | `"Điều 15"` phải giữ nguyên, không bị lỗi encoding | Mất dấu → mất nghĩa: "điều" ≠ "dieu" |
| **Mã pháp luật** | `"NĐ-01/2024/NĐ-CP"` phải giữ nguyên chuỗi | BM25 search dựa trên exact match mã này |
| **Loại bỏ noise** | Header/footer lặp lại, watermark, page number | Giảm noise trong chunks |

#### Bước 3: Chunking — "Nghệ thuật" chia tài liệu

```mermaid
graph TD
    subgraph "❌ Chunking SAI"
        Bad1["Chunk 1: ...Điều 15. Quyền và<br/>nghĩa vụ của..."]
        Bad2["Chunk 2: ...người lao động<br/>trong trường hợp..."]
        Note1["⚠️ Cắt giữa 1 Điều<br/>→ Mất ngữ cảnh!"]
    end

    subgraph "✅ Chunking ĐÚNG"
        Good1["Chunk 1:<br/>Điều 14. Trách nhiệm...<br/>(toàn bộ Điều 14)"]
        Good2["Chunk 2:<br/>Điều 15. Quyền và nghĩa vụ<br/>của người lao động<br/>trong trường hợp...<br/>(toàn bộ Điều 15)"]
        Note2["✅ Mỗi chunk = 1 đơn vị<br/>logic hoàn chỉnh"]
    end

    style Bad1 fill:#FFCDD2,stroke:#C62828
    style Bad2 fill:#FFCDD2,stroke:#C62828
    style Good1 fill:#C8E6C9,stroke:#2E7D32
    style Good2 fill:#C8E6C9,stroke:#2E7D32
```

**Nguyên tắc Chunking cho tài liệu pháp luật Việt Nam:**

| Nguyên tắc | Chi tiết | SRS liên quan |
|---|---|---|
| **Tôn trọng cấu trúc Điều/Khoản** | Không cắt giữa 1 Điều — mỗi chunk ít nhất chứa 1 Điều hoàn chỉnh | §3.3: Chunking 500-1000 tokens |
| **Overlap (chồng lấp)** | 100-150 tokens overlap giữa 2 chunks liền kề → giữ ngữ cảnh chuyển tiếp | §3.4: Semantic search ≥ 80% |
| **Metadata phong phú** | Mỗi chunk gắn: document_id, chunk_index, page, section, Điều/Khoản number | §3.1: Metadata bắt buộc |
| **Kích thước phù hợp** | 500-1000 tokens (tiếng Việt ~300-600 từ) — quá ngắn mất context, quá dài loãng | §3.3: Size configurable |

#### Bước 4 & 5: Embedding & Indexing

| Hành động | Chi tiết | Kiểm tra chất lượng |
|---|---|---|
| Tạo embedding | `model.encode(chunk_text)` → vector 1024-dim | Vector không null, dim = 1024 |
| Lưu ChromaDB | `collection.add(ids, embeddings, metadatas, documents)` | Verify count tăng đúng |
| Lưu PostgreSQL | `INSERT INTO document_chunks (...)` | Verify FK constraint, text không rỗng |
| Verify search | Query test: "quy trình mua hàng" → phải trả về chunks liên quan | Similarity score > 0.5 |

### 4.4. Sản phẩm Bàn giao Giai đoạn 3

| # | Sản phẩm | Mô tả |
|---|---|---|
| 1 | **ETL Pipeline Script** | Script Python chạy end-to-end: extract → clean → chunk → embed → index |
| 2 | **Vector Database có dữ liệu** | ChromaDB collection `knowledge_base` với tất cả tài liệu đã xử lý |
| 3 | **PostgreSQL có metadata** | Bảng `documents_metadata` + `document_chunks` đã có dữ liệu |
| 4 | **Báo cáo chất lượng dữ liệu** | Số lượng tài liệu, chunks, avg token/chunk, duplicate rate |
| 5 | **Test search cơ bản** | 20 câu query test → verify kết quả search hợp lý |

### 4.5. Checklist GĐ3: PASS/FAIL

- [ ] Tất cả tài liệu đã được ingest (0 file bị bỏ sót)
- [ ] Chunks không bị cắt giữa Điều/Khoản
- [ ] Unicode đã chuẩn hóa NFC
- [ ] Mã pháp luật (NĐ-xx, TT-xx) được bảo toàn nguyên vẹn
- [ ] Test search 20 câu query → ≥ 16/20 trả về kết quả phù hợp (80%)
- [ ] Không có chunks trống hoặc quá ngắn (< 50 tokens)

---

## 5. GIAI ĐOẠN 4: CODING & PHÁT TRIỂN (IMPLEMENTATION)

### 5.1. Từ Thiết kế → Code: Cấu trúc Thư mục

**Cấu trúc thư mục phản ánh kiến trúc đã thiết kế ở GĐ2:**

```
attech-rag/
├── src/
│   ├── api/                          ← GĐ2: API Layer
│   │   ├── main.py                   # FastAPI app entry point
│   │   ├── routes/
│   │   │   ├── query.py              # POST /api/v1/query      ← UC-001,002
│   │   │   ├── ingest.py             # POST /api/v1/ingest     ← UC-004
│   │   │   ├── auth.py               # POST /api/v1/auth/*     ← Đăng nhập
│   │   │   ├── sessions.py           # GET /api/v1/sessions    ← UC-003
│   │   │   └── analytics.py          # GET /api/v1/analytics   ← UC-006
│   │   └── middleware/
│   │       ├── auth_middleware.py     # JWT validation          ← SRS §7
│   │       └── rate_limiter.py       # Rate limiting           ← SRS §8.1
│   │
│   ├── core/                          ← GĐ2: RAG Engine
│   │   ├── retrieval/
│   │   │   ├── vector_search.py      # ChromaDB search         ← SRS §3.4
│   │   │   ├── keyword_search.py     # BM25/PostgreSQL FTS     ← SRS §3.4
│   │   │   └── hybrid_ranker.py      # 0.7×sem + 0.3×kw       ← SRS §3.4
│   │   ├── synthesis/
│   │   │   ├── context_builder.py    # Xây context từ chunks   ← SRS §3.4
│   │   │   ├── prompt_template.py    # System + User prompt    ← SRS §3.4
│   │   │   └── fallback.py           # Xử lý "không biết"     ← GĐ1: Fallback
│   │   └── generation/
│   │       ├── llm_client.py         # Gọi LLM API            ← SRS §3.4
│   │       ├── citation_extractor.py # Trích citations         ← GĐ1: Citations
│   │       └── streaming.py          # SSE streaming           ← SRS §8.1
│   │
│   ├── data/                          ← GĐ3: Data Pipeline
│   │   ├── extractors/
│   │   │   ├── pdf_extractor.py      # PyMuPDF                 ← GĐ3 Bước 1
│   │   │   ├── docx_extractor.py     # python-docx             ← GĐ3 Bước 1
│   │   │   └── jsonl_parser.py       # JSON Lines              ← GĐ3 Bước 1
│   │   ├── processors/
│   │   │   ├── vietnamese_nlp.py     # NLP tiếng Việt          ← GĐ3 Bước 2
│   │   │   ├── chunker.py           # Chunking logic           ← GĐ3 Bước 3
│   │   │   └── metadata_tagger.py    # Gắn metadata            ← GĐ3 Bước 3
│   │   └── embeddings/
│   │       └── embedding_service.py  # Qwen3 embedding         ← GĐ3 Bước 4
│   │
│   ├── auth/                          ← SRS §7: Bảo mật
│   │   ├── jwt_handler.py            # Tạo/verify JWT
│   │   ├── rbac.py                   # Role-Based Access Control
│   │   └── permission_filter.py      # Lọc documents theo quyền
│   │
│   └── models/                        ← GĐ2: Database Schema
│       ├── user.py                   # Pydantic model: User
│       ├── document.py               # Pydantic model: Document
│       └── chat.py                   # Pydantic model: Session, Message
│
├── tests/                             ← GĐ5: Testing
│   ├── unit/
│   ├── integration/
│   └── data/
│       └── ground_truth_100.json     # 100 cặp query-answer
│
├── docker-compose.yml                 ← GĐ6: Deployment
├── Dockerfile
└── requirements.txt
```

### 5.2. Trình tự Code — Code Cái gì Trước?

```mermaid
graph TD
    subgraph "Sprint 1: Nền tảng (Tuần 1-2)"
        S1A["1. Database migrations<br/>Tạo bảng PostgreSQL"]
        S1B["2. Auth service<br/>JWT + RBAC"]
        S1C["3. Health check API"]
    end

    subgraph "Sprint 2: Data Pipeline (Tuần 3-4)"
        S2A["4. Extractors<br/>(PDF, Docx, JSONL)"]
        S2B["5. Vietnamese NLP<br/>(Unicode, dấu)"]
        S2C["6. Chunker + Embedder"]
        S2D["7. ChromaDB indexing"]
    end

    subgraph "Sprint 3: RAG Core (Tuần 5-6)"
        S3A["8. Vector search"]
        S3B["9. BM25 keyword search"]
        S3C["10. Hybrid ranker"]
        S3D["11. Prompt template<br/>+ LLM call"]
        S3E["12. Citation extractor"]
        S3F["13. Fallback logic"]
    end

    subgraph "Sprint 4: API + UI (Tuần 7-8)"
        S4A["14. Query API endpoint<br/>(streaming)"]
        S4B["15. Ingest API endpoint"]
        S4C["16. Chat UI<br/>(Streamlit)"]
        S4D["17. Admin panel"]
    end

    S1A --> S1B --> S1C
    S1C --> S2A --> S2B --> S2C --> S2D
    S2D --> S3A --> S3B --> S3C --> S3D --> S3E --> S3F
    S3F --> S4A --> S4B --> S4C --> S4D

    style S3A fill:#FCE4EC,stroke:#C62828,stroke-width:2px
    style S3D fill:#FCE4EC,stroke:#C62828,stroke-width:2px
```

**Nguyên tắc "RAG Core First":**

> Code RAG Engine (search + generate) TRƯỚC → validate chất lượng → SAU ĐÓ mới code UI

Lý do: Nếu RAG Engine trả lời sai → UI đẹp cũng vô nghĩa. Phải đảm bảo core hoạt động trước.

### 5.3. Ví dụ Code — Luồng chính (Happy Path)

**File `src/core/retrieval/hybrid_ranker.py`:**

```python
# Truy vết: SRS §3.4 (Hybrid search)
#           UC-002 (Đặt câu hỏi theo quyền)

class HybridRanker:
    """
    Kết hợp vector similarity + BM25 keyword search
    Công thức: final_score = α × semantic_score + β × keyword_score
    Với: α = 0.7 (SRS §3.4), β = 0.3
    """
    
    def __init__(self, alpha: float = 0.7, beta: float = 0.3):
        self.alpha = alpha  # Trọng số semantic
        self.beta = beta    # Trọng số keyword
    
    async def search(
        self,
        query: str,
        user_level: str,       # Từ JWT token → SRS §2.2
        department: str,       # Từ JWT token → SRS §2.2
        top_k: int = 10        # SRS §3.4: default = 5-10
    ) -> list[SearchResult]:
        
        # Bước 1: Vector search (ChromaDB)
        # → SRS §3.4: "Semantic search với độ chính xác ≥80%"
        vector_results = await self.vector_search.search(query, top_k=50)
        
        # Bước 2: Keyword search (PostgreSQL BM25)  
        # → SRS §3.4: "Hybrid search (kết hợp semantic và keyword)"
        keyword_results = await self.keyword_search.search(query, top_k=50)
        
        # Bước 3: Lọc theo quyền
        # → SRS §2.2: "Filtering theo access level của user"
        filtered = self._filter_by_permission(
            results=vector_results + keyword_results,
            user_level=user_level,
            department=department
        )
        
        # Bước 4: Hybrid scoring
        scored = self._merge_and_score(filtered)
        
        return scored[:top_k]
    
    def _filter_by_permission(self, results, user_level, department):
        """
        Truy vết: SRS §2.2 — Phân quyền
        Guest → chỉ public
        Employee → public + employee_only
        Manager → public + employee + manager_only  
        Director → tất cả
        """
        level_hierarchy = {
            "guest": ["public"],
            "employee": ["public", "employee_only"],
            "manager": ["public", "employee_only", "manager_only"],
            "director": ["public", "employee_only", "manager_only", "director_only"]
        }
        allowed = level_hierarchy.get(user_level, ["public"])
        return [r for r in results if r.access_level in allowed]
```

**File `src/core/synthesis/fallback.py`:**

```python
# Truy vết: GĐ1 Thiết kế UX — Fallback
#           SRS §8.1: "Hệ thống trả lời chính xác ≥80%"
#           → 20% không biết → PHẢI thú nhận

class FallbackHandler:
    """
    Khi similarity score quá thấp hoặc không tìm thấy documents
    → Trả lời "Tôi không biết" thay vì bịa (Hallucination)
    """
    
    SIMILARITY_THRESHOLD = 0.50  # Dưới ngưỡng → kích hoạt fallback
    
    def should_fallback(self, search_results: list) -> bool:
        if not search_results:
            return True
        max_score = max(r.similarity_score for r in search_results)
        return max_score < self.SIMILARITY_THRESHOLD
    
    def generate_fallback_response(self, query: str) -> dict:
        return {
            "answer": (
                "Xin lỗi, tôi không tìm thấy thông tin về vấn đề này "
                "trong tài liệu nội bộ ATTECH. Bạn có thể:\n"
                "1. Thử diễn đạt câu hỏi khác\n"
                "2. Liên hệ phòng ban liên quan để được hỗ trợ trực tiếp"
            ),
            "citations": [],
            "is_fallback": True,
            "confidence": 0.0
        }
```

### 5.4. Sản phẩm Bàn giao Giai đoạn 4

| # | Sản phẩm | Mô tả |
|---|---|---|
| 1 | **Source code hoàn chỉnh** | Repository với cấu trúc thư mục rõ ràng |
| 2 | **README.md** | Hướng dẫn setup, run, deploy |
| 3 | **requirements.txt** | Danh sách dependencies với version cố định |
| 4 | **Dockerfile + docker-compose.yml** | Containerization |
| 5 | **API Documentation** | Auto-generated từ FastAPI (Swagger/ReDoc) |

### 5.5. Checklist GĐ4: PASS/FAIL

- [ ] Mỗi file code có comment truy vết về SRS/UC
- [ ] Code chạy được trên Docker (docker-compose up)
- [ ] API endpoint `/api/v1/query` trả về kết quả hợp lý cho 5 câu hỏi test
- [ ] Fallback kích hoạt đúng khi hỏi câu ngoài phạm vi
- [ ] Citations hiển thị đúng (document_id, page, section)
- [ ] RBAC hoạt động: Guest không thấy tài liệu employee_only

---

## 6. GIAI ĐOẠN 5: KIỂM THỬ & ĐÁNH GIÁ (TESTING & EVALUATION)

### 6.1. Tại sao AI cần Kiểm thử Khác biệt?

> **"Với phần mềm truyền thống, kết quả đúng/sai rõ ràng. Với AI, câu trả lời có thể 'gần đúng' nhưng sai bản chất — cần đánh giá chất lượng riêng."**

```mermaid
graph LR
    subgraph "Phần mềm Truyền thống"
        T1["Input: 2+2"] --> T2["Expected: 4"]
        T2 --> T3["✅ PASS hoặc ❌ FAIL<br/>Rõ ràng 100%"]
    end

    subgraph "Hệ thống AI/RAG"
        A1["Input: 'Quy trình mua hàng?'"]
        A2["Output: Câu trả lời dài 200 từ"]
        A3["❓ Đúng bao nhiêu %?<br/>Có bịa không?<br/>Có trích dẫn đúng không?"]
    end

    style T3 fill:#C8E6C9
    style A3 fill:#FFF3E0,stroke:#E65100,stroke-width:2px
```

### 6.2. 4 Tầng Kiểm thử

```mermaid
graph TD
    subgraph "Tầng 1: Unit Test (Code đúng)"
        UT1["Test từng function<br/>riêng lẻ"]
        UT2["Ví dụ: test_chunker()<br/>test_permission_filter()"]
    end

    subgraph "Tầng 2: Integration Test (Hệ thống hoạt động)"
        IT1["Test end-to-end<br/>API → RAG → Response"]
        IT2["Ví dụ: POST /api/v1/query<br/>→ verify response format"]
    end

    subgraph "Tầng 3: RAG Evaluation (AI trả lời đúng)"
        RE1["RAGAS Framework"]
        RE2["Faithfulness: Có bịa không?"]
        RE3["Relevancy: Đúng trọng tâm?"]
        RE4["Precision: Context đúng?"]
    end

    subgraph "Tầng 4: Load Test (Chịu tải)"
        LT1["100 concurrent users"]
        LT2["Response time < 60s"]
        LT3["Error rate < 1%"]
    end

    UT1 --> IT1 --> RE1 --> LT1

    style RE1 fill:#FCE4EC,stroke:#C62828,stroke-width:2px
```

### 6.3. Tầng 3 Chi tiết: RAG Evaluation với RAGAS

**Đây là phần Gemini nói "Với AI, Unit Test là chưa đủ" — cần framework đánh giá chuyên biệt.**

#### Bước 1: Chuẩn bị Ground Truth Dataset

**Ground Truth là gì?** Là bộ câu hỏi + câu trả lời đúng do CON NGƯỜI tạo ra — làm chuẩn để so sánh với câu trả lời của AI.

| # | Câu hỏi (Question) | Câu trả lời đúng (Ground Truth) | Tài liệu nguồn (Context) |
|---|---|---|---|
| 1 | Quy trình mua hàng gồm mấy bước? | 5 bước: (1) Lập phiếu đề xuất, (2) Trưởng phòng duyệt, (3) Phòng mua hàng báo giá, (4) GĐ phê duyệt, (5) Thực hiện mua | QT-MH-001, trang 3-5 |
| 2 | Ai ký duyệt nghỉ phép trên 3 ngày? | Giám đốc | QĐ-NS-002, Điều 15, Khoản 3 |
| ... | ... | ... | ... |
| 100 | ... | ... | ... |

> **SRS §8.1 yêu cầu:** Test dataset ≥ 100 cặp query-answer

#### Bước 2: Chạy RAGAS Evaluation

```mermaid
graph TD
    GT["📋 Ground Truth<br/>100 cặp Q&A"] --> Pipeline
    
    subgraph Pipeline["🔄 RAGAS Pipeline"]
        Step1["1. Gửi câu hỏi vào RAG"]
        Step2["2. Thu câu trả lời + context"]
        Step3["3. So sánh với Ground Truth"]
        Step4["4. Tính điểm 4 metrics"]
    end

    Pipeline --> Results

    subgraph Results["📊 Kết quả"]
        M1["Faithfulness ≥ 85%<br/>(Bot có bịa không?)"]
        M2["Answer Relevancy ≥ 85%<br/>(Trả lời đúng trọng tâm?)"]
        M3["Context Precision ≥ 80%<br/>(Search đúng tài liệu?)"]
        M4["Context Recall ≥ 80%<br/>(Tìm đủ thông tin?)"]
    end

    style GT fill:#E3F2FD,stroke:#1565C0
    style M1 fill:#C8E6C9,stroke:#2E7D32
```

**4 Metrics RAGAS giải thích bằng tiếng Việt:**

| Metric | Ý nghĩa | Ví dụ FAIL | Target (SRS §8.1) |
|---|---|---|---|
| **Faithfulness** (Trung thành) | Câu trả lời có ĐÚNG với tài liệu gốc không? Có bịa thêm không? | Bot nói "mua hàng cần 7 bước" nhưng tài liệu ghi 5 bước | ≥ 85% |
| **Answer Relevancy** (Liên quan) | Câu trả lời có ĐÚNG TRỌNG TÂM câu hỏi không? | Hỏi "quy trình mua hàng" nhưng bot trả lời về "quy trình nghỉ phép" | ≥ 85% |
| **Context Precision** (Chính xác context) | Hệ thống có tìm ĐÚNG tài liệu liên quan không? | Hỏi về mua hàng nhưng search trả về tài liệu nhân sự | ≥ 80% |
| **Context Recall** (Đầy đủ context) | Hệ thống có tìm ĐỦ thông tin cần thiết không? | Bot chỉ tìm được 2/5 bước trong quy trình | ≥ 80% |

### 6.4. Tầng 4: Load Testing

| Test | Mô tả | Công cụ | Target (SRS §8.1) |
|---|---|---|---|
| **Load Test** | 100 users gửi query đồng thời | Locust / k6 | Response < 60s (p95) |
| **Stress Test** | 200 users (gấp đôi target) | Locust / k6 | Không crash, graceful degrade |
| **Spike Test** | 0 → 100 users trong 10 giây | Locust / k6 | Recovery < 30s |
| **Security Test** | SQL injection, JWT tampering | OWASP ZAP | 0 high/critical vulnerabilities |

### 6.5. Sản phẩm Bàn giao Giai đoạn 5

| # | Sản phẩm | Mô tả |
|---|---|---|
| 1 | **Ground Truth Dataset** | 100 cặp query-answer, đã validate bởi domain expert |
| 2 | **RAGAS Evaluation Report** | Scores cho 4 metrics, so với target SRS §8.1 |
| 3 | **Unit Test Suite** | ≥ 80% code coverage |
| 4 | **Integration Test Report** | Tất cả API endpoints PASS |
| 5 | **Load Test Report** | Performance dưới 100 concurrent users |
| 6 | **Security Scan Report** | OWASP ZAP scan results |

### 6.6. Checklist GĐ5: PASS/FAIL — Gate cuối trước Production

- [ ] RAGAS Faithfulness ≥ 85%
- [ ] RAGAS Answer Relevancy ≥ 85%
- [ ] Unit test coverage ≥ 80%
- [ ] Load test: 100 users, response < 60s (p95)
- [ ] Security: 0 high/critical vulnerabilities
- [ ] RBAC test: Guest KHÔNG thấy tài liệu restricted (100% pass)
- [ ] Fallback test: 10 câu hỏi ngoài phạm vi → 10/10 trả lời fallback

---

## 7. GIAI ĐOẠN 6: TRIỂN KHAI & VẬN HÀNH (PRODUCTION & DEVOPS)

### 7.1. Từ Code → Production

```mermaid
graph TD
    subgraph "Bước 1: Containerization"
        D1["🐳 Dockerfile cho mỗi service"]
        D2["📦 docker-compose.yml<br/>Orchestrate tất cả containers"]
    end

    subgraph "Bước 2: Triển khai"
        D3["🖥️ Server .70 (Debian)<br/>PostgreSQL, ChromaDB, Redis<br/>FastAPI, Streamlit<br/>Prometheus, Grafana"]
        D4["🖥️ Server .88 (DietPi/GPU)<br/>Embedding Model<br/>Data Pipeline"]
    end

    subgraph "Bước 3: Monitoring"
        D5["📊 Prometheus<br/>Thu thập metrics"]
        D6["📈 Grafana Dashboards<br/>Hiển thị real-time"]
        D7["📝 Logging<br/>Lưu logs tập trung"]
    end

    subgraph "Bước 4: Vận hành"
        D8["🔄 Backup hàng ngày"]
        D9["🚨 Alert khi lỗi"]
        D10["📋 Runbook<br/>Hướng dẫn xử lý sự cố"]
    end

    D1 --> D2 --> D3
    D2 --> D4
    D3 --> D5 --> D6
    D3 --> D7
    D6 --> D8
    D6 --> D9
    D9 --> D10
```

### 7.2. Docker Compose — Cấu hình Production

```yaml
# docker-compose.yml
# Truy vết: SRS §8.1 (100 concurrent users, 99.5% uptime)
version: '3.8'

services:
  # === DATA LAYER ===
  postgres:           # SRS §3.2: Relational Database
    image: postgres:15
    ports: ["15432:5432"]
    environment:
      POSTGRES_DB: knowledge_base_v2
      POSTGRES_USER: kb_admin
    volumes:
      - pg_data:/var/lib/postgresql/data

  chromadb:           # SRS §3.2: Vector Database
    image: chromadb/chroma:1.0.0
    ports: ["8000:8000"]
    volumes:
      - chroma_data:/chroma/chroma

  redis:              # SRS §8.1: Cache cho performance
    image: redis:7
    ports: ["6379:6379"]

  # === APPLICATION LAYER ===
  fastapi:            # SRS §3.2: API Backend
    build: ./backend
    ports: ["8080:8000"]
    depends_on: [postgres, chromadb, redis]
    environment:
      DATABASE_URL: postgresql://kb_admin:***@postgres:5432/knowledge_base_v2
      CHROMA_HOST: chromadb
      REDIS_URL: redis://redis:6379

  streamlit:          # SRS §3.5: Chat UI
    build: ./frontend
    ports: ["8501:8501"]
    depends_on: [fastapi]

  # === MONITORING LAYER ===
  prometheus:         # SRS §8.1: Performance monitoring
    image: prom/prometheus
    ports: ["9090:9090"]

  grafana:            # SRS §8.1: Dashboard
    image: grafana/grafana
    ports: ["3000:3000"]
```

### 7.3. Monitoring — Theo dõi sau khi lên Production

**3 Dashboard Grafana:**

| Dashboard | Metrics | Alert khi | SRS |
|---|---|---|---|
| **System Health** | CPU, Memory, Disk, Network | CPU > 80%, Disk > 90% | §8.1: 99.5% uptime |
| **RAG Quality** | Response time, Accuracy, Fallback rate | Response > 60s (p95), Fallback > 20% | §8.1: <60s, ≥80% accuracy |
| **User Activity** | Queries/hour, Active users, Top questions | Queries drop > 50% (có thể hệ thống lỗi) | §8.1: User satisfaction |

**Log những gì:**

| Log | Mục đích | Dùng để |
|---|---|---|
| **Câu hỏi mà bot fallback** | Bot "không biết" trả lời | Bổ sung tài liệu vào hệ thống |
| **Câu hỏi có feedback tiêu cực** | User đánh giá "không hữu ích" | Cải thiện prompt / chunking |
| **API response time > 30s** | Chậm bất thường | Tối ưu query / thêm cache |
| **Permission denied events** | Ai đó cố truy cập tài liệu cấm | Kiểm tra bảo mật |

### 7.4. Sản phẩm Bàn giao Giai đoạn 6

| # | Sản phẩm | Mô tả |
|---|---|---|
| 1 | **docker-compose.yml** | File orchestration cho toàn bộ hệ thống |
| 2 | **Deployment Guide** | Hướng dẫn từng bước deploy lên server |
| 3 | **Grafana Dashboards** | 3 dashboard đã cấu hình sẵn |
| 4 | **Runbook** | Hướng dẫn xử lý sự cố cho từng tình huống |
| 5 | **Backup Script** | Script backup database hàng ngày |
| 6 | **User Manual** | Hướng dẫn sử dụng cho nhân viên |

### 7.5. Checklist GĐ6: PASS/FAIL — GO LIVE

- [ ] `docker-compose up` chạy thành công trên production server
- [ ] Tất cả health checks PASS (`/api/v1/health`)
- [ ] Grafana dashboards hiển thị đúng metrics
- [ ] Backup chạy đúng (test restore 1 lần)
- [ ] 20 users pilot test trong 1 tuần: satisfaction ≥ 4.0/5.0
- [ ] Runbook đã review bởi ops team
- [ ] SSL/HTTPS đã cấu hình

---

## 8. PHỤ LỤC: MA TRẬN TRUY VẾT YÊU CẦU

### 8.1. End-to-End Traceability Matrix

Bảng này cho thấy **từng yêu cầu SRS được hiện thực hóa qua TẤT CẢ giai đoạn như thế nào**:

| SRS Section | Yêu cầu | GĐ1: UX | GĐ2: Kiến trúc | GĐ3: Data | GĐ4: Code | GĐ5: Test | GĐ6: Deploy |
|---|---|---|---|---|---|---|---|
| §1.3 | NV cần kiểm chứng thông tin | Citations UI | API trả citations | Metadata có page/section | `citation_extractor.py` | Test citation accuracy | Log citation clicks |
| §2.2 | 4 loại người dùng | Use Case per role | `users` table, RBAC | — | `rbac.py`, `permission_filter.py` | RBAC test (0 leak) | Permission audit log |
| §3.2 | CSDL kép | — | PostgreSQL + ChromaDB | Dual indexing | DB client code | Integration test | docker-compose |
| §3.3 | Data pipeline | — | Pipeline architecture | **ETL Pipeline** | `extractors/`, `chunker.py` | Data quality report | Cron job ingestion |
| §3.4 | Hybrid search ≥80% | — | Hybrid architecture | Ground truth data | `hybrid_ranker.py` | **RAGAS ≥ 80%** | RAG Quality dashboard |
| §3.4 | Fallback | Fallback UI message | Fallback in API response | — | `fallback.py` | Fallback test 10/10 | Log unanswered queries |
| §7.1 | Bảo mật | — | On-premise, JWT | — | `auth_middleware.py` | Security scan | HTTPS, firewall |
| §8.1 | 100 concurrent users | — | Redis cache | — | Async FastAPI | **Load test 100 users** | Prometheus monitoring |
| §8.1 | Response < 60s | Streaming UI | Streaming API design | Optimized chunks | `streaming.py` | p95 < 60s verified | Alert if > 60s |
| §8.1 | User satisfaction ≥ 4.0 | Feedback buttons | Feedback API | — | Feedback collection | Pilot test 20 users | Feedback dashboard |

### 8.2. Tổng kết Sản phẩm Bàn giao Mỗi Giai đoạn

```mermaid
graph LR
    subgraph "GĐ1"
        G1["📋 Use Case Diagram<br/>📋 Sequence Diagrams<br/>🎨 Wireframes<br/>📊 Traceability Matrix"]
    end

    subgraph "GĐ2"
        G2["🏗️ Architecture Diagram<br/>📊 ERD + SQL Scripts<br/>📄 API Specification<br/>📋 Tech Decision Record"]
    end

    subgraph "GĐ3"
        G3["🔄 ETL Pipeline Script<br/>🧬 Vector DB có data<br/>🐘 PostgreSQL có metadata<br/>📊 Data Quality Report"]
    end

    subgraph "GĐ4"
        G4["💻 Source Code<br/>📄 README.md<br/>📦 Dockerfile<br/>📋 API Docs (Swagger)"]
    end

    subgraph "GĐ5"
        G5["📊 RAGAS Report<br/>🧪 Unit Test (≥80%)<br/>🔥 Load Test Report<br/>🔐 Security Scan"]
    end

    subgraph "GĐ6"
        G6["🐳 docker-compose.yml<br/>📈 Grafana Dashboards<br/>📋 Deployment Guide<br/>📖 User Manual<br/>🚨 Runbook"]
    end

    G1 --> G2 --> G3 --> G4 --> G5 --> G6
```

---

## TÓM TẮT — 1 TRANG

| Giai đoạn | Câu hỏi trả lời | Input | Output chính | Thời gian |
|---|---|---|---|---|
| **GĐ1: UX & Logic** | "User làm gì với hệ thống?" | Đặc tả SRS | Use Cases, Wireframes | 1-2 tuần |
| **GĐ2: Kiến trúc** | "Hệ thống cần gì để hoạt động?" | Use Cases | ERD, API Spec, Architecture | 1-2 tuần |
| **GĐ3: Dữ liệu** | "Dữ liệu xử lý thế nào?" | Tài liệu gốc (PDF/Docx) | Vector DB + PostgreSQL có data | 2-3 tuần |
| **GĐ4: Coding** | "Code chạy thế nào?" | Architecture + Data | Source code hoàn chỉnh | 3-4 tuần |
| **GĐ5: Kiểm thử** | "Hệ thống đạt yêu cầu chưa?" | Source code + Ground truth | RAGAS report, Load test | 1-2 tuần |
| **GĐ6: Production** | "Chạy ổn định ngoài thực tế?" | Tested code | Docker deployed, Monitoring | 1-2 tuần |

**Tổng: ~10-15 tuần** từ Đặc tả → Production

---

> **Nguyên tắc xuyên suốt:**  
> 1. **Truy vết (Traceability):** Mọi dòng code → Use Case → SRS  
> 2. **Checkpoint (Gate):** Mỗi giai đoạn có checklist PASS/FAIL trước khi tiến tiếp  
> 3. **RAG Core First:** Validate AI trả lời đúng TRƯỚC KHI làm đẹp UI  
> 4. **Garbage in, Garbage out:** 70% effort dành cho xử lý dữ liệu (GĐ3)  

