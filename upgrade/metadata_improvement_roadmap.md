# LỘ TRÌNH CẢI THIỆN METADATA — TỪ GỐC RỄ ĐẾN ĐỘT PHÁ
## ATTECH RAG Knowledge Assistant — Giải quyết "nợ kỹ thuật" metadata

**Ngày lập:** 12/02/2026  
**Người thực hiện:** Technical Lead  
**Thời gian tổng:** 6 tuần (chia 4 giai đoạn)  

---

## 1. CHẨN ĐOÁN: VẤN ĐỀ THỰC SỰ LÀ GÌ?

### Vòng lặp bế tắc hiện tại

```
Upload docs → metadata trống/sai → sửa thủ công (nhưng không kịp)
     ↓                                        ↓
Graph RAG trống (0 edges)              Metadata Search vô dụng
     ↓                                        ↓
Không có cross-reference              Hybrid Search thiếu 1 chân
     ↓                                        ↓
RAG chỉ dựa vào Semantic Search → accuracy bị giới hạn ~75%
```

### Bảng hiện trạng metadata (dựa trên project knowledge)

| Field trong JSONB | Có dữ liệu? | Chất lượng | Ảnh hưởng |
|---|---|---|---|
| `identification.document_number` | ~60% docs | Trung bình | Substring/Metadata Search |
| `identification.document_type` | ~70% docs | Tốt | Filter, routing |
| `identification.issue_date` | ~30% docs | Kém — nhiều NULL | Timeline, freshness ranking |
| `authority.organization` | ~20% docs | Rất kém — hầu hết "General" | Graph RAG, filter |
| `authority.department` | ~10% docs | Rất kém | RBAC, department filter |
| `domain.category` | ~50% docs | Trung bình | Graph RAG edges, routing |
| `domain.keywords` | ~30% docs | Kém — nhiều empty arrays | Graph RAG edges, search boost |
| `relationships.based_on` | ~15% docs | Rất kém — chứa text thay vì law_id | Graph RAG — BLOCKED |
| `relationships.relates_to` | ~5% docs | Gần như trống | Graph RAG — BLOCKED |
| `hierarchy.parent_id` | ~10% docs | Sai format (string thay vì UUID) | Parent-child links — BROKEN |
| `financial.budget` | ~40% docs | Trung bình | Filter (ít dùng) |

### Gốc rễ: Metadata kém KHÔNG phải vì thiếu schema

Schema metadata JSONB đã thiết kế tốt (v3.0/v3.1 với identification, authority, domain, 
relationships, financial, content_stats...). Vấn đề nằm ở 3 chỗ:

1. **FR-03.1 (Document Processing)** — document.json được tạo với metadata sơ sài. 
   Extraction logic dựa vào regex đơn giản, không đủ cho Vietnamese legal docs.

2. **Không có validation gate** — Documents đi thẳng từ FR-03.1 → FR-03.3 (import) 
   mà không kiểm tra metadata completeness. FR-03.2 Quality Control là mock service.

3. **Không có enrichment pipeline** — Sau khi import, không có cơ chế tự động bổ sung 
   metadata từ content analysis.

---

## 2. NGUYÊN TẮC TIẾP CẬN

### Không cố sửa hết metadata cùng lúc

Với 42 docs hiện tại thì sửa tay được. Nhưng target 100K docs thì bắt buộc phải tự động.
Lộ trình đi từ "manual fix cho data hiện có" → "semi-auto cho data mới" → "full-auto pipeline".

### Ưu tiên theo impact lên search quality

Không phải field nào cũng quan trọng ngang nhau. Thứ tự impact:

```
CRITICAL (trực tiếp ảnh hưởng search):
  1. document_number (law_id) — Substring Search, Metadata Search
  2. keywords                 — Graph RAG edges, search boosting
  3. category                 — Graph RAG edges, query routing
  4. issue_date               — Freshness ranking, timeline queries
  5. relationships.based_on   — Graph RAG cross-reference

HIGH (ảnh hưởng filtering/RBAC):
  6. organization             — Authority filter, Graph RAG
  7. department               — RBAC filtering
  8. document_type            — Query routing

MEDIUM (nice-to-have):
  9. parent_id hierarchy      — Parent-child navigation
  10. financial data          — Specialized queries
```

---

## 3. LỘ TRÌNH 4 GIAI ĐOẠN

```
Tuần 1-2          Tuần 3           Tuần 4           Tuần 5-6
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ GĐ 1     │    │ GĐ 2     │    │ GĐ 3     │    │ GĐ 4     │
│ Audit &  │ →  │ Auto     │ →  │ Tích hợp │ →  │ Graph    │
│ Manual   │    │ Enrichment│    │ vào Search│    │ RAG Live │
│ Fix      │    │ Pipeline  │    │ Algorithms│    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
  Nền tảng        Tự động hóa     Khai thác        Đột phá
```

---

### GIAI ĐOẠN 1: AUDIT & MANUAL FIX (Tuần 1-2)

**Mục tiêu:** Biết chính xác hiện trạng, sửa data hiện có, tạo "ground truth" cho testing

#### Bước 1.1: Chạy Metadata Audit Script (Ngày 1)

Tạo script đánh giá completeness cho toàn bộ database:

```python
# scripts/audit_metadata_completeness.py
"""
Audit toàn bộ metadata trong documents_metadata_v2.
Output: Báo cáo chi tiết từng document, tổng hợp theo field.
"""

import asyncio
import asyncpg
import json
from collections import defaultdict

CRITICAL_FIELDS = {
    # path trong JSONB → tên hiển thị → validator function
    ("identification", "document_number"): {
        "name": "Số hiệu văn bản",
        "validate": lambda v: bool(v) and len(str(v).strip()) > 2,
        "impact": "CRITICAL"
    },
    ("identification", "document_type"): {
        "name": "Loại văn bản", 
        "validate": lambda v: bool(v) and v not in ("unknown", "other", ""),
        "impact": "HIGH"
    },
    ("identification", "issue_date"): {
        "name": "Ngày ban hành",
        "validate": lambda v: bool(v) and v != "null" and len(str(v)) >= 8,
        "impact": "CRITICAL"
    },
    ("authority", "organization"): {
        "name": "Cơ quan ban hành",
        "validate": lambda v: bool(v) and v.lower() not in ("general", "unknown", ""),
        "impact": "HIGH"
    },
    ("authority", "department"): {
        "name": "Phòng ban",
        "validate": lambda v: bool(v) and v.lower() not in ("general", "unknown", ""),
        "impact": "HIGH"
    },
    ("domain", "category"): {
        "name": "Lĩnh vực",
        "validate": lambda v: bool(v) and v not in ("unknown", "other", ""),
        "impact": "CRITICAL"
    },
    ("domain", "keywords"): {
        "name": "Từ khóa",
        "validate": lambda v: isinstance(v, list) and len(v) >= 2,
        "impact": "CRITICAL"
    },
    ("relationships", "based_on"): {
        "name": "Căn cứ pháp lý",
        "validate": lambda v: isinstance(v, list) and len(v) > 0,
        "impact": "CRITICAL"
    },
    ("relationships", "relates_to"): {
        "name": "Văn bản liên quan",
        "validate": lambda v: isinstance(v, list) and len(v) > 0,
        "impact": "MEDIUM"
    },
}

async def audit_metadata():
    conn = await asyncpg.connect(
        host="192.168.1.70", port=5432,
        database="knowledge_base_v2",
        user="kb_admin", password="1234567890"
    )
    
    rows = await conn.fetch("""
        SELECT document_id, title, metadata 
        FROM documents_metadata_v2 
        ORDER BY title
    """)
    
    # Per-document report
    doc_reports = []
    # Aggregate stats
    field_stats = defaultdict(lambda: {"total": 0, "valid": 0, "invalid_docs": []})
    
    for row in rows:
        meta = json.loads(row["metadata"]) if row["metadata"] else {}
        doc_report = {
            "document_id": str(row["document_id"]),
            "title": row["title"][:80],
            "missing_fields": [],
            "invalid_fields": [],
            "completeness_score": 0
        }
        
        valid_count = 0
        total_fields = len(CRITICAL_FIELDS)
        
        for (section, field), config in CRITICAL_FIELDS.items():
            field_key = f"{section}.{field}"
            stat = field_stats[field_key]
            stat["total"] += 1
            
            # Extract value
            value = None
            if section in meta and isinstance(meta[section], dict):
                value = meta[section].get(field)
            
            # Validate
            is_valid = config["validate"](value)
            if is_valid:
                stat["valid"] += 1
                valid_count += 1
            else:
                stat["invalid_docs"].append(row["title"][:50])
                if value is None or value == "" or value == []:
                    doc_report["missing_fields"].append(config["name"])
                else:
                    doc_report["invalid_fields"].append(
                        f"{config['name']}: '{value}'"
                    )
        
        doc_report["completeness_score"] = round(
            valid_count / total_fields * 100, 1
        )
        doc_reports.append(doc_report)
    
    await conn.close()
    
    # Print report
    print("=" * 80)
    print("METADATA COMPLETENESS AUDIT REPORT")
    print(f"Total documents: {len(rows)}")
    print("=" * 80)
    
    # Field-level summary
    print("\n📊 FIELD COMPLETENESS SUMMARY:\n")
    print(f"{'Field':<35} {'Valid':<8} {'Total':<8} {'Rate':<8} {'Impact'}")
    print("-" * 75)
    
    for (section, field), config in CRITICAL_FIELDS.items():
        key = f"{section}.{field}"
        stat = field_stats[key]
        rate = stat["valid"] / max(stat["total"], 1) * 100
        status = "✅" if rate >= 80 else "⚠️" if rate >= 50 else "❌"
        print(
            f"{status} {config['name']:<32} "
            f"{stat['valid']:<8} {stat['total']:<8} "
            f"{rate:>5.1f}%   {config['impact']}"
        )
    
    # Per-document detail
    print(f"\n📋 DOCUMENTS BY COMPLETENESS:\n")
    doc_reports.sort(key=lambda x: x["completeness_score"])
    
    for doc in doc_reports:
        score = doc["completeness_score"]
        status = "✅" if score >= 80 else "⚠️" if score >= 50 else "❌"
        print(f"{status} [{score:>5.1f}%] {doc['title']}")
        if doc["missing_fields"]:
            print(f"         Missing: {', '.join(doc['missing_fields'])}")
        if doc["invalid_fields"]:
            print(f"         Invalid: {', '.join(doc['invalid_fields'][:3])}")
    
    # Overall score
    avg_score = sum(d["completeness_score"] for d in doc_reports) / len(doc_reports)
    print(f"\n{'=' * 80}")
    print(f"OVERALL METADATA COMPLETENESS: {avg_score:.1f}%")
    print(f"Target: ≥80%")
    print(f"{'=' * 80}")
    
    return doc_reports, field_stats

if __name__ == "__main__":
    asyncio.run(audit_metadata())
```

**Output mong đợi:** Biết chính xác field nào thiếu bao nhiêu %, document nào tệ nhất.

#### Bước 1.2: Manual Fix cho 42 documents hiện có (Ngày 2-5)

Vì chỉ có 42 docs, manual fix là feasible và tạo ra "gold standard" dataset.

**Phương pháp: Dùng Metadata Editor đã có** (port 8005) kết hợp SQL scripts.

```sql
-- FIX 1: Department — thay "General" bằng giá trị đúng
-- Trích từ authority.organization hoặc content analysis
UPDATE documents_metadata_v2
SET metadata = jsonb_set(
    metadata,
    '{authority,department}',
    '"Phòng Nghiên cứu Phát triển"'::jsonb
)
WHERE title ILIKE '%DTCT%' OR title ILIKE '%nghiên cứu%';

-- FIX 2: Organization — thay "General" 
UPDATE documents_metadata_v2
SET metadata = jsonb_set(
    metadata,
    '{authority,organization}',
    '"Công ty ATTECH"'::jsonb
)
WHERE metadata->'authority'->>'organization' IN ('General', '', NULL);

-- FIX 3: Issue date — trích từ document_number pattern
-- Ví dụ: "265/2025/NĐ-CP" → year 2025
UPDATE documents_metadata_v2
SET metadata = jsonb_set(
    metadata,
    '{identification,issue_date}',
    ('"2025-01-01"')::jsonb
)
WHERE metadata->'identification'->>'document_number' LIKE '%/2025/%'
  AND (metadata->'identification'->>'issue_date') IS NULL;

-- FIX 4: Relationships — fix governing_laws chứa text thay vì law_id
-- Phải làm từng doc vì mỗi doc có based_on khác nhau
-- Dùng Metadata Editor UI cho phần này

-- FIX 5: Parent ID — convert string → UUID
UPDATE documents_metadata_v2 d1
SET metadata = jsonb_set(
    d1.metadata,
    '{hierarchy,parent_id}',
    to_jsonb(d2.document_id::text)
)
FROM documents_metadata_v2 d2
WHERE d1.metadata->'hierarchy'->>'parent_id' = 
      d2.metadata->'identification'->>'document_number'
  AND d1.metadata->'hierarchy'->>'parent_id' IS NOT NULL;
```

**Checklist cho mỗi document:**
- [ ] document_number chính xác (VD: "265/2025/NĐ-CP")
- [ ] document_type đúng (nghi_dinh, quyet_dinh, thong_tu, luat...)
- [ ] issue_date có (YYYY-MM-DD format)
- [ ] organization là tên cơ quan thực (không phải "General")
- [ ] category đúng lĩnh vực (tai_chinh, lao_dong, hanh_chinh...)
- [ ] keywords có ít nhất 3-5 từ khóa relevant
- [ ] based_on chứa law_id (không phải text snippet)

#### Bước 1.3: Chạy lại Graph RAG sau khi fix (Ngày 5-6)

```bash
# Sau khi metadata đã clean:
python populate_graph_correct.py    # Sync docs → graph_documents
python create_semantic_links.py     # Tạo edges dựa trên metadata mới
python validate_graph_links.py      # Verify

# Kỳ vọng: từ 0 edges → 300-500 edges (gần target 507)
```

#### Bước 1.4: Tạo test dataset (Ngày 6-7)

```python
# scripts/create_metadata_test_dataset.py
"""
Tạo 20 test queries + expected metadata filters để đo impact.
"""

TEST_QUERIES = [
    {
        "query": "quy định nghỉ phép năm",
        "expected_metadata": {
            "category": "lao_dong",
            "document_type": "luat",
            "keywords_should_contain": ["nghỉ phép", "lao động"]
        },
        "expected_top3_law_ids": ["45/2019/QH14"]  # Bộ luật Lao động
    },
    {
        "query": "265/2025/NĐ-CP",
        "expected_metadata": {
            "document_number": "265/2025/NĐ-CP"
        },
        "expected_top1_exact": True
    },
    {
        "query": "quy định an toàn hàng không do Bộ GTVT ban hành",
        "expected_metadata": {
            "category": "hang_khong",
            "organization": "Bộ Giao thông Vận tải"
        }
    },
    # ... 17 queries nữa covering các scenarios
]
```

**Deliverable Giai đoạn 1:**
- ✅ Audit report: biết chính xác % completeness mỗi field
- ✅ 42 documents có metadata clean (≥80% completeness)
- ✅ Graph RAG có edges thực (300-500 edges)
- ✅ Test dataset 20 queries để đo improvement

---

### GIAI ĐOẠN 2: AUTO-ENRICHMENT PIPELINE (Tuần 3)

**Mục tiêu:** Khi import document mới, metadata được tự động trích xuất và bổ sung — 
không cần sửa tay nữa.

#### Kiến trúc: Metadata Enrichment Service

```
TRƯỚC (hiện tại):
FR-03.1 tạo document.json (metadata sơ sài)
    → FR-03.3 import nguyên vào DB
    → metadata trống → sửa tay

SAU (target):
FR-03.1 tạo document.json (metadata sơ sài)
    → ⭐ MetadataEnricher (auto-extract từ content)
    → ⭐ MetadataValidator (kiểm tra completeness)
    → FR-03.3 import vào DB (metadata đầy đủ)
    → Graph links tự động tạo
```

#### Vị trí trong codebase

```
FR-03.3/
├── src/
│   ├── core/
│   │   ├── metadata/                    # ⭐ THƯ MỤC MỚI
│   │   │   ├── __init__.py
│   │   │   ├── enricher.py              # Auto-extraction từ content
│   │   │   ├── validator.py             # Kiểm tra completeness
│   │   │   ├── legal_code_extractor.py  # Extract law_id patterns
│   │   │   └── keyword_extractor.py     # Vietnamese keyword extraction
│   │   ├── search/                      # Có sẵn
│   │   └── database/                    # Có sẵn
│   └── ...
```

#### Bước 2.1: Legal Code Extractor (Ngày 1-2)

Đây là component có ROI cao nhất — trích xuất chính xác mã số văn bản pháp luật.

```python
# src/core/metadata/legal_code_extractor.py
"""
Trích xuất mã văn bản pháp luật từ nội dung Vietnamese legal documents.

Patterns recognized:
  - Luật số: 45/2019/QH14
  - Nghị định: 265/2025/NĐ-CP, 76/2018/NĐ-CP
  - Thông tư: 01/2024/TT-BTC
  - Quyết định: 737/QĐ-CQĐHQ
  - Công văn: 1234/CV-VPCP
  - Nghị quyết: 01/NQ-CP
"""

import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class LegalReference:
    """Một tham chiếu văn bản pháp luật được trích xuất."""
    law_id: str                    # "265/2025/NĐ-CP"
    law_type: str                  # "nghi_dinh"
    issuing_body_code: str         # "CP" (Chính phủ)
    issuing_body_full: str         # "Chính phủ"
    year: Optional[int]            # 2025
    context: str                   # Câu chứa reference
    position: int                  # Vị trí trong text


# Mapping mã cơ quan → tên đầy đủ
ISSUING_BODY_MAP = {
    "QH": "Quốc hội",
    "CP": "Chính phủ",
    "TTg": "Thủ tướng Chính phủ",
    "BTC": "Bộ Tài chính",
    "BGTVT": "Bộ Giao thông Vận tải",
    "BCA": "Bộ Công an",
    "BQP": "Bộ Quốc phòng",
    "BKHCN": "Bộ Khoa học và Công nghệ",
    "BLĐTBXH": "Bộ Lao động Thương binh và Xã hội",
    "BTNMT": "Bộ Tài nguyên và Môi trường",
    "BCT": "Bộ Công Thương",
    "BXD": "Bộ Xây dựng",
    "BNN": "Bộ Nông nghiệp",
    "BYT": "Bộ Y tế",
    "BGDĐT": "Bộ Giáo dục và Đào tạo",
    "VPCP": "Văn phòng Chính phủ",
    "CQĐHQ": "Cơ quan Đại diện Hàng không",
    # ... thêm theo nhu cầu ATTECH
}

# Mapping prefix → loại văn bản
LAW_TYPE_MAP = {
    "NĐ": "nghi_dinh",
    "TT": "thong_tu",
    "QĐ": "quyet_dinh",
    "NQ": "nghi_quyet",
    "CV": "cong_van",
    "CT": "chi_thi",
    "QH": "luat",
    "VBHN": "van_ban_hop_nhat",
}

# Regex patterns cho Vietnamese legal codes
# KHÔNG preprocess — giữ nguyên format gốc
LEGAL_CODE_PATTERNS = [
    # Pattern 1: Số/Năm/Loại-Cơ quan (phổ biến nhất)
    # VD: 265/2025/NĐ-CP, 01/2024/TT-BTC, 76/2018/NĐ-CP
    re.compile(
        r'(\d{1,4})/(\d{4})/(NĐ|TT|QĐ|NQ|CT|VBHN)-([A-ZĐÀ-Ỹa-zđà-ỹ&]+)',
        re.UNICODE
    ),
    
    # Pattern 2: Số/Loại-Cơ quan (không có năm)
    # VD: 737/QĐ-CQĐHQ, 1234/CV-VPCP
    re.compile(
        r'(\d{1,5})/(QĐ|CV|CT|NQ|TB)-([A-ZĐÀ-Ỹa-zđà-ỹ&]+)',
        re.UNICODE
    ),
    
    # Pattern 3: Luật số XX/YYYY/QHXX
    # VD: 45/2019/QH14
    re.compile(
        r'(\d{1,3})/(\d{4})/(QH\d{1,2})',
        re.UNICODE
    ),
    
    # Pattern 4: Số hiệu nội bộ ATTECH
    # VD: DTCT.2024.05, QT.ATTECH.001
    re.compile(
        r'([A-ZĐ]{2,6})\.(\d{4})\.(\d{2,3})',
        re.UNICODE
    ),
]


class LegalCodeExtractor:
    """Trích xuất mã văn bản pháp luật từ text."""
    
    def extract_all_references(self, text: str) -> List[LegalReference]:
        """
        Tìm tất cả mã văn bản trong text.
        
        Ưu điểm so với approach cũ (NER/regex đơn giản):
        - Không preprocess text (giữ nguyên dấu, format gốc)
        - Phân loại được loại văn bản và cơ quan ban hành
        - Trả về context (câu chứa reference) để verify
        """
        references = []
        seen = set()  # Deduplicate
        
        for pattern in LEGAL_CODE_PATTERNS:
            for match in pattern.finditer(text):
                law_id = match.group(0)
                
                if law_id in seen:
                    continue
                seen.add(law_id)
                
                ref = self._parse_match(match, text)
                if ref:
                    references.append(ref)
        
        return references
    
    def extract_document_own_id(self, text: str, title: str) -> Optional[str]:
        """
        Trích xuất mã của chính document này (không phải reference).
        Thường xuất hiện trong tiêu đề hoặc dòng đầu tiên.
        """
        # Ưu tiên tìm trong title
        refs = self.extract_all_references(title)
        if refs:
            return refs[0].law_id
        
        # Fallback: tìm trong 500 ký tự đầu
        first_part = text[:500]
        refs = self.extract_all_references(first_part)
        if refs:
            return refs[0].law_id
        
        return None
    
    def extract_based_on_references(self, text: str) -> List[str]:
        """
        Trích xuất danh sách văn bản được viện dẫn (căn cứ pháp lý).
        
        Tìm trong các đoạn bắt đầu bằng:
        - "Căn cứ..."
        - "Theo quy định tại..."
        - "Thực hiện theo..."
        """
        based_on = []
        
        # Tìm đoạn "Căn cứ" (thường ở đầu văn bản pháp luật)
        cancu_pattern = re.compile(
            r'[Cc]ăn\s+cứ[^;.]*?(?:;|\.|\n)',
            re.UNICODE | re.DOTALL
        )
        
        for cancu_match in cancu_pattern.finditer(text[:3000]):  # Chỉ xét 3000 ký tự đầu
            cancu_text = cancu_match.group(0)
            refs = self.extract_all_references(cancu_text)
            for ref in refs:
                if ref.law_id not in based_on:
                    based_on.append(ref.law_id)
        
        return based_on
    
    def _parse_match(self, match, full_text: str) -> Optional[LegalReference]:
        """Parse regex match thành LegalReference."""
        law_id = match.group(0)
        groups = match.groups()
        
        # Detect law_type và issuing_body
        law_type = "unknown"
        issuing_code = ""
        year = None
        
        # Pattern 1: số/năm/loại-cơ quan
        if len(groups) >= 4 and groups[1].isdigit():
            year = int(groups[1])
            type_code = groups[2]
            issuing_code = groups[3]
            law_type = LAW_TYPE_MAP.get(type_code, "unknown")
        
        # Pattern 2: số/loại-cơ quan
        elif len(groups) >= 3 and not groups[1].isdigit():
            type_code = groups[1]
            issuing_code = groups[2]
            law_type = LAW_TYPE_MAP.get(type_code, "unknown")
        
        # Pattern 3: QH
        elif len(groups) >= 3 and "QH" in groups[2]:
            year = int(groups[1])
            law_type = "luat"
            issuing_code = groups[2]
        
        # Extract context (câu chứa reference)
        start = max(0, match.start() - 50)
        end = min(len(full_text), match.end() + 50)
        context = full_text[start:end].strip()
        
        issuing_full = ISSUING_BODY_MAP.get(issuing_code, issuing_code)
        
        return LegalReference(
            law_id=law_id,
            law_type=law_type,
            issuing_body_code=issuing_code,
            issuing_body_full=issuing_full,
            year=year,
            context=context,
            position=match.start()
        )
```

#### Bước 2.2: Vietnamese Keyword Extractor (Ngày 2-3)

```python
# src/core/metadata/keyword_extractor.py
"""
Trích xuất keywords từ Vietnamese legal text.
Thuần Python — KHÔNG dùng LLM (tiết kiệm token).
Dùng underthesea cho word segmentation + POS tagging.
"""

from typing import List, Tuple
from collections import Counter
import re

# Import Vietnamese NLP
from underthesea import word_tokenize, pos_tag

# Vietnamese stopwords cho legal domain
LEGAL_STOPWORDS = {
    # Common Vietnamese stopwords
    "và", "của", "các", "có", "được", "trong", "là", "cho", "với",
    "này", "đã", "từ", "theo", "về", "không", "một", "những",
    "khi", "để", "hoặc", "nhưng", "nếu", "trên", "đến", "do",
    "tại", "cũng", "nên", "còn", "sẽ",
    
    # Legal boilerplate words (xuất hiện ở hầu hết mọi văn bản)
    "quy_định", "điều", "khoản", "điểm", "mục", "chương",
    "ban_hành", "thực_hiện", "áp_dụng", "hiệu_lực",
    "thi_hành", "chịu_trách_nhiệm",
}

# Domain-specific compound nouns cần giữ nguyên
COMPOUND_TERMS = {
    "hàng_không": "hàng không",
    "an_toàn_bay": "an toàn bay",
    "quản_lý_bay": "quản lý bay",
    "không_lưu": "không lưu",
    "CNS_ATM": "CNS/ATM",
    "sân_bay": "sân bay",
    "tổ_bay": "tổ bay",
    "lao_động": "lao động",
    "bảo_hiểm_xã_hội": "bảo hiểm xã hội",
    "nghỉ_phép": "nghỉ phép",
    "hợp_đồng_lao_động": "hợp đồng lao động",
    "doanh_nghiệp": "doanh nghiệp",
    "thuế_thu_nhập": "thuế thu nhập",
    # Thêm domain terms cho ATTECH
}


class VietnameseKeywordExtractor:
    """
    Trích xuất keywords cho Vietnamese legal documents.
    Approach: TF-IDF đơn giản + POS filtering (chỉ lấy nouns).
    """
    
    def extract_keywords(
        self, 
        text: str, 
        title: str = "",
        max_keywords: int = 10,
        min_frequency: int = 2
    ) -> List[str]:
        """
        Extract top keywords từ document text.
        
        Args:
            text: Nội dung document
            title: Tiêu đề (keywords từ title được boost)
            max_keywords: Số keywords tối đa
            min_frequency: Tần suất tối thiểu
            
        Returns:
            List keywords đã sắp xếp theo relevance
        """
        # 1. Word segmentation
        tokens = word_tokenize(text, format="text").split()
        
        # 2. POS tagging — chỉ giữ nouns (N, Np, Nc, Nu)
        tagged = pos_tag(text)
        noun_tokens = [
            word.lower().replace(" ", "_")
            for word, tag in tagged
            if tag in ("N", "Np", "Nc", "Nu", "Ny")
            and len(word) > 1
        ]
        
        # 3. Filter stopwords
        filtered = [
            t for t in noun_tokens
            if t not in LEGAL_STOPWORDS
            and len(t) > 2
        ]
        
        # 4. Count frequency
        counter = Counter(filtered)
        
        # 5. Boost keywords from title
        if title:
            title_tokens = word_tokenize(title, format="text").split()
            for t in title_tokens:
                t_lower = t.lower().replace(" ", "_")
                if t_lower in counter:
                    counter[t_lower] *= 3  # Triple boost cho title keywords
        
        # 6. Boost compound terms
        for compound, display in COMPOUND_TERMS.items():
            if compound in counter:
                counter[compound] *= 2  # Double boost cho domain terms
        
        # 7. Filter by frequency and return
        keywords = [
            word.replace("_", " ")
            for word, count in counter.most_common(max_keywords * 2)
            if count >= min_frequency
        ][:max_keywords]
        
        return keywords
    
    def extract_category(self, text: str, keywords: List[str]) -> str:
        """
        Phân loại document vào category dựa trên keywords.
        Rule-based — không dùng LLM.
        """
        text_lower = text.lower()
        keyword_set = set(k.lower() for k in keywords)
        
        # Category rules (ordered by specificity)
        CATEGORY_RULES = [
            ("hang_khong", [
                "hàng không", "bay", "sân bay", "phi công", "tổ bay",
                "không lưu", "CNS", "ATM", "ICAO", "radar"
            ]),
            ("lao_dong", [
                "lao động", "nghỉ phép", "hợp đồng", "tiền lương",
                "bảo hiểm xã hội", "thai sản", "việc làm"
            ]),
            ("tai_chinh", [
                "tài chính", "ngân sách", "thuế", "kế toán",
                "kiểm toán", "đầu tư", "vốn"
            ]),
            ("khoa_hoc_cong_nghe", [
                "khoa học", "công nghệ", "nghiên cứu", "sáng chế",
                "phát minh", "chuyển giao"
            ]),
            ("hanh_chinh", [
                "hành chính", "tổ chức", "nhân sự", "quy chế",
                "nội quy", "điều lệ"
            ]),
            ("an_toan", [
                "an toàn", "bảo hộ", "phòng cháy", "cứu hộ",
                "môi trường"
            ]),
        ]
        
        scores = {}
        for category, terms in CATEGORY_RULES:
            score = 0
            for term in terms:
                if term in text_lower:
                    score += text_lower.count(term)
                if term in keyword_set:
                    score += 5  # Bonus nếu xuất hiện trong extracted keywords
            scores[category] = score
        
        if not scores or max(scores.values()) == 0:
            return "khac"  # fallback
        
        return max(scores, key=scores.get)
```

#### Bước 2.3: Metadata Enricher — Orchestrator (Ngày 3-4)

```python
# src/core/metadata/enricher.py
"""
Orchestrator: Kết hợp các extractors để enrich metadata tự động.
Được gọi TRƯỚC khi import vào database.
"""

import json
import logging
from typing import Dict, Any, Optional
from .legal_code_extractor import LegalCodeExtractor
from .keyword_extractor import VietnameseKeywordExtractor

logger = logging.getLogger(__name__)


class MetadataEnricher:
    """
    Tự động bổ sung metadata cho document trước khi import.
    
    Nguyên tắc:
    - KHÔNG ghi đè metadata đã có (chỉ bổ sung fields trống)
    - KHÔNG dùng LLM (thuần Python, deterministic)
    - Luôn giữ nguyên legal codes (KHÔNG preprocess)
    """
    
    def __init__(self):
        self.legal_extractor = LegalCodeExtractor()
        self.keyword_extractor = VietnameseKeywordExtractor()
    
    def enrich(
        self,
        metadata: Dict[str, Any],
        full_content: str,
        title: str
    ) -> Dict[str, Any]:
        """
        Enrich metadata từ content analysis.
        
        Args:
            metadata: JSONB metadata hiện có (có thể thiếu fields)
            full_content: Nội dung đầy đủ document
            title: Tiêu đề document
            
        Returns:
            metadata đã được bổ sung
        """
        enriched = json.loads(json.dumps(metadata))  # Deep copy
        
        # Đảm bảo structure tồn tại
        for section in ["identification", "authority", "domain", 
                        "relationships", "financial"]:
            if section not in enriched:
                enriched[section] = {}
        
        # 1. Enrich identification
        self._enrich_identification(enriched, full_content, title)
        
        # 2. Enrich domain (keywords + category)
        self._enrich_domain(enriched, full_content, title)
        
        # 3. Enrich relationships (based_on)
        self._enrich_relationships(enriched, full_content)
        
        # 4. Enrich authority (organization từ legal codes)
        self._enrich_authority(enriched, full_content, title)
        
        logger.info(
            f"Enriched metadata for '{title[:50]}': "
            f"identification={bool(enriched['identification'].get('document_number'))}, "
            f"keywords={len(enriched['domain'].get('keywords', []))}, "
            f"based_on={len(enriched['relationships'].get('based_on', []))}"
        )
        
        return enriched
    
    def _enrich_identification(self, meta, content, title):
        """Bổ sung document_number, document_type, issue_date."""
        ident = meta["identification"]
        
        # Document number
        if not ident.get("document_number"):
            own_id = self.legal_extractor.extract_document_own_id(content, title)
            if own_id:
                ident["document_number"] = own_id
        
        # Document type (từ pattern trong document_number)
        if not ident.get("document_type") or ident["document_type"] == "unknown":
            refs = self.legal_extractor.extract_all_references(title)
            if refs:
                ident["document_type"] = refs[0].law_type
        
        # Issue date (từ year trong document_number)
        if not ident.get("issue_date"):
            refs = self.legal_extractor.extract_all_references(
                ident.get("document_number", "") or title
            )
            if refs and refs[0].year:
                ident["issue_date"] = f"{refs[0].year}-01-01"
    
    def _enrich_domain(self, meta, content, title):
        """Bổ sung keywords và category."""
        domain = meta["domain"]
        
        # Keywords
        existing_keywords = domain.get("keywords", [])
        if not existing_keywords or len(existing_keywords) < 3:
            extracted = self.keyword_extractor.extract_keywords(
                content, title, max_keywords=10
            )
            # Merge: giữ existing + thêm mới
            merged = list(set(existing_keywords + extracted))[:15]
            domain["keywords"] = merged
        
        # Category
        if not domain.get("category") or domain["category"] in ("unknown", "other", "khac"):
            domain["category"] = self.keyword_extractor.extract_category(
                content, domain.get("keywords", [])
            )
    
    def _enrich_relationships(self, meta, content):
        """Bổ sung based_on (căn cứ pháp lý)."""
        rels = meta["relationships"]
        
        existing_based_on = rels.get("based_on", [])
        if not existing_based_on:
            extracted = self.legal_extractor.extract_based_on_references(content)
            if extracted:
                rels["based_on"] = extracted
    
    def _enrich_authority(self, meta, content, title):
        """Bổ sung organization từ legal code analysis."""
        auth = meta["authority"]
        
        if not auth.get("organization") or auth["organization"].lower() in ("general", "unknown", ""):
            refs = self.legal_extractor.extract_all_references(title)
            if refs and refs[0].issuing_body_full:
                auth["organization"] = refs[0].issuing_body_full
```

#### Bước 2.4: Metadata Validator — Quality Gate (Ngày 4-5)

```python
# src/core/metadata/validator.py
"""
Validation gate: Kiểm tra metadata ĐẠT CHUẨN trước khi import.
Thay thế cho FR-03.2 (mock service).
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    PASS = "pass"           # Đủ metadata, import ngay
    WARNING = "warning"     # Thiếu một số fields, import + flag
    FAIL = "fail"           # Thiếu fields critical, KHÔNG import


@dataclass
class ValidationResult:
    level: ValidationLevel
    score: float                # 0-100
    missing_critical: List[str]
    missing_optional: List[str]
    warnings: List[str]
    
    @property
    def can_import(self) -> bool:
        return self.level in (ValidationLevel.PASS, ValidationLevel.WARNING)


class MetadataValidator:
    """
    Validate metadata quality trước khi import.
    
    Thresholds:
    - PASS: score ≥ 80 (tất cả critical fields có)
    - WARNING: score 50-79 (thiếu một số, nhưng có basics)
    - FAIL: score < 50 (thiếu quá nhiều)
    """
    
    # Fields và weights
    CRITICAL_FIELDS = {
        # (section, field): weight
        ("identification", "document_number"): 15,
        ("identification", "document_type"): 10,
        ("identification", "issue_date"): 10,
        ("domain", "keywords"): 15,
        ("domain", "category"): 10,
    }
    
    HIGH_FIELDS = {
        ("authority", "organization"): 10,
        ("authority", "department"): 5,
        ("relationships", "based_on"): 15,
    }
    
    OPTIONAL_FIELDS = {
        ("relationships", "relates_to"): 5,
        ("financial", "budget"): 5,
    }
    
    def validate(self, metadata: Dict[str, Any]) -> ValidationResult:
        """Validate metadata completeness."""
        score = 0
        max_score = 0
        missing_critical = []
        missing_optional = []
        warnings = []
        
        # Check critical fields
        for (section, field), weight in self.CRITICAL_FIELDS.items():
            max_score += weight
            value = self._get_value(metadata, section, field)
            if self._is_valid(value, field):
                score += weight
            else:
                missing_critical.append(f"{section}.{field}")
        
        # Check high fields
        for (section, field), weight in self.HIGH_FIELDS.items():
            max_score += weight
            value = self._get_value(metadata, section, field)
            if self._is_valid(value, field):
                score += weight
            else:
                missing_optional.append(f"{section}.{field}")
        
        # Check optional fields
        for (section, field), weight in self.OPTIONAL_FIELDS.items():
            max_score += weight
            value = self._get_value(metadata, section, field)
            if self._is_valid(value, field):
                score += weight
        
        # Calculate percentage
        pct = (score / max_score * 100) if max_score > 0 else 0
        
        # Determine level
        if pct >= 80 and not missing_critical:
            level = ValidationLevel.PASS
        elif pct >= 50:
            level = ValidationLevel.WARNING
            warnings.append(
                f"Metadata completeness {pct:.0f}% (target: 80%). "
                f"Missing: {', '.join(missing_critical)}"
            )
        else:
            level = ValidationLevel.FAIL
            warnings.append(
                f"Metadata completeness {pct:.0f}% — DƯỚI NGƯỠNG. "
                f"Cannot import without: {', '.join(missing_critical)}"
            )
        
        return ValidationResult(
            level=level,
            score=round(pct, 1),
            missing_critical=missing_critical,
            missing_optional=missing_optional,
            warnings=warnings
        )
    
    def _get_value(self, metadata, section, field):
        if section in metadata and isinstance(metadata[section], dict):
            return metadata[section].get(field)
        return None
    
    def _is_valid(self, value, field):
        if value is None or value == "" or value == []:
            return False
        if isinstance(value, str) and value.lower() in ("unknown", "other", "general", "null"):
            return False
        if isinstance(value, list) and len(value) == 0:
            return False
        if field == "keywords" and isinstance(value, list) and len(value) < 2:
            return False
        return True
```

#### Bước 2.5: Tích hợp vào Import Pipeline (Ngày 5)

Sửa `simple_import_processor.py`:

```python
# Thêm vào import pipeline
from src.core.metadata.enricher import MetadataEnricher
from src.core.metadata.validator import MetadataValidator, ValidationLevel

enricher = MetadataEnricher()
validator = MetadataValidator()

async def process_document(doc_json_path: str):
    """Import pipeline CẬP NHẬT với enrichment + validation."""
    
    # Step 1: Load document.json (có sẵn)
    with open(doc_json_path) as f:
        doc_data = json.load(f)
    
    metadata = doc_data.get("metadata", {})
    content = extract_full_content(doc_data)
    title = doc_data.get("title", "")
    
    # Step 2: ⭐ Auto-enrich metadata
    enriched_metadata = enricher.enrich(metadata, content, title)
    
    # Step 3: ⭐ Validate
    validation = validator.validate(enriched_metadata)
    
    if validation.level == ValidationLevel.FAIL:
        logger.warning(
            f"⚠️ SKIP '{title}': metadata score {validation.score}% "
            f"(missing: {validation.missing_critical})"
        )
        # Vẫn import nhưng flag cho manual review
        enriched_metadata["_needs_review"] = True
        enriched_metadata["_validation_score"] = validation.score
    
    if validation.warnings:
        for w in validation.warnings:
            logger.info(f"  → {w}")
    
    # Step 4: Import vào DB với enriched metadata
    doc_data["metadata"] = enriched_metadata
    await import_to_database(doc_data)
    
    # Step 5: ⭐ Auto-sync Graph RAG
    if validation.can_import:
        await sync_to_graph(doc_data["document_id"])
    
    return validation
```

**Deliverable Giai đoạn 2:**
- ✅ LegalCodeExtractor: trích xuất chính xác mã văn bản từ content
- ✅ KeywordExtractor: trích xuất 5-10 keywords thuần Python
- ✅ MetadataEnricher: orchestrator tự động bổ sung
- ✅ MetadataValidator: quality gate trước khi import
- ✅ Import pipeline tích hợp enrichment + validation
- ✅ Documents mới tự động có metadata ≥80% completeness

---

### GIAI ĐOẠN 3: TÍCH HỢP METADATA VÀO SEARCH ALGORITHMS (Tuần 4)

**Mục tiêu:** Metadata không chỉ để "trang trí" mà thực sự cải thiện search quality.

#### Bước 3.1: Metadata-Boosted Hybrid Search (Ngày 1-2)

Hiện tại HybridRanker dùng: `0.7 * semantic + 0.3 * keyword`. 
Thêm metadata signals vào scoring:

```python
# Cập nhật hybrid_ranker.py

class MetadataAwareHybridRanker:
    """
    HybridRanker nâng cấp: kết hợp metadata signals vào ranking.
    """
    
    async def combine_results(self, query, raw_results, top_k=20):
        """
        Score = 0.5 * semantic 
              + 0.2 * keyword 
              + 0.15 * metadata_match    # ⭐ MỚI
              + 0.1 * freshness          # ⭐ MỚI 
              + 0.05 * authority          # ⭐ MỚI
        """
        
        for result in raw_results:
            # Existing scores
            semantic_score = result.get("similarity_score", 0)
            keyword_score = normalize(result.get("bm25_score", 0))
            
            # ⭐ Metadata match score
            metadata_score = self._calc_metadata_match(query, result)
            
            # ⭐ Freshness score (docs mới hơn được boost)
            freshness_score = self._calc_freshness(result)
            
            # ⭐ Authority score (Luật > NĐ > TT > QĐ)
            authority_score = self._calc_authority(result)
            
            result["combined_score"] = (
                0.50 * semantic_score +
                0.20 * keyword_score +
                0.15 * metadata_score +
                0.10 * freshness_score +
                0.05 * authority_score
            )
        
        return sorted(raw_results, key=lambda x: x["combined_score"], reverse=True)[:top_k]
    
    def _calc_metadata_match(self, query: str, result: dict) -> float:
        """
        Tính điểm dựa trên metadata match với query.
        VD: query "nghị định về thuế" → boost docs có category=tai_chinh, type=nghi_dinh
        """
        score = 0.0
        metadata = result.get("metadata", {})
        query_lower = query.lower()
        
        # Category match
        category = metadata.get("domain", {}).get("category", "")
        category_keywords = {
            "tai_chinh": ["thuế", "tài chính", "ngân sách", "kế toán"],
            "lao_dong": ["lao động", "nghỉ phép", "lương", "bảo hiểm"],
            "hang_khong": ["hàng không", "bay", "sân bay", "phi công"],
        }
        for cat, terms in category_keywords.items():
            if cat == category and any(t in query_lower for t in terms):
                score += 0.4
                break
        
        # Keyword overlap
        doc_keywords = metadata.get("domain", {}).get("keywords", [])
        if doc_keywords:
            query_words = set(query_lower.split())
            keyword_words = set(k.lower() for k in doc_keywords)
            overlap = query_words & keyword_words
            if overlap:
                score += min(len(overlap) * 0.15, 0.4)
        
        # Document type match
        doc_type = metadata.get("identification", {}).get("document_type", "")
        type_keywords = {
            "luat": ["luật", "bộ luật"],
            "nghi_dinh": ["nghị định"],
            "thong_tu": ["thông tư"],
            "quyet_dinh": ["quyết định"],
        }
        for dtype, terms in type_keywords.items():
            if dtype == doc_type and any(t in query_lower for t in terms):
                score += 0.2
                break
        
        return min(score, 1.0)
    
    def _calc_freshness(self, result: dict) -> float:
        """
        Docs mới hơn được boost (quan trọng cho pháp luật: 
        NĐ mới thay thế NĐ cũ).
        """
        from datetime import datetime, timedelta
        
        metadata = result.get("metadata", {})
        issue_date_str = metadata.get("identification", {}).get("issue_date", "")
        
        if not issue_date_str:
            return 0.3  # Default trung bình nếu không có date
        
        try:
            issue_date = datetime.fromisoformat(issue_date_str[:10])
            now = datetime.now()
            age_days = (now - issue_date).days
            
            # Docs < 1 năm: score 1.0
            # Docs 1-3 năm: score 0.7
            # Docs 3-5 năm: score 0.5
            # Docs > 5 năm: score 0.3
            if age_days < 365:
                return 1.0
            elif age_days < 365 * 3:
                return 0.7
            elif age_days < 365 * 5:
                return 0.5
            else:
                return 0.3
        except:
            return 0.3
    
    def _calc_authority(self, result: dict) -> float:
        """
        Hierarchy pháp lý: Luật > Nghị định > Thông tư > Quyết định.
        Docs cấp cao hơn được boost khi relevance tương đương.
        """
        metadata = result.get("metadata", {})
        doc_type = metadata.get("identification", {}).get("document_type", "")
        
        AUTHORITY_SCORES = {
            "luat": 1.0,
            "nghi_dinh": 0.9,
            "nghi_quyet": 0.85,
            "thong_tu": 0.8,
            "quyet_dinh": 0.7,
            "cong_van": 0.5,
            "chi_thi": 0.6,
        }
        
        return AUTHORITY_SCORES.get(doc_type, 0.4)
```

#### Bước 3.2: Query Router sử dụng metadata (Ngày 2-3)

```python
# src/core/search/query_router.py
"""
Intelligent query routing: chọn search strategy tối ưu dựa trên query analysis.
Metadata-aware — chỉ dùng Metadata Search khi metadata đủ tốt.
"""

from enum import Enum
from typing import List
import re


class SearchStrategy(Enum):
    EXACT_LOOKUP = "exact_lookup"      # law_id → Substring only
    SEMANTIC_HEAVY = "semantic_heavy"  # Conceptual → 0.8 semantic + 0.2 keyword
    HYBRID_BALANCED = "hybrid"         # Mixed → standard hybrid
    METADATA_FIRST = "metadata_first"  # Filtered → metadata filter + semantic
    TEMPORAL = "temporal"              # Time-based → freshness boost


class QueryRouter:
    """
    Phân loại query và chọn strategy tối ưu.
    Rule-based — KHÔNG dùng LLM.
    """
    
    # Patterns cho legal code detection
    LEGAL_CODE_PATTERN = re.compile(
        r'\d{1,4}/\d{4}/[A-ZĐ]{2,4}-[A-ZĐ]+|'  # 265/2025/NĐ-CP
        r'\d{1,5}/[A-ZĐ]{2,4}-[A-ZĐ]+',           # 737/QĐ-CQĐHQ
        re.UNICODE
    )
    
    def route(self, query: str) -> SearchStrategy:
        """Phân loại query và trả về strategy tối ưu."""
        query_lower = query.strip().lower()
        
        # 1. Exact lookup: query là legal code
        if self.LEGAL_CODE_PATTERN.search(query):
            return SearchStrategy.EXACT_LOOKUP
        
        # 2. Metadata-first: query chứa filter conditions
        if self._has_metadata_filters(query_lower):
            return SearchStrategy.METADATA_FIRST
        
        # 3. Temporal: query hỏi về thời gian/hiệu lực
        if self._is_temporal_query(query_lower):
            return SearchStrategy.TEMPORAL
        
        # 4. Semantic-heavy: query conceptual, dài
        if len(query.split()) > 8:
            return SearchStrategy.SEMANTIC_HEAVY
        
        # 5. Default: hybrid balanced
        return SearchStrategy.HYBRID_BALANCED
    
    def _has_metadata_filters(self, query: str) -> bool:
        """Detect nếu query chứa metadata filter hints."""
        filter_patterns = [
            r'do\s+(bộ|chính phủ|quốc hội|thủ tướng)',  # "do Bộ GTVT ban hành"
            r'loại\s+(luật|nghị định|thông tư)',          # "loại nghị định"
            r'năm\s+\d{4}',                               # "năm 2024"
            r'lĩnh vực\s+\w+',                            # "lĩnh vực tài chính"
            r'(ban hành|của)\s+(bộ|sở|cục)',              # "ban hành bởi Bộ..."
        ]
        return any(re.search(p, query) for p in filter_patterns)
    
    def _is_temporal_query(self, query: str) -> bool:
        """Detect temporal queries."""
        temporal_keywords = [
            "hiện hành", "mới nhất", "còn hiệu lực",
            "thay thế", "hết hiệu lực", "sửa đổi",
            "bổ sung", "bãi bỏ", "gần đây"
        ]
        return any(kw in query for kw in temporal_keywords)
```

#### Bước 3.3: Tích hợp Graph RAG vào Retrieval (Ngày 3-5)

```python
# Thêm vào SearchOrchestrator

async def search_with_graph_expansion(self, query, top_k=10):
    """
    Enhanced search: kết quả chính + documents liên quan qua Graph.
    
    Flow:
    1. Standard search → top results
    2. Với mỗi top result, query Graph RAG → related docs
    3. Merge và rerank toàn bộ
    """
    # Step 1: Standard search
    primary_results = await self.search_documents(query, top_k=top_k)
    
    if not primary_results:
        return primary_results
    
    # Step 2: Graph expansion cho top 3 results
    expanded_doc_ids = set()
    for result in primary_results[:3]:
        doc_id = result.get("document_id")
        if not doc_id:
            continue
        
        # Query graph edges
        related = await self._get_graph_neighbors(doc_id, max_hops=1)
        expanded_doc_ids.update(related)
    
    # Step 3: Fetch expanded docs (nếu chưa trong results)
    existing_ids = {r.get("document_id") for r in primary_results}
    new_ids = expanded_doc_ids - existing_ids
    
    if new_ids:
        # Fetch chunks từ related docs, score by graph relationship
        graph_results = await self._fetch_graph_related_chunks(
            new_ids, query, max_per_doc=2
        )
        
        # Tag graph results
        for r in graph_results:
            r["source"] = "graph_expansion"
            r["combined_score"] *= 0.8  # Slight discount vs primary
        
        primary_results.extend(graph_results)
    
    # Step 4: Rerank combined results
    primary_results.sort(key=lambda x: x["combined_score"], reverse=True)
    
    return primary_results[:top_k]

async def _get_graph_neighbors(self, document_id, max_hops=1):
    """Query graph_edges để tìm documents liên quan."""
    query = """
        SELECT DISTINCT dm2.document_id
        FROM graph_documents gd1
        JOIN graph_edges e ON e.source_graph_doc_id = gd1.graph_doc_id
        JOIN graph_documents gd2 ON gd2.graph_doc_id = e.target_graph_doc_id
        JOIN documents_metadata_v2 dm2 ON dm2.document_id = gd2.source_document_id
        WHERE gd1.source_document_id = $1
          AND e.is_active = true
          AND e.confidence >= 0.6
        ORDER BY e.confidence DESC
        LIMIT 10
    """
    rows = await self.db_pool.fetch(query, document_id)
    return {row["document_id"] for row in rows}
```

**Deliverable Giai đoạn 3:**
- ✅ HybridRanker sử dụng metadata signals (category, freshness, authority)
- ✅ QueryRouter chọn search strategy theo query type
- ✅ Graph RAG expansion tích hợp vào search pipeline
- ✅ Benchmark: accuracy tăng thêm 5-10% nhờ metadata

---

### GIAI ĐOẠN 4: GRAPH RAG LIVE + AUTO-SYNC (Tuần 5-6)

**Mục tiêu:** Graph RAG hoạt động tự động, không cần manual scripts.

#### Bước 4.1: Database Trigger cho auto-sync (Ngày 1-2)

```sql
-- Trigger: Khi insert/update document → tự động sync graph
CREATE OR REPLACE FUNCTION sync_document_to_graph_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Sync document vào graph_documents
    INSERT INTO graph_documents (
        source_document_id, 
        document_title,
        document_metadata
    ) VALUES (
        NEW.document_id,
        NEW.title,
        NEW.metadata
    ) ON CONFLICT (source_document_id) DO UPDATE
    SET document_title = NEW.title,
        document_metadata = NEW.metadata,
        updated_at = NOW();
    
    -- Flag cho edge regeneration (async job sẽ xử lý)
    INSERT INTO graph_sync_queue (document_id, action, created_at)
    VALUES (NEW.document_id, 'sync_edges', NOW())
    ON CONFLICT DO NOTHING;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_document_graph_sync
AFTER INSERT OR UPDATE ON documents_metadata_v2
FOR EACH ROW
EXECUTE FUNCTION sync_document_to_graph_trigger();

-- Queue table cho async edge creation
CREATE TABLE IF NOT EXISTS graph_sync_queue (
    id SERIAL PRIMARY KEY,
    document_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    error_message TEXT
);
```

#### Bước 4.2: Background worker xử lý graph sync queue (Ngày 2-3)

```python
# scripts/graph_sync_worker.py
"""
Background worker: Xử lý graph_sync_queue.
Chạy như cron job hoặc daemon.

Crontab entry:
*/5 * * * * cd /path/to/project && python graph_sync_worker.py
"""

async def process_sync_queue():
    """Xử lý các documents chờ sync edges."""
    conn = await get_db_connection()
    
    # Lấy pending items
    pending = await conn.fetch("""
        SELECT id, document_id FROM graph_sync_queue
        WHERE status = 'pending'
        ORDER BY created_at
        LIMIT 50
    """)
    
    for item in pending:
        try:
            # Tạo edges cho document này
            await create_edges_for_document(conn, item["document_id"])
            
            # Mark done
            await conn.execute("""
                UPDATE graph_sync_queue 
                SET status = 'completed', processed_at = NOW()
                WHERE id = $1
            """, item["id"])
            
        except Exception as e:
            await conn.execute("""
                UPDATE graph_sync_queue 
                SET status = 'error', error_message = $2, processed_at = NOW()
                WHERE id = $1
            """, item["id"], str(e))
    
    await conn.close()
```

#### Bước 4.3: Cache invalidation khi metadata thay đổi (Ngày 3-4)

```python
# Thêm vào import pipeline và metadata editor

async def invalidate_caches_for_document(document_id: str):
    """
    Khi metadata thay đổi → invalidate cached search results 
    liên quan đến document này.
    """
    redis = await get_redis()
    
    # Pattern: tìm tất cả cache keys chứa document_id
    # Hoặc đơn giản hơn: flush toàn bộ search cache
    await redis.delete("search_cache:*")
    
    # Log
    logger.info(f"Cache invalidated for document {document_id}")
```

#### Bước 4.4: Monitoring metadata quality (Ngày 4-5)

```python
# Prometheus metrics cho metadata quality
from prometheus_client import Gauge, Counter

metadata_completeness = Gauge(
    'rag_metadata_completeness_percent',
    'Average metadata completeness score',
)

metadata_enrichment_count = Counter(
    'rag_metadata_enrichments_total',
    'Number of documents auto-enriched',
    ['field']
)

validation_results = Counter(
    'rag_metadata_validation_total',
    'Metadata validation results',
    ['level']  # pass, warning, fail
)
```

**Deliverable Giai đoạn 4:**
- ✅ Database trigger tự động sync document → graph
- ✅ Background worker tạo edges tự động
- ✅ Cache invalidation khi metadata/document thay đổi
- ✅ Prometheus metrics cho metadata quality
- ✅ Zero manual intervention cho toàn bộ pipeline

---

## 4. KPI TRACKING

| Metric | Hiện tại | Sau GĐ 1 | Sau GĐ 2 | Sau GĐ 3 | Sau GĐ 4 |
|--------|----------|-----------|-----------|-----------|-----------|
| Metadata completeness | ~15% | ≥80% (42 docs) | ≥80% (new docs) | ≥80% | ≥85% |
| Graph RAG edges | 0 | 300-500 | +auto | used in search | auto-maintained |
| Metadata Search accuracy | ~20% | ~50% | ~70% | ~85% | ~85% |
| Overall RAG accuracy | ~75% | ~77% | ~80% | ~85% | ~87% |
| Manual intervention needed | Every import | Fix old docs only | Rare | None | None |

---

## 5. TÓM TẮT

```
HIỆN TẠI:
  Upload → metadata trống → sửa tay (không kịp) → Graph RAG chết
  → Metadata Search vô dụng → accuracy bị giới hạn

SAU LỘ TRÌNH:
  Upload → Auto-Enrich (Python, no LLM) → Validate (quality gate)
  → Import + Auto Graph Sync → Metadata-Boosted Search
  → Graph RAG Expansion → accuracy ≥85%
```

**6 tuần, 4 giai đoạn, từ manual → semi-auto → full-auto.**

Giai đoạn 1 (manual fix) có thể bắt đầu ngay ngày mai.
Giai đoạn 2 (auto enrichment) là investment quan trọng nhất — 
giải quyết gốc rễ vấn đề cho 100K docs tương lai.
