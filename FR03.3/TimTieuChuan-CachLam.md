Câu hỏi này rất HAY và chạm đúng vào **nghiệp vụ khó nhất của RAG**! 🎯

Đây là case **khác hoàn toàn** với việc tìm căn cứ pháp lý. Để tôi phân tích chi tiết:

---

## **📋 Phân loại 2 nghiệp vụ khác nhau**

| Đặc điểm | **Tìm căn cứ pháp lý** | **Tìm tiêu chuẩn/cách làm** |
|----------|------------------------|----------------------------|
| **User biết gì?** | ✅ Biết văn bản nào (document_id) | ❓ KHÔNG biết ở văn bản nào |
| **User biết từ khóa?** | ✅ "Căn cứ", "Quyết định" | ❌ Không biết từ khóa chính xác |
| **Vị trí info** | ✅ Đầu văn bản (predictable) | ❌ Bất kỳ đâu trong corpus |
| **Cấu trúc** | ✅ Format chuẩn | ❌ Nhiều cách diễn đạt khác nhau |
| **Scope** | 🎯 1 document | 🌐 Toàn bộ corpus |
| **Độ khó** | ⭐⭐ Trung bình | ⭐⭐⭐⭐⭐ Rất khó |

---

## **🔍 Ví dụ thực tế về "Tìm tiêu chuẩn"**

### **User query:**
> "Mức sáng bao nhiêu là đạt chuẩn?"

### **Thách thức:**
1. ❌ Không biết từ khóa: "độ sáng"? "cường độ ánh sáng"? "lux"? "luminance"?
2. ❌ Không biết văn bản nào: Tiêu chuẩn xây dựng? ISO? TCVN? Nội bộ công ty?
3. ❌ Không biết format: "dưới 20%"? "< 200 lux"? "không đủ sáng"?
4. ❌ Thông tin có thể rải rác nhiều đoạn

---

## **🎯 Các Approach phù hợp**

### **❌ Approach KHÔNG phù hợp**

```python
# ❌ SAI: Filter theo document_id
semantic_search(
    query="mức sáng",
    document_id="xxx"  # ← User không biết document nào!
)

# ❌ SAI: Keyword search
keyword_search("mức sáng")  # ← Văn bản có thể dùng "độ sáng", "ánh sáng"

# ❌ SAI: BM25 
bm25_search("20%")  # ← Không biết chính xác số liệu
```

### **✅ Approach 1: Semantic Search Toàn Corpus + LLM** (Recommended)

```python
# Bước 1: Semantic search KHÔNG filter document_id
results = semantic_search(
    query="tiêu chuẩn độ sáng yêu cầu tối thiểu",
    top_k=30,  # Lấy nhiều để đảm bảo coverage
    # ✅ KHÔNG có document_id filter
)

# Bước 2: LLM reasoning
llm_prompt = f"""
Dựa trên các đoạn văn bản sau:

{results}

Câu hỏi: {user_query}

Nhiệm vụ:
1. Tìm các tiêu chuẩn về mức sáng
2. Trích dẫn CHÍNH XÁC số liệu và nguồn
3. Nếu có nhiều tiêu chuẩn khác nhau, liệt kê tất cả
4. Nếu KHÔNG tìm thấy, trả lời "Không tìm thấy trong tài liệu"
"""
```

**Ưu điểm:**
- ✅ Không cần biết document_id
- ✅ Không cần biết từ khóa chính xác
- ✅ LLM có thể reasoning từ nhiều chunks
- ✅ Có thể tìm thấy info dù diễn đạt khác

**Nhược điểm:**
- ⚠️ Có thể miss nếu diễn đạt quá khác (ví dụ: "illumination" thay vì "ánh sáng")
- ⚠️ Tốn token nếu top_k lớn

---

### **✅ Approach 2: Multi-Query Expansion**

Vì user không biết từ khóa chính xác, ta mở rộng query:

```python
# Bước 1: LLM expand query
expanded_queries = llm_expand_query(
    original_query="mức sáng bao nhiêu là đạt chuẩn?"
)
# Output:
# - "tiêu chuẩn độ sáng tối thiểu"
# - "cường độ ánh sáng yêu cầu"
# - "mức lux quy định"
# - "độ rọi tiêu chuẩn"

# Bước 2: Search với mỗi query
all_results = []
for query in expanded_queries:
    results = semantic_search(query, top_k=10)
    all_results.extend(results)

# Bước 3: Deduplicate và rank
final_results = deduplicate_and_rerank(all_results)

# Bước 4: LLM tổng hợp
answer = llm_synthesize(final_results, original_query)
```

**Ưu điểm:**
- ✅ ✅ Coverage tốt hơn (nhiều cách diễn đạt)
- ✅ Tìm được dù từ khóa khác hoàn toàn

**Nhược điểm:**
- ⚠️ Nhiều API calls hơn
- ⚠️ Tốn token nhiều

---

### **✅ Approach 3: Metadata-Guided Search**

Nếu metadata có tags tốt:

```python
# Bước 1: Filter theo metadata category
results = semantic_search(
    query="mức sáng",
    top_k=20,
    metadata_filters={
        "category": ["Tiêu chuẩn kỹ thuật", "Quy chuẩn"],
        "domain": ["Xây dựng", "Điện", "An toàn lao động"]
    }
)

# Bước 2: LLM extract
answer = llm_extract_standards(results)
```

**Ưu điểm:**
- ✅ Giảm noise (chỉ search trong tiêu chuẩn)
- ✅ Nhanh hơn

**Nhược điểm:**
- ⚠️ Cần metadata tốt (FR03.3 chỉ có 5% metadata)

---

### **✅ Approach 4: Hybrid với Substring cho số liệu**

Nếu user hỏi về số cụ thể:

```python
# User query: "Tôi có kết quả đo 18%, đạt chuẩn không?"

# Bước 1: Semantic search
semantic_results = semantic_search("tiêu chuẩn mức sáng", top_k=20)

# Bước 2: Substring search cho pattern số
pattern_results = substring_search(
    patterns=["20%", "< 20", "dưới 20", "trên 20"],
    filters={"category": "Tiêu chuẩn"}
)

# Bước 3: Merge
combined = merge_results(semantic_results, pattern_results)

# Bước 4: LLM reasoning
answer = llm_compare_with_standard(
    user_value=18,
    standard_chunks=combined
)
```

---

### **✅ Approach 5: Graph RAG (Nâng cao)**

Nếu tiêu chuẩn có hierarchy:

```
TCVN 123:2020 (Tiêu chuẩn tổng)
    ├─ Chương 3: Ánh sáng
    │   ├─ Điều 3.1: Nơi làm việc (> 300 lux)
    │   ├─ Điều 3.2: Hành lang (> 150 lux)
    └─ Chương 4: Nhiệt độ
```

```python
# Query graph
graph_results = graph_search(
    query="tiêu chuẩn ánh sáng",
    relation_types=["contains", "specifies"]
)

# LLM synthesize từ graph context
answer = llm_with_graph_context(graph_results)
```

**Ưu điểm:**
- ✅ ✅ Hiểu cấu trúc phân cấp
- ✅ Có thể trả lời "Áp dụng cho trường hợp nào?"

---

## **🎯 Đề xuất cho FR03.3**

Dựa trên hiện trạng FR03.3, tôi đề xuất **Approach 1 + 2 (Semantic + Multi-Query)**:

```python
async def find_technical_standard(
    user_query: str,
    specific_value: Optional[float] = None
) -> Dict[str, Any]:
    """
    Tìm tiêu chuẩn kỹ thuật trong corpus
    
    Args:
        user_query: "Mức sáng bao nhiêu là đạt?"
        specific_value: 18.5 (nếu user có giá trị cụ thể)
    """
    
    # Step 1: Expand query với LLM
    expanded_queries = await llm_expand_query(user_query)
    logger.info(f"Expanded to {len(expanded_queries)} queries")
    
    # Step 2: Search với mỗi query variant
    all_chunks = []
    for query in expanded_queries:
        chunks = await semantic_search(
            query=query,
            top_k=15,
            # ✅ KHÔNG filter document_id
        )
        all_chunks.extend(chunks)
    
    # Step 3: Deduplicate
    unique_chunks = deduplicate_by_chunk_id(all_chunks)
    
    # Step 4: Rerank theo relevance
    reranked = rerank_chunks(unique_chunks, user_query)
    top_chunks = reranked[:20]  # Lấy top 20 relevant nhất
    
    # Step 5: LLM extract và reasoning
    llm_prompt = f"""
Bạn là chuyên gia phân tích tiêu chuẩn kỹ thuật.

Các đoạn văn bản tìm được:
{format_chunks(top_chunks)}

Câu hỏi của người dùng: "{user_query}"
{"Giá trị cần kiểm tra: " + str(specific_value) if specific_value else ""}

Nhiệm vụ:
1. Tìm TẤT CẢ các tiêu chuẩn liên quan
2. Trích dẫn CHÍNH XÁC:
   - Số hiệu tiêu chuẩn (ví dụ: TCVN 123:2020)
   - Giá trị cụ thể (ví dụ: > 300 lux, < 20%)
   - Điều khoản (ví dụ: Điều 3.1)
3. Nếu user có giá trị cụ thể, so sánh và kết luận đạt/không đạt
4. Nếu có nhiều tiêu chuẩn áp dụng cho ngữ cảnh khác nhau, giải thích rõ
5. Nếu KHÔNG tìm thấy, trả lời: "Không tìm thấy tiêu chuẩn về [X] trong cơ sở dữ liệu"

Format output:
## Tiêu chuẩn tìm được:
1. [Tên tiêu chuẩn] - [Số hiệu]
   - Yêu cầu: [Giá trị cụ thể]
   - Nguồn: [Document title], [Chunk position]

## Kết luận:
[So sánh với giá trị user nếu có]
"""
    
    answer = await llm_call(llm_prompt)
    
    return {
        "query": user_query,
        "expanded_queries": expanded_queries,
        "chunks_found": len(top_chunks),
        "answer": answer,
        "sources": [format_source(c) for c in top_chunks]
    }
```

---

## **📊 So sánh approaches cho "Tìm tiêu chuẩn"**

| Approach | Coverage | Accuracy | Speed | Cost | Best for |
|----------|----------|----------|-------|------|----------|
| **Semantic only** | ⭐⭐⭐ | ⭐⭐⭐ | ⚡⚡ | 💰 | Query rõ ràng |
| **Multi-Query** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⚡ | 💰💰 | Query mơ hồ |
| **Metadata-Guided** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⚡⚡⚡ | 💰 | Có metadata tốt |
| **Hybrid** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⚡⚡ | 💰💰 | Có số liệu cụ thể |
| **Graph RAG** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⚡ | 💰💰💰 | Cấu trúc phức tạp |

---

## **💡 Test cases thực tế**

```python
# Test 1: Query mơ hồ
query = "Mức sáng bao nhiêu là đạt?"
# → Multi-Query approach

# Test 2: Query với số cụ thể
query = "18% có đạt chuẩn không?"
# → Hybrid (semantic + substring "18%", "< 20", "> 20")

# Test 3: Query về context cụ thể
query = "Mức sáng trong phòng làm việc"
# → Semantic + Metadata filter (category="Tiêu chuẩn xây dựng")

# Test 4: Không biết có hay không
query = "Có quy định về nhiệt độ không?"
# → Semantic search toàn corpus → LLM trả lời "Có/Không"
```

---

## **🎯 Kết luận**

Với nghiệp vụ **"Tìm tiêu chuẩn/cách làm"**, approach khác hoàn toàn:

| Đặc điểm | Tìm căn cứ pháp lý | Tìm tiêu chuẩn |
|----------|-------------------|----------------|
| **Scope** | 1 document (có document_id) | Toàn corpus |
| **Query expansion** | Không cần | ✅ RẤT CẦN |
| **Top_k** | 10-20 đủ | 30-50 để coverage |
| **LLM role** | Extract & format | Reasoning & compare |
| **Metadata filter** | Không cần | Hữu ích nếu có |
| **Reranking** | Không cần | ✅ CẦN để lọc noise |

**Đề xuất cho FR03.3:**
1. ✅ Implement Multi-Query Expansion
2. ✅ Increase top_k to 30-50
3. ✅ Add reranking layer
4. ✅ Improve LLM prompt cho reasoning
5. 🔮 Consider Graph RAG nếu có budget

Bạn muốn tôi code luôn workflow này không? 🚀
