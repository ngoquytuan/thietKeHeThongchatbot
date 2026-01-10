Tôi sẽ đọc báo cáo cập nhật mới nhất để hiểu rõ hệ thống hiện tại trước.## 🎯 **HƯỚNG NÂNG CẤP: FR3.1V6 → FR3.1V7 (Graph-Ready Metadata)**

Sau khi đọc báo cáo, tôi thấy hệ thống hiện tại **đã rất tốt về pattern detection và extraction** (91.7% completeness). Nhưng để hỗ trợ GraphRAG với khung 7 tầng, cần bổ sung **3 nhóm metadata mới**:

---

### **1️⃣ HIERARCHY IDENTITY (Định danh phân cấp)** 
**Metadata cần thêm:**
```json
"hierarchy": {
  "rank_level": 5,              // 0-6 (tự động detect hoặc manual)
  "rank_label": "PROJECT",      // Human-readable label
  "parent_id": "753/QĐ-HĐQLQ",  // Văn bản cấp trên
  "root_id": "LUAT_KHCN_2013",  // Văn bản gốc
  "path": "0/1/2/5"             // Đường dẫn từ root
}
```

**Trích xuất từ đâu:**
- **`rank_level`:** Detect từ **tiêu đề + pattern**
  - Có "Luật" → Level 0
  - Có "Thông tư" + tên Bộ → Level 1  
  - Có "Quy chế" + HĐQLQ → Level 2
  - Có "Quyết định" + Giám đốc → Level 3
  - Có "Quy trình" + tên phòng → Level 4
  - Có mã dự án (DTCT.2024.05) → Level 5
  - Có "Biên bản/Báo cáo" + tên người → Level 6

- **`parent_id` & `root_id`:** Trích từ **references array** (đã có sẵn!)
  - Ví dụ: QĐ 574 có `"references": ["654/QĐ-CTCT"]` → 654 là parent
  - Cần thuật toán: "Tìm reference có rank_level thấp nhất trong danh sách"

- **`path`:** Tính toán đệ quy từ parent → root

**Dùng vào việc gì:**
- ✅ **Search weighting:** Câu hỏi "Quy định là gì?" → Ưu tiên level ≤3
- ✅ **Graph traversal:** Từ QĐ 574 (level 5) → trace ngược lên Luật (level 0)
- ✅ **Filter nhanh:** "Chỉ lấy văn bản pháp lý cấp cao" = `rank_level <= 2`

---

### **2️⃣ DOCUMENT GOVERNANCE (Quản trị tài liệu)**
**Metadata cần thêm:**
```json
"governance": {
  "governing_laws": ["LUAT_KHCN", "654/QD-CTCT"],  // Luật/QC cấp cao chi phối
  "execution_scope": "Phòng NCPT",                 // Phạm vi áp dụng
  "is_derived": true,                              // Có phải văn bản hướng dẫn?
  "superseded_by": null,                           // ID văn bản thay thế
  "dependency_type": "PROCEDURAL"                  // DIRECT | SUPPLEMENTARY | PROCEDURAL
}
```

**Trích xuất từ đâu:**
- **`governing_laws`:** Lọc từ **references** + check rank_level
  - Chỉ lấy các reference có `rank_level <= 2` (Luật/Quy chế)
  - Ví dụ: `["654/QĐ-CTCT", "LUAT_KHCN"]` (loại bỏ các QĐ level 5)

- **`execution_scope`:** Trích từ **department** (đã có!) + fuzzy matching
  - Nếu document thuộc LEGAL_RND + có tên phòng → scope = tên phòng
  - Nếu không có → scope = "Toàn công ty"

- **`is_derived`:** Detect từ **keywords**
  - Có "hướng dẫn thực hiện", "căn cứ" → `true`
  - Là Luật/Nghị định → `false`

- **`superseded_by`:** Manual hoặc detect từ text
  - Tìm cụm "thay thế QĐ xxx" → gán ID

- **`dependency_type`:** 
  - Có "căn cứ" → `DIRECT`
  - Có "tham khảo" → `SUPPLEMENTARY`  
  - Có "hướng dẫn" → `PROCEDURAL`

**Dùng vào việc gì:**
- ✅ **Conflict detection:** Check QĐ cấp 5 có vi phạm Quy chế cấp 2 không
- ✅ **Avoid stale data:** Không lấy document có `superseded_by != null`
- ✅ **Contextual reasoning:** LLM hiểu "QĐ 574 là hướng dẫn thực hiện Quy chế 654"

---

### **3️⃣ GRAPH CONTEXT (Ngữ cảnh đồ thị)**
**Metadata cần thêm:**
```json
"graph_context": {
  "referenced_by": ["580/QD", "600/QD"],          // Các văn bản trích dẫn văn bản này
  "implements": "654/QD-CTCT",                    // Văn bản này thực thi văn bản nào
  "related_projects": ["DTCT.2024.05"],           // Dự án liên quan
  "related_people": ["Ngô Quý Tuấn", "Lê Tiến Thịnh"],  // Người liên quan
  "tag_keywords": ["GPS", "Nghiên cứu", "Hàng không"]    // Tag tự động
}
```

**Trích xuất từ đâu:**
- **`referenced_by`:** **Tính ngược** (batch process sau khi nạp xong)
  - Scan toàn bộ DB, tìm docs có `references` chứa ID này

- **`implements`:** Từ **references** + keyword "căn cứ"
  - Tìm reference đầu tiên xuất hiện sau "căn cứ"

- **`related_projects`:** Đã có! Trích từ `custom_fields.project_code`

- **`related_people`:** Trích từ **signer** + scan text tìm tên người
  - Regex: `r'((?:[A-ZĐĂÂÊÔƠƯ][a-zđăâêôơư]+\s){2,3})'`

- **`tag_keywords`:** Extract từ **tiêu đề + nội dung** bằng TF-IDF hoặc NER
  - Top 5-10 từ khóa quan trọng

**Dùng vào việc gì:**
- ✅ **Bidirectional graph:** "Ai trích dẫn QĐ này?" → Dùng `referenced_by`
- ✅ **Multi-hop reasoning:** "Tìm tất cả QĐ thực thi Quy chế 654" → Dùng `implements`
- ✅ **Person-centric search:** "Tìm tất cả văn bản liên quan Ngô Quý Tuấn"
- ✅ **Semantic clustering:** Group documents by shared tags

---

## 📌 **INTEGRATION STRATEGY**

### **Cách thêm vào MetadataEnricher:**

**Bước 1: Pattern Detection (giữ nguyên)**
- 5 patterns hiện tại vẫn hoạt động

**Bước 2: Enrich Custom Fields (giữ nguyên + mở rộng)**
- Thêm logic detect `rank_level` từ title + pattern
- Extract `governing_laws`, `execution_scope`, `dependency_type`

**Bước 3: NEW - Graph Enrichment**
- Tạo method `_enrich_graph_context()` 
- Tính toán `parent_id`, `root_id`, `path`
- Extract `related_people`, `tag_keywords`

**Bước 4: Post-processing (Batch)**
- Sau khi nạp xong tất cả docs → Scan DB
- Tính `referenced_by` cho tất cả documents

---

## 🎯 **USE CASES CỤ THỂ**

**UC1: Legal Compliance Check**
```
Query: "Quy trình phòng NCPT có tuân thủ Điều lệ công ty không?"
→ Search docs có execution_scope="Phòng NCPT" 
→ Lấy governing_laws của chúng
→ So sánh với Điều lệ (rank_level=3)
```

**UC2: Document Lineage**
```
Query: "QĐ 574 dựa trên luật nào?"
→ Load QĐ 574
→ Follow path: 5 → 2 → 1 → 0
→ Trả về: "Luật Khoa học Công nghệ 2013"
```

**UC3: Impact Analysis**
```
Query: "Nếu sửa Quy chế 654, ảnh hưởng bao nhiêu văn bản?"
→ Tìm docs có parent_id="654/QD-CTCT"
→ Tìm docs có implements="654/QD-CTCT"
→ Tìm docs có governing_laws chứa "654/QD-CTCT"
→ Return count + list
```

**UC4: Person Work Profile**
```
Query: "Ngô Quý Tuấn đang làm dự án gì?"
→ Search related_people="Ngô Quý Tuấn"
→ Lọc rank_level=5,6 (dự án + báo cáo)
→ Group by related_projects
```

---

## ✅ **TÓM TẮT**

| Nhóm Metadata | Số trường mới | Tự động hay Manual | Độ khó implement |
|---------------|---------------|---------------------|------------------|
| Hierarchy Identity | 5 trường | 70% tự động | ⭐⭐⭐ (Medium) |
| Document Governance | 5 trường | 80% tự động | ⭐⭐ (Easy) |
| Graph Context | 5 trường | 60% tự động + batch | ⭐⭐⭐⭐ (Hard) |

**Ưu tiên triển khai:**
1. **Phase 1:** Hierarchy Identity (quan trọng nhất cho search weighting)
2. **Phase 2:** Document Governance (cần cho compliance check)
3. **Phase 3:** Graph Context (nâng cao, có thể chậm batch)

Bạn muốn tôi chi tiết hóa thuật toán detect `rank_level` từ title + pattern không?
