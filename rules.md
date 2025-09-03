Always check and follow these rules before starting anything. Always ask me if you feel that any of my requirements conflict with the rules.
Current Checklist:
#### **Task 2: Design Database Schema**
- [ ] **Design `documents_metadata` table** with required fields
- [ ] **Create `departments`, `document_tags`, `access_permissions` tables**
- [ ] **Design indexes for performance**
- [ ] **Create migration scripts**
- [ ] **Setup PostgreSQL database**
**Language Priority**: **Vietnamese** is the number 1 priority processing language
When **writing documents**, always try to use **Vietnamese**, with specialized terms not abbreviated, for example AI.
### **EMBEDDING & AI MODELS**
1. **Embedding Models**: Always use `Qwen/Qwen3-Embedding-0.6B`
2. **Embedding Library**: Required to use `sentence-transformers` for best performance
3. **GPU Support**: Always install `torch` with GPU support because the machine has GPU


### **PYTHON & DEPENDENCIES**
5. **Python Version**: Required Python 3.10.11 to install `underthesea`, `pyvi`
6. **Vietnamese Processing**: Always use `pyvi>=0.1.1` and `underthesea` for processing Vietnamese language
7. **Requirements**: According to the defined requirements.txt file (sentence-transformers>=2.2.2, torch>=2.0.0)

### **FRONTEND & DEPLOYMENT**
8. **NextJS Version**: If using NextJS, version 18.x is required for easy dependency installation
9. **Containerization**: Always deploy in Docker when testing/developing
10. **Database**: PostgreSQL as relational DB, Chroma/FAISS as Vector DB

### **DATA & PROCESSING**
11. **Language Priority**: Vietnamese is the number 1 priority processing language
12. **Text Processing**: Always normalize Unicode, process diacritics correctly
13. **Chunk Size**: Default 512 tokens, overlap 50 tokens for document splitting
14. **Ground Truth**: Requires at least 100 query-document pairs to evaluate price

### **PERFORMANCE & OPTIMIZATION**
15. **GPU Memory**: Batch size suitable for VRAM (usually 8-16 for consumer GPU)
16. **Response Time**: Text processing <100ms, embedding <500ms, RAG query <3s
17. **Caching**: Cache embeddings and frequent queries to optimize speed
18. **Vector Index**: Use FAISS IndexFlatIP for accuracy, IndexIVFFlat for scale

### **SECURITY & ACCESS**
19. **Role-based Access**: 4 levels: Guest < Employee < Manager < Director
20. **Document Security**: Always check user permission before returning results
21. **API Security**: JWT authentication, rate limiting, input sanitization

### **QUALITY & TESTING**
22. **Evaluation Metrics**: Hit Rate@5 ≥ 85%, MRR ≥ 0.75 for model pass
23. **Vietnamese Test Cases**: Required to test with diacritics, abbreviations, technical terms
24. **Unit Tests**: Coverage ≥ 80% for core modules
25. **Integration Tests**: Test end-to-end workflow before deploying to production

### **PROJECT MANAGEMENT**
26. **Phase Order**: Phase 1 (Models) → Phase 2 (Data) → Phase 3 (Core) → Phase 4 (UI)
27. **Checkpoints**: Each phase must pass checkpoint before moving to the next phase
28. **Documentation**: Always update README, API docs, deployment guide in parallel with the code
29. **Version Control**: GitFlow workflow, feature branches, code review mandatory
30. **Monitoring**: Log performance metrics, error rates, user feedback from day one
31. **Resources **: always have a mermaidchart to illustrate when writing documents and instructions.
