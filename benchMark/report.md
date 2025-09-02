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
Tôi sẽ tạo dataset khó hơn để thử thách thực sự khả năng của model. Dataset mới sẽ có nhiều chủ đề tương tự, câu hỏi ambiguous và yêu cầu reasoning.

## 📚 data/content.md (Dataset khó hơn)

```markdown
# Hệ thống Quản lý Tri thức Doanh nghiệp

## Quy trình Mua hàng và Thanh toán

### Quy trình Mua hàng Nội bộ
Nhân viên cần tuân thủ quy trình mua hàng nội bộ khi có nhu cầu mua sắm cho công ty. Đầu tiên, nhân viên phải tạo yêu cầu mua hàng (Purchase Request) trên hệ thống ERP với đầy đủ thông tin: mô tả sản phẩm, số lượng, đơn giá ước tính, lý do mua hàng. Yêu cầu này cần được phê duyệt bởi trưởng phòng trực tiếp.

Sau khi được phê duyệt, bộ phận Procurement sẽ tiến hành tìm kiếm nhà cung cấp phù hợp. Đối với các đơn hàng có giá trị dưới 50 triệu đồng, có thể chọn nhà cung cấp trực tiếp. Đối với đơn hàng trên 50 triệu đồng, bắt buộc phải có ít nhất 3 báo giá từ các nhà cung cấp khác nhau.

### Quy trình Thanh toán Khách hàng
Quy trình thanh toán cho khách hàng được thiết kế để đảm bảo tính minh bạch và chính xác. Khi khách hàng thực hiện thanh toán, bộ phận Kế toán sẽ kiểm tra và đối chiếu với hóa đơn đã xuất. Các phương thức thanh toán được chấp nhận bao gồm: chuyển khoản ngân hàng, tiền mặt (với hạn mức tối đa 20 triệu đồng), và thẻ tín dụng.

Thời gian xử lý thanh toán thường là 1-2 ngày làm việc đối với chuyển khoản, và ngay lập tức đối với tiền mặt hoặc thẻ. Tất cả các giao dịch thanh toán đều được ghi nhận trong hệ thống kế toán và tạo biên lai điện tử gửi cho khách hàng.

## Chính sách Nhân sự và Phúc lợi

### Chính sách Nghỉ phép
Công ty áp dụng chính sách nghỉ phép linh hoạt nhằm đảm bảo cân bằng giữa công việc và cuộc sống của nhân viên. Nhân viên toàn thời gian được hưởng 12 ngày nghỉ phép có lương trong năm, không bao gồm các ngày lễ tết theo quy định của nhà nước.

Nhân viên có thể tích lũy tối đa 5 ngày nghỉ phép sang năm sau. Việc xin nghỉ phép cần được đăng ký trước ít nhất 3 ngày làm việc thông qua hệ thống HR. Trường hợp nghỉ đột xuất do ốm đau, nhân viên cần báo cáo cho quản lý trực tiếp trong vòng 4 giờ kể từ giờ làm việc.

### Chính sách Đào tạo và Phát triển
Công ty cam kết đầu tư vào việc phát triển năng lực của nhân viên thông qua các chương trình đào tạo đa dạng. Mỗi nhân viên được phân bổ ngân sách đào tạo tối thiểu 10 triệu đồng mỗi năm. Các hình thức đào tạo bao gồm: khóa học trực tuyến, hội thảo chuyên môn, chứng chỉ nghề nghiệp.

Nhân viên tham gia đào tạo bằng ngân sách công ty cần cam kết làm việc tối thiểu 18 tháng sau khi hoàn thành khóa học. Trường hợp vi phạm cam kết, nhân viên phải hoàn trả 70% chi phí đào tạo. Công ty cũng khuyến khích nhân viên tự học và sẽ hỗ trợ 50% chi phí cho các khóa học có liên quan đến công việc.

## Hệ thống Công nghệ Thông tin

### Bảo mật Thông tin và Dữ liệu
Công ty áp dụng các biện pháp bảo mật thông tin nghiêm ngặt để bảo vệ dữ liệu khách hàng và tài sản trí tuệ của doanh nghiệp. Tất cả nhân viên phải sử dụng mật khẩu mạnh với độ dài tối thiểu 12 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt.

Việc truy cập vào các hệ thống quan trọng được kiểm soát thông qua VPN và xác thực đa yếu tố (MFA). Dữ liệu nhạy cảm được mã hóa cả khi lưu trữ và truyền tải. Nhân viên không được phép sử dụng thiết bị cá nhân để truy cập dữ liệu công ty, trừ khi đã cài đặt phần mềm bảo mật được công ty phê duyệt.

### Quy trình Sao lưu và Phục hồi Dữ liệu
Hệ thống sao lưu dữ liệu được thực hiện tự động hàng ngày vào lúc 2:00 AM. Dữ liệu được sao lưu ở 3 vị trí khác nhau: server nội bộ, cloud storage, và băng từ offline. Thời gian lưu trữ là 7 năm đối với dữ liệu quan trọng và 3 năm đối với dữ liệu thông thường.

Quy trình phục hồi dữ liệu được kiểm tra định kỳ mỗi quý để đảm bảo tính khả dụng. RTO (Recovery Time Objective) của hệ thống là 4 giờ và RPO (Recovery Point Objective) là 1 giờ. Trong trường hợp xảy ra sự cố, bộ phận IT sẽ kích hoạt plan phục hồi và thông báo cho toàn bộ nhân viên.

## Quy trình Kinh doanh và Marketing

### Quy trình Phát triển Sản phẩm Mới
Việc phát triển sản phẩm mới tại công ty tuân theo quy trình Gate Stage standardized. Giai đoạn đầu là nghiên cứu thị trường và xác định nhu cầu khách hàng thông qua khảo sát và phân tích competitive. Đội ngũ Product Manager sẽ tạo Product Requirements Document (PRD) chi tiết.

Sau khi PRD được phê duyệt, đội phát triển sẽ tạo prototype và tiến hành user testing với nhóm khách hàng mục tiêu. Feedback được tích hợp để hoàn thiện sản phẩm trước khi chuyển sang giai đoạn sản xuất hàng loạt. Toàn bộ quá trình từ ý tưởng đến launch thường mất 6-9 tháng.

### Chiến lược Marketing Số
Công ty tập trung vào marketing số với ngân sách phân bổ 60% cho digital channels và 40% cho traditional marketing. Các kênh digital chính bao gồm: social media marketing, search engine optimization, email marketing, và content marketing. ROI mục tiêu cho các chiến dịch digital là tối thiểu 300%.

Việc đo lường hiệu quả marketing được thực hiện thông qua các KPI như Cost Per Acquisition (CPA), Customer Lifetime Value (CLV), và conversion rate. Dữ liệu được thu thập và phân tích hàng tuần để tối ưu hóa chiến dịch. Công ty sử dụng marketing automation tools để cá nhân hóa trải nghiệm khách hàng.

## Tuân thủ Pháp luật và Audit

### Quy định Tuân thủ GDPR và Bảo vệ Dữ liệu
Công ty tuân thủ nghiêm ngặt các quy định GDPR khi xử lý dữ liệu cá nhân của khách hàng EU. Khách hàng có quyền yêu cầu xem, sửa đổi, hoặc xóa dữ liệu cá nhân của mình bất kỳ lúc nào. Thời gian xử lý các yêu cầu này không quá 30 ngày.

Data Processing Impact Assessment (DPIA) được thực hiện đối với tất cả các hoạt động xử lý dữ liệu có rủi ro cao. Công ty đã bổ nhiệm Data Protection Officer (DPO) chuyên trách giám sát việc tuân thủ. Nhân viên được đào tạo định kỳ về quy định bảo vệ dữ liệu cá nhân.

### Quy trình Audit Nội bộ
Audit nội bộ được thực hiện hàng năm bởi đội ngũ độc lập để đánh giá tính hiệu quả của các quy trình và kiểm soát nội bộ. Phạm vi audit bao gồm: quy trình tài chính, quản trị rủi ro, tuân thủ pháp luật, và bảo mật thông tin.

Kết quả audit được báo cáo trực tiếp lên Ban Giám đốc và Hội đồng Quản trị. Các phát hiện được phân loại theo mức độ nghiêm trọng: Critical, High, Medium, Low. Management phải có action plan khắc phục trong vòng 90 ngày đối với các phát hiện Critical và High. Việc theo dõi thực hiện khắc phục được thực hiện hàng quý.
```

## 📋 data/test_suite.json (Câu hỏi khó)

```json
[
  {
    "id": 1,
    "question": "Giá trị đơn hàng nào yêu cầu phải có ít nhất 3 báo giá?",
    "expected_chunk": "chunk_0",
    "category": "procurement_policy"
  },
  {
    "id": 2,
    "question": "Hạn mức thanh toán bằng tiền mặt là bao nhiều?",
    "expected_chunk": "chunk_0",
    "category": "payment_policy"
  },
  {
    "id": 3,
    "question": "Nhân viên cần báo cáo bệnh trong thời gian bao lâu?",
    "expected_chunk": "chunk_1",
    "category": "hr_policy"
  },
  {
    "id": 4,
    "question": "Ngân sách đào tạo tối thiểu cho mỗi nhân viên mỗi năm là bao nhiều?",
    "expected_chunk": "chunk_1",
    "category": "training_policy"
  },
  {
    "id": 5,
    "question": "Độ dài tối thiểu của mật khẩu được yêu cầu là gì?",
    "expected_chunk": "chunk_2",
    "category": "security_policy"
  },
  {
    "id": 6,
    "question": "RTO của hệ thống phục hồi dữ liệu là bao nhiều giờ?",
    "expected_chunk": "chunk_2",
    "category": "data_recovery"
  },
  {
    "id": 7,
    "question": "Thời gian phát triển sản phẩm từ ý tưởng đến launch thường là bao lâu?",
    "expected_chunk": "chunk_3",
    "category": "product_development"
  },
  {
    "id": 8,
    "question": "ROI mục tiêu tối thiểu cho các chiến dịch digital marketing là bao nhiều phần trăm?",
    "expected_chunk": "chunk_3",
    "category": "marketing_strategy"
  },
  {
    "id": 9,
    "question": "Thời gian xử lý yêu cầu GDPR của khách hàng không được quá bao lâu?",
    "expected_chunk": "chunk_4",
    "category": "gdpr_compliance"
  },
  {
    "id": 10,
    "question": "Các phát hiện audit Critical và High cần được khắc phục trong thời gian bao lâu?",
    "expected_chunk": "chunk_4",
    "category": "audit_process"
  },
  {
    "id": 11,
    "question": "Ai chịu tr책nhiệm phê duyệt yêu cầu mua hàng nội bộ?",
    "expected_chunk": "chunk_0",
    "category": "approval_process"
  },
  {
    "id": 12,
    "question": "Nhân viên vi phạm cam kết đào tạo phải hoàn trả bao nhiều phần trăm chi phí?",
    "expected_chunk": "chunk_1",
    "category": "training_commitment"
  },
  {
    "id": 13,
    "question": "Dữ liệu quan trọng được lưu trữ trong bao nhiều năm?",
    "expected_chunk": "chunk_2",
    "category": "data_retention"
  },
  {
    "id": 14,
    "question": "Tỷ lệ phân bổ ngân sách giữa digital và traditional marketing là gì?",
    "expected_chunk": "chunk_3",
    "category": "budget_allocation"
  },
  {
    "id": 15,
    "question": "Việc theo dõi khắc phục audit được thực hiện với tần suất như thế nào?",
    "expected_chunk": "chunk_4",
    "category": "audit_followup"
  },
  {
    "id": 16,
    "question": "Nhân viên có thể tích lũy tối đa bao nhiêu ngày nghỉ phép sang năm sau?",
    "expected_chunk": "chunk_1",
    "category": "leave_policy"
  },
  {
    "id": 17,
    "question": "Hệ thống sao lưu dữ liệu được thực hiện vào thời gian nào trong ngày?",
    "expected_chunk": "chunk_2",
    "category": "backup_schedule"
  },
  {
    "id": 18,
    "question": "Cost Per Acquisition được sử dụng để đo lường điều gì?",
    "expected_chunk": "chunk_3",
    "category": "marketing_kpi"
  }
]
```

## ⚙️ Cập nhật configs/model_config.json

```json
{
  "model": {
    "name": "Qwen/Qwen3-Embedding-0.6B",
    "device": "auto",
    "batch_size": 32,
    "max_seq_length": 512,
    "normalize_embeddings": true
  },
  "evaluation": {
    "chunk_size": 120,
    "chunk_overlap": 20,
    "top_k": 5,
    "similarity_threshold": 0.0
  },
  "output": {
    "reports_dir": "reports",
    "save_detailed_results": true,
    "generate_visualizations": true
  }
}
```

Dataset này khó hơn vì:
- **Nhiều thông tin số cụ thể** cần trích xuất chính xác
- **Chủ đề tương tự nhau** dễ gây nhầm lẫn
- **Câu hỏi yêu cầu reasoning** thay vì chỉ keyword matching
- **Thông tin phân tán** giữa các chunks
- **Thuật ngữ chuyên môn** đòi hỏi hiểu ngữ cảnh

Chạy benchmark này sẽ cho kết quả realistic hơn, có thể MRR sẽ giảm xuống 0.6-0.8 và Hit Rate@5 khoảng 70-85%.
---
PS C:\undertest\ragX\benchMark> python benchmark.py
✅ Configuration loaded from configs/model_config.json
🇻🇳 Vietnamese Embedding Benchmark Tool
============================================================
Model: Qwen/Qwen3-Embedding-0.6B
Reports directory: C:\undertest\ragX\benchMark\reports
============================================================

📚 STEP 1: Processing Vietnamese text data
----------------------------------------
✅ Đã tạo 10 chunks từ data/content.md
📊 Số từ trung bình mỗi chunk: 112.3
📏 Khoảng từ: 104 - 117 từ
✅ Đã load 18 câu hỏi test
💾 Đã xuất thông tin chunks: reports\chunks_info.json

🤖 STEP 2: Loading embedding model
----------------------------------------
🚀 GPU detected: NVIDIA GeForce RTX 2080 Ti
💾 GPU memory: 11.8 GB
📥 Loading model: Qwen/Qwen3-Embedding-0.6B...
✅ Model loaded successfully in 6.24s
✅ Model loaded: Qwen/Qwen3-Embedding-0.6B
🔧 Device: cuda
📐 Embedding dimension: 1024
📐 Model info: {'name': 'Qwen/Qwen3-Embedding-0.6B', 'device': 'cuda', 'embedding_dimension': 1024, 'max_seq_length': 32768, 'model_size_mb': 2272.7, 'supports_batch': True, 'gpu_name': 'NVIDIA GeForce RTX 2080 Ti', 'gpu_memory_total': 11.810832384}

🔄 STEP 3: Generating embeddings
----------------------------------------
🔄 Encoding 10 texts...
Batches: 100%|███████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.15it/s]
✅ Encoding completed in 0.47s
⚡ Speed: 21.3 texts/second
📊 Shape: (10, 1024)
⚡ Embedding generation completed in 0.47s
📊 Speed: 21.2 texts/second

🔍 STEP 4: Running similarity search evaluation
----------------------------------------
🔍 Running batch search for 18 queries...
🔄 Encoding 18 texts...
✅ Encoding completed in 0.06s
⚡ Speed: 310.3 texts/second
📊 Shape: (18, 1024)
🔍 Search completed in 0.08s
⚡ Search speed: 216.9 queries/second

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
⏱️  Total time: 7.38s
🎯 Overall MRR: 1.000
📊 Hit Rate@5: 100.0%
💾 Reports saved in: C:\undertest\ragX\benchMark\reports
💾 Detailed results saved: reports\benchmark_results_20250903_060332.json

📋 Next Steps:
1. Open 'reports/benchmark_report.html' in your browser
2. Review interactive charts in 'reports/charts/' directory
3. Check detailed results in the JSON files
