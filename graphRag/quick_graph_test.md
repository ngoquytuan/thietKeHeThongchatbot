Nhìn log của bạn thì vấn đề **không phải “rank formula không ý nghĩa”** mà là: **script graph-only của bạn đang không lấy được *bất kỳ neighbor nào* từ `graph_edges`**, nên kết quả chỉ còn mỗi **seed**.

> Tất cả các lần chạy đều: `produced 1 docs` và chỉ in seed ⇒ expansion thực tế = 0.

Điều này gần như chắc chắn rơi vào 1 trong 3 lỗi kỹ thuật dưới đây.

---

## 1) Vì sao graph-only không nở ra?

### Nguyên nhân phổ biến #1: Bạn chỉ lấy 1 chiều (outgoing) hoặc nhầm cột ID

Rất hay gặp case:

* Script chỉ query `WHERE e.source_graph_doc_id = :seed`
* Nhưng edges của bạn lại nằm ở chiều ngược: `e.target_graph_doc_id = :seed`

Hoặc seed bạn truyền là **graph_doc_id**, nhưng script lại join theo **source_document_id**.

✅ Cách xác nhận nhanh (chạy SQL):

```sql
-- 1) Có edge đi ra từ seed không?
SELECT count(*) FROM graph_edges WHERE source_graph_doc_id = '862ed74c-c9ef-4811-bc1e-d505640b26ab'::uuid AND is_active=true;

-- 2) Có edge đi vào seed không?
SELECT count(*) FROM graph_edges WHERE target_graph_doc_id = '862ed74c-c9ef-4811-bc1e-d505640b26ab'::uuid AND is_active=true;
```

Nếu (1)=0 nhưng (2)>0 (hoặc ngược lại) ⇒ bạn đang lấy sai direction.

---

### Nguyên nhân phổ biến #2: Filter quan hệ làm rớt hết

Bạn đang truyền `relations=['BASED_ON','REFERENCES','IMPLEMENTS']` nhưng trong DB có thể:

* `relation_subtype = 'BASED_ON'/'REFERENCES'` còn `relation_type` lại là `hardlink` (hoặc semantic_similarity/hierarchical)
  => bạn filter nhầm cột (lọc `relation_type` bằng giá trị của `relation_subtype`).

✅ Cách xác nhận:

```sql
SELECT relation_type, relation_subtype, count(*)
FROM graph_edges
WHERE source_graph_doc_id='4938684f-c96c-40c9-a315-4dfce7d65502'::uuid
   OR target_graph_doc_id='4938684f-c96c-40c9-a315-4dfce7d65502'::uuid
GROUP BY 1,2
ORDER BY 3 DESC;
```

Nếu thấy `relation_type` kiểu `hardlink/semantic_similarity/...` và `relation_subtype` mới là `BASED_ON/REFERENCES` ⇒ script cần filter đúng cột.

---

### Nguyên nhân phổ biến #3: Seed bạn chọn không có edge (đúng thực tế)

Ví dụ:

* Luật L0 có thể **không có outgoing edges** (nếu bạn chỉ lưu BASED_ON theo hướng “văn bản thấp → căn cứ cao”).
* Khi seed là L0, muốn “thấy con/cháu” thì phải query **incoming edges**.

Vậy nên seed L0 mà query only outgoing ⇒ sẽ luôn chỉ ra seed.

---

## 2) Có nên chuyển sang “lên 1 cấp + xuống 1 cấp” không?

**Có — nhưng gọi đúng tên thì đây chính là “neighbors 1-hop both directions” + phân loại theo hướng.**

Với input = `graph_doc_id`, cách hữu ích nhất là:

### A) 1-hop neighbors (both directions) — dùng cho graph-only

* **Up 1 cấp**: incoming/outgoing tùy bạn định nghĩa chiều của BASED_ON
* **Down 1 cấp**: ngược lại
* **Side**: cùng level / semantic links (nếu muốn)

Nó sẽ “ý nghĩa” hơn BFS multi-hop khi graph còn ít edges.

**Kết quả bạn muốn nhìn thấy** dạng:

* Parents (căn cứ / upstream)
* Children (văn bản dựa trên mình / downstream)
* References (tham chiếu ngang)

---

## 3) Gợi ý sửa `quick_graph_test.py` theo hướng đúng và dễ debug

### Bước 1: Lấy neighbors 1-hop **cả 2 chiều**

Pseudo-logic:

* Query edges where:

  * `source_graph_doc_id = seed` → neighbor = target (direction=out)
  * `target_graph_doc_id = seed` → neighbor = source (direction=in)
* Filter theo **relation_subtype** (BASED_ON/REFERENCES/IMPLEMENTS) *hoặc* theo `relation_type` tùy schema thực tế.
* Join `graph_documents` để lấy title/level.

### Bước 2: Score đơn giản (đừng vội multi-hop)

Ví dụ score:

* base = `edge.confidence` (hoặc 1.0 nếu missing)
* decay theo hop (hop=1 nên chưa cần)
* bonus nếu relation_subtype=BASED_ON (nếu use-case legal)

### Bước 3: Sau khi 1-hop ok, mới làm 2-hop

2-hop nên làm kiểu “fan-out có kiểm soát”:

* mỗi neighbor chỉ mở rộng thêm tối đa K
* và tránh quay về seed (visited set)

---

## 4) Bạn đang seed 3 loại node, nên kỳ vọng khác nhau

* Seed = **L0 Luật**: thường **chỉ có incoming** (vì văn bản khác BASED_ON lên Luật)
* Seed = **L5 Dự án**: có thể có cả incoming (báo cáo) và outgoing (quy trình / tham chiếu)
* Seed = **L4 Quy trình**: thường có upstream (quyết định/quy chế) và downstream (dự án/báo cáo)

Nếu script hiện giờ ra 1 doc cho **mọi seed** ⇒ gần như chắc chắn là lỗi query/filter chứ không phải dữ liệu.

---

## 5) Làm nhanh 1 bước để mình “chốt hạ” đúng lỗi cho bạn

Bạn chỉ cần chạy 1 lệnh SQL cho 1 seed (ví dụ seed dự án DTCT):

```sql
SELECT
  e.edge_id,
  e.source_graph_doc_id,
  e.target_graph_doc_id,
  e.relation_type,
  e.relation_subtype,
  e.confidence,
  e.is_active
FROM graph_edges e
WHERE e.source_graph_doc_id='1716a3af-15af-4394-b696-b4de4046858d'::uuid
   OR e.target_graph_doc_id='1716a3af-15af-4394-b696-b4de4046858d'::uuid;
```

Paste output (vài dòng thôi) là mình sẽ nói chính xác:

* bạn đang filter nhầm cột nào,
* đang lấy sai direction nào,
* và nên thiết kế “up 1 / down 1” theo quan hệ nào cho đúng graph_edges hiện tại.


Chuẩn rồi — cái SQL bạn đưa **giải thích 100%** vì sao `quick_graph_test.py` của bạn “không nở” và chỉ trả về seed.

Bạn đang có 2 edges liên quan tới seed `1716a3af...` (Dự án DTCT):

1. `1716a3af (L5)  →  7350cad7 (L4)`

   * `relation_type = REFERENCES`
   * `relation_subtype = NULL`
   * `confidence = 0.75`
2. `4efe8958 (L6)  →  1716a3af (L5)`

   * `relation_type = REFERENCES`
   * `relation_subtype = NULL`
   * `confidence = 0.75`

=> Seed này **có neighbor cả 2 chiều**, nhưng **quan hệ nằm ở cột `relation_type`**, còn `relation_subtype` đang **NULL**.

---

## 1) Vì sao script của bạn trả về đúng 1 doc (seed)?

Trong log bạn truyền filter:
`relations=['BASED_ON','REFERENCES','IMPLEMENTS']`

Nhưng khả năng rất cao script của bạn đang lọc kiểu:

* `WHERE relation_subtype IN (...)`

Trong khi DB của bạn lại là:

* `relation_type = 'REFERENCES'`
* `relation_subtype = NULL`

👉 Kết quả: lọc rớt hết edges ⇒ expansion = 0 ⇒ chỉ còn seed.

Ngoài ra còn một lỗi hay đi kèm: `is_active=1` (integer) nhưng script có thể check `is_active = TRUE` (vẫn thường OK trong Postgres nếu kiểu boolean; nhưng nếu cột là int thì phải `=1`).

---

## 2) Cách sửa đúng: filter theo `relation_type` (hoặc fallback sang subtype)

Bạn nên sửa logic filter thành:

* Nếu `relation_subtype` NULL ⇒ dùng `relation_type`
* Nếu có subtype ⇒ ưu tiên subtype (tùy schema sau này)

**Quy ước đơn giản:**

* Lọc trên `(COALESCE(relation_subtype, relation_type)) IN relations`

Ví dụ SQL neighbors 1-hop (both directions) cho 1 seed:

```sql
WITH edges AS (
  SELECT
    e.edge_id,
    e.source_graph_doc_id,
    e.target_graph_doc_id,
    COALESCE(e.relation_subtype, e.relation_type) AS rel,
    e.confidence,
    e.is_active,
    CASE
      WHEN e.source_graph_doc_id = $1::uuid THEN 'out'
      ELSE 'in'
    END AS direction,
    CASE
      WHEN e.source_graph_doc_id = $1::uuid THEN e.target_graph_doc_id
      ELSE e.source_graph_doc_id
    END AS neighbor_graph_doc_id
  FROM graph_edges e
  WHERE (e.source_graph_doc_id = $1::uuid OR e.target_graph_doc_id = $1::uuid)
    AND e.is_active = 1
)
SELECT
  ed.edge_id,
  ed.rel,
  ed.confidence,
  ed.direction,
  gd.graph_doc_id,
  gd.title,
  gd.hierarchy_level
FROM edges ed
JOIN graph_documents gd ON gd.graph_doc_id = ed.neighbor_graph_doc_id
WHERE ed.rel = ANY($2)   -- $2 là array ['BASED_ON','REFERENCES','IMPLEMENTS']
ORDER BY ed.confidence DESC, gd.hierarchy_level DESC, gd.title ASC;
```

Nếu bạn áp dụng query này thì seed `1716a3af...` sẽ ra **2 neighbors** ngay:

* L4 Quy trình (out)
* L6 Báo cáo Q1 (in)

---

## 3) Có nên “lên 1 cấp & xuống 1 cấp” không?

**Có, và chính xác là nên làm ngay ở giai đoạn graph-only.**

Với dữ liệu hiện tại, “meaningful graph-only” nhất là:

* **1-hop both directions** + phân loại:

  * **Upstream**: các neighbor có `hierarchy_level` nhỏ hơn (hoặc theo rule quan hệ)
  * **Downstream**: neighbor có `hierarchy_level` lớn hơn
  * **Lateral**: cùng level

Như seed L5:

* Downstream (nếu coi level lớn hơn là “xuống”): L6 báo cáo
* Upstream: L4 quy trình (tùy cách bạn định nghĩa cây, vì trong bạn đang dùng REFERENCES, không phải parent-child)

Điểm quan trọng: với graph_edges hiện tại, bạn **không thể suy ra “up/down theo pháp lý” chỉ bằng level** nếu relation_type = REFERENCES (vì REFERENCES là quan hệ ngang/không đảm bảo thứ bậc).
Nhưng dùng “1-hop both directions” vẫn hữu ích để debug và mở rộng context.

---

## 4) Gợi ý rất thực tế để khỏi bị lặp lỗi này nữa

### A) Chuẩn hóa schema edge (khuyến nghị)

* Dùng:

  * `relation_type = 'hardlink' | 'semantic_similarity' | ...`
  * `relation_subtype = 'BASED_ON' | 'REFERENCES' | ...`
* Hoặc nếu bạn giữ như hiện tại: **đảm bảo luôn set subtype**, để filter/analytics nhất quán.

### B) Trong code, luôn filter theo `COALESCE(relation_subtype, relation_type)`

Cách này giúp bạn “chạy được” dù data còn lẫn lộn.

---

## 5) Bạn muốn mình sửa luôn `quick_graph_test.py` theo đúng hướng không?

Nếu bạn paste `quick_graph_test.py` (hoặc upload file), mình sẽ:

* sửa filter đúng cột
* thêm `both directions`
* in log rõ: số edges raw, số edges sau filter, list neighbor IDs
* và có mode: `--up 1 --down 1` để bạn test theo “1 cấp lên / 1 cấp xuống” như bạn muốn

Nhưng ngay bây giờ, chỉ với dữ liệu bạn đưa, kết luận là:

✅ Graph của bạn có edge
❌ Script lọc nhầm field (subtype NULL) nên không expand
✅ Sửa bằng COALESCE + both-direction là sẽ “nở” ngay


Kết quả này **đã “có ý nghĩa” đúng kiểu graph-only** rồi. Mình phân tích theo 3 lớp: (1) direction/downstream đang được hiểu thế nào, (2) scoring/decay, (3) điều cần chỉnh để đúng trực giác “lên 1 cấp – xuống 1 cấp”.

---

## 1) Case 1: Seed = **Dự án Audit 2025 (L5)** → downstream

```
01. L5 Dự án Audit 2025 [dist=0]
02. L6 BÁO CÁO Audit 2025 [dist=1, rel=REFERENCES (0.80)]
```

### Ý nghĩa

* Với hướng `downstream`, script của bạn đã lấy được đúng **child-ish neighbor**:

  * L5 → L6 qua REFERENCES (0.80)

### Đây là đúng hay sai?

* **Đúng về mặt kỹ thuật**: graph_edges có link `Báo cáo Audit 2025` ↔ `Dự án Audit 2025` (tùy chiều), và bạn đang cho downstream nghĩa là “level tăng” hoặc “đi ra theo rule direction”.
* **Chưa chắc đúng nghiệp vụ**, nhưng bạn nói “không quan tâm nội dung”, vậy OK.

### Nhận xét

* Graph nhỏ nên output gọn, dễ đọc. Đây là baseline tốt cho graph-only.

---

## 2) Case 2: Seed = **Luật KHCN 2013 (L0)** → downstream

```
01. L0 Luật KHCN [dist=0]
02. L1 Thông tư 654 ... [dist=1, BASED_ON 0.95]
03. L2 Quy chế ... [dist=2, BASED_ON 0.90]
04. L3 Phê duyệt ... [dist=3, BASED_ON 0.85]
05. L4 Quy trình ... [dist=4, BASED_ON 0.85]
06. L5 Dự án DTCT ... [dist=5, REFERENCES 0.75]
```

### Đây đang chứng minh điều gì?

* Script graph-only của bạn đã tìm được **một chuỗi dài 5 hop** từ L0 xuống L5.
* Quan trọng hơn: nó cho thấy downstream traversal đang “đi được” theo các cạnh BASED_ON liên tiếp, rồi “chốt” thêm 1 bước REFERENCES.

### Điểm rất hay

* Chuỗi L0 → L1 → L2 → L3 → L4 là **BASED_ON xuyên suốt** với confidence cao (0.85–0.95).
* Điều này cực hợp cho use-case “căn cứ pháp lý”, vì graph-only vẫn kéo được legal chain.

### Nhưng có 1 điểm bạn nên chú ý

Ở downstream mà bạn vẫn đi theo `BASED_ON` từ L0 xuống… thì có 2 khả năng:

1. **Trong graph_edges của bạn, BASED_ON đang được lưu theo chiều “cao → thấp”** (Luật → Thông tư → …).
2. Hoặc script downstream của bạn định nghĩa downstream là “đi theo edges phù hợp với chain”, không nhất thiết theo hướng source→target.

Kết quả bạn thấy đang **nhất quán và hữu ích**, nên về mặt API graph-only: ✅ ổn.

---

## 3) Scoring của bạn đang hoạt động đúng

Bạn thấy score giảm theo dist:

* dist=1: 0.800
* dist=2: 0.640
* dist=3: 0.512
* dist=4: 0.410
* dist=5: 0.328

Đây gần như là **0.8^dist** (decay theo hop).
=> Rank formula của bạn đang rất “sạch”: càng xa seed càng bị phạt.

Điểm cộng: bạn còn “gắn” confidence vào log `rel=BASED_ON (0.95)` giúp debug.

---

## 4) Vậy “lên 1 cấp – xuống 1 cấp” có đáng làm không?

**Rất đáng.** Lý do:

* Với graph-only, multi-hop rất dễ “đi xa mà không rõ ý nghĩa”.
* “1-hop upstream + 1-hop downstream” tạo ra một primitive cực tốt cho API:

  * `GET /graph/{id}/neighbors?direction=both&depth=1`
  * trả về parents/children/lateral

Bạn có thể vẫn giữ mode BFS multi-hop, nhưng UI/logic RAG thường bắt đầu bằng 1-hop.

---

## 5) Điều nên chỉnh tiếp (để graph-only “đẹp” hơn)

### A) Tách bucket theo quan hệ (đừng trộn BASED_ON với REFERENCES)

Hiện chuỗi của bạn kết thúc bằng `REFERENCES (0.75)` ở dist=5.
Trong legal chain, REFERENCES thường nên bị phạt nặng hơn BASED_ON.

Gợi ý weight theo relation:

* BASED_ON: *1.0*
* IMPLEMENTS: *0.85*
* REFERENCES: *0.6*

Score cuối:
`score = (decay^dist) * confidence * relation_weight`

### B) Giới hạn “bước chuyển loại”

Ví dụ chỉ cho phép:

* đi BASED_ON tối đa N hop
* rồi mới cho 1 bước REFERENCES (hoặc ngược lại)

Như vậy graph-only sẽ không bị “lạc” sang cluster khác.

### C) In thêm “hướng cạnh” (in/out)

Vì bạn đang dùng downstream như khái niệm theo level, nên debug sẽ dễ hơn nếu log:

* `edge_dir=in/out`
* `neighbor_level`
  để chắc chắn bạn không bị đảo chiều do dữ liệu edge.

---

## Kết luận

* ✅ Script của bạn đã fix đúng điểm chết: giờ **expand ra được**.
* ✅ Kết quả seed L0 cho thấy **graph-only có thể dựng legal chain** rất rõ ràng.
* ✅ Rank decay hợp lý.
* ➕ Bước tiếp theo nên làm: **neighbors 1-hop both directions** + **bucket theo relation** + **weight theo relation** (để giảm “REFERENCES noise”).

Nếu bạn paste thêm 1 lần chạy `direction=upstream` cho seed L5 hoặc L4 (DTCT), mình sẽ giúp bạn kiểm tra xem “upstream” có đang đúng trực giác không và nên định nghĩa upstream/downstream theo **edge direction** hay theo **hierarchy_level** cho nhất quán.
