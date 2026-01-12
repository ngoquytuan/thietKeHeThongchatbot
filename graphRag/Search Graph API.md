Bạn đã có “đồ thị tối thiểu” rồi, giờ **Search Graph API** nên được thiết kế theo 2 lớp nhu cầu:

1. **RAG retrieval** (lấy context nhanh, ít hop, có filter)
2. **Graph explorer** (lấy subgraph để debug/visualize, có path, có lineage)

Dưới đây là bộ endpoint mình khuyên dùng (đủ để chạy production + dễ mở rộng). Mình bám theo schema/ý tưởng trong manual (graph_documents/graph_edges + is_active + confidence) và pattern “get document with related docs” đã có sẵn.  

---

## 1) Quy ước dữ liệu để API “đỡ đau”

Vì bạn đang có `BASED_ON` và `REFERENCES`, còn hệ thống hiện hữu hay dùng `semantic_similarity / hierarchical / parent_child`, mình khuyên chuẩn hóa như sau:

* `relation_type` = **strategy / nhóm lớn**

  * `hardlink` (các quan hệ pháp lý/logic: BASED_ON, REFERENCES, AMENDS, SUPERSEDES…)
  * `semantic_similarity` (same_category, shared_keywords…)
  * `hierarchical` (same_level_peers / parent_child nếu có)
* `relation_subtype` = **nhãn cụ thể**

  * `BASED_ON`, `REFERENCES`, `AMENDS`, `SUPERSEDES`, `IMPLEMENTS`…

Như vậy API filter rất “sạch”: lọc theo `relation_type` để chia bucket, lọc theo `relation_subtype` để đúng nghiệp vụ.

---

## 2) Endpoint cốt lõi (cho RAG + UI)

### A. Resolve (chuẩn hóa đầu vào)

**GET** `/api/graph/resolve?identifier=...`

* identifier có thể là `document_id`, `graph_doc_id`, `law_id`, `document_number`, `task_code`
  **Trả về**: center node (graph_doc_id + source_document_id + title + hierarchy_level…)

> Endpoint này giúp frontend/backend khỏi phải “đoán” kiểu ID mỗi lần. (Trong manual cũng đang làm kiểu “try UUID then law_id…”.) 

---

### B. 1-hop Neighbors (endpoint quan trọng nhất cho RAG)

**GET** `/api/graph/{id}/neighbors`
Query params (gợi ý):

* `direction=in|out|both` (mặc định `both`)
* `relation_type=hardlink,semantic_similarity,hierarchical` hoặc `all`
* `relation_subtype=BASED_ON,REFERENCES,...` (optional)
* `min_confidence=0.7`
* `verified_only=true|false` (nếu bạn có cờ verified)
* `active_only=true` (map vào `is_active=true`)
* `limit=50`

**Response (gợi ý)**

```json
{
  "center": {...},
  "neighbors": [
    {
      "node": {...},
      "edge": {
        "edge_id": "...",
        "direction": "out",
        "relation_type": "hardlink",
        "relation_subtype": "BASED_ON",
        "confidence": 0.85,
        "weight": 0.7,
        "context": "Căn cứ ...",
        "metadata": {...}
      }
    }
  ],
  "stats": {"total": 12, "by_subtype": {"BASED_ON": 3, "REFERENCES": 9}}
}
```

Đây chính là thứ bạn nhét vào prompt RAG: “doc chính + top N neighbor theo confidence”. (Manual có ví dụ join graph_edges → graph_documents → documents_metadata_v2.) 

---

### C. Subgraph (N-hop) để debug/visualize

**GET** `/api/graph/{id}/subgraph?depth=2`
Params:

* `depth=1..3` (khuyên <=2 cho API realtime)
* các filter như neighbors (relation_type, subtype, confidence, active_only…)
* `max_nodes=300`, `max_edges=1000` (chống bùng nổ)

**Response**: format “viz-ready”

```json
{
  "nodes": [{ "id": "graph_doc_id", "title": "...", "level": 3, "law_id": "..." }],
  "edges": [{ "id": "edge_id", "source": "...", "target": "...", "subtype": "BASED_ON", "confidence": 0.85 }]
}
```

---

### D. Lineage (cực hữu ích cho BASED_ON)

Bạn đang tạo chuỗi BASED_ON kiểu L3 → L2 → L1 → L0. API nên có 2 endpoint “đi theo luật”:

**GET** `/api/graph/{id}/lineage/up?relation_subtype=BASED_ON&max_hops=10`
**GET** `/api/graph/{id}/lineage/down?relation_subtype=BASED_ON&max_hops=10`

Trả về 1 đường (hoặc nhiều đường) “căn cứ” rõ ràng để show UI và để RAG lấy “căn cứ pháp lý gốc”.

---

### E. Path (truy vết “vì sao liên quan”)

**GET** `/api/graph/path?from=...&to=...&max_hops=6&strategy=hardlink`

* Dùng BFS/shortest path (ưu tiên edge confidence cao, hoặc hạn chế subtype).

Endpoint này cực hay để giải thích cho user: “Báo cáo Q1/2025 liên quan Luật KHCN vì …”.

---

## 3) Search theo “đồ thị” thay vì keyword (Graph-aware search)

Vector search vẫn là bước 1. Nhưng bạn nên có endpoint “rerank bằng graph”:

### F. Graph-expanded retrieval

**POST** `/api/search/rag`
Body:

* `query`
* `top_k=5` (vector)
* `graph_expand_hops=1`
* `expand_per_doc=3`
* `expand_filter={ relation_type: ["hardlink","semantic_similarity"], min_confidence: 0.75 }`

Flow:

1. vector search → ra 5 doc
2. với mỗi doc, gọi neighbors/subgraph 1-hop → lấy thêm context “căn cứ/được tham chiếu/liên quan”
3. dedup + cap tổng context (ví dụ 12 docs)

Đây đúng tinh thần “Graph RAG enhances vector search by leveraging relationships” trong manual. 

---

## 4) Gợi ý SQL nền cho 2 endpoint quan trọng

### Neighbors (1-hop, both directions)

* Outgoing: `source_graph_doc_id = center`
* Incoming: `target_graph_doc_id = center`
* Join `graph_documents` để lấy node data
* Filter `is_active = true`, `confidence >= ...`, subtype/type

Manual cũng nhấn mạnh cách join này. 

### Subgraph (N-hop)

* Dùng `WITH RECURSIVE` để nở theo hop
* Có “guardrail”: `depth`, `max_nodes`, `min_confidence`, `active_only`

---

## 5) Chốt lại: tối thiểu bạn nên làm ngay (ít mà hiệu quả)

Nếu bạn chỉ làm **3 endpoint** trước để chạy được:

1. `GET /api/graph/resolve`
2. `GET /api/graph/{id}/neighbors`
3. `GET /api/graph/{id}/subgraph?depth=2`

Là bạn đã:

* debug được các edge bạn vừa insert,
* build UI explore,
* và quan trọng nhất: **bơm graph context vào RAG** giống đúng hướng dẫn trong tài liệu hệ thống.  

Nếu bạn muốn, mình có thể viết luôn **spec JSON response chuẩn** (schema Pydantic) và “bộ filter” cho đúng case BASED_ON/REFERENCES (kèm rule: chỉ expand hardlink khi verified=true).
