PS C:\undertest\ragX\benchMark> python benchmark.py
✅ Configuration loaded from configs/model_config.json
🇻🇳 Vietnamese Embedding Benchmark Tool
============================================================
Model: Qwen/Qwen3-Embedding-0.6B
Reports directory: C:\undertest\ragX\benchMark\reports
============================================================

📚 STEP 1: Processing Vietnamese text data
----------------------------------------
✅ Đã tạo 6 chunks từ data/content.md
📊 Số từ trung bình mỗi chunk: 123.2
📏 Khoảng từ: 32 - 148 từ
✅ Đã load 16 câu hỏi test
💾 Đã xuất thông tin chunks: reports\chunks_info.json

🤖 STEP 2: Loading embedding model
----------------------------------------
🚀 GPU detected: NVIDIA GeForce RTX 2080 Ti
💾 GPU memory: 11.8 GB
📥 Loading model: Qwen/Qwen3-Embedding-0.6B...
✅ Model loaded successfully in 6.71s
✅ Model loaded: Qwen/Qwen3-Embedding-0.6B
🔧 Device: cuda
📐 Embedding dimension: 1024
📐 Model info: {'name': 'Qwen/Qwen3-Embedding-0.6B', 'device': 'cuda', 'embedding_dimension': 1024, 'max_seq_length': 32768, 'model_size_mb': 2272.7, 'supports_batch': True, 'gpu_name': 'NVIDIA GeForce RTX 2080 Ti', 'gpu_memory_total': 11.810832384}

🔄 STEP 3: Generating embeddings
----------------------------------------
🔄 Encoding 6 texts...
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.58it/s]
✅ Encoding completed in 0.39s
⚡ Speed: 15.3 texts/second
📊 Shape: (6, 1024)
⚡ Embedding generation completed in 0.40s
📊 Speed: 15.2 texts/second

🔍 STEP 4: Running similarity search evaluation
----------------------------------------
🔍 Running batch search for 16 queries...
🔄 Encoding 16 texts...
✅ Encoding completed in 0.05s
⚡ Speed: 307.5 texts/second
📊 Shape: (16, 1024)
🔍 Search completed in 0.08s
⚡ Search speed: 202.6 queries/second

📊 STEP 5: Calculating performance metrics
----------------------------------------
📈 Performance Summary:
   MRR: 1.000
   Hit_Rate@1: 100.0%
   Hit_Rate@3: 100.0%
   Hit_Rate@5: 100.0%
   Precision@5: 1.000
   Recall@5: 1.000
   NDCG@5: 2.948
   MAP@5: 0.457

📊 STEP 6: Generating visualizations and reports
----------------------------------------
📊 Metrics overview saved: reports\charts\metrics_overview.html
📈 Detailed analysis saved: reports\charts\detailed_analysis.html
🎯 Radar chart saved: reports\charts\performance_radar.html
📊 Category performance chart saved: reports\charts\category_performance.html
📋 HTML report saved: reports\benchmark_report.html
🧹 Memory cleanup completed

🎉 BENCHMARK COMPLETED SUCCESSFULLY!
============================================================
⏱️  Total time: 7.76s
🎯 Overall MRR: 1.000
📊 Hit Rate@5: 100.0%
💾 Reports saved in: C:\undertest\ragX\benchMark\reports
💾 Detailed results saved: reports\benchmark_results_20250903_055445.json

📋 Next Steps:
1. Open 'reports/benchmark_report.html' in your browser
2. Review interactive charts in 'reports/charts/' directory
3. Check detailed results in the JSON files

---
## 📊 Phân tích kết quả benchmark của bạn:

### ✅ **Kết quả chung: TUYỆT VỜI**
- **MRR: 1.000** (Perfect score - tất cả câu hỏi đều tìm thấy đáp án đúng ở vị trí #1)
- **Hit Rate@1: 100%** (Tất cả 16 câu hỏi đều có đáp án đúng ở top-1)
- **Hit Rate@5: 100%** (Tất cả câu hỏi đều có đáp án trong top-5)

### 🔍 **Điều này có ý nghĩa gì?**

**1. Dataset quá đơn giản:**
- Chỉ có 6 chunks, nhưng 16 câu hỏi
- Trung bình mỗi chunk có ~2.7 câu hỏi liên quan
- Model dễ dàng phân biệt được nội dung các chunks

**2. Model Qwen3-Embedding-0.6B hoạt động rất tốt với tiếng Việt:**
- Hiểu được semantic meaning của các câu hỏi
- Matching chính xác với nội dung chunks
- Embedding quality cao (1024 dimensions)

**3. Performance metrics bất thường:**
- **NDCG@5: 2.948** (>1.0 là bất thường - có lỗi trong tính toán)
- **MAP@5: 0.457** (thấp hơn expected với perfect hit rate)

### 🎯 **Đánh giá thực tế:**

**Positive:**
- Model load nhanh (6.71s)
- Embedding speed tốt (15.3 texts/s cho chunks, 307.5 queries/s)
- GPU utilization hiệu quả
- Không có crash hoặc memory issues

**Concerns:**
- Dataset quá easy, không realistic
- Một số metrics tính toán sai (NDCG > 1.0)
- Thiếu challenge để test model limits

### 💡 **Recommendations:**

**1. Tăng độ khó dataset:**
```json
// configs/model_config.json
{
  "evaluation": {
    "chunk_size": 100,     // Tạo nhiều chunks hơn
    "chunk_overlap": 15,   // Giảm overlap
  }
}
```

**2. Thêm content phức tạp hơn:**
- Thêm nhiều chủ đề khác nhau vào `data/content.md`
- Tạo câu hỏi ambiguous hoặc trick questions
- Thêm content tương tự nhau để test discrimination

**3. Fix metrics calculation:**
- NDCG@5 không được > 1.0
- MAP@5 calculation cần review

### 🏆 **Kết luận:**
Model Qwen3-Embedding-0.6B **hoạt động xuất sắc** với tiếng Việt trong test case này, nhưng dataset hiện tại quá đơn giản để đánh giá đầy đủ khả năng của model. Cần dataset challenging hơn để có benchmark meaningful.

Bạn có muốn tôi tạo dataset khó hơn để test thực sự khả năng của model không?
