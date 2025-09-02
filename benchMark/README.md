## 📖 README.md


# Vietnamese Qwen3 Embedding Benchmark 🇻🇳

Công cụ benchmark chuyên dụng cho model **Qwen/Qwen3-Embedding-0.6B** trên dữ liệu tiếng Việt với tối ưu GPU.

## ✨ Tính năng

- **🎯 Chuyên dụng cho Qwen3**: Tối ưu cho model Qwen/Qwen3-Embedding-0.6B
- **🇻🇳 Tiếng Việt**: Hỗ trợ đầy đủ xử lý văn bản tiếng Việt (pyvi, underthesea)
- **⚡ GPU Acceleration**: Tự động detect và sử dụng GPU/CUDA
- **📊 Metrics đầy đủ**: MRR, Hit Rate@K, MAP, NDCG, Precision, Recall
- **📈 Visualizations**: Interactive charts với Plotly
- **📋 HTML Reports**: Báo cáo HTML chi tiết và professional

## 🚀 Cài đặt

### 1. Clone project
```bash
git clone <your-repo>
cd vietnamese_qwen3_benchmark
```

### 2. Tạo virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cài đặt GPU support (nếu có)
```bash
# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1  
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## 📊 Cách sử dụng

### Chạy benchmark đơn giản
```bash
python benchmark.py
```

### Với custom config
```bash
python benchmark.py --config configs/model_config.json --verbose
```

### Cấu trúc sau khi chạy
```
vietnamese_qwen3_benchmark/
├── reports/
│   ├── benchmark_report.html          # Báo cáo HTML chính
│   ├── benchmark_results_20241201_143022.json
│   ├── chunks_info.json               # Debug info cho chunks
│   └── charts/
│       ├── metrics_overview.html      # Interactive charts
│       ├── detailed_analysis.html
│       ├── performance_radar.html
│       └── category_performance.html
└── model_cache/                       # Cached models
```

## ⚙️ Configuration

### Tùy chỉnh model trong `configs/model_config.json`:
```json
{
  "model": {
    "name": "Qwen/Qwen3-Embedding-0.6B",  // ← Thay đổi model ở đây
    "device": "auto",
    "batch_size": 32,
    "max_seq_length": 512,
    "normalize_embeddings": true
  }
}
```

### Thay đổi dữ liệu test:
- **Content**: Chỉnh sửa `data/content.md`
- **Questions**: Cập nhật `data/test_suite.json`

## 📈 Metrics được đánh giá

| Metric | Mô tả | Mục tiêu |
|--------|-------|----------|
| **MRR** | Mean Reciprocal Rank | > 0.65 |
| **Hit Rate@1** | Top-1 accuracy | > 50% |
| **Hit Rate@5** | Top-5 accuracy | > 75% |
| **Precision@5** | Precision at 5 | > 0.6 |
| **NDCG@5** | Ranking quality | > 0.6 |
| **MAP@5** | Mean Average Precision | > 0.5 |

## 🎯 Kết quả mẫu

```
🎉 BENCHMARK COMPLETED SUCCESSFULLY!
============================================================
⏱️  Total time: 45.23s
🎯 Overall MRR: 0.724
📊 Hit Rate@5: 81.2%
💾 Reports saved in: /path/to/reports
```

## 🔧 Troubleshooting

### CUDA Out of Memory
```bash
# Giảm batch size trong config
"batch_size": 16  # hoặc 8
```

### Model không tải được
```bash
# Xóa cache và thử lại
rm -rf model_cache/
python benchmark.py
```

### Lỗi Vietnamese NLP
```bash
pip uninstall underthesea pyvi
pip install underthesea pyvi
```

## 📊 Hiểu kết quả

### Performance Levels:
- **Excellent** (MRR ≥ 0.7): Sẵn sàng production
- **Good** (MRR ≥ 0.5): Có thể sử dụng với optimizations
- **Average** (MRR ≥ 0.3): Cần fine-tuning
- **Poor** (MRR < 0.3): Cần đổi model hoặc cải thiện data

### Phân tích Category:
- Kiểm tra category nào có hiệu suất thấp nhất
- Xem câu hỏi nào khó nhất (không tìm thấy trong top-5)
- Phân tích score gap giữa top-1 và correct answer

## 🔄 Workflow tùy chỉnh

### Thay đổi model
```bash
# Chỉnh sửa configs/model_config.json
{
  "model": {
    "name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  }
}
```

### Thêm dữ liệu mới
```bash
# 1. Cập nhật data/content.md với nội dung mới
# 2. Tạo câu hỏi tương ứng trong data/test_suite.json
# 3. Chạy benchmark
python benchmark.py
```

### Batch processing nhiều models
```bash
# Tạo script để test nhiều models
for model in "Qwen/Qwen3-Embedding-0.6B" "sentence-transformers/LaBSE"
do
    echo "Testing $model"
    # Update config and run
    python benchmark.py --config configs/${model//\//_}.json
done
```

## 🎛️ Advanced Usage

### Memory optimization
```python
# Trong embedding_manager.py, tùy chỉnh:
def _get_optimal_batch_size(self, requested_batch_size: int) -> int:
    if self.device == "cuda":
        available_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        if available_memory < 4:
            return 8    # Giảm cho GPU nhỏ
        elif available_memory >= 16:
            return 128  # Tăng cho GPU lớn
```

### Custom metrics
```python
# Trong src/metrics.py, thêm metric mới:
def calculate_custom_metric(self, search_results, ground_truth):
    # Custom logic here
    return custom_score
```

## 📝 Logs và Debug

### Enable verbose logging
```bash
python benchmark.py --verbose
```

### Debug chunks
```bash
# Xem chunks_info.json để hiểu cách text được chia
cat reports/chunks_info.json | jq '.chunks[0]'
```

### Memory monitoring
```bash
# Theo dõi GPU memory trong quá trình chạy
watch -n 1 nvidia-smi
```

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/new-feature`
3. Test với Vietnamese data
4. Commit: `git commit -m 'Add Vietnamese feature'`
5. Push: `git push origin feature/new-feature`
6. Tạo Pull Request

## 📄 License

MIT License - xem LICENSE file.

## 🙏 Credits

- [Qwen Team](https://github.com/QwenLM/Qwen) - Qwen3-Embedding model
- [Sentence Transformers](https://www.sbert.net/) - Embedding framework
- [underthesea](https://github.com/undertheseanlp/underthesea) - Vietnamese NLP
- [pyvi](https://github.com/trungtv/pyvi) - Vietnamese tokenization

---

**Happy Benchmarking! 🚀**

Nếu gặp vấn đề, tạo issue trong repository hoặc liên hệ qua email.
```

## 🎯 Hướng dẫn chạy nhanh:

### 1. Cài đặt cơ bản:
```bash
# Clone và setup
git clone <repo>
cd vietnamese_qwen3_benchmark

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Chạy benchmark:
```bash
python benchmark.py
```

### 3. Xem kết quả:
- Mở `reports/benchmark_report.html` trong browser
- Xem các charts interactive trong `reports/charts/`
- Kiểm tra JSON results cho detailed data

## 🔧 Điều chỉnh model:

Để thay đổi model, chỉnh sửa `configs/model_config.json`:
```json
{
  "model": {
    "name": "your-model-name-here",  // ← Thay đổi tại đây
    "device": "auto",
    "batch_size": 32
  }
}
```

## 📊 Output Structure:

Sau khi chạy xong, bạn sẽ có:

1. **HTML Report**: `reports/benchmark_report.html` - Báo cáo tổng quan
2. **Interactive Charts**: `reports/charts/` - Các biểu đồ interactive
3. **JSON Results**: `reports/benchmark_results_*.json` - Dữ liệu chi tiết
4. **Debug Info**: `reports/chunks_info.json` - Thông tin chunks

## 🎯 Expected Performance:

Với Qwen3-Embedding-0.6B trên Vietnamese data:
- **MRR**: 0.65-0.75 (good range)  
- **Hit Rate@5**: 75-85%
- **Processing Speed**: 50-100 texts/second (GPU)
- **Memory Usage**: ~2-4GB GPU RAM

Project này được tối ưu hóa đặc biệt cho Vietnamese text processing và Qwen3 model, với GPU acceleration và comprehensive metrics để đánh giá performance một cách chính xác nhất.
