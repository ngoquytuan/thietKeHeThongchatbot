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




SELECT sync_document_to_graph('ID_CỦA_TÀI_LIỆU_GỐC');

