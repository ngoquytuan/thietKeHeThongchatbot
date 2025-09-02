Tôi sẽ tìm hiểu về dự án của bạn trong project knowledge để tạo ra danh sách các rules triển khai phù hợp.Dựa trên project knowledge, tôi sẽ tạo ra một danh sách các rules phải thực hiện khi triển khai dự án Hệ thống Trợ lý Tri thức Nội bộ. Từ thông tin về embedding models và kết quả đánh giá, đây là các quy tắc cốt lõi:

## **DANH SÁCH CÁC RULES TRIỂN KHAI DỰ ÁN**

### **📊 RULES VỀ EMBEDDING MODELS**

**Rule 1: Lựa chọn Model chính**
- **PHẢI** sử dụng `Qwen/Qwen3-Embedding-0.6B` làm model chính cho production
- **Lý do**: Đạt MRR và Hit Rate cao nhất (0.7812, 68.75%) với tốc độ xử lý vượt trội (37.9 giây)
- **Backup**: Sử dụng `AITeamVN/Vietnamese_Embedding` như model dự phòng

**Rule 2: Cấu hình Model Parameters**
- Max sequence length: **512 tokens**
- Batch size: **16** (cho Qwen3), **32** (cho Vietnamese_Embedding)  
- Normalize embeddings: **TRUE**
- Dimension: **1024** (cho cả hai model chính)

**Rule 3: Fallback Strategy**
- Khi model chính không khả dụng, tự động chuyển sang `paraphrase-multilingual-MiniLM-L12-v2`
- Model này có dimension **384**, tốc độ nhanh (23.1 giây) và vẫn đạt MRR 0.7188

### **🔧 RULES VỀ KỸ THUẬT**

**Rule 4: Xử lý Text Tiếng Việt**
- **PHẢI** sử dụng PyVi tokenizer thay vì underthesea
- Implement Unicode normalization cho tất cả input text
- Xử lý diacritics một cách chính xác
- Chunking size: **512 tokens** với respect sentence boundaries

**Rule 5: GPU Optimization**
- Target GPU utilization: **>70%**
- Memory requirement: **<2GB GPU RAM** per model
- Batch processing: **ENABLED**
- Implement model caching và lazy loading

**Rule 6: Performance Targets**
- **Hit Rate@5**: Tối thiểu **75%** cho Vietnamese queries
- **MRR**: Tối thiểu **0.65**  
- **Response time**: **<100ms** per query (bao gồm embedding + search)
- **Concurrent users**: Hỗ trợ tối đa **100 người dùng đồng thời**

### **📁 RULES VỀ DỮ LIỆU**

**Rule 7: Data Classification**
- Phân loại tài liệu theo 4 levels: **Guest, Nhân viên, Trưởng phòng, Giám đốc**
- Mỗi document phải có metadata về department và access level
- Implement proper access control dựa trên user role

**Rule 8: Document Processing**
- Support formats: **PDF, Word, TXT, JSON**
- Chunk size: **512 tokens** với overlap **50 tokens**
- Text preprocessing pipeline với Vietnamese-specific handling
- Validate document quality trước khi embedding

**Rule 9: Test Data Quality**
- **PHẢI** fix lỗi `chunk_7` trong test_suite.json trước khi production
- Ground truth dataset tối thiểu **200 query-document pairs**
- Cross-validation với holdout dataset **20%**

### **🏗️ RULES VỀ KIẾN TRÚC HỆ THỐNG**

**Rule 10: System Architecture**
- Implement microservices architecture với Docker containers
- API Gateway cho user authentication và rate limiting  
- Separate services: Document Processing, Embedding, Search, User Management
- Load balancer cho high availability

**Rule 11: Database Design**
- Vector database: **Qdrant** hoặc **Weaviate** cho embedding storage
- PostgreSQL cho metadata và user management
- Redis cho caching và session management
- Backup strategy cho tất cả databases

**Rule 12: Security & Compliance**
- JWT-based authentication
- Role-based access control (RBAC)
- Encrypt tất cả data at rest và in transit
- Audit logging cho tất cả user actions
- Regular security scanning

### **📈 RULES VỀ MONITORING & MAINTENANCE**

**Rule 13: Quality Assurance**
- Unit tests: **>90% code coverage**
- Integration tests cho end-to-end pipeline
- Performance testing với load simulation
- Validation tests với multiple evaluation runs

**Rule 14: Production Monitoring**
- Real-time metrics dashboard
- Alert system cho system health
- User feedback collection mechanism
- Model performance monitoring với automated retraining triggers

**Rule 15: Scalability Requirements**
- Auto-scaling based on CPU/Memory usage
- Database partitioning strategy
- CDN cho static resources
- Horizontal scaling capability cho embedding services

### **⚠️ RULES VỀ RISK MANAGEMENT**

**Rule 16: Error Handling**
- Graceful degradation khi models không khả dụng
- Comprehensive error logging và reporting
- User-friendly error messages bằng tiếng Việt
- Automatic retry mechanism với exponential backoff

**Rule 17: Data Privacy**
- Không log sensitive user queries
- Data anonymization cho analytics
- GDPR-compliant data handling
- Regular data cleanup policies

**Rule 18: Business Continuity**
- Disaster recovery plan với RTO <30 phút
- Regular backup testing
- Model versioning và rollback capability
- Maintenance window planning

### **🚀 RULES VỀ DEPLOYMENT**

**Rule 19: Environment Strategy**
- Development → Staging → Production pipeline
- Infrastructure as Code (Terraform/CloudFormation)
- Blue-green deployment cho zero downtime
- Automated testing trong mỗi stage

**Rule 20: Success Criteria**
- User adoption rate: **>60%** trong 3 tháng đầu
- Query response accuracy: **>75%** user satisfaction
- System uptime: **>99.5%**
- Performance benchmarks đạt tất cả targets đã định

---

**📋 CHECKLIST TRIỂN KHAI:**
- [ ] Setup embedding models theo Rule 1-3
- [ ] Implement Vietnamese text processing theo Rule 4  
- [ ] Optimize GPU usage theo Rule 5
- [ ] Setup monitoring system theo Rule 13-14
- [ ] Configure security theo Rule 12
- [ ] Test performance targets theo Rule 6
- [ ] Deploy theo environment strategy Rule 19
- [ ] Validate success criteria Rule 20

Những rules này được dựa trên kết quả đánh giá thực tế từ project knowledge và đảm bảo dự án sẽ được triển khai thành công với chất lượng cao cho hệ thống Trợ lý Tri thức Nội bộ.