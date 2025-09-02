Tiếp tục với README.md:


có hiệu suất thấp nhất
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
