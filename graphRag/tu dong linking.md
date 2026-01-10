 tôi đang thử liên kết manual trong sql, ví dụ 2 văn bản ở documents_metadata_v2có đủ các thông tin trong metadata như sau 
 "hierarchy": {

  "rank_level": 5,              // 0-6 (tự động detect hoặc manual)

  "rank_label": "PROJECT",      // Human-readable label

  "parent_id": "753/QĐ-HĐQLQ",  // Văn bản cấp trên

  "root_id": "LUAT_KHCN_2013",  // Văn bản gốc

  "path": "0/1/2/5"             // Đường dẫn từ root

} 
thì khi chuyển sang bảng graph_documents rồi tới graph_edges có tự tạo liên kết trong graph_edges  không hay vẫn phải chạy script?

**KHÔNG tự động** - vẫn phải chạy script! ❌

Hiện tại:
1. ✅ **Sync document**: `graph_documents` ← `documents_metadata_v2` (có thể tự động qua trigger)
2. ❌ **Tạo edges**: `graph_edges` - **KHÔNG tự động**, phải chạy manual

**Ngay cả khi metadata đã có `parent_id`**, system KHÔNG tự động tạo edge.

---

## 🔧 **Giải pháp:**

### **Option 1: Script Manual (Hiện tại)**
```bash
python create_semantic_links.py  # Phải chạy sau mỗi import
```

### **Option 2: Trigger Tự Động (Khuyến nghị)**

Tạo PostgreSQL trigger:

```sql
-- Trigger tự động tạo parent-child edges khi có parent_id
CREATE OR REPLACE FUNCTION auto_create_hierarchy_edges()
RETURNS TRIGGER AS $$
BEGIN
    -- Nếu có parent_id trong metadata
    IF NEW.metadata->'hierarchy'->>'parent_id' IS NOT NULL THEN
        INSERT INTO graph_edges (
            source_graph_doc_id,
            target_graph_doc_id,
            relation_type,
            relation_subtype,
            confidence
        )
        SELECT 
            NEW.graph_doc_id,
            parent_gd.graph_doc_id,
            'hierarchical',
            'parent',
            1.0
        FROM graph_documents parent_gd
        WHERE parent_gd.law_id = NEW.metadata->'hierarchy'->>'parent_id'
        ON CONFLICT DO NOTHING;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
CREATE TRIGGER trigger_auto_hierarchy_edges
AFTER INSERT OR UPDATE ON graph_documents
FOR EACH ROW
EXECUTE FUNCTION auto_create_hierarchy_edges();
```

Với trigger này → **TỰ ĐỘNG** tạo edges khi sync! ✅

---

**Bạn muốn tôi tạo trigger này không?** (5 phút là xong) 🚀
