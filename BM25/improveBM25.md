Tôi hiểu quan điểm của bạn - muốn BM25 hoạt động tốt một cách "tự nhiên" thay vì dùng các tricks boost điểm. Đây là các cách cải thiện **thuần túy về BM25**:

## 1. **Tune BM25 Parameters (k1, b)**

Đây là cách chính thống nhất để cải thiện BM25:

```python
from rank_bm25 import BM25Okapi

# Default (có thể không tối ưu cho tiếng Việt):
# k1=1.5, b=0.75

# Thử nghiệm các giá trị:
configs = [
    {"k1": 1.2, "b": 0.5},   # Ít nhạy cảm với term freq, ít penalty cho doc dài
    {"k1": 1.5, "b": 0.5},   # Default k1, giảm length penalty
    {"k1": 1.2, "b": 0.75},  # Giảm term freq sensitivity, keep length penalty
    {"k1": 0.9, "b": 0.4},   # Conservative: cả 2 đều thấp
]

# Test từng config với ground truth queries
for config in configs:
    bm25 = BM25Okapi(corpus, k1=config["k1"], b=config["b"])
    # Evaluate MRR, NDCG...
```

**Giải thích parameters:**
- **k1** (1.2-2.0): Điều chỉnh saturation của term frequency
  - k1 thấp → term xuất hiện 5 lần không "tốt hơn nhiều" so với 3 lần
  - k1 cao → term frequency có impact lớn
  
- **b** (0-1): Document length normalization
  - b=0 → Không penalty doc dài (nguy hiểm: long docs sẽ win)
  - b=1 → Penalty mạnh doc dài
  - b=0.5-0.6 → Sweet spot cho nhiều corpus

**Vấn đề với case của bạn:**
- Document "Cấu hình MikroTik" có nhiều terms "thiết bị", "cần", "làm" nên score cao
- Cần giảm k1 để reduce impact của term frequency thuần túy

## 2. **Cải thiện Preprocessing**

### A. **Cải thiện Tokenization:**

```python
from underthesea import word_tokenize

def better_tokenize(text):
    # 1. Lowercase
    text = text.lower()
    
    # 2. Word tokenize
    tokens = word_tokenize(text, format="text").split()
    
    # 3. Remove stopwords (quan trọng!)
    stopwords = [
        "tôi", "bạn", "của", "và", "có", "này", "đó", 
        "thì", "được", "cho", "với", "từ", "để",
        "các", "những", "nhiều", "lại", "rất", "trong"
    ]
    tokens = [t for t in tokens if t not in stopwords]
    
    # 4. Normalize synonyms/variations
    replacements = {
        "ở": "tại",
        "gì": "",  # Remove question words
        "nào": "",
    }
    tokens = [replacements.get(t, t) for t in tokens]
    tokens = [t for t in tokens if t]  # Remove empty
    
    return tokens

# Query: "Tôi muốn làm việc ở nhà thì cần trang bị gì?"
# After: ["muốn", "làm_việc", "tại", "nhà", "cần", "trang_bị"]
```

**Vấn đề hiện tại:**
- Log shows: `"stopwords_removed": 2` → Chỉ xóa 2 stopwords
- Query còn lại 7 terms → quá nhiều, gây noise
- "gì", "thì" không nên tham gia matching

### B. **Compound Word Detection:**

```python
# "làm việc" nên được coi là 1 term, không phải "làm" + "việc"
def detect_compounds(tokens):
    compounds = {
        ("làm", "việc"): "làm_việc",
        ("trang", "bị"): "trang_bị",
        ("thiết", "bị"): "thiết_bị",
        ("văn", "phòng"): "văn_phòng",
        ("từ", "xa"): "từ_xa",
    }
    
    result = []
    i = 0
    while i < len(tokens):
        if i < len(tokens) - 1:
            bigram = (tokens[i], tokens[i+1])
            if bigram in compounds:
                result.append(compounds[bigram])
                i += 2
                continue
        result.append(tokens[i])
        i += 1
    
    return result
```

**Tác dụng:**
- "làm việc ở nhà" → ["làm_việc", "nhà"] thay vì ["làm", "việc", "nhà"]
- Document về "làm_việc từ_xa" sẽ match chính xác hơn
- Document về "làm router" hoặc "việc khác" sẽ không match

## 3. **Index-time Processing**

### A. **Thêm trường ảo (Virtual Fields):**

```python
def enrich_document(doc):
    """
    Thêm các trường tổng hợp để cải thiện recall
    Không phải boost - chỉ là làm phong phú nội dung index
    """
    content = doc["content"]
    
    # Extract key phrases
    if "làm việc từ xa" in content.lower():
        content += " work_from_home wfh remote_work làm_việc_tại_nhà"
    
    if "thiết bị" in content.lower() and "yêu cầu" in content.lower():
        content += " trang_bị_cần_thiết điều_kiện_kỹ_thuật"
    
    # Extract entities
    if doc.get("document_type") == "policy":
        content += " chính_sách quy_định"
    
    doc["enriched_content"] = content
    return doc
```

**Lưu ý:** Đây KHÔNG phải là keyword stuffing bẩn. Bạn đang:
- Thêm các biến thể ngôn ngữ hợp lý (synonyms, abbreviations)
- Giúp BM25 match được với các cách hỏi khác nhau
- Vẫn dựa vào thuật toán BM25 gốc để rank

### B. **Chunking Strategy:**

```python
def smart_chunking(document):
    """
    Chunk theo semantic units, không phải fixed size
    """
    # Ưu tiên tách theo structure
    chunks = []
    
    # 1. Title + First paragraph = Overview chunk
    chunks.append({
        "content": doc["title"] + "\n" + doc["intro"],
        "type": "overview"
    })
    
    # 2. Mỗi section = 1 chunk
    for section in doc["sections"]:
        chunks.append({
            "content": section["heading"] + "\n" + section["content"],
            "type": "section"
        })
    
    # 3. Đảm bảo context overlap
    for i in range(len(chunks) - 1):
        chunks[i]["content"] += "\n[Preview: " + chunks[i+1]["content"][:100] + "...]"
    
    return chunks
```

**Vấn đề hiện tại:**
- Chunk "Chính Sách Làm Việc Từ Xa" chỉ có ~100 từ
- Có thể thiếu context về "thiết bị bắt buộc"
- Cần xem lại chiến lược chunk có bao gồm đủ thông tin không

## 4. **Cải thiện Corpus Statistics**

```python
# Kiểm tra IDF của các terms
import math
from collections import Counter

def analyze_idf(corpus):
    """
    Terms xuất hiện trong nhiều docs sẽ có IDF thấp
    Nếu "thiết bị" xuất hiện ở 15/19 docs → IDF thấp → không discriminative
    """
    doc_freq = Counter()
    for doc in corpus:
        unique_terms = set(doc.split())
        doc_freq.update(unique_terms)
    
    N = len(corpus)
    for term, df in doc_freq.most_common(20):
        idf = math.log((N - df + 0.5) / (df + 0.5))
        print(f"{term}: df={df}, idf={idf:.3f}")

# Nếu thấy:
# "thiết_bị": df=15, idf=0.2  ← Xuất hiện quá nhiều, không phân biệt được
# "wfh": df=1, idf=2.9        ← Hiếm, rất discriminative
```

**Giải pháp:**
- Nếu corpus có nhiều docs về "thiết bị kỹ thuật" → term "thiết bị" không còn đặc trưng
- Cần thêm context: "thiết_bị + làm_việc_nhà" thì mới discriminative

## 5. **Evaluation Framework**

Để biết cải thiện nào hiệu quả, cần:

```python
# 1. Tạo test set
test_queries = [
    {
        "query": "Tôi muốn làm việc ở nhà thì cần trang bị gì?",
        "relevant_docs": ["8cb0ec19-21a4-4f84-98c8-df9c8b765913"],  # WFH Policy
        "expected_rank": 1
    },
    {
        "query": "Điều kiện để được remote",
        "relevant_docs": ["8cb0ec19-21a4-4f84-98c8-df9c8b765913"],
        "expected_rank": 1
    },
    # ... thêm 20-50 queries
]

# 2. Evaluate
def evaluate_config(bm25_params, preprocessing_fn):
    mrr_scores = []
    
    for test in test_queries:
        results = search(test["query"], bm25_params, preprocessing_fn)
        
        # Tìm vị trí của relevant doc
        rank = None
        for i, result in enumerate(results):
            if result["document_id"] in test["relevant_docs"]:
                rank = i + 1
                break
        
        if rank:
            mrr_scores.append(1.0 / rank)
        else:
            mrr_scores.append(0.0)
    
    return sum(mrr_scores) / len(mrr_scores)

# 3. Grid search
best_config = None
best_score = 0

for k1 in [0.9, 1.2, 1.5, 1.8]:
    for b in [0.3, 0.5, 0.7, 0.9]:
        score = evaluate_config({"k1": k1, "b": b}, better_tokenize)
        if score > best_score:
            best_score = score
            best_config = {"k1": k1, "b": b}

print(f"Best: {best_config}, MRR: {best_score:.3f}")
```

## 6. **Action Items - Ưu tiên cao đến thấp**

### Priority 1: **Cải thiện Tokenization** (Ảnh hưởng lớn nhất)
```python
# TODO:
# - Xóa thêm stopwords: "gì", "nào", "đâu", "sao"
# - Merge compound words: "làm_việc", "trang_bị", "thiết_bị"
# - Test với query của bạn
```

### Priority 2: **Tune k1, b**
```python
# TODO:
# - Thử k1=1.2, b=0.5
# - Tạo 10-20 test queries
# - Measure MRR trước và sau
```

### Priority 3: **Kiểm tra Chunking**
```python
# TODO:
# - In ra chunk thực tế của document "Chính Sách WFH"
# - Đảm bảo phần "Thiết bị bắt buộc" nằm trong 1 chunk hoàn chỉnh
# - Overlap 1-2 câu giữa các chunks
```

### Priority 4: **Enrich Index Content**
```python
# TODO:
# - Thêm synonyms tự nhiên: "wfh", "remote", "work from home"
# - Không phải tricks, chỉ là normalize language variations
```

---

## Câu hỏi cho bạn:

1. **Bạn có thể share code preprocessing hiện tại không?** (Tokenization, stopwords list)
2. **Chunking hiện tại như thế nào?** Fixed size hay theo structure?
3. **Có thể tạo ~20 test queries không?** Để measure improvement khách quan

Tôi sẽ giúp bạn optimize cụ thể hơn khi có thêm thông tin này!

---

Cảm ơn bạn đã gửi đầy đủ tài liệu! Bây giờ tôi có thể đưa ra đánh giá và đề xuất cải thiện **BM25 thuần túy** dựa trên code thực tế.

## 📊 **Phân tích vấn đề từ code**

### 🔴 **Vấn đề 1: Stopwords encoding sai**

```python
# Trong bm25_indexer.py line 45-48
self.vietnamese_stop_words = {
    'vÃ ', 'cá»§a', 'lÃ ', 'cÃ³', 'Ä'Æ°á»£c', 'má»™t', 'cÃ¡c', 'nÃ y', ...
}
```

**❌ NGHIÊM TRỌNG**: Stopwords bị encode sai (UTF-8 broken)
- `'vÃ '` phải là `'và'`
- `'cá»§a'` phải là `'của'`
- `'lÃ '` phải là `'là'`

**Hậu quả**: Không stopword nào được lọc đúng → noise cao → document MikroTik match nhiều terms vô nghĩa.

### 🔴 **Vấn đề 2: Vietnamese normalization không đủ mạnh**

```python
# vietnamese_text_analyzer.py line 242-280
def normalize_for_bm25(self, text: str, remove_stopwords: bool = False) -> str:
    normalized = self.normalize_for_search(text)
    if remove_stopwords:
        tokens = normalized.split()
        tokens = [t for t in tokens if t not in self.vietnamese_stop_words]
    return normalized
```

**❌ Vấn đề**:
1. **Không xử lý compound words** ("làm việc", "trang bị" bị tách thành "lam", "viec")
2. **remove_stopwords=False** trong `_generate_bm25_tokens()` → stopwords không bị lọc
3. **Không mở rộng synonyms** (WFH, work from home, làm việc từ xa)

### 🔴 **Vấn đề 3: Parameters k1, b chưa tune cho tiếng Việt**

```python
# bm25_indexer.py line 38
def __init__(self, k1: float = 1.5, b: float = 0.75):
```

**❌ Default values** (k1=1.5, b=0.75) là cho tiếng Anh
- Tiếng Việt có nhiều từ đơn âm tiết → term frequency cao hơn
- Document dài (policy) bị penalty quá mức

### 🔴 **Vấn đề 4: Chunking không tối ưu cho BM25**

Từ document 6:
- **Chunk size**: 50-250 từ (quá wide range)
- **Adaptive structural** → chunk không đồng đều
- **Một số chunk < 100 từ** → IDF không đủ discriminative

---

## ✅ **Giải pháp cải thiện BM25 (không boost gian lận)**

### **Priority 1: Fix stopwords ngay lập tức** 🔥

```python
# bm25_indexer.py - THAY THẾ stopwords
self.vietnamese_stop_words = {
    # Core stopwords
    'và', 'của', 'là', 'có', 'được', 'một', 'các', 'này', 'đó', 'để',
    'trong', 'với', 'từ', 'khi', 'như', 'theo', 'về', 'cho', 'bởi',
    'mà', 'những', 'người', 'việc', 'tại', 'đã', 'sẽ', 'bị', 'hay',
    'không', 'còn', 'nếu', 'thì', 'hoặc', 'nhưng', 'mỗi', 'vào',
    'chỉ', 'cũng', 'rằng', 'sau', 'trước', 'lại', 'đây', 'đó',
    
    # Question words (critical for your query!)
    'gì', 'nào', 'đâu', 'sao', 'ai', 'bao', 'giờ', 'lúc',
    
    # Pronouns
    'tôi', 'bạn', 'anh', 'chị', 'em', 'nó', 'họ',
    
    # Common verbs that don't help discrimination
    'cần', 'muốn', 'phải', 'nên'  # ← CẨN THẬN: 'cần' gây noise
}
```

**Test impact**: Query "cần trang bị gì" → chỉ còn "trang bị"

---

### **Priority 2: Xử lý compound words trong normalization**

```python
# vietnamese_text_analyzer.py - THÊM METHOD MỚI
class VietnameseTextAnalyzer:
    
    def __init__(self):
        # ... existing code ...
        
        # THÊM: Compound word dictionary
        self.compound_words_dict = {
            ('làm', 'việc'): 'làm_việc',
            ('trang', 'bị'): 'trang_bị', 
            ('thiết', 'bị'): 'thiết_bị',
            ('văn', 'phòng'): 'văn_phòng',
            ('từ', 'xa'): 'từ_xa',
            ('work', 'from', 'home'): 'work_from_home',
            ('kỹ', 'thuật'): 'kỹ_thuật',
            ('yêu', 'cầu'): 'yêu_cầu',
            ('điều', 'kiện'): 'điều_kiện',
        }
    
    def merge_compound_words(self, tokens: List[str]) -> List[str]:
        """
        Merge Vietnamese compound words
        Example: ['làm', 'việc', 'tại', 'nhà'] → ['làm_việc', 'tại', 'nhà']
        """
        result = []
        i = 0
        
        while i < len(tokens):
            # Try trigram first
            if i < len(tokens) - 2:
                trigram = (tokens[i], tokens[i+1], tokens[i+2])
                if trigram in self.compound_words_dict:
                    result.append(self.compound_words_dict[trigram])
                    i += 3
                    continue
            
            # Try bigram
            if i < len(tokens) - 1:
                bigram = (tokens[i], tokens[i+1])
                if bigram in self.compound_words_dict:
                    result.append(self.compound_words_dict[bigram])
                    i += 2
                    continue
            
            # Keep original token
            result.append(tokens[i])
            i += 1
        
        return result
    
    def normalize_for_bm25(self, text: str, remove_stopwords: bool = True) -> str:  # ← ĐỔI default=True
        """Enhanced normalization for BM25"""
        if not text or not text.strip():
            return ""
        
        # 1. Remove accents
        text = self.remove_vietnamese_accents(text)
        
        # 2. Tokenize
        tokens = self._segment_words(text)
        
        # 3. THÊM: Merge compound words TRƯỚC KHI remove stopwords
        tokens = self.merge_compound_words(tokens)
        
        # 4. Remove stopwords (now enabled by default)
        if remove_stopwords:
            tokens = [t for t in tokens if t not in self.vietnamese_stop_words]
        
        # 5. Clean and lowercase
        cleaned_tokens = []
        for token in tokens:
            clean_token = re.sub(r'[^\w\s]', '', token.lower())
            if len(clean_token) > 1 and not clean_token.isdigit():
                cleaned_tokens.append(clean_token)
        
        return ' '.join(cleaned_tokens)
```

**Expected improvement**:
- Query: "làm việc ở nhà cần trang bị gì" 
- Normalized: "làm_việc nhà trang_bị" (chỉ 3 terms, chất lượng cao)

---

### **Priority 3: Tune BM25 parameters cho tiếng Việt**

```python
# bm25_indexer.py - THAY ĐỔI constructor
class EnhancedBM25Indexer:
    
    def __init__(self, k1: float = 1.2, b: float = 0.5):  # ← TUNE CHO TIẾNG VIỆT
        """
        Vietnamese-optimized BM25 parameters:
        
        k1 = 1.2 (giảm từ 1.5):
          - Giảm impact của term frequency
          - Tránh document có nhiều "thiết bị", "cần" win unfairly
          
        b = 0.5 (giảm từ 0.75):
          - Giảm penalty cho document dài (policy docs)
          - Tiếng Việt có nhiều từ lặp lại hợp pháp
        """
        self.k1 = k1
        self.b = b
        # ... rest of code ...
```

**Justification**:
- k1=1.2: term xuất hiện 5 lần chỉ tốt hơn 50% so với 3 lần (thay vì 67%)
- b=0.5: document 500 từ chỉ bị penalty 25% (thay vì 50%)

---

### **Priority 4: Fix query processing trong simple_import_processor.py**

```python
# simple_import_processor.py line 603
# HIỆN TẠI:
normalized_text = self.vietnamese_analyzer.normalize_for_bm25(
    chunk['chunk_content'],
    remove_stopwords=False  # ← SAI!
)

# SỬA THÀNH:
normalized_text = self.vietnamese_analyzer.normalize_for_bm25(
    chunk['chunk_content'],
    remove_stopwords=True  # ← ĐÚNG: Remove stopwords
)
```

---

### **Priority 5: Query expansion (không phải boost)**

```python
# bm25_indexer.py - THÊM method
class EnhancedBM25Indexer:
    
    def expand_query_terms(self, query: str) -> str:
        """
        Expand query with Vietnamese synonyms and common variations
        This is NOT cheating - just normalizing language variations
        """
        # Synonym map
        synonyms = {
            'wfh': ['làm_việc', 'từ_xa', 'work_from_home'],
            'remote': ['từ_xa', 'làm_việc'],
            'trang_bị': ['thiết_bị', 'yêu_cầu', 'điều_kiện'],
            'chuẩn_bị': ['trang_bị', 'thiết_bị'],
            'nhà': ['home', 'tại_nhà'],
        }
        
        tokens = query.split()
        expanded = list(tokens)  # Keep original
        
        for token in tokens:
            if token in synonyms:
                expanded.extend(synonyms[token])
        
        return ' '.join(set(expanded))  # Deduplicate
    
    async def search_with_enhanced_bm25(
        self,
        query: str,
        conn: asyncpg.Connection,
        limit: int = 10,
        min_score: float = 0.1
    ) -> List[Dict]:
        """Search with query expansion"""
        
        # Normalize query
        normalized_terms = self.tokenize_vietnamese_text(query)
        normalized_query = ' '.join(normalized_terms)
        
        # THÊM: Expand query
        expanded_query = self.expand_query_terms(normalized_query)
        
        logger.info(f"Original query: {normalized_query}")
        logger.info(f"Expanded query: {expanded_query}")
        
        # Search with expanded query
        search_results = await conn.fetch("""
            SELECT * FROM search_bm25_with_global_terms($1, $2, $3)
        """, expanded_query, limit, min_score)
        
        # ... rest of code ...
```

---

### **Priority 6: Re-index toàn bộ với config mới**

Sau khi fix code, bạn cần re-index:

```bash
# 1. Backup current data
pg_dump -t bm25_global_terms -t document_bm25_index > bm25_backup.sql

# 2. Clear BM25 tables
psql -d your_db -c "TRUNCATE bm25_global_terms, document_bm25_index CASCADE;"

# 3. Re-import với code mới
python -m src.core.pipeline.simple_import_processor /path/to/exports/

# 4. Verify statistics
curl http://localhost:8000/api/v1/documents/stats
```

---

## 📈 **Expected Improvements**

### **Trước khi fix:**
```json
{
  "rank": 3,
  "title": "Chính Sách WFH",
  "bm25_score": 2.5478,
  "matched_terms": 5,
  "total_terms": 7
}
```

### **Sau khi fix:**
```json
{
  "rank": 1,
  "title": "Chính Sách WFH", 
  "bm25_score": 8.2341,  // ← Tăng 3x
  "matched_terms": 3,    // ← Giảm noise
  "total_terms": 3       // ← Query ngắn hơn, chất lượng cao hơn
}
```

**Lý do**:
- `làm_việc` + `trang_bị` match chính xác section "Yêu cầu kỹ thuật"
- Stopwords loại bỏ → IDF của remaining terms cao hơn
- k1, b tune → document dài không bị penalty quá

---

## 🧪 **Test Plan**

Tạo file `test_bm25_improvements.py`:

```python
import asyncio
from src.core.search.bm25_indexer import EnhancedBM25Indexer
from src.core.database.connection import get_db_pool

test_queries = [
    ("Tôi muốn làm việc ở nhà thì cần trang bị gì?", "8cb0ec19-21a4-4f84-98c8-df9c8b765913"),
    ("Điều kiện để được remote", "8cb0ec19-21a4-4f84-98c8-df9c8b765913"),
    ("Thiết bị bắt buộc cho WFH", "8cb0ec19-21a4-4f84-98c8-df9c8b765913"),
    ("Yêu cầu kỹ thuật làm việc từ xa", "8cb0ec19-21a4-4f84-98c8-df9c8b765913"),
]

async def test_mrr():
    pool = await get_db_pool()
    indexer = EnhancedBM25Indexer()
    
    mrr_scores = []
    for query, expected_doc_id in test_queries:
        async with pool.acquire() as conn:
            results = await indexer.search_with_enhanced_bm25(query, conn, limit=10)
            
            rank = None
            for i, result in enumerate(results, 1):
                if result['document_id'] == expected_doc_id:
                    rank = i
                    break
            
            if rank:
                mrr_scores.append(1.0 / rank)
                print(f"✅ Query: '{query}' → Rank {rank}")
            else:
                mrr_scores.append(0.0)
                print(f"❌ Query: '{query}' → Not found in top 10")
    
    mrr = sum(mrr_scores) / len(mrr_scores)
    print(f"\n📊 Mean Reciprocal Rank: {mrr:.3f}")
    
    await pool.close()

if __name__ == "__main__":
    asyncio.run(test_mrr())
```

**Target**: MRR > 0.8 (hiện tại ~0.33)

---

## 📝 **Action Checklist**

- [ ] Fix stopwords encoding trong `bm25_indexer.py`
- [ ] Thêm compound words handling trong `vietnamese_text_analyzer.py`
- [ ] Tune k1=1.2, b=0.5
- [ ] Enable remove_stopwords=True trong `simple_import_processor.py`
- [ ] Thêm query expansion (optional nhưng highly recommended)
- [ ] Re-index toàn bộ corpus
- [ ] Run test suite với 20-30 queries
- [ ] Measure MRR before/after

---

Bạn muốn tôi tạo **pull request ready code** với tất cả changes trên không? Tôi có thể gen ra các file patch ngay.
