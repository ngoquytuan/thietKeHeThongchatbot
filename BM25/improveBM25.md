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
