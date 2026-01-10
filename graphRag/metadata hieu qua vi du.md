Để hiểu các metadata này, hãy xem ví dụ cụ thể:

## 📋 **Ví Dụ Thực Tế: Nghị định 265/2025/NĐ-CP**

```json
{
  "graph_doc_id": "a1b2c3d4-...",        // ID trong bảng graph_documents
  "document_id": "e5f6g7h8-...",         // ID trong bảng documents_metadata_v2
  "law_id": "265/2025/NĐ-CP",            // Mã văn bản (do user đặt)
  "document_number": "265/2025/NĐ-CP",   // Số hiệu văn bản chính thức
  "title": "Nghị định về quản lý bay...",
  
  "hierarchy_level": 3,     // Cấp độ: 1=Luật, 2=Nghị định Chính phủ, 3=Thông tư
  "is_root_node": false,    // false = CÓ văn bản cha (căn cứ)
  "is_leaf_node": false,    // false = CÓ văn bản con (thông tư hướng dẫn)
  
  "parent_count": 2,        // Có 2 văn bản cha (ví dụ: Luật + Nghị định cũ)
  "child_count": 5          // Có 5 văn bản con (ví dụ: 5 thông tư hướng dẫn)
}
```

## 🔗 **Hierarchy Level (Cấp bậc văn bản)**

```
Level 1: Hiến pháp, Luật
   ↓
Level 2: Nghị định của Chính phủ  ← is_root_node=false, parent_count=1
   ↓
Level 3: Thông tư của Bộ          ← center_node này
   ↓
Level 4: Quyết định cụ thể        ← is_leaf_node=false, child_count=5
   ↓
Level 5: Hướng dẫn chi tiết
```

## 💡 **Ý Nghĩa:**

- **is_root_node = true**: Văn bản gốc (như Hiến pháp), không dựa trên văn bản nào
- **is_leaf_node = true**: Văn bản cuối cùng, không có văn bản nào hướng dẫn thêm
- **parent_count = 2**: Văn bản này "căn cứ" vào 2 văn bản khác
- **child_count = 5**: Có 5 văn bản "hướng dẫn thi hành" văn bản này

Rõ chưa? 😊
