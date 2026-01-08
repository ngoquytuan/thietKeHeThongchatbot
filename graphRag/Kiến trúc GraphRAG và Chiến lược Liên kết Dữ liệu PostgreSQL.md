Việc triển khai GraphRAG trên PostgreSQL là một hướng đi tối ưu vì bạn có thể tận dụng sức mạnh của Recursive CTE và tính nhất quán của dữ liệu mà không cần thêm hạ tầng phức tạp như Neo4j. Để giải quyết khó khăn trong việc tạo linking (liên kết), trước hết bạn cần hiểu rõ cấu trúc các bảng chuyên dụng cho đồ thị.
Dưới đây là chi tiết về 6 bảng mà bạn đang quan tâm và vai trò của chúng trong hệ thống:
1. Giải thích các bảng trong Schema Graph
Hệ thống này được thiết kế theo nguyên tắc cô lập kiến trúc (Architectural Isolation), tức là các bảng đồ thị hoạt động độc lập để không làm ảnh hưởng đến hiệu năng của hệ thống tìm kiếm chính.
• graph_documents: Là bản sao (mirror) của bảng tài liệu chính nhưng được bổ sung các thông tin về phân cấp (hierarchy level) từ L0 đến L5. Nó giúp hệ thống biết tài liệu nào là văn bản nền tảng (L0 - ví dụ: Luật, Điều lệ) và tài liệu nào là quyết định cụ thể (L3-L5).
• graph_edges: Đây là bảng quan trọng nhất, lưu trữ các mối quan hệ (cạnh) giữa các tài liệu. Nó chứa thông tin về điểm đầu (source), điểm cuối (target) và loại quan hệ như BASED_ON (căn cứ theo), IMPLEMENTS (thực hiện), hay SUPERSEDES (thay thế).
• graph_validation_rules: Chứa các quy tắc định nghĩa tính hợp lệ của đồ thị. Ví dụ: quy tắc "không được có vòng lặp" (No Cycles) hoặc "văn bản cấp thấp phải tham chiếu đến văn bản cấp cao hơn".
• graph_validation_log: Là nơi ghi lại các vi phạm (violations) khi dữ liệu không thỏa mãn các quy tắc trong bảng graph_validation_rules. Ví dụ: nếu một văn bản cấp 5 không có tham chiếu đến cấp 0, hệ thống sẽ log lại để bạn kiểm tra.
• graph_changelog: Lưu trữ nhật ký thay đổi (audit trail). Bất kỳ hành động thêm, sửa, xóa nào trên đồ thị đều được ghi lại để biết ai đã thực hiện, vào lúc nào, giúp bảo vệ tính toàn vẹn của dữ liệu.
• graph_templates: Chứa các mẫu cấu trúc đồ thị chuẩn. Ví dụ: một "Standard Project Hierarchy" (Phân cấp dự án chuẩn) giúp hệ thống tự động gợi ý cấu trúc khi bạn import tài liệu mới của một dự án tương tự.
--------------------------------------------------------------------------------
2. Gợi ý để tạo Linking giữa các tài liệu hiệu quả
Nếu bạn đang gặp khó khăn khi nối dây giữa các tài liệu, đặc biệt khi metadata hiện tại có thể bị thiếu (thường chỉ khoảng 5% tài liệu có metadata đầy đủ), bạn có thể áp dụng 3 chiến lược sau:
Chiến lược 1: Hard Linking (Độ tin cậy 90-100%)
Dựa trên các mã định danh có độ chính xác tuyệt đối để tự động tạo liên kết:
• Mã nhiệm vụ/Dự án (Task/Project Code): Nếu hai tài liệu cùng chứa mã ĐTCT.2024.05, chúng chắc chắn có liên quan.
• Số hiệu văn bản (Law ID): Sử dụng Regex để bóc tách số hiệu (ví dụ: 265/2025/NĐ-CP) từ nội dung.
• Trường "Căn cứ": Đây là "mỏ vàng" để trích xuất quan hệ BASED_ON. Bạn có thể dùng citation_service.py để bóc tách các tham chiếu này.
Chiến lược 2: Semantic & Inferred Linking (Độ tin cậy 40-80%)
Khi không có mã định danh khớp hoàn toàn, hãy dùng trọng số để gợi ý liên kết:
• Overlap từ khóa: Nếu hai tài liệu có chung >70% từ khóa chuyên môn, hãy gắn nhãn is_suggested để con người duyệt.
• Thứ tự thời gian: Một văn bản "Báo cáo" thường sẽ là con của một văn bản "Quyết định" nếu chúng cùng phòng ban và báo cáo ra đời sau.
Chiến lược 3: Quy trình 2 bước để tối ưu hiệu năng
Thay vì tạo liên kết trực tiếp, hãy làm theo quy trình:
1. Bước 1: Cập nhật thông tin quan hệ vào cột JSONB metadata của tài liệu. Điều này giúp dữ liệu linh hoạt và dễ chỉnh sửa.
2. Bước 2: Chạy script Extract để đẩy các quan hệ từ JSONB vào bảng graph_edges. Bảng này sẽ giúp các truy vấn tìm kiếm đồ thị (như tìm cây phả hệ văn bản) chạy nhanh hơn gấp nhiều lần so với việc quét JSON.
Lời khuyên: Bạn nên bắt đầu bằng việc chạy một script kiểm tra (Enrichment) để tự động phân cấp tài liệu dựa trên tiêu đề và nội dung, sau đó mới tiến hành tạo các liên kết tự động.
Sơ đồ tư duy về Linking: Hãy tưởng tượng graph_documents là các nút thắt, và graph_edges chính là những sợi dây nối chúng lại. Việc tạo linking giống như việc bạn tìm các đầu dây tương ứng thông qua các "nhãn" (Task code, Law ID) để dệt thành một tấm lưới kiến thức bền chặt..
