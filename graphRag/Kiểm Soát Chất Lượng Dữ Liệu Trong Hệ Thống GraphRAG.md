Đúng vậy, việc thiết lập các quy tắc kiểm tra (validation rules) ngay từ đầu sẽ giúp bạn "dễ thở" hơn rất nhiều trong quá trình triển khai GraphRAG. Thay vì phải rà soát thủ công hàng ngàn tài liệu, các quy tắc này sẽ đóng vai trò như một bộ lọc tự động để kiểm soát chất lượng dữ liệu.
Dưới đây là lý do tại sao các quy tắc này lại quan trọng và cách chúng hỗ trợ bạn:
1. Biến bảng graph_validation_log thành một "Danh sách việc cần làm"
Trong thực tế, hiện tại có tới 95% tài liệu của bạn có thể đang thiếu metadata đầy đủ,. Khi bạn thiết lập các quy tắc trong bảng graph_validation_rules, hệ thống sẽ tự động quét và ghi lại tất cả các lỗi vào bảng graph_validation_log,.
• Thay vì hoang mang không biết bắt đầu sửa từ đâu, bạn chỉ cần nhìn vào log để biết chính xác tài liệu nào đang thiếu rank_level hoặc tài liệu nào là văn bản cấp thấp (L5) mà chưa có tham chiếu đến văn bản nền tảng (L0),.
2. Đảm bảo tính nhất quán của "Phả hệ tài liệu"
Hệ thống của bạn dựa trên mô hình phân cấp từ L0 đến L5. Các quy tắc check metadata sẽ đảm bảo:
• Quy tắc tham chiếu ngược (Upward Reference): Đảm bảo văn bản cấp thấp phải căn cứ vào văn bản cấp cao hơn (ví dụ: Quyết định phải căn cứ vào Luật),.
• Phát hiện vòng lặp (No Cycles): Ngăn chặn lỗi logic khi Văn bản A căn cứ vào B, nhưng B lại căn cứ ngược lại vào A, điều này sẽ làm hỏng các truy vấn đệ quy (Recursive CTE) sau này,.
3. Hỗ trợ quá trình "Làm giàu dữ liệu" (Enrichment)
Khi bạn thực hiện Phase 2 (Enrichment) để bổ sung metadata cho 95% tài liệu còn thiếu, các rule này đóng vai trò là "người giám sát",:
• Nó giúp bạn biết script tự động trích xuất của bạn có hoạt động chính xác không.
• Nếu một tài liệu sau khi chạy script mà vẫn không thỏa mãn các quy tắc, nó sẽ bị "gắn cờ" để bạn xử lý thủ công hoặc điều chỉnh lại regex,.
4. Các quy tắc gợi ý bạn nên có sẵn
Dựa trên nguồn tài liệu, bạn nên triển khai ngay 3 quy tắc cốt lõi đã được thiết kế sẵn trong schema,:
• L5_MUST_REF_L01: Văn bản cụ thể cấp 5 bắt buộc phải tham chiếu đến ít nhất một văn bản nền tảng cấp 0 hoặc 1.
• NO_CYCLES: Tuyệt đối không để xảy ra quan hệ vòng tròn giữa các tài liệu.
• BASED_ON_UPWARD: Quan hệ "Căn cứ theo" (BASED_ON) phải luôn hướng lên cấp cao hơn trong hệ thống phân cấp.
Lời khuyên: Việc triển khai các quy tắc này giúp bạn chuyển từ thế "đi tìm lỗi" sang thế "xử lý lỗi đã được chỉ điểm". Nó giống như việc bạn có một người giám sát công trình đi kiểm tra từng viên gạch; bạn sẽ không bao giờ phải lo lắng về việc xây xong ngôi nhà mới phát hiện ra nền móng bị hổng,.

Để thực hiện bước **Validation** (Kiểm tra tính hợp lệ) sau khi bạn đã Hardlink thủ công, bạn cần triển khai một hệ thống kiểm soát bằng SQL. Mục tiêu là phát hiện sớm các lỗi logic đồ thị có thể gây treo hệ thống (như vòng lặp vô tận) hoặc sai lệch kiến thức.

Dưới đây là hướng dẫn chi tiết từng bước:

### Bước 1: Thiết lập các quy tắc kiểm tra (`graph_validation_rules`)

Trước tiên, bạn cần định nghĩa "thế nào là một liên kết sai" vào bảng `graph_validation_rules`. Mỗi rule sẽ là một logic SQL.

| Rule ID | Name | Description | Logic Kiểm tra |
| --- | --- | --- | --- |
| **R01** | Circular Reference | Phát hiện vòng lặp | A link tới B, B link ngược lại tới A. |
| **R02** | Hierarchy Violation | Vi phạm cấp bậc | Văn bản cấp cao (Level 0) không được "Căn cứ" vào cấp thấp (Level 3). |
| **R03** | Self-Reference | Tự tham chiếu | Một văn bản không thể tự làm "Căn cứ" cho chính nó. |

### Bước 2: Tạo Procedure thực thi Validation

Bạn nên tạo một Function/Procedure trong PostgreSQL để quét qua các `graph_edges` mới và đối chiếu với `graph_validation_rules`.

**Mẫu Code SQL để kiểm tra Vòng lặp (Circular Reference):**
Đây là lỗi nguy hiểm nhất vì nó khiến các truy vấn Recursive CTE (đệ quy) của GraphRAG bị chạy vô tận.

```sql
-- Ví dụ kiểm tra lỗi R01: Phát hiện vòng lặp trực tiếp (A <-> B)
INSERT INTO graph_validation_log (edge_id, rule_id, error_message, severity)
SELECT 
    e.edge_id, 
    'R01', 
    'Vòng lặp phát hiện: ' || e.source_graph_doc_id || ' trỏ ngược lại ' || e.target_graph_doc_id,
    'CRITICAL'
FROM graph_edges e
JOIN graph_edges e2 ON e.source_graph_doc_id = e2.target_graph_doc_id 
                   AND e.target_graph_doc_id = e2.source_graph_doc_id;

```

**Mẫu Code SQL kiểm tra vi phạm cấp bậc (Hierarchy Violation):**

```sql
-- Ví dụ kiểm tra lỗi R02: Cấp thấp không thể là cha của cấp cao
INSERT INTO graph_validation_log (edge_id, rule_id, error_message, severity)
SELECT 
    e.edge_id, 
    'R02', 
    'Vi phạm cấp bậc: Văn bản nguồn (Level ' || s.hierarchy_level || ') không thể dẫn chiếu tới văn bản đích có level thấp hơn (Level ' || t.hierarchy_level || ')',
    'WARNING'
FROM graph_edges e
JOIN graph_documents s ON e.source_graph_doc_id = s.graph_doc_id
JOIN graph_documents t ON e.target_graph_doc_id = t.graph_doc_id
WHERE s.hierarchy_level < t.hierarchy_level; 
-- (Giả định Level 0 là cao nhất, Level 3 là thấp nhất)

```

### Bước 3: Quy trình chạy thực tế khi Hardlink

Khi bạn thực hiện Hardlink thủ công, hãy tuân theo quy trình này:

1. **Chèn dữ liệu (Insert):** Thêm link vào `graph_edges`.
2. **Chạy Script Validation:** Thực thi lệnh gọi các hàm kiểm tra trên.
3. **Kiểm tra bảng `graph_validation_log`:**
* Nếu bảng **trống**: Các link bạn tạo đã an toàn.
* Nếu bảng **có dữ liệu**: Dựa vào `error_message` để biết link nào đang bị sai.


4. **Xử lý hậu kỳ:** * Xóa hoặc sửa các `edge_id` bị báo lỗi trong log.
* Đánh dấu `verified = true` trong bảng `graph_edges` cho các link đã vượt qua kiểm tra.



### Lưu ý quan trọng:

Để ngăn chặn lỗi ngay từ đầu (Proactive), bạn có thể cài đặt một **Trigger** trên bảng `graph_edges`. Mỗi khi bạn `INSERT` một link thủ công, Trigger sẽ tự động chạy các hàm Validation này. Nếu phát hiện vòng lặp, nó sẽ chặn lệnh `INSERT` và báo lỗi ngay lập tức, không cho phép dữ liệu sai lọt vào database.

Bạn có muốn tôi viết mẫu mã **Trigger** này để bảo vệ database của bạn không?

Việc bạn bị báo lỗi `ERROR: column "edge_id" of relation "graph_validation_log" does not exist` là do cấu trúc bảng trong database của bạn có thể đang đặt tên cột ID khác (thường là `id`, `log_id` hoặc bạn chưa tạo cột này).

Để test manual các rule này một cách an toàn mà không cần insert vào bảng log, bạn nên sử dụng câu lệnh `SELECT` để kiểm tra kết quả trả về trước.

Dưới đây là cách test manual từng rule và cách sửa lỗi SQL cho bạn:

---

### 1. Test Rule: Circular Reference (Vòng lặp)

Để sửa lỗi và test nhanh, hãy chạy lệnh `SELECT` này. Nó sẽ liệt kê ra các cặp tài liệu đang bị trỏ vòng quanh nhau:

```sql
-- Test xem có cặp nào A -> B và B -> A không
SELECT 
    e1.source_graph_doc_id AS doc_a,
    e1.target_graph_doc_id AS doc_b,
    'Circular Link' AS issue
FROM graph_edges e1
JOIN graph_edges e2 ON e1.source_graph_doc_id = e2.target_graph_doc_id 
                   AND e1.target_graph_doc_id = e2.source_graph_doc_id
WHERE e1.edge_id < e2.edge_id; -- Tránh hiện 1 cặp 2 lần (A-B và B-A)

```

* **Nếu kết quả trả về 0 dòng:** Chúc mừng, đồ thị của bạn chưa có vòng lặp trực tiếp.

### 2. Test Rule: Hierarchy Violation (Vi phạm cấp bậc)

Rule này kiểm tra xem có văn bản "cha" nào lại đi "căn cứ" vào văn bản "con" không (Ví dụ: Luật căn cứ vào Nghị định - điều này sai logic pháp lý).

```sql
SELECT 
    e.edge_id,
    s.law_id AS source_law, s.hierarchy_level AS source_lv,
    t.law_id AS target_law, t.hierarchy_level AS target_lv
FROM graph_edges e
JOIN graph_documents s ON e.source_graph_doc_id = s.graph_doc_id
JOIN graph_documents t ON e.target_graph_doc_id = t.graph_doc_id
WHERE s.hierarchy_level < t.hierarchy_level; 
-- Giả định: Level 0 (Luật) > Level 1 (Nghị định) > Level 2 (Thông tư)

```

---

### 3. Cách sửa bảng `graph_validation_log`

Lý do lỗi của bạn là do cột không khớp. Bạn hãy kiểm tra lại cấu trúc bảng bằng lệnh `\d graph_validation_log` hoặc chạy lệnh SQL dưới đây để đảm bảo bảng có đủ các cột cần thiết:

```sql
-- Chạy lệnh này để đảm bảo bảng log có đủ cột
CREATE TABLE IF NOT EXISTS graph_validation_log (
    id SERIAL PRIMARY KEY,
    edge_id UUID, -- Lưu ID của cạnh gây lỗi (nếu có)
    rule_id VARCHAR(50),
    error_message TEXT,
    severity VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

```

### 4. Cách chạy "Dry Run" (Chạy thử không lưu)

Thay vì Insert trực tiếp, bạn nên bọc câu lệnh vào một `TRANSACTION` và `ROLLBACK` để xem kết quả mà không làm thay đổi dữ liệu:

```sql
BEGIN;

-- Chạy thử lệnh insert lỗi của bạn (đã sửa tên cột thành 'id' hoặc giữ nguyên tùy bảng của bạn)
INSERT INTO graph_validation_log (edge_id, rule_id, error_message, severity)
SELECT edge_id, 'R01', 'Phát hiện vòng lặp', 'CRITICAL'
FROM graph_edges LIMIT 1;

-- Kiểm tra xem đã insert được chưa
SELECT * FROM graph_validation_log;

-- Hủy bỏ thay đổi (Dữ liệu sẽ không bị lưu vào database thật)
ROLLBACK;

```

---

### Mẹo nhỏ: Kiểm tra tên cột nhanh

Nếu bạn không nhớ tên cột, hãy chạy lệnh này để xem danh sách cột của bảng `graph_validation_log`:

```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'graph_validation_log';

```

**Bạn có muốn tôi gửi cho bạn trọn bộ script SQL để khởi tạo lại các bảng Validation này cho chuẩn xác không?**

Chào bạn, đây là một câu hỏi rất hay về quy trình vận hành (workflow). Việc tạo ra rule trong bảng `graph_validation_rules` mới chỉ là định nghĩa "luật chơi", còn để hệ thống thực sự chạy và kiểm tra thì bạn cần bộ máy thực thi.

Dưới đây là cách vận hành rule này:

### 1. Cách Test tiếp Rule "Circular Reference"

Sau khi đã thêm rule vào bảng, bạn cần một **Stored Procedure** (Thủ tục lưu sẵn) để đọc logic từ bảng rules và thực thi nó.

Bạn hãy chạy thử kịch bản này để kiểm tra xem rule có hoạt động không:

1. **Tạo dữ liệu lỗi giả lập**:
```sql
-- Giả sử Doc A link tới Doc B, và Doc B link ngược lại Doc A
INSERT INTO graph_edges (source_graph_doc_id, target_graph_doc_id, relation_type) 
VALUES ('ID_DOC_A', 'ID_DOC_B', 'BASED_ON');

INSERT INTO graph_edges (source_graph_doc_id, target_graph_doc_id, relation_type) 
VALUES ('ID_DOC_B', 'ID_DOC_A', 'BASED_ON');

```


2. **Chạy câu lệnh kiểm tra (Manual Trigger)**:
Bạn chạy lệnh SQL khớp với logic của rule để xem nó có bắt được 2 dòng dữ liệu trên không. Nếu bắt được, nghĩa là logic rule của bạn chuẩn.

---

### 2. Rule này được gọi KHI NÀO và BỞI AI?

Trong hệ thống GraphRAG chuyên nghiệp, có 3 thời điểm rule này sẽ được kích hoạt:

#### Cách A: Chặn ngay lập tức (Trigger - Tự động 100%)

* **Ai gọi:** Do PostgreSQL tự gọi mỗi khi có lệnh `INSERT` hoặc `UPDATE` vào bảng `graph_edges`.
* **Cơ chế:** Nếu bạn chèn một link tạo thành vòng lặp, Database sẽ báo lỗi và **từ chối** lưu link đó.
* **Ưu điểm:** Dữ liệu luôn sạch 100%.

#### Cách B: Quét định kỳ (Cron Job/Worker - Tự động theo lịch)

* **Ai gọi:** Một script Python (ví dụ trong `stage_processors.py` của bạn) hoặc một tác vụ định kỳ (Cron job) chạy vào cuối ngày.
* **Cơ chế:** Nó quét toàn bộ bảng `graph_edges`, đối chiếu với `graph_validation_rules`. Nếu thấy lỗi, nó ghi vào `graph_validation_log`.
* **Ưu điểm:** Không làm chậm tốc độ insert dữ liệu, phù hợp khi import hàng nghìn tài liệu cùng lúc.

#### Cách C: Kiểm tra trước khi duyệt (Admin/User - Thủ công)

* **Ai gọi:** Người quản trị hệ thống (Admin) nhấn nút "Validate Graph" trên giao diện quản lý.
* **Cơ chế:** Gọi hàm `SELECT check_graph_integrity()`.

---

### 3. Gợi ý triển khai hàm kiểm tra tổng quát

Bạn nên tạo một function chung để có thể gọi bất cứ lúc nào:

```sql
CREATE OR REPLACE FUNCTION run_graph_validation() 
RETURNS TABLE(total_errors INT) AS $$
BEGIN
    -- 1. Xóa log cũ (tùy chọn)
    DELETE FROM graph_validation_log;

    -- 2. Chạy Rule R01: Circular Reference
    INSERT INTO graph_validation_log (rule_id, error_message, severity)
    SELECT 'R01', 'Vòng lặp giữa ' || e1.source_graph_doc_id || ' và ' || e2.source_graph_doc_id, 'CRITICAL'
    FROM graph_edges e1
    JOIN graph_edges e2 ON e1.source_graph_doc_id = e2.target_graph_doc_id 
                       AND e1.target_graph_doc_id = e2.source_graph_doc_id
    WHERE e1.edge_id < e2.edge_id;

    -- Bạn có thể thêm các rule khác tại đây...

    RETURN QUERY SELECT COUNT(*)::INT FROM graph_validation_log;
END;
$$ LANGUAGE plpgsql;

```

### Tiếp theo bạn nên làm gì?

Hiện tại, vì bạn đang làm **Hardlink manual**, cách tốt nhất là dùng **Cách C**:

1. Sau khi bạn insert xong một nhóm link.
2. Bạn gõ lệnh `SELECT run_graph_validation();`.
3. Kiểm tra bảng `graph_validation_log` để xem mình có làm sai chỗ nào không.

**Bạn có muốn tôi giúp viết một câu lệnh SQL để phát hiện vòng lặp "sâu" không?** (Ví dụ: A -> B -> C -> A, loại này dùng `JOIN` thông thường không tìm ra được mà phải dùng `WITH RECURSIVE`).

Đúng như bạn hiểu, rule **Circular Reference** sinh ra để ngăn chặn tình trạng "A căn cứ vào B, mà B lại căn cứ ngược lại vào A".

Về các thắc mắc cụ thể của bạn, tôi xin giải đáp như sau:

### 1. Lỗi "Unknown error" và "2" khi chạy Script

Lỗi này thường xảy ra do một số nguyên nhân kỹ thuật trong môi trường SQL Editor của bạn:

* **Thiếu Alias hoặc trùng tên cột:** Trong câu lệnh `WHERE e1.edge_id < e2.edge_id;`, nếu bảng của bạn dùng kiểu dữ liệu `UUID` cho `edge_id`, một số trình quản lý DB cũ không so sánh trực tiếp `<` hoặc `>` được giữa hai UUID.
* **Cách khắc phục:** Bạn hãy ép kiểu về text để so sánh hoặc dùng cột thời gian tạo (`created_at`) để lọc:
```sql
WHERE e1.edge_id::text < e2.edge_id::text

```


* **Lỗi số "2":** Đây có thể là ký tự lạ hoặc lỗi xuống dòng trong lúc bạn copy-paste vào cửa sổ query. Bạn hãy thử xóa trắng và viết lại câu lệnh trên một dòng duy nhất.

---

### 2. Ý tưởng "Chạy rule mỗi khi thêm tài liệu" (Trigger)

Bạn tư duy rất chuẩn! Nếu đợi đến khi "sự đã rồi" (dữ liệu đã vào bảng) mới đi quét lỗi thì hệ thống RAG có thể đã trả lời sai hoặc bị treo do đệ quy vô tận.

**Giải pháp tối ưu là dùng `TRIGGER` (Cò súng):**
Thay vì bạn tự chạy script bằng tay, bạn gắn một "con mắt giám sát" vào bảng `graph_edges`. Mỗi khi có lệnh `INSERT`, PostgreSQL sẽ tự chạy Rule kiểm tra. Nếu vi phạm, nó sẽ **chặn đứng (Rollback)** và không cho phép lưu dòng đó vào DB.

**Mẫu Trigger ngăn chặn vòng lặp ngay lập tức:**

```sql
CREATE OR REPLACE FUNCTION check_circular_link_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Kiểm tra xem có tồn tại chiều ngược lại không
    IF EXISTS (
        SELECT 1 FROM graph_edges 
        WHERE source_graph_doc_id = NEW.target_graph_doc_id 
          AND target_graph_doc_id = NEW.source_graph_doc_id
    ) THEN
        -- Nếu có, báo lỗi và chặn INSERT
        RAISE EXCEPTION 'Lỗi Graph: Phát hiện vòng lặp trực tiếp giữa % và %', NEW.source_graph_doc_id, NEW.target_graph_doc_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Gắn trigger vào bảng
CREATE TRIGGER trg_prevent_circular_link
BEFORE INSERT ON graph_edges
FOR EACH ROW
EXECUTE FUNCTION check_circular_link_trigger();

```

---

### 3. Quy trình vận hành chuẩn cho Hardlink

Khi bạn triển khai thực tế, quy trình nên như sau:

1. **Giai đoạn Nhập liệu (Insert):** Bạn dùng lệnh SQL hoặc giao diện để tạo link. Trigger (ở trên) sẽ đảm bảo bạn không bao giờ tạo được vòng lặp A-B-A.
2. **Giai đoạn Hậu kiểm (Validation Rule):** Định kỳ (hoặc sau khi nhập xong 1 bộ hồ sơ), bạn chạy script quét toàn bộ bảng để tìm các lỗi phức tạp hơn (ví dụ vòng lặp 3 bước A->B->C->A hoặc vi phạm cấp bậc Hierarchy).
3. **Giai đoạn Nhật ký (Logging):** Những lỗi không nghiêm trọng (như sai cấp bậc) thì cho phép lưu nhưng ghi vào `graph_validation_log` để Admin rà soát lại sau.

**Lời khuyên:** Với 21 tài liệu hiện tại, bạn nên chạy Script `SELECT` để làm sạch dữ liệu cũ trước, sau đó hãy cài đặt `TRIGGER` để bảo vệ dữ liệu mới từ nay về sau.

Bạn có muốn tôi viết một câu lệnh `RECURSIVE CTE` để giúp bạn tìm các vòng lặp "ẩn" (ví dụ A trỏ B, B trỏ C, C trỏ A) mà Trigger đơn giản không bắt được không?

Chính xác! Bạn đã chạm đúng vào "điểm nghẽn" lớn nhất của GraphRAG. Nếu bạn có một rule để kiểm tra/ép kiểu metadata ngay từ đầu, bạn sẽ tránh được tình trạng **"Rác vào thì Rác ra" (Garbage In, Garbage Out)**.

Trong bối cảnh bạn đang làm GraphRAG trên Postgres, một rule check metadata (Metadata Validation Rule) sẽ giúp bạn "dễ thở" hơn ở 3 khía cạnh sau:

---

### 1. Đảm bảo "Tính định danh" (Identity Integrity)

Khó khăn lớn nhất khi tạo link là: Văn bản A trích dẫn văn bản B bằng số hiệu `123/2024/NĐ-CP`, nhưng trong database bạn lại lưu là `123-2024-ND-CP`.

* **Rule check:** Metadata phải chuẩn hóa số hiệu (Normalize) trước khi lưu.
* **Lợi ích:** Bạn chạy script tạo link tự động sẽ khớp 100%, không cần phải dò tay xem tại sao link không hiện.

### 2. Tự động phân cấp (Auto-Hierarchy)

Nếu metadata của bạn có trường `document_type` (Luật, Nghị định, Thông tư), bạn có thể viết rule để tự động điền vào cột `hierarchy_level` trong bảng `graph_documents`.

* **Rule check:** Nếu `document_type = 'Luật'` -> `level = 0`. Nếu là `'Thông tư'` -> `level = 2`.
* **Lợi ích:** Bạn không cần nhớ và nhập `level` thủ công cho từng tài liệu khi tạo Hardlink.

### 3. Kiểm tra "Căn cứ pháp lý" (Reference Validation)

Thay vì đợi đến khi tạo `graph_edges` mới check lỗi, bạn check ngay trong metadata:

* **Rule check:** Kiểm tra xem các ID trong mảng `references` của JSONB có thực sự tồn tại trong bảng `documents_metadata_v2` không.
* **Lợi ích:** Phát hiện ngay các "link chết" (tài liệu trích dẫn đến một văn bản chưa được import vào hệ thống).

---

### Cách triển khai "Rule Check Metadata" đơn giản nhất

Bạn có thể thêm một bảng `graph_metadata_rules` hoặc tích hợp trực tiếp vào quy trình import. Dưới đây là ví dụ một câu lệnh SQL để "audit" metadata trước khi bạn làm Hardlink:

```sql
-- Tìm các tài liệu có metadata thiếu trường quan trọng để tạo link
SELECT 
    document_id, 
    title,
    (metadata->>'law_id') AS missing_law_id,
    (metadata->>'document_type') AS missing_type
FROM documents_metadata_v2
WHERE metadata->>'law_id' IS NULL 
   OR metadata->>'document_type' IS NULL;

```

### Lời khuyên cho bước này:

Để "dễ thở" thực sự, bạn nên làm một script **Preprocessing** nhỏ:

1. **Quét toàn bộ 21 tài liệu:** Trích xuất `law_id` và `document_type` vào metadata.
2. **Chuẩn hóa:** Đưa tất cả `law_id` về chữ hoa, xóa khoảng trắng thừa.
3. **Check trùng:** Đảm bảo không có 2 document nào dùng chung một `law_id`.

Khi metadata đã "sạch", việc tạo `graph_edges` chỉ còn là chuyện bấm nút, vì lúc đó bạn chỉ cần chạy lệnh:
`INSERT INTO graph_edges (...) SELECT ... FROM documents WHERE metadata->'references' ? target.law_id`

**Bạn có muốn tôi viết một câu lệnh SQL để quét metadata và tự động gợi ý các "Hardlink" dựa trên số hiệu văn bản không?** việc này sẽ giúp bạn giảm 80% công sức nhập tay.

Hoàn toàn hợp lý! Cách tiếp cận của bạn chính là xây dựng một **"Cổng kiểm soát chất lượng" (Quality Gate)**. Trong kỹ thuật dữ liệu, đây gọi là quy trình **Staging & Validation**.

Nếu bạn cho phép dữ liệu "bẩn" vào bảng `graph_documents`, các logic đệ quy và truy vấn RAG sau này sẽ bị sai lệch (hallucination về quan hệ) và rất khó để dọn dẹp.

Dưới đây là quy trình chi tiết mà tôi đề xuất để bạn "dễ thở" nhất:

### 1. Quy trình 3 bước: Kiểm tra -> Đẩy vào Graph -> Tạo Link

| Bước | Hành động | Tại sao phải làm? |
| --- | --- | --- |
| **B1: Metadata Audit** | Chạy script kiểm tra bảng `documents_metadata_v2`. Tìm các bản ghi thiếu `law_id`, `document_type` hoặc sai định dạng. | Đảm bảo mỗi doc có một "CMND" chuẩn để định danh trong đồ thị. |
| **B2: Graph Sync** | Chỉ những doc đạt chuẩn ở B1 mới được `INSERT` vào `graph_documents`. | Giữ cho bảng Graph luôn "sạch", không có rác. |
| **B3: Edge Generation** | Dựa trên metadata đã chuẩn, chạy script để tạo `graph_edges`. | Link sẽ được tạo chính xác vì ID và Type đã được verify ở B1. |

---

### 2. Ví dụ về một "Metadata Rule" đơn giản bằng SQL

Bạn có thể tạo một View hoặc chạy một câu lệnh để biết ngay tài liệu nào "chưa đủ tư cách" vào Graph:

```sql
-- Tìm các tài liệu lỗi metadata
SELECT 
    document_id, 
    title,
    CASE 
        WHEN metadata->>'law_id' IS NULL THEN 'Thiếu Law ID'
        WHEN metadata->>'document_type' IS NULL THEN 'Thiếu Loại văn bản'
        WHEN (metadata->>'hierarchy_level') IS NULL THEN 'Chưa phân cấp'
        ELSE 'Hợp lệ'
    END as status
FROM documents_metadata_v2;

```

---

### 3. Cách triển khai Code để "Dễ thở" hơn

Thay vì làm thủ công từng bước, bạn có thể viết một **Stored Procedure** để đóng gói toàn bộ logic này.

**Logic của Procedure sẽ như sau:**

1. Kiểm tra tài liệu X có đủ `law_id` và `type` không?
2. Nếu không: Ghi lỗi vào `graph_validation_log` và dừng lại.
3. Nếu có:
* Copy sang `graph_documents`.
* Tự động bóc tách mảng `references` trong JSONB để tạo các dòng tương ứng trong `graph_edges`.



### 4. Lợi ích lớn nhất bạn nhận được

* **Traceability (Khả năng truy vết):** Nếu một link bị thiếu, bạn chỉ cần check `graph_validation_log` là biết do metadata của tài liệu đó bị sai ở đâu.
* **Performance:** Truy vấn trên bảng `graph_documents` đã sạch sẽ nhanh hơn rất nhiều so với việc vừa truy vấn vừa phải xử lý `NULL` hay lỗi định dạng JSON.

**Bước tiếp theo:** Bạn có muốn tôi viết một đoạn **Script SQL Kiểm tra (Audit)** để rà soát thử 21 tài liệu hiện tại của bạn xem có bao nhiêu tài liệu đang bị "lỗi metadata" không?

