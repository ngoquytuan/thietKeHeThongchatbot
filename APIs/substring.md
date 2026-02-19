Dưới vai trò là Senior Technical Auditor, tôi đã phân tích tài liệu bàn giao hệ thống **Substring Search Engine** (phiên bản 2.1). Đây là một thành phần quan trọng trong kiến trúc RAG, đóng vai trò là công cụ tìm kiếm văn bản thuần túy (lexical search) để bổ trợ cho tìm kiếm ngữ nghĩa (semantic search).

Dưới đây là chi tiết về nguyên lý hoạt động và các ứng dụng thực tế của hệ thống này:

---

## 1. Nguyên lý hoạt động (How It Works)

Hệ thống hoạt động dựa trên việc truy vấn trực tiếp vào cơ sở dữ liệu PostgreSQL mà không cần qua các mô hình học máy hay embedding. Quy trình cụ thể gồm 5 bước chính:

### A. Lựa chọn và Mở rộng Trường Tìm kiếm

Người dùng có thể chỉ định tìm kiếm trên các trường cụ thể như `law_id`, `title`, `agency`, `law_type`, `tags`, hoặc `content`. Nếu người dùng chọn `ALL`, hệ thống sẽ tự động mở rộng truy vấn ra tất cả 6 trường metadata và nội dung.

### B. Xây dựng Câu lệnh SQL Động (Dynamic SQL)

Hệ thống sử dụng toán tử `ILIKE` để thực hiện tìm kiếm không phân biệt hoa thường và hỗ trợ tốt tiếng Việt có dấu.

* **Mẫu truy vấn:** `WHERE (field) ILIKE '%query%'`.
* Việc sử dụng ký tự `%` ở cả hai đầu cho phép tìm kiếm chuỗi con (substring) ở bất kỳ vị trí nào trong văn bản.

### C. Cơ chế Chấm điểm theo Trọng số (Scoring Mechanism)

Đây là điểm thông minh của hệ thống. Thay vì trả về kết quả thô, hệ thống sử dụng câu lệnh `CASE` trong SQL để gán điểm dựa trên mức độ quan trọng của trường khớp dữ liệu:

| Trường Tìm kiếm (Search Field) | Trọng số (Weight) | Ý nghĩa |
| --- | --- | --- |
| **law_id** | **1.0** | Ưu tiên cao nhất (khớp mã hiệu văn bản). |
| **title** | **0.9** | Khớp tiêu đề văn bản. |
| **agency** | **0.8** | Khớp cơ quan ban hành. |
| **law_type** | **0.7** | Khớp loại văn bản. |
| **tags** | **0.6** | Khớp các từ khóa. |
| **content** | **0.5** | Khớp trong nội dung (độ ưu tiên thấp nhất). |

### D. Thực thi và Tổng hợp

Hệ thống sử dụng `DISTINCT ON (document_id, chunk_id)` để đảm bảo không trả về kết quả trùng lặp, sau đó sắp xếp theo `substring_score` giảm dần và `chunk_position` tăng dần để giữ đúng thứ tự tài liệu.

---

## 2. Ứng dụng của Substring Search

Hệ thống này được thiết kế để giải quyết các bài toán mà tìm kiếm ngữ nghĩa (Vector Search) thường gặp khó khăn:

* **Tìm kiếm chính xác mã hiệu văn bản:** Ví dụ truy vấn `"265/2025/NĐ-CP"`. Đây là ứng dụng quan trọng nhất với độ chính xác tuyệt đối (Score 1.0).
* **Tìm kiếm theo thực thể cố định:** Tìm nhanh các văn bản theo **Cơ quan ban hành** (Bộ Tài chính, Chính phủ) hoặc **Loại văn bản** (Nghị quyết, Thông tư).
* **Xử lý các từ viết tắt/Mã code:** Các thuật ngữ chuyên ngành như `"KH&CN"` hoặc các mã kỹ thuật mà mô hình embedding có thể không hiểu rõ ngữ nghĩa.
* **Cơ chế dự phòng (Fallback Friendly):** Trong hệ thống Hybrid Search, Substring Search được dùng làm phương án dự phòng khi tìm kiếm ngữ nghĩa không trả về kết quả phù hợp cho các truy vấn mang tính từ khóa cứng.
* **Tìm kiếm chuỗi con một phần:** Tìm các cụm từ cụ thể trong nội dung văn bản mà không cần quan tâm đến ngữ cảnh rộng hơn.

---

## 3. Lưu ý từ góc độ Auditor

Qua tài liệu, tôi nhận thấy một vấn đề về dữ liệu cần lưu ý: Các thử nghiệm hiện tại thường trả về điểm **0.5 (Content)** thay vì **1.0 (Law ID)**.

> **Nguyên nhân:** Không phải lỗi code, mà do trường `metadata.law_id` trong database đang bị trống hoặc không chứa dữ liệu khớp chính xác, dẫn đến việc hệ thống phải "rơi" xuống mức ưu tiên thấp nhất là tìm trong nội dung.

Bạn có muốn tôi tiến hành kiểm tra sâu hơn vào cấu trúc SQL hoặc các kịch bản kiểm thử (Test Cases) để chuẩn bị cho giai đoạn Deep Validation tiếp theo không?
