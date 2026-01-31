# 🚀 Implementation Plan: Metadata-as-a-Skill v7.1

**Target:** FR-03.1 v7.1 Release  
**Timeline:** 3 days (MVP) + 1 day (testing)  
**Developer:** Vietnamese RAG Expert

---

## 📅 DEVELOPMENT TIMELINE

### Day 1: Core Schema & Extraction Logic (8 hours)

```
[Hour 1-2] Schema Design & Update
├─ Update metadata schema
├─ Add usage_instructions field
└─ Backward compatibility check

[Hour 3-4] Trigger Logic
├─ Implement should_generate_instructions()
├─ Pattern detection for complex docs
└─ Token budget calculator

[Hour 5-6] Basic Extraction
├─ _extract_scope()
├─ _extract_interpretation_logic()
└─ _extract_prerequisites()

[Hour 7-8] Testing & Integration
├─ Unit tests for each function
├─ Integration with MetadataExtractor
└─ Sample document testing
```

### Day 2: Advanced Features (8 hours)

```
[Hour 1-2] Confidence Scoring
├─ _calculate_confidence()
├─ Supersedes detection
└─ Age-based scoring

[Hour 3-4] Usage Hints Generation
├─ _generate_usage_hints()
├─ Template-based generation
└─ Document type specific logic

[Hour 5-6] Token Budget Management
├─ _compress_instructions()
├─ Shorthand notation converter
└─ Priority-based field selection

[Hour 7-8] UI Integration
├─ Add instructions editor to Streamlit
├─ Manual override interface
└─ Preview display
```

### Day 3: Production Ready (8 hours)

```
[Hour 1-2] Migration Script
├─ Scan existing documents
├─ Generate instructions for complex docs
└─ Update database

[Hour 3-4] Quality Assurance
├─ Test with 20+ real documents
├─ Measure token overhead
└─ Accuracy benchmarking

[Hour 5-6] Documentation
├─ Update DEVELOPER_GUIDE.md
├─ Update metadata_user_manual
└─ Create migration guide

[Hour 7-8] Deployment
├─ Code review
├─ Deploy to production
└─ Monitor metrics
```

---

## 📦 CODE SKELETON

### 1. Schema Update

```python
# vietnamese_metadata_extractor.py (Line ~80)

# ADD to METADATA_SCHEMA
METADATA_SCHEMA = {
    # ... existing fields ...
    
    "usage_instructions": {
        "scope": {
            "applicable_to": "",
            "excludes": "",
            "supersedes": []
        },
        "interpretation_logic": {},
        "pre_requisites": {
            "must_read_with": [],
            "context_documents": []
        },
        "confidence_score": {
            "value": 0.0,
            "reason": ""
        },
        "usage_hints": {
            "when_to_use": "",
            "when_not_to_use": "",
            "special_cases": ""
        }
    }
}
```

### 2. Trigger Logic

```python
# vietnamese_metadata_extractor.py (NEW function)

def should_generate_instructions(self, metadata: Dict) -> bool:
    """
    Determine if document is complex enough to need usage instructions
    
    Returns:
    --------
    bool
        True if should generate, False otherwise
    """
    triggers = []
    
    # Trigger 1: High-level legal document (Level 0-2)
    if metadata.get('hierarchy', {}).get('level', 999) <= 2:
        triggers.append("high_level")
    
    # Trigger 2: Many relationships (>3 based_on)
    based_on = metadata.get('relationships', {}).get('based_on', [])
    if len(based_on) > 3:
        triggers.append("many_deps")
    
    # Trigger 3: Supersedes old documents
    replaces = metadata.get('relationships', {}).get('replaces', [])
    amends = metadata.get('relationships', {}).get('amends', [])
    if replaces or amends:
        triggers.append("supersedes")
    
    # Trigger 4: Has financial data
    if metadata.get('financial', {}).get('budget', 0) > 0:
        triggers.append("financial")
    
    # Trigger 5: Has strict prohibitions
    prohibitions = metadata.get('prohibitions', {})
    if prohibitions.get('strict_count', 0) > 5:
        triggers.append("strict_rules")
    
    # Trigger 6: Complex custom fields
    custom = metadata.get('custom_fields', {})
    if len(custom) > 5:
        triggers.append("complex_custom")
    
    # Need at least 2 triggers
    return len(triggers) >= 2


def _count_tokens(self, text: Any) -> int:
    """
    Count tokens in text or dict
    
    Parameters:
    -----------
    text : str or dict
        Text or dictionary to count tokens
    
    Returns:
    --------
    int
        Number of tokens
    """
    if isinstance(text, dict):
        text = json.dumps(text, ensure_ascii=False)
    elif not isinstance(text, str):
        text = str(text)
    
    # Simple approximation: Vietnamese ~1.3 chars per token
    return len(text) // 1.3
```

### 3. Scope Extraction

```python
# vietnamese_metadata_extractor.py (NEW function)

def _extract_scope(self, text: str, metadata: Dict) -> Dict:
    """
    Extract scope: applicable_to, excludes, supersedes
    
    Parameters:
    -----------
    text : str
        Document text
    metadata : Dict
        Current metadata
    
    Returns:
    --------
    Dict
        {
            "applicable_to": str,
            "excludes": str,
            "supersedes": [str]
        }
    """
    scope = {
        "applicable_to": "",
        "excludes": "",
        "supersedes": []
    }
    
    # Pattern 1: Áp dụng cho...
    applies_patterns = [
        r"áp dụng (?:cho|đối với)\s+(.+?)(?:\.|;|\n)",
        r"phạm vi áp dụng:?\s+(.+?)(?:\.|;|\n)",
        r"hiệu lực (?:từ|tại)\s+(.+?)(?:\.|;|\n)"
    ]
    
    for pattern in applies_patterns:
        if match := re.search(pattern, text, re.IGNORECASE):
            scope["applicable_to"] = match.group(1).strip()[:100]  # Max 100 chars
            break
    
    # Pattern 2: Không áp dụng cho...
    excludes_patterns = [
        r"không áp dụng (?:cho|đối với)\s+(.+?)(?:\.|;|\n)",
        r"loại trừ:?\s+(.+?)(?:\.|;|\n)",
        r"ngoại trừ\s+(.+?)(?:\.|;|\n)"
    ]
    
    for pattern in excludes_patterns:
        if match := re.search(pattern, text, re.IGNORECASE):
            scope["excludes"] = match.group(1).strip()[:100]
            break
    
    # Pattern 3: Supersedes (from relationships)
    replaces = metadata.get('relationships', {}).get('replaces', [])
    amends = metadata.get('relationships', {}).get('amends', [])
    scope["supersedes"] = replaces + amends
    
    return scope
```

### 4. Interpretation Logic Extraction

```python
# vietnamese_metadata_extractor.py (NEW function)

def _extract_interpretation_logic(self, text: str, metadata: Dict) -> Dict:
    """
    Extract interpretation rules for complex sections
    
    Parameters:
    -----------
    text : str
        Document text
    metadata : Dict
        Current metadata
    
    Returns:
    --------
    Dict
        Dynamic fields based on document content
    """
    logic = {}
    
    # Rule 1: Financial table interpretation
    if self._has_financial_table(text):
        logic["financial_table"] = self._analyze_financial_table(text, metadata)
    
    # Rule 2: Approval conditions
    if "phê duyệt" in text.lower() or "approval" in text.lower():
        logic["approval_conditions"] = self._extract_approval_logic(text)
    
    # Rule 3: Timeline interpretation
    if any(word in text.lower() for word in ["deadline", "thời hạn", "hạn chót", "thời gian"]):
        logic["timeline_interpretation"] = self._extract_timeline_logic(text)
    
    # Rule 4: VAT/Tax handling
    if "vat" in text.lower() or "thuế" in text.lower():
        logic["tax_handling"] = self._extract_tax_logic(text)
    
    # Compress to stay within budget (max 150 tokens)
    if self._count_tokens(logic) > 150:
        logic = self._compress_logic(logic, max_tokens=150)
    
    return logic


def _has_financial_table(self, text: str) -> bool:
    """Check if document has financial table"""
    indicators = [
        "ngân sách",
        "kinh phí",
        "chi phí",
        "vnd",
        "triệu đồng",
        "tỷ đồng"
    ]
    return sum(1 for ind in indicators if ind in text.lower()) >= 3


def _analyze_financial_table(self, text: str, metadata: Dict) -> str:
    """Analyze financial table and generate interpretation rule"""
    rules = []
    
    # Check for VAT notes
    if "chưa bao gồm" in text.lower() and "vat" in text.lower():
        rules.append("Cột ngân sách có 2 dạng: (1) Đã VAT, (2) Chưa VAT - xem cột Ghi chú")
        rules.append("Nếu 'Chưa bao gồm 10% VAT' → nhân 1.1")
    
    # Check for BHXH/BHYT
    if "bhxh" in text.lower() or "bhyt" in text.lower():
        rules.append("Một số hạng mục đã bao gồm BHXH, BHYT - xem cột Ghi chú")
    
    # Extract total if available
    if budget := metadata.get('financial', {}).get('budget'):
        rules.append(f"Tổng ngân sách: {budget:,} VND")
    
    return ". ".join(rules)


def _extract_approval_logic(self, text: str) -> str:
    """Extract approval workflow logic"""
    # Pattern: Nếu ... thì ... phê duyệt
    pattern = r"nếu\s+(.+?)\s+(?:thì|:)\s+(.+?)\s+phê duyệt"
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    if matches:
        rules = []
        for condition, approver in matches[:3]:  # Max 3 rules
            rules.append(f"{condition.strip()} → {approver.strip()}")
        return ". ".join(rules)
    
    return "Xem điều khoản phê duyệt trong tài liệu"


def _extract_timeline_logic(self, text: str) -> str:
    """Extract timeline interpretation rules"""
    if "deadline" in text.lower() or "hạn chót" in text.lower():
        return "Các mốc thời gian là DEADLINE (hạn chót), không phải estimate"
    elif "dự kiến" in text.lower() or "ước tính" in text.lower():
        return "Các mốc thời gian là DỰ KIẾN, có thể thay đổi"
    else:
        return "Xem phần thời gian trong tài liệu"


def _extract_tax_logic(self, text: str) -> str:
    """Extract tax/VAT handling logic"""
    if "chưa bao gồm vat" in text.lower():
        return "Một số số liệu chưa bao gồm 10% VAT. Khi tính tổng thực tế, nhân 1.1 cho các hạng mục 'Chưa bao gồm VAT'"
    elif "đã bao gồm vat" in text.lower():
        return "Số liệu đã bao gồm VAT, không cần cộng thêm"
    else:
        return "Xem cột Ghi chú để biết VAT đã bao gồm hay chưa"
```

### 5. Prerequisites Extraction

```python
# vietnamese_metadata_extractor.py (NEW function)

def _extract_prerequisites(self, metadata: Dict) -> Dict:
    """
    Extract prerequisite documents
    
    Parameters:
    -----------
    metadata : Dict
        Current metadata
    
    Returns:
    --------
    Dict
        {
            "must_read_with": [str],
            "context_documents": [str]
        }
    """
    prereqs = {
        "must_read_with": [],
        "context_documents": []
    }
    
    # Rule 1: based_on documents are prerequisites
    based_on = metadata.get('relationships', {}).get('based_on', [])
    if based_on:
        prereqs["must_read_with"] = based_on[:3]  # Max 3 to save tokens
    
    # Rule 2: Parent documents in hierarchy
    parent_docs = metadata.get('hierarchy', {}).get('parent_docs', [])
    if parent_docs:
        prereqs["context_documents"] = parent_docs[:2]  # Max 2
    
    return prereqs
```

### 6. Confidence Scoring

```python
# vietnamese_metadata_extractor.py (NEW function)

def _calculate_confidence(self, metadata: Dict) -> Dict:
    """
    Calculate confidence score for this document
    
    Parameters:
    -----------
    metadata : Dict
        Current metadata
    
    Returns:
    --------
    Dict
        {
            "value": float (0.0 - 1.0),
            "reason": str
        }
    """
    confidence = {"value": 0.8, "reason": ""}  # Default
    
    # Factor 1: Supersedes old documents (+0.2)
    if metadata.get('relationships', {}).get('replaces'):
        confidence["value"] = 1.0
        old_docs = metadata['relationships']['replaces']
        confidence["reason"] = f"Thay thế hoàn toàn {', '.join(old_docs[:2])}"
        return confidence
    
    # Factor 2: Recent document (+0.1 if < 6 months)
    issue_date_str = metadata.get('identification', {}).get('issue_date', '')
    if issue_date_str:
        try:
            issue_date = datetime.fromisoformat(issue_date_str)
            months_old = (datetime.now() - issue_date).days / 30
            if months_old < 6:
                confidence["value"] = min(1.0, confidence["value"] + 0.1)
                confidence["reason"] = f"Tài liệu mới ({int(months_old)} tháng)"
        except:
            pass
    
    # Factor 3: High hierarchy level (+0.1 if level <= 2)
    level = metadata.get('hierarchy', {}).get('level', 999)
    if level <= 2:
        confidence["value"] = min(1.0, confidence["value"] + 0.1)
        if not confidence["reason"]:
            confidence["reason"] = f"Tài liệu cấp cao (Level {level})"
    
    # Factor 4: Is deprecated (-0.5)
    if metadata.get('relationships', {}).get('replaced_by'):
        confidence["value"] = 0.3
        new_doc = metadata['relationships']['replaced_by'][0]
        confidence["reason"] = f"Đã bị thay thế bởi {new_doc}"
    
    return confidence
```

### 7. Usage Hints Generation

```python
# vietnamese_metadata_extractor.py (NEW function)

def _generate_usage_hints(self, text: str, metadata: Dict) -> Dict:
    """
    Generate usage hints based on document type and content
    
    Parameters:
    -----------
    text : str
        Document text
    metadata : Dict
        Current metadata
    
    Returns:
    --------
    Dict
        {
            "when_to_use": str,
            "when_not_to_use": str,
            "special_cases": str
        }
    """
    hints = {
        "when_to_use": "",
        "when_not_to_use": "",
        "special_cases": ""
    }
    
    doc_type = metadata.get('doc_type_group', 'GENERAL')
    
    # Template 1: LEGAL_RND documents
    if doc_type == "LEGAL_RND":
        # When to use
        projects = metadata.get('graph_context', {}).get('project_nodes', [])
        if projects:
            hints["when_to_use"] = f"Khi user hỏi về {', '.join(projects[:2])}"
        
        # Special cases for superseded docs
        if replaces := metadata.get('relationships', {}).get('replaces'):
            hints["special_cases"] = f"Thay thế {', '.join(replaces[:2])}. Nếu conflict → ưu tiên tài liệu này"
    
    # Template 2: HR_POLICY documents
    elif doc_type == "HR_POLICY":
        hints["when_to_use"] = "Khi nhân viên hỏi về quy định, chính sách nhân sự"
        hints["when_not_to_use"] = "Không dùng cho vấn đề tài chính, kế toán (xem tài liệu QMS)"
    
    # Template 3: IT_MANUAL documents
    elif doc_type == "IT_MANUAL":
        hints["when_to_use"] = "Khi user hỏi về hướng dẫn sử dụng hệ thống, phần mềm"
        hints["when_not_to_use"] = "Không dùng cho troubleshooting (xem IT Support KB)"
    
    # Template 4: Documents with financial data
    if metadata.get('financial', {}).get('budget'):
        if not hints["special_cases"]:
            hints["special_cases"] = "Xem kỹ cột Ghi chú trong bảng ngân sách để biết VAT đã bao gồm chưa"
    
    # Compress to max 100 tokens
    total_tokens = sum(self._count_tokens(v) for v in hints.values())
    if total_tokens > 100:
        hints = self._compress_hints(hints, max_tokens=100)
    
    return hints


def _compress_hints(self, hints: Dict, max_tokens: int = 100) -> Dict:
    """Compress hints to fit token budget"""
    # Priority: special_cases > when_to_use > when_not_to_use
    compressed = {}
    budget_left = max_tokens
    
    for key in ["special_cases", "when_to_use", "when_not_to_use"]:
        if hints[key]:
            tokens = self._count_tokens(hints[key])
            if tokens <= budget_left:
                compressed[key] = hints[key]
                budget_left -= tokens
            else:
                # Truncate to fit
                compressed[key] = hints[key][:int(budget_left * 1.3)]  # ~1.3 chars per token
                break
    
    return compressed
```

### 8. Main Integration

```python
# vietnamese_metadata_extractor.py (MODIFY extract() method)

def extract(self, text: str, filename: str = "") -> Dict:
    """
    Main extraction method
    
    MODIFIED: Add usage_instructions extraction
    """
    # ... existing code ...
    
    # ADD: Extract usage instructions if needed
    if self.should_generate_instructions(result):
        result['usage_instructions'] = self._extract_usage_instructions(text, result)
    else:
        result['usage_instructions'] = {}  # Empty for simple docs
    
    return result


def _extract_usage_instructions(self, text: str, metadata: Dict) -> Dict:
    """
    Extract complete usage instructions
    
    Parameters:
    -----------
    text : str
        Document text
    metadata : Dict
        Current metadata
    
    Returns:
    --------
    Dict
        Complete usage_instructions object
    """
    instructions = {
        "scope": self._extract_scope(text, metadata),
        "interpretation_logic": self._extract_interpretation_logic(text, metadata),
        "pre_requisites": self._extract_prerequisites(metadata),
        "confidence_score": self._calculate_confidence(metadata),
        "usage_hints": self._generate_usage_hints(text, metadata)
    }
    
    # Token budget check
    total_tokens = self._count_tokens(instructions)
    if total_tokens > 350:  # Max budget
        instructions = self._compress_instructions(instructions, max_tokens=350)
    
    return instructions


def _compress_instructions(self, instructions: Dict, max_tokens: int = 350) -> Dict:
    """
    Compress instructions to fit token budget
    
    Priority:
    1. confidence_score (always keep)
    2. scope.supersedes (critical for conflicts)
    3. interpretation_logic (high value)
    4. usage_hints.special_cases
    5. Others
    """
    compressed = {"confidence_score": instructions["confidence_score"]}  # Always keep
    budget_left = max_tokens - self._count_tokens(compressed)
    
    # Priority 2: scope.supersedes
    if instructions["scope"].get("supersedes"):
        compressed["scope"] = {"supersedes": instructions["scope"]["supersedes"]}
        budget_left -= self._count_tokens(compressed["scope"])
    
    # Priority 3: interpretation_logic (truncate if needed)
    if instructions["interpretation_logic"] and budget_left > 100:
        logic_tokens = self._count_tokens(instructions["interpretation_logic"])
        if logic_tokens <= budget_left - 100:  # Keep 100 for others
            compressed["interpretation_logic"] = instructions["interpretation_logic"]
        else:
            # Keep only first 2 rules
            logic = instructions["interpretation_logic"]
            compressed["interpretation_logic"] = dict(list(logic.items())[:2])
        budget_left -= self._count_tokens(compressed["interpretation_logic"])
    
    # Add remaining fields if budget allows
    # ... (similar logic for other fields)
    
    return compressed
```

---

## 🧪 TEST CASES

### Test 1: Simple Document (No Instructions)

```python
def test_simple_document_no_instructions():
    """Test that simple documents don't generate instructions"""
    
    # Given: Simple report with no complex features
    text = """
    BÁO CÁO TIẾN ĐỘ THÁNG 12
    
    Dự án đang diễn ra tốt. Team đã hoàn thành 80% công việc.
    """
    
    extractor = VietnameseMetadataExtractor()
    result = extractor.extract(text)
    
    # Then: No instructions should be generated
    assert result['usage_instructions'] == {}
    print("✅ Test passed: Simple doc has no instructions")


def test_complex_document_has_instructions():
    """Test that complex documents generate instructions"""
    
    # Given: Complex decision with financial data + supersedes
    text = """
    QUYẾT ĐỊNH 324/QĐ-CTCT
    V/v Phê duyệt Dự án AISAS
    
    Căn cứ Quyết định 210/QĐ-CTCT (nay đã bị thay thế);
    
    QUYẾT ĐỊNH:
    Điều 1. Phê duyệt ngân sách 2,120,000,000 VND
    
    Phụ lục 1:
    | Hạng mục | Ngân sách | Ghi chú |
    | Thiết bị | 1,200,000,000 | Chưa bao gồm 10% VAT |
    """
    
    extractor = VietnameseMetadataExtractor()
    result = extractor.extract(text)
    
    # Then: Should have instructions
    assert 'usage_instructions' in result
    assert 'scope' in result['usage_instructions']
    assert 'interpretation_logic' in result['usage_instructions']
    
    # Should detect supersedes
    assert '210/QĐ-CTCT' in result['usage_instructions']['scope']['supersedes']
    
    # Should have financial interpretation
    assert 'financial_table' in result['usage_instructions']['interpretation_logic']
    assert 'VAT' in result['usage_instructions']['interpretation_logic']['financial_table']
    
    print("✅ Test passed: Complex doc has complete instructions")


def test_token_budget_limit():
    """Test that instructions respect token budget"""
    
    # Given: Very complex document
    text = """
    ... very long complex document ...
    """
    
    extractor = VietnameseMetadataExtractor()
    result = extractor.extract(text)
    
    # Then: Instructions should be under 350 tokens
    instructions_tokens = extractor._count_tokens(result['usage_instructions'])
    assert instructions_tokens <= 350
    
    print(f"✅ Test passed: Instructions = {instructions_tokens} tokens (< 350)")


def test_confidence_scoring():
    """Test confidence score calculation"""
    
    # Test 1: New document replacing old one → confidence = 1.0
    metadata = {
        'relationships': {
            'replaces': ['210/QĐ-CTCT']
        }
    }
    
    extractor = VietnameseMetadataExtractor()
    confidence = extractor._calculate_confidence(metadata)
    
    assert confidence['value'] == 1.0
    assert '210/QĐ-CTCT' in confidence['reason']
    
    # Test 2: Deprecated document → confidence = 0.3
    metadata = {
        'relationships': {
            'replaced_by': ['450/QĐ-CTCT']
        }
    }
    
    confidence = extractor._calculate_confidence(metadata)
    assert confidence['value'] == 0.3
    
    print("✅ Test passed: Confidence scoring works correctly")
```

---

## 🎨 UI MOCKUP (Streamlit)

```python
# app.py - Add to metadata editor section

def render_usage_instructions_editor():
    """Render UI for editing usage instructions"""
    
    st.markdown("### 📖 Usage Instructions (Tùy chọn)")
    
    if not st.session_state.result.document_meta.get('usage_instructions'):
        if st.button("➕ Tạo Usage Instructions"):
            # Generate instructions
            instructions = generate_instructions(
                st.session_state.result.text,
                st.session_state.result.document_meta
            )
            st.session_state.result.document_meta['usage_instructions'] = instructions
            st.rerun()
        return
    
    instructions = st.session_state.result.document_meta['usage_instructions']
    
    # Section 1: Scope
    with st.expander("🎯 Scope - Phạm vi áp dụng", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            applicable = st.text_area(
                "Áp dụng cho",
                value=instructions['scope'].get('applicable_to', ''),
                help="Tài liệu này áp dụng cho đối tượng/thời gian nào?"
            )
        
        with col2:
            excludes = st.text_area(
                "Loại trừ",
                value=instructions['scope'].get('excludes', ''),
                help="Không áp dụng cho trường hợp nào?"
            )
        
        supersedes = st.text_input(
            "Thay thế các tài liệu",
            value=", ".join(instructions['scope'].get('supersedes', [])),
            help="Danh sách doc_number, cách nhau bởi dấu phẩy"
        )
    
    # Section 2: Interpretation Logic
    with st.expander("📊 Interpretation Logic - Cách đọc/hiểu"):
        logic = instructions.get('interpretation_logic', {})
        
        # Financial table
        if 'financial_table' in logic:
            financial = st.text_area(
                "Cách đọc bảng tài chính",
                value=logic['financial_table'],
                height=100
            )
        
        # Approval logic
        if 'approval_conditions' in logic:
            approval = st.text_area(
                "Logic phê duyệt",
                value=logic['approval_conditions']
            )
        
        # Add custom logic
        st.markdown("**Thêm logic tùy chỉnh:**")
        custom_key = st.text_input("Tên logic (vd: 'vat_calculation')")
        custom_value = st.text_area("Mô tả logic")
        if st.button("➕ Thêm logic"):
            if custom_key and custom_value:
                logic[custom_key] = custom_value
                st.success(f"Đã thêm logic: {custom_key}")
    
    # Section 3: Usage Hints
    with st.expander("💡 Usage Hints - Gợi ý sử dụng"):
        hints = instructions.get('usage_hints', {})
        
        when_use = st.text_area(
            "Khi nào dùng tài liệu này?",
            value=hints.get('when_to_use', ''),
            help="VD: Khi user hỏi về ngân sách dự án AISAS"
        )
        
        when_not_use = st.text_area(
            "Khi nào KHÔNG dùng?",
            value=hints.get('when_not_to_use', ''),
            help="VD: Không dùng cho vấn đề kế toán nội bộ"
        )
        
        special = st.text_area(
            "Trường hợp đặc biệt",
            value=hints.get('special_cases', ''),
            help="VD: Nếu conflict với QĐ 210 → ưu tiên QĐ 324"
        )
    
    # Token budget indicator
    total_tokens = count_tokens(instructions)
    budget_color = "green" if total_tokens <= 350 else "red"
    st.markdown(f"**Token budget:** :{budget_color}[{total_tokens}/350]")
    
    if total_tokens > 350:
        st.warning("⚠️ Instructions quá dài! Hãy rút gọn để dưới 350 tokens.")
    
    # Save button
    if st.button("💾 Lưu Usage Instructions"):
        # Update instructions
        instructions['scope'] = {
            'applicable_to': applicable,
            'excludes': excludes,
            'supersedes': [s.strip() for s in supersedes.split(',') if s.strip()]
        }
        instructions['usage_hints'] = {
            'when_to_use': when_use,
            'when_not_to_use': when_not_use,
            'special_cases': special
        }
        
        st.session_state.result.document_meta['usage_instructions'] = instructions
        st.success("✅ Đã lưu Usage Instructions!")
        st.rerun()
```

---

## 📝 MIGRATION SCRIPT

```python
# migrate_add_usage_instructions.py

import json
from pathlib import Path
from vietnamese_metadata_extractor import VietnameseMetadataExtractor

def migrate_existing_documents(documents_dir: str):
    """
    Migrate existing documents to add usage_instructions
    
    Parameters:
    -----------
    documents_dir : str
        Directory containing document.json files
    """
    extractor = VietnameseMetadataExtractor()
    stats = {"total": 0, "updated": 0, "skipped": 0}
    
    for doc_file in Path(documents_dir).rglob("*_document.json"):
        stats["total"] += 1
        
        # Load document
        with open(doc_file, 'r', encoding='utf-8') as f:
            doc_meta = json.load(f)
        
        # Check if already has usage_instructions
        if 'usage_instructions' in doc_meta:
            stats["skipped"] += 1
            continue
        
        # Check if should generate
        if not extractor.should_generate_instructions(doc_meta):
            doc_meta['usage_instructions'] = {}  # Empty for simple docs
            stats["skipped"] += 1
        else:
            # Load passages to get original text
            passages_file = str(doc_file).replace('_document.json', '_passages.jsonl')
            if not Path(passages_file).exists():
                stats["skipped"] += 1
                continue
            
            # Read passages
            passages = []
            with open(passages_file, 'r', encoding='utf-8') as f:
                for line in f:
                    passages.append(json.loads(line))
            
            # Reconstruct text
            text = "\n\n".join([p['content'] for p in passages])
            
            # Generate instructions
            doc_meta['usage_instructions'] = extractor._extract_usage_instructions(text, doc_meta)
            stats["updated"] += 1
        
        # Save back
        with open(doc_file, 'w', encoding='utf-8') as f:
            json.dump(doc_meta, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Updated: {doc_file.name}")
    
    print("\n" + "="*50)
    print("MIGRATION COMPLETE")
    print(f"Total documents: {stats['total']}")
    print(f"Updated: {stats['updated']}")
    print(f"Skipped: {stats['skipped']}")
    print("="*50)


if __name__ == "__main__":
    migrate_existing_documents("/path/to/documents")
```

---

## ✅ CHECKLIST

### Day 1: Core Implementation
- [ ] Add `usage_instructions` to METADATA_SCHEMA
- [ ] Implement `should_generate_instructions()`
- [ ] Implement `_extract_scope()`
- [ ] Implement `_extract_interpretation_logic()`
- [ ] Implement `_extract_prerequisites()`
- [ ] Implement `_calculate_confidence()`
- [ ] Implement `_generate_usage_hints()`
- [ ] Unit tests for each function
- [ ] Integration test with sample document

### Day 2: Advanced Features
- [ ] Implement `_compress_instructions()`
- [ ] Token budget validator
- [ ] UI for editing instructions
- [ ] Preview display
- [ ] A/B testing setup

### Day 3: Production
- [ ] Migration script
- [ ] Test with 20+ real documents
- [ ] Measure token overhead
- [ ] Benchmark accuracy improvement
- [ ] Update documentation
- [ ] Code review
- [ ] Deploy to production

---

**Ready to start? Let me know and I'll begin coding! 🚀**
