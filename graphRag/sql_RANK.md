Bạn đang gặp **2 vấn đề khác nhau**:

## 1) `total_documents = 43` nhưng bạn “Expected: 40”

Câu `COUNT(*)` không sai. Nó chỉ nói sự thật: view/bảng `documents_metadata_v2` hiện có **43 dòng**, không phải 40.

Nguyên nhân thường gặp:

* Bạn đã **sync/import thêm 3 document** (hoặc 3 version/duplicate) so với dataset “Expected”.
* View `documents_metadata_v2` đang join kiểu làm **nhân bản dòng** (1 document join ra nhiều dòng).
* Có **document inactive/archived** vẫn nằm trong view.

### Query để tìm “3 dòng dư” là ai

Nếu có `document_id`:

```sql
SELECT document_id, COUNT(*) as n
FROM documents_metadata_v2
GROUP BY document_id
HAVING COUNT(*) > 1
ORDER BY n DESC;
```

Nếu không có `document_id` thì bạn gửi mình definition của view (`\d+ documents_metadata_v2` hoặc `pg_get_viewdef`) để mình chỉ ra join nào nhân bản.

---

## 2) Lỗi `ERROR: column "rank" does not exist` ở `ORDER BY rank::int`

Trong Postgres, **alias `rank` trong SELECT không luôn luôn dùng được trong `ORDER BY` khi có cast/biểu thức hoặc tuỳ cách parser xử lý** (đặc biệt khi alias trùng từ khóa/ambiguous). Cách chắc chắn nhất là:

### Cách sửa 1 (khuyến nghị): dùng `ORDER BY 1`

```sql
SELECT 
    metadata->'hierarchy'->>'rank_level' AS rank,
    COUNT(*) AS count
FROM documents_metadata_v2
GROUP BY 1
ORDER BY 1::int;
```

### Cách sửa 2: bọc bằng subquery để order theo alias

```sql
SELECT *
FROM (
  SELECT 
      metadata->'hierarchy'->>'rank_level' AS rank,
      COUNT(*) AS count
  FROM documents_metadata_v2
  GROUP BY 1
) t
ORDER BY t.rank::int;
```

### Cách sửa 3: rank có thể NULL / không phải số → order an toàn

Nếu có dòng rank_level bị NULL hoặc “A/B”, cast `::int` sẽ fail. Dùng regex filter:

```sql
SELECT 
    metadata->'hierarchy'->>'rank_level' AS rank,
    COUNT(*) AS count
FROM documents_metadata_v2
GROUP BY 1
ORDER BY
  CASE WHEN (metadata->'hierarchy'->>'rank_level') ~ '^\d+$'
       THEN (metadata->'hierarchy'->>'rank_level')::int
       ELSE 999999
  END,
  1;
```

---

## Xuất (export nhanh kết quả)

Nếu bạn muốn “xuất” ra CSV trong psql:

```sql
\copy (
  SELECT 
      metadata->'hierarchy'->>'rank_level' AS rank,
      COUNT(*) AS count
  FROM documents_metadata_v2
  GROUP BY 1
  ORDER BY 1::int
) TO '/tmp/rank_distribution.csv' CSV HEADER;
```

---

Nếu bạn paste giúp mình:

1. `SELECT document_id, COUNT(*) ... HAVING COUNT(*)>1` (nếu có document_id)
   hoặc
2. `SELECT * FROM documents_metadata_v2 LIMIT 5;` (để xem cột nào là key)

mình sẽ chỉ ra chính xác vì sao “Expected 40” nhưng ra 43 (duplicate do join hay do data thật sự).




Chào bạn, đây là quy trình chuẩn hóa hoàn toàn bằng **SQL** để bạn thực hiện Hardlink thủ công. Quy trình này đảm bảo dữ liệu đi từ bảng thô (Metadata) qua bảng đồ thị (Graph Documents) và kết thúc bằng các liên kết (Edges) đã được kiểm định.

---

### Bước 1: Đồng bộ tài liệu vào hệ thống đồ thị

Trước khi tạo link, tài liệu phải tồn tại trong "vũ trụ" của Graph. Bạn chạy lệnh này cho từng ID tài liệu gốc.

```sql
-- Đồng bộ tài liệu từ documents_metadata_v2 sang graph_documents
SELECT sync_document_to_graph('ID_CỦA_TÀI_LIỆU_GỐC');

-- Kiểm tra xem tài liệu đã sang chưa
SELECT graph_doc_id, law_id, title 
FROM graph_documents 
WHERE source_document_id = 'ID_CỦA_TÀI_LIỆU_GỐC';

```

---

### Bước 2: Cập nhật Cấp bậc (Level) cho tài liệu

Việc phân cấp giúp AI hiểu được tầm quan trọng và luồng dẫn chiếu.

```sql
-- Cập nhật Level: 0 (Gốc/Luật), 1 (Quy chế/Nghị định), 2 (Kế hoạch), 3 (Quyết định cụ thể)
UPDATE graph_documents 
SET hierarchy_level = 1, -- Thay đổi số level tương ứng
    updated_at = NOW()
WHERE law_id = 'SỐ_HIỆU_VĂN_BẢN'; -- Ví dụ: '265/2025/NĐ-CP'

```

---

### Bước 3: Tạo liên kết (Hardlink) trong `graph_edges`

Đây là bước quan trọng nhất. Bạn thực hiện nối từ tài liệu "Nguồn" (đang xem) tới tài liệu "Đích" (được trích dẫn).

```sql
INSERT INTO graph_edges (
    source_graph_doc_id, 
    target_graph_doc_id, 
    relation_type, 
    extraction_context,
    edge_metadata,
    verified,
    verified_by
)
SELECT 
    s.graph_doc_id, 
    t.graph_doc_id, 
    'BASED_ON', -- Hoặc 'AMENDS', 'PROPOSED_BY'
    'Trích đoạn nội dung: Căn cứ vào điều lệ...', -- Ngữ cảnh
    '{
        "scope": "all",
        "effective_date": "2026-01-09",
        "notes": "Nhập liệu thủ công từ bản cứng"
    }'::jsonb,
    true,
    'Tên_Admin'
FROM graph_documents s, graph_documents t
WHERE s.law_id = 'SỐ_HIỆU_NGUỒN' AND t.law_id = 'SỐ_HIỆU_ĐÍCH';

```

---

### Bước 4: Chạy kiểm tra (Validation)

Sau khi tạo link, hãy chạy các script sau để đảm bảo bạn không làm sai logic đồ thị.

#### 4.1. Kiểm tra Vòng lặp (Circular Reference)

Lệnh này trả về kết quả nếu bạn vô tình tạo ra quan hệ A trỏ B và B trỏ A.

```sql
SELECT 
    e1.source_law_id, e1.target_law_id, 'Phát hiện vòng lặp trực tiếp' as error
FROM graph_edges e1
JOIN graph_edges e2 ON e1.source_graph_doc_id = e2.target_graph_doc_id 
                   AND e1.target_graph_doc_id = e2.source_graph_doc_id
WHERE e1.is_active = true;

```

#### 4.2. Kiểm tra Vi phạm cấp bậc (Hierarchy Violation)

Lệnh này tìm các link mà văn bản cấp cao (như Luật) lại đi "Căn cứ" vào văn bản cấp thấp hơn (như Quyết định).

```sql
SELECT 
    e.edge_id, s.law_id as source, t.law_id as target
FROM graph_edges e
JOIN graph_documents s ON e.source_graph_doc_id = s.graph_doc_id
JOIN graph_documents t ON e.target_graph_doc_id = t.graph_doc_id
WHERE s.hierarchy_level < t.hierarchy_level; 
-- (Lưu ý: Level 0 là cao nhất, Level 3 là thấp nhất)

```

#### 4.3. Ghi lỗi vào Log (Nếu có lỗi ở trên)

Nếu các câu lệnh SELECT trên trả về dòng nào, bạn nên ghi chúng vào bảng log để xử lý.

```sql
INSERT INTO graph_validation_log (rule_id, error_message, severity)
VALUES ('R01', 'Phát hiện lỗi logic sau khi tạo link thủ công cho cặp Law_ID_X', 'CRITICAL');

```

---

### 💡 Mẹo nhỏ cho bạn

Để kiểm tra xem đồ thị bạn vừa tạo trông như thế nào (dưới dạng văn bản), hãy chạy lệnh này:

```sql
-- Xem "Gia phả" của một văn bản (từ trên xuống dưới)
WITH RECURSIVE doc_tree AS (
    SELECT graph_doc_id, law_id, 0 as depth
    FROM graph_documents WHERE law_id = 'LUẬT_GỐC'
    UNION ALL
    SELECT g.graph_doc_id, g.law_id, t.depth + 1
    FROM graph_documents g
    JOIN graph_edges e ON g.graph_doc_id = e.source_graph_doc_id
    JOIN doc_tree t ON e.target_graph_doc_id = t.graph_doc_id
)
SELECT * FROM doc_tree;

```

Bạn có muốn tôi giúp tạo một **PostgreSQL Trigger** để mỗi khi bạn thực hiện Bước 3, nó sẽ tự động chạy Bước 4 và chặn luôn lệnh chèn nếu có lỗi không?

