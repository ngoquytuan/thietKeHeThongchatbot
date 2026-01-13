Ý tưởng endpoint **`GET /api/graph/resolve?identifier=...`** là **rất đúng cho prototype** và mình khuyên bạn làm ngay, vì nó “khóa” được một vấn đề đau đầu nhất: **client không phải đoán identifier là loại gì**. Trong manual của team cũng đang đi theo hướng “try UUID trước rồi fallback theo law_id/document_number/task_code”. 

Dưới đây là cách thiết kế cho **chắc, dễ dùng, và không vấp ambiguity**.

---

## 1) Hành vi endpoint nên như thế nào

### Input

`identifier` có thể là:

* `graph_doc_id` (UUID)
* `source_document_id` / `document_id` (UUID)
* `law_id` (string)
* `document_number` (string)
* `task_code` (string)

### Output đề xuất

Trả về **center node** tối thiểu để mọi API khác dùng:

```json
{
  "match_type": "graph_doc_id|document_id|law_id|document_number|task_code",
  "confidence": 1.0,
  "center": {
    "graph_doc_id": "uuid",
    "source_document_id": "uuid",
    "title": "...",
    "hierarchy_level": 3,
    "law_id": "...",
    "document_number": "...",
    "task_code": "..."
  },
  "candidates": [] 
}
```

### Quy tắc quan trọng: xử lý “trùng”

* Nếu `identifier` match **nhiều hơn 1 node** (hay gặp với `task_code`, đôi khi `document_number`), bạn có 2 lựa chọn:

  1. **HTTP 409 Conflict** + trả `candidates[]` (khuyến nghị cho frontend UX tốt)
  2. Trả 200 nhưng `center=null` và `candidates[]` có nhiều phần tử

Prototype thường chọn (1) để client buộc chọn lại.

---

## 2) Chiến lược resolve (thứ tự match)

Mình đề xuất thứ tự sau để giảm nhầm:

1. **Nếu parse được UUID**:

   * match `graph_documents.graph_doc_id = uuid`
   * nếu không có, match `graph_documents.source_document_id = uuid`

2. Nếu không phải UUID:

   * match exact `law_id = identifier`
   * match exact `document_number = identifier`
   * match exact `task_code = identifier`

3. (Optional) Nếu muốn “thông minh hơn”:

   * match case-insensitive (`ILIKE`) cho law_id/document_number
   * normalize task_code (D/Đ, dấu cách, chấm…) — nhưng cái này để sau.

---

## 3) SQL mẫu (dễ implement, chạy nhanh)

### A) Case UUID

```sql
SELECT
  graph_doc_id::text,
  source_document_id::text AS source_document_id,
  title,
  hierarchy_level,
  law_id,
  document_number,
  task_code
FROM graph_documents
WHERE graph_doc_id = $1::uuid
   OR source_document_id = $1::uuid
LIMIT 2;
```

### B) Case string (law_id / document_number / task_code)

```sql
SELECT
  graph_doc_id::text,
  source_document_id::text AS source_document_id,
  title,
  hierarchy_level,
  law_id,
  document_number,
  task_code
FROM graph_documents
WHERE law_id = $1
   OR document_number = $1
   OR task_code = $1
ORDER BY
  CASE
    WHEN law_id = $1 THEN 1
    WHEN document_number = $1 THEN 2
    WHEN task_code = $1 THEN 3
    ELSE 9
  END,
  hierarchy_level ASC
LIMIT 5;
```

---

## 4) Index nên có để endpoint này “mượt”

Trên `graph_documents` (theo cấu trúc bảng trong manual) :

* unique/BTREE index cho:

  * `graph_doc_id` (PK)
  * `source_document_id`
* BTREE index cho:

  * `law_id`
  * `document_number`
  * `task_code`

Nếu `law_id/document_number/task_code` có thể null nhiều, vẫn ok.

---

## 5) Error handling tối thiểu (để frontend dễ làm)

* `404 Not Found`: không match gì
* `409 Conflict`: match > 1 (kèm `candidates`)
* `200 OK`: match đúng 1

---

## 6) Vì sao endpoint này đáng làm ngay (cho prototype GraphRAG)

Nó giúp tất cả endpoint sau **đơn giản**:

* `/api/graph/{id}/neighbors`
* `/api/graph/{id}/context`
* `/api/graph/{id}/subgraph`
* `/api/graph/{id}/lineage`

Client chỉ cần gọi:

1. `/resolve?identifier=...` → lấy `graph_doc_id`
2. gọi các endpoint còn lại bằng `graph_doc_id`

=> Không còn cảnh “nhầm UUID vs law_id” nữa.

---

Nếu bạn muốn, mình có thể viết luôn **pseudo-code FastAPI** (hoặc hàm Python thuần) cho `resolve()` theo đúng rule trên, kèm case 409 trả `candidates` để frontend chọn.
