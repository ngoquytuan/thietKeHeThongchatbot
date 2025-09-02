Dựa trên tài liệu dự án, tôi sẽ tạo cho bạn một danh sách các rules (quy tắc) ngắn gọn để triển khai dự án này:

## 🔧 RULES TRIỂN KHAI DỰ ÁN

### **EMBEDDING & AI MODELS**
1. **Embedding Models**: Luôn sử dụng `Qwen/Qwen3-Embedding-0.6B`, back up là `AITeamVN/Vietnamese_Embedding` cả hai có hiệu suất ngang bằng cho tiếng Việt
2. **Thư viện Embedding**: Bắt buộc dùng `sentence-transformers` để đạt hiệu quả cao nhất
3. **GPU Support**: Luôn cài `torch` với GPU support vì máy có GPU
4. **LLM Models**: Ưu tiên GLM-4.5-Air cho RAG, fallback là OpenAI GPT-4

### **PYTHON & DEPENDENCIES**
5. **Python Version**: Bắt buộc Python 3.10.11 để cài được `underthesea`, `pyvi`
6. **Vietnamese Processing**: Luôn dùng `pyvi>=0.1.1` và `underthesea` cho xử lý tiếng Việt
7. **Requirements**: Theo đúng file requirements.txt đã định nghĩa (sentence-transformers>=2.2.2, torch>=2.0.0)

### **FRONTEND & DEPLOYMENT**
8. **NextJS Version**: Nếu dùng NextJS thì bắt buộc version 18.x để dễ cài dependencies
9. **Containerization**: Luôn triển khai trong Docker khi testing/development
10. **Database**: PostgreSQL làm relational DB, Chroma/FAISS làm Vector DB

### **DATA & PROCESSING**
11. **Language Priority**: Tiếng Việt là ngôn ngữ xử lý ưu tiên số 1
12. **Text Processing**: Luôn normalize Unicode, xử lý diacritics đúng chuẩn
13. **Chunk Size**: Default 512 tokens, overlap 50 tokens cho document splitting
14. **Ground Truth**: Cần ít nhất 100 query-document pairs để đánh giá

### **PERFORMANCE & OPTIMIZATION**
15. **GPU Memory**: Batch size phù hợp với VRAM (thường 8-16 cho consumer GPU)
16. **Response Time**: Text processing <100ms, embedding <500ms, RAG query <3s
17. **Caching**: Cache embeddings và frequent queries để tối ưu speed
18. **Vector Index**: Dùng FAISS IndexFlatIP cho accuracy, IndexIVFFlat cho scale

### **SECURITY & ACCESS**
19. **Role-based Access**: 4 levels: Guest < Employee < Manager < Director
20. **Document Security**: Luôn check user permission trước khi return results
21. **API Security**: JWT authentication, rate limiting, input sanitization

### **QUALITY & TESTING**
22. **Evaluation Metrics**: Hit Rate@5 ≥ 85%, MRR ≥ 0.75 để model pass
23. **Vietnamese Test Cases**: Bắt buộc test với diacritics, abbreviations, technical terms
24. **Unit Tests**: Coverage ≥ 80% cho core modules
25. **Integration Tests**: Test end-to-end workflow trước deploy production

### **PROJECT MANAGEMENT**
26. **Phase Order**: Phase 1 (Models) → Phase 2 (Data) → Phase 3 (Core) → Phase 4 (UI)
27. **Checkpoints**: Mỗi phase phải pass checkpoint trước khi chuyển phase tiếp theo
28. **Documentation**: Luôn update README, API docs, deployment guide song song với code
29. **Version Control**: GitFlow workflow, feature branches, code review mandatory
30. **Monitoring**: Log performance metrics, error rates, user feedback từ ngày đầu


Bạn có muốn tôi detail hóa thêm rule nào hoặc thêm rules cho aspect cụ thể nào không?
