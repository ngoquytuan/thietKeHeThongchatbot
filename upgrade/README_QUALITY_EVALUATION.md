# Hướng Dẫn Đánh Giá Chất Lượng Search - Sử Dụng Queries Thực Tế

## 📋 Tổng Quan

Bộ công cụ này giúp bạn đánh giá chất lượng search của FR03.3 bằng cách:
1. ✅ Tự động tạo test queries từ **dữ liệu thực tế** trong database
2. ✅ Chạy evaluation với queries phù hợp với domain của bạn
3. ✅ So sánh các search methods (semantic, BM25, keyword, hybrid)
4. ✅ Phát hiện vấn đề và đưa ra khuyến nghị cải thiện

## 🚀 Workflow - 3 Bước Đơn Giản

### **BƯỚC 1: Khám Phá Database và Tạo Test Queries** (5-10 phút)

```bash
python explore_database_for_test_queries.py
```

**Script này sẽ:**
- ✅ Thống kê tổng quan: số văn bản, số chunks
- ✅ Liệt kê các loại văn bản (Luật, Nghị định, Thông tư...)
- ✅ Liệt kê cơ quan ban hành (Quốc hội, Chính phủ, Bộ...)
- ✅ Tự động gợi ý test queries dựa trên data thực tế
- ✅ Tạo 2 files JSON:
  - `suggested_test_queries.json` - Gợi ý queries theo category
  - `gold_standard_template.json` - Template cho evaluation

**Output mẫu:**
```
==================================================
1. THỐNG KÊ TỔNG QUAN
==================================================
Tổng số văn bản: 12,345
Tổng số chunks: 67,890

==================================================
2. CÁC LOẠI VĂN BẢN (Top 20)
==================================================
Loại văn bản                              | Số lượng   | %
--------------------------------------------------------------------------------
Nghị định                                 |      3,456 | 28.0%
Thông tư                                  |      2,345 | 19.0%
Quyết định                                |      1,234 | 10.0%
...
```

### **BƯỚC 2: Review và Customize Test Queries** (10-15 phút)

Mở file `gold_standard_template.json` và review:

```json
[
  {
    "query": "Nghị định 01/2021/NĐ-CP",
    "expected_docs": ["Nghị định 01/2021/NĐ-CP"],
    "min_top1_score": 0.90,
    "category": "exact_lookup",
    "note": "Tìm chính xác: Nghị định 01/2021/NĐ-CP..."
  },
  {
    "query": "điều kiện thành lập công ty cổ phần",
    "expected_keywords": ["điều kiện", "thành lập", "công ty cổ phần"],
    "min_top1_score": 0.70,
    "category": "concept_search",
    "note": "Tìm theo khái niệm từ: Luật Doanh nghiệp..."
  }
]
```

**Bạn có thể:**
- ✅ Adjust `min_top1_score` cho phù hợp
- ✅ Thêm queries thủ công (ví dụ: queries mà users thường hỏi)
- ✅ Xóa queries không liên quan
- ✅ Thêm expected_docs cho accuracy check

**💡 Tip:** Nên có ít nhất 30-50 queries đa dạng để đánh giá đầy đủ.

### **BƯỚC 3: Chạy Evaluation** (5-10 phút)

#### **Option A: Quick Test (Test nhanh)**
```bash
python quick_quality_check.py health
```

Kiểm tra nhanh sức khỏe hệ thống với vài queries mẫu.

#### **Option B: Full Evaluation - Single Method**
```bash
python evaluate_search_quality_from_gold_standard.py
```

Đánh giá đầy đủ với hybrid search (default).

#### **Option C: Compare All Methods**
```bash
python evaluate_search_quality_from_gold_standard.py compare
```

So sánh tất cả methods: semantic, BM25, keyword, hybrid.

**Output mẫu:**
```
==================================================
KẾT QUẢ TỔNG HỢP
==================================================
Tổng số queries:     50
✅ Passed:           38 (76.0%)
❌ Failed:           12 (24.0%)

📊 Điểm trung bình:
   Top-1 Score:      0.723
   Top-3 Avg Score:  0.681

📂 PHÂN TÍCH THEO CATEGORY:
Category                  | Pass/Total   | Rate   | Top-1  | Top-3
--------------------------------------------------------------------------------
exact_lookup              |  15/ 15      | 100.0% | 0.892  | 0.854
concept_search            |  18/ 25      |  72.0% | 0.698  | 0.651
type_search               |   5/ 10      |  50.0% | 0.612  | 0.578
```

---

## 📊 Hiểu Kết Quả Evaluation

### **Metrics Quan Trọng:**

| Metric | Good | Acceptable | Needs Work |
|--------|------|------------|------------|
| **Pass Rate** | > 80% | 60-80% | < 60% |
| **Top-1 Score** | > 0.75 | 0.60-0.75 | < 0.60 |
| **Top-3 Avg** | > 0.70 | 0.55-0.70 | < 0.55 |

### **Categories:**

1. **exact_lookup** - Tìm theo số hiệu chính xác
   - Expected: Top-1 Score > 0.90
   - Nếu thấp → Vấn đề với exact matching hoặc metadata

2. **concept_search** - Tìm theo khái niệm
   - Expected: Top-1 Score > 0.70
   - Nếu thấp → Embedding model yếu hoặc chunking không tốt

3. **type_search** - Tìm theo loại văn bản
   - Expected: Top-1 Score > 0.65
   - Nếu thấp → Metadata filtering cần cải thiện

4. **issuing_body_search** - Tìm theo cơ quan ban hành
   - Expected: Top-1 Score > 0.65
   - Nếu thấp → Metadata cần chuẩn hóa

---

## 🔧 Tools Bổ Sung

### **Quick Test Một Query:**
```bash
python quick_quality_check.py "luật doanh nghiệp 2020" hybrid
```

### **So Sánh Methods Cho Một Query:**
```bash
python quick_quality_check.py compare "điều kiện thành lập công ty"
```

Output:
```
==================================================
BẢNG SO SÁNH
==================================================
Method       | Top-1 Score  | Top-3 Avg    | Results
--------------------------------------------------------------------------------
semantic     |        0.805 |        0.762 |        8
bm25         |        0.678 |        0.623 |       10
keyword      |        0.534 |        0.501 |        5
hybrid       |        0.646 |        0.612 |       10

⚠️  WARNING: Hybrid (0.646) < Semantic (0.805)
   Gap: 0.159 points (19.8% worse)
   → Hybrid weights cần được tối ưu!
```

---

## 🎯 Recommended Actions Dựa Trên Kết Quả

### **Nếu Pass Rate < 60%:**
1. Xem chi tiết failed queries
2. Tìm patterns (loại queries nào fail nhiều?)
3. Cải thiện cho category fail nhiều nhất

### **Nếu Hybrid < Semantic:**
1. Review hybrid weights trong `src/api/main.py`
2. Thử config:
   ```python
   semantic_weight = 0.6  # Tăng vì semantic tốt
   bm25_weight = 0.3
   keyword_weight = 0.1
   ```
3. Re-test và compare

### **Nếu Top-1 Score < 0.60:**
1. Kiểm tra embedding model quality
2. Review document chunking strategy
3. Xem xét fine-tune hoặc đổi model

### **Nếu Zero-result Rate > 10%:**
1. Phân tích queries không có kết quả
2. Thêm content cho missing topics
3. Cải thiện query preprocessing

---

## 📁 Files Tạo Ra

### **Input Files:**
- `gold_standard_template.json` - Test queries (bạn customize)

### **Output Files:**
- `eval_semantic.json` - Kết quả semantic search
- `eval_bm25.json` - Kết quả BM25
- `eval_keyword.json` - Kết quả keyword search
- `eval_hybrid.json` - Kết quả hybrid
- `evaluation_results_hybrid_YYYYMMDD_HHMMSS.json` - Kết quả chi tiết

---

## 🔄 Workflow Lặp Lại (Iterative Improvement)

```
1. Run evaluation → Identify issues
   ↓
2. Make improvements (weights, chunking, etc.)
   ↓
3. Re-run evaluation → Measure improvement
   ↓
4. Repeat until quality targets met
```

---

## 💡 Tips & Best Practices

1. **Tạo queries đa dạng:**
   - Mix exact lookups, concepts, và edge cases
   - Include queries với/không dấu
   - Include abbreviations và formal names

2. **Set realistic thresholds:**
   - `exact_lookup`: 0.90+ (strict)
   - `concept_search`: 0.70+ (moderate)
   - `edge_cases`: 0.50+ (lenient)

3. **Iterate regularly:**
   - Run evaluation weekly
   - Track improvements over time
   - Adjust queries based on real user feedback

4. **Use real user queries:**
   - Mine từ search logs
   - Prioritize high-frequency queries
   - Include queries that failed in production

---

## ❓ FAQ

**Q: Cần bao nhiêu test queries?**
A: Minimum 30, recommended 50-100 queries đa dạng.

**Q: Gold standard template có thể edit sau không?**
A: Có! Bạn nên update thường xuyên dựa trên user feedback.

**Q: Nếu hybrid luôn tệ hơn semantic?**
A: Review weights. Thử tăng semantic_weight lên 0.6-0.7.

**Q: Evaluation mất bao lâu?**
A: ~1-2 giây/query. 50 queries ≈ 2 phút (với rate limiting).

---

## 📞 Next Steps

Sau khi có evaluation results:

1. **Phân tích chi tiết** failed queries
2. **Identify patterns** - queries nào fail nhiều?
3. **Prioritize fixes** - fix high-impact issues trước
4. **Re-evaluate** - measure improvement
5. **Document findings** - track progress

---

**Chúc bạn đánh giá thành công! 🚀**
