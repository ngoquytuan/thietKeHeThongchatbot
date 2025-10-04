#!/usr/bin/env python3
"""
EMPIRICAL-based quality tests - measure actual behavior
File: tests/integration/test_search_quality_empirical.py
"""

import pytest
from sentence_transformers import SentenceTransformer
import numpy as np
import unicodedata
import re


class TestSearchQualityEmpirical:
    """
    Test actual model behavior, không predict thresholds
    Focus: Consistency, stability, và clear separation
    """
    
    @pytest.fixture(scope="class")
    def setup_model(self):
        model = SentenceTransformer(
            "Qwen/Qwen3-Embedding-0.6B",
            device="cuda"
        )
        return {"model": model}
    
    
    def preprocess_text(self, text: str) -> str:
        if not text:
            return ""
        text = unicodedata.normalize('NFC', text)
        text = text.lower()
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    
    def calculate_similarity(self, query: str, doc: str, model) -> float:
        query_proc = self.preprocess_text(query)
        doc_proc = self.preprocess_text(doc)
        
        query_emb = model.encode([query_proc])[0]
        doc_emb = model.encode([doc_proc])[0]
        
        cosine_sim = np.dot(query_emb, doc_emb) / (
            np.linalg.norm(query_emb) * np.linalg.norm(doc_emb)
        )
        
        return float(cosine_sim)
    
    
    def test_exact_match_near_perfect(self, setup_model):
        """Exact matches phải ≥ 0.95"""
        model = setup_model["model"]
        
        test_cases = [
            "cách xác định hướng nhà",
            "quy trình nghỉ phép",
            "chính sách bảo hiểm xã hội",
        ]
        
        for query in test_cases:
            similarity = self.calculate_similarity(query, query, model)
            assert similarity >= 0.95, f"Exact match: {similarity:.4f}"
            print(f"✅ Exact match '{query[:30]}...': {similarity:.4f}")
    
    
    def test_completely_different_domains(self, setup_model):
        """Completely different domains phải có clear separation"""
        model = setup_model["model"]
        
        # HR domain vs Food domain
        hr_queries = [
            "chính sách bảo hiểm nhân viên",
            "quy trình nghỉ phép",
        ]
        
        food_docs = [
            "cách nấu phở bò truyền thống",
            "công thức làm bánh mì giòn",
            "hướng dẫn làm gỏi cuốn",
        ]
        
        for query in hr_queries:
            for food_doc in food_docs:
                similarity = self.calculate_similarity(query, food_doc, model)
                
                # Relaxed threshold: different domains nên < 0.55
                assert similarity < 0.55, \
                    f"Cross-domain too high: {similarity:.4f}\n" \
                    f"  Query: '{query}'\n" \
                    f"  Doc: '{food_doc}'"
                
                print(f"✅ Cross-domain: {similarity:.4f} < 0.55")
    
    
    def test_same_domain_higher_than_different(self, setup_model):
        """Same domain > different domain (statistical)"""
        model = setup_model["model"]
        
        query = "quy trình nghỉ phép"
        
        # Same domain (HR/policy)
        same_domain_docs = [
            "chính sách nghỉ lễ",
            "quy định thời gian làm việc",
            "hướng dẫn đăng ký phép năm",
        ]
        
        # Different domain (Food)
        diff_domain_docs = [
            "cách nấu phở",
            "công thức làm bánh",
            "hướng dẫn nấu ăn",
        ]
        
        same_sims = [
            self.calculate_similarity(query, doc, model)
            for doc in same_domain_docs
        ]
        
        diff_sims = [
            self.calculate_similarity(query, doc, model)
            for doc in diff_domain_docs
        ]
        
        avg_same = np.mean(same_sims)
        avg_diff = np.mean(diff_sims)
        
        print(f"\nQuery: '{query}'")
        print(f"  Same domain avg: {avg_same:.4f}")
        print(f"  Diff domain avg: {avg_diff:.4f}")
        print(f"  Separation: {avg_same - avg_diff:.4f}")
        
        # Statistical separation
        assert avg_same > avg_diff, \
            f"Same domain ({avg_same:.4f}) should be > diff domain ({avg_diff:.4f})"
    
    
    def test_consistency_across_paraphrases(self, setup_model):
        """Paraphrases phải có similarity cao"""
        model = setup_model["model"]
        
        paraphrase_pairs = [
            ("quy trình nghỉ phép", "thủ tục xin nghỉ"),
            ("chính sách bảo hiểm", "quy định về bảo hiểm"),
            ("hướng dẫn cài đặt", "cách cài đặt"),
        ]
        
        for query, paraphrase in paraphrase_pairs:
            similarity = self.calculate_similarity(query, paraphrase, model)
            
            # Paraphrases nên > 0.70
            assert similarity > 0.70, \
                f"Paraphrase too low: {similarity:.4f}\n" \
                f"  '{query}' vs '{paraphrase}'"
            
            print(f"✅ Paraphrase: {similarity:.4f} - '{query}' vs '{paraphrase}'")
    
    
    def test_preprocessing_normalization(self, setup_model):
        """Case và whitespace không ảnh hưởng"""
        model = setup_model["model"]
        
        base = "quy trình nghỉ phép"
        variants = [
            "QUY TRÌNH NGHỈ PHÉP",
            "Quy Trình Nghỉ Phép",
            "quy   trình    nghỉ   phép",
        ]
        
        for variant in variants:
            similarity = self.calculate_similarity(base, variant, model)
            assert similarity >= 0.95, f"Normalization failed: {similarity:.4f}"
            print(f"✅ Normalized: {similarity:.4f}")
    
    
    def test_ranking_consistency(self, setup_model):
        """
        Test ranking consistency:
        Cho 1 query, ranking của documents phải stable
        """
        model = setup_model["model"]
        
        query = "chính sách bảo hiểm nhân viên"
        
        documents = [
            "chính sách bảo hiểm nhân viên",  # Exact
            "quy định bảo hiểm xã hội",  # Related
            "chính sách phúc lợi công ty",  # Somewhat related
            "quy trình tuyển dụng",  # Different aspect
            "hướng dẫn nấu ăn",  # Unrelated
        ]
        
        # Calculate similarities
        results = []
        for doc in documents:
            sim = self.calculate_similarity(query, doc, model)
            results.append({"doc": doc, "similarity": sim})
        
        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        print(f"\nQuery: '{query}'")
        print("Ranking:")
        for i, r in enumerate(results):
            print(f"  {i+1}. {r['similarity']:.4f} - {r['doc'][:50]}")
        
        # Key assertions:
        # 1. Exact match phải top
        assert results[0]["doc"] == "chính sách bảo hiểm nhân viên", \
            "Exact match not top!"
        
        # 2. Unrelated phải bottom
        assert results[-1]["doc"] == "hướng dẫn nấu ăn", \
            "Unrelated not bottom!"
        
        # 3. Top similarity > bottom similarity với margin đủ lớn
        margin = results[0]["similarity"] - results[-1]["similarity"]
        assert margin > 0.40, f"Separation too small: {margin:.4f}"
    
    
    def test_stability_over_runs(self, setup_model):
        """
        Test stability: Same query-doc pair nên return same similarity
        """
        model = setup_model["model"]
        
        query = "quy trình nghỉ phép"
        doc = "chính sách nghỉ lễ"
        
        # Calculate 5 times
        similarities = [
            self.calculate_similarity(query, doc, model)
            for _ in range(5)
        ]
        
        # Standard deviation phải rất thấp
        std = np.std(similarities)
        
        print(f"\nQuery: '{query}'")
        print(f"Doc: '{doc}'")
        print(f"Similarities: {[f'{s:.6f}' for s in similarities]}")
        print(f"Std dev: {std:.8f}")
        
        # Stability check
        assert std < 0.0001, f"Unstable: std={std:.8f}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])