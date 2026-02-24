Chào bạn, với tư cách là tư vấn viên kiến trúc hệ thống, tôi khẳng định **bạn hoàn toàn có thể và RẤT NÊN sử dụng Keycloak** cho hệ thống chatbot "Offline-First, Role-Aware" này.

Keycloak đặc biệt phù hợp với yêu cầu của bạn về một hệ thống hoạt động trong mạng LAN, bảo mật cao và phân quyền dựa trên vai trò (Role-Based Access Control - RBAC).

Dưới đây là phân tích chi tiết về chi phí, lợi ích và cách tích hợp vào kiến trúc hiện tại của bạn:

### 1. Đánh giá sự phù hợp & Chi phí

#### **Chi phí Tài chính (License)**
*   **Miễn phí (0đ):** Keycloak là phần mềm mã nguồn mở (Open Source - Apache License 2.0). Bạn không mất phí bản quyền, phù hợp với mục tiêu "tự triển khai" và "không dùng cloud" của bạn.

#### **Chi phí Tài nguyên (Phần cứng)**
Đây là điểm cần lưu ý vì bạn đang chạy local trên server 16GB RAM:
*   **RAM:** Keycloak chạy trên Java, nên khá ngốn RAM. Nó cần tối thiểu **512MB - 1GB RAM** để hoạt động ổn định.
*   **CPU:** Tiêu tốn ít CPU khi nhàn rỗi, nhưng sẽ tăng khi có nhiều người đăng nhập cùng lúc.
*   **Đánh giá:** Với server 16GB RAM, bạn phải chia sẻ tài nguyên giữa: *Ollama (LLM) + Vector DB + Backend API + Keycloak*. Nếu chạy model LLM lớn (ví dụ Llama 3 8B cần ~6-8GB VRAM/RAM), việc dành 1GB cho Keycloak là khả thi nhưng cần tinh chỉnh kỹ docker resource limits.

#### **Tại sao nên dùng Keycloak thay vì tự code Module Auth?**
Trong kế hoạch cũ, bạn định dành **2 tuần** để tự xây dựng module Authentication (Login/Register/JWT). Dùng Keycloak sẽ mang lại lợi ích lớn hơn:
1.  **Role-Aware chuẩn chỉnh:** Bạn cần chatbot trả lời theo vai trò (Kế toán, Kỹ thuật...). Keycloak quản lý Roles rất mạnh mẽ, bạn chỉ cần map User vào Role trong giao diện Admin thay vì code logic phức tạp.
2.  **Tích hợp LDAP/Active Directory:** Nếu công ty bạn đã có hệ thống AD (Windows), Keycloak có thể đồng bộ user từ AD về. Nhân viên dùng luôn pass công ty để chat, không cần tạo nick mới. Đây là tính năng "sát thủ" cho môi trường doanh nghiệp.
3.  **Bảo mật:** Tự code auth rất dễ dính lỗi bảo mật. Keycloak là chuẩn công nghiệp, hỗ trợ sẵn 2FA, Password Policy, Session Management.

---

### 2. Cách tích hợp vào Kiến trúc hiện tại

Chúng ta sẽ sửa đổi kiến trúc Docker Compose và API Gateway để nhúng Keycloak vào.

#### **Bước 1: Cập nhật Docker Compose**
Thêm service `keycloak` và một database riêng cho nó (hoặc dùng chung Postgres nhưng khác database name) vào file `docker-compose.yml`.

```yaml
services:
  # ... các service khác (ollama, vector-db ...)

  keycloak:
    image: quay.io/keycloak/keycloak:23.0.0
    command: start-dev # Dùng start-dev cho môi trường LAN/Dev
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://db:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: password
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin
    ports:
      - "8080:8080"
    depends_on:
      - db
    deploy:
      resources:
        limits:
          memory: 1024M # Giới hạn RAM để không ảnh hưởng Ollama
```

#### **Bước 2: Cấu hình Keycloak (Admin Panel)**
1.  Truy cập `http://localhost:8080`.
2.  Tạo **Realm** mới (ví dụ: `ChatbotInternal`).
3.  Tạo **Client** (ví dụ: `chatbot-app`) với giao thức OpenID Connect (OIDC).
4.  **Quan trọng:** Tạo **Roles** tương ứng với nghiệp vụ của bạn: `technician`, `accountant`, `general_staff`.
5.  Tạo Users và gán họ vào các Roles này.

#### **Bước 3: Tích hợp Backend (FastAPI - Module 5)**
Thay vì tự viết logic verify password, API Gateway sẽ chỉ kiểm tra **Access Token (JWT)** do Keycloak cấp.

*   **Thư viện:** Dùng `python-keycloak` hoặc `fastapi-keycloak`.
*   **Logic:**
    1.  Frontend gửi Request kèm Header: `Authorization: Bearer <token>`.
    2.  FastAPI middleware giải mã Token.
    3.  Đọc trường `resource_access` trong Token để lấy danh sách **Roles**.
    4.  Truyền `user_role` này vào **Module 4 (RAG Pipeline)** để lọc tài liệu.

#### **Bước 4: Tích hợp Frontend (React/Web UI - Module 6)**
*   Sử dụng thư viện OIDC client (như `react-oidc-context`).
*   Khi người dùng vào trang web, nếu chưa login, tự động chuyển hướng sang trang đăng nhập của Keycloak.
*   Sau khi login xong, Keycloak trả về Token chứa thông tin User và Roles.

---

### 3. Đánh giá rủi ro và Khuyến nghị

**Rủi ro:**
*   **Cấu hình phức tạp:** Keycloak có rất nhiều tính năng, dễ bị "ngợp" khi mới tiếp cận.
*   **Single Point of Failure:** Nếu container Keycloak chết, không ai đăng nhập được.

**Lời khuyên của tôi:**
1.  **Nên dùng Keycloak** nếu công ty bạn có trên 10 nhân viên hoặc đã có sẵn LDAP/AD. Nó giúp hệ thống chuyên nghiệp và dễ quản lý về sau.
2.  **Không dùng Keycloak** (giữ nguyên phương án tự code JWT đơn giản) nếu đây chỉ là dự án nhỏ, dưới 5 người dùng, server quá yếu (dưới 8GB RAM), hoặc team không ai rành về IAM.
3.  **Hành động tiếp theo:**
    *   Yêu cầu team DevOps thêm Keycloak vào `docker-compose.yml` ngay trong **Phase 1 (Foundation)**.
    *   Cập nhật **Module 5 (API Gateway)** trong tài liệu thiết kế để ghi rõ: "Authentication: Bearer Token validate via Keycloak Public Key" thay vì "LDAP integration manual".

Bạn có muốn tôi cung cấp cấu hình mẫu `docker-compose.yml` tích hợp sẵn Keycloak và PostgreSQL không?
