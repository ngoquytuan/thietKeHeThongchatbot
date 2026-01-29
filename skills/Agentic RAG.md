Bạn đã nắm bắt rất đúng vấn đề then chốt về chi phí và cơ chế vận hành của LLM. Câu trả lời ngắn gọn là: **Đúng, nhưng có cách để tối ưu.**

Dưới đây là phân tích chi tiết về việc tiêu tốn token và luồng xử lý của hệ thống:

### 1. Về lượng Token tiêu tốn

Mỗi khi bạn gửi một yêu cầu lên API (OpenAI, Anthropic, hoặc Local LLM), toàn bộ nội dung trong **System Prompt** (nơi chứa `skill.md`) sẽ được gửi đi kèm với câu hỏi của người dùng.

* **Công thức tính token đầu vào (Input):**


* **Hệ quả:** Nếu file `skill.md` của bạn dài 500 tokens, thì mỗi câu hỏi dù ngắn chỉ 10 tokens, bạn vẫn phải trả tiền cho ít nhất 510 tokens đầu vào. Trong hội thoại nhiều lượt (multi-turn), con số này sẽ cộng dồn rất nhanh.

---

### 2. Luồng xử lý: Skill -> Search -> Response

Thực tế, LLM không "đọc rồi đi tìm" theo kiểu con người cầm tờ giấy hướng dẫn đi vào kho. Nó hoạt động theo một trong hai mô hình sau tùy cách bạn code:

#### Mô hình 1: RAG truyền thống (Linh hoạt hơn nhưng tốn token)

1. **Bước 1:** Hệ thống lấy `User Query` đi tìm kiếm trong Vector DB (không dùng LLM ở bước này để tiết kiệm).
2. **Bước 2:** Đóng gói tất cả: `Skill` + `Kết quả tìm được` + `User Query` gửi cho LLM.
3. **Bước 3:** LLM đọc toàn bộ "combo" này và đưa ra câu trả lời dựa trên kỹ năng đã dạy.

#### Mô hình 2: Agentic RAG (Thông minh nhất)

1. **Bước 1:** Gửi `Skill` + `User Query` cho LLM.
2. **Bước 2:** LLM đọc skill và hiểu rằng: "À, tôi cần dùng công cụ tìm kiếm pháp lý". Nó sẽ xuất ra một lệnh gọi hàm (Function Calling).
3. **Bước 3:** Code Python của bạn thực hiện tìm kiếm và gửi kết quả ngược lại cho LLM.
4. **Bước 4:** LLM tổng hợp và trả lời.
*Ở mô hình này, LLM thực sự "đọc skill" trước để quyết định cách tìm kiếm.*

---

### 3. Cách tối ưu để không bị "đốt" token

Nếu bạn lo lắng về việc tốn token cho `skill.md`, bạn có thể áp dụng các kỹ thuật sau:

* **Context Caching:** Một số API (như Claude hoặc Gemini) hiện nay đã hỗ trợ "ghi nhớ" phần prompt hệ thống. Bạn chỉ trả tiền đầy đủ cho lần đầu, các lần sau chỉ trả một phần phí rất nhỏ cho phần đã lưu trong cache.
* **Prompt Compression:** Viết `skill.md` theo dạng danh sách (bullet points) cực kỳ ngắn gọn, lược bỏ các từ nối không cần thiết. LLM vẫn hiểu rất tốt các chỉ dẫn dạng từ khóa.
* **Phân tách Skill:** Thay vì nạp một file `skill.md` khổng lồ chứa tất cả kỹ năng, hãy dùng một LLM nhỏ (như GPT-4o-mini hoặc Phi-3) để phân loại xem user đang hỏi về lĩnh vực nào, sau đó mới nạp skill tương ứng.

---

### Tóm lại

Việc tốn thêm token cho `skill.md` là một **khoản đầu tư xứng đáng** để đổi lấy sự chính xác và an toàn của chatbot pháp lý. Nếu không có nó, LLM sẽ trả lời rất mông lung và không tuân thủ đúng định dạng trích dẫn mà bạn cần.

Bạn có muốn tôi giúp bạn tối ưu lại bản thảo `skill.md` ở trên để nó **ngắn gọn nhất có thể (tiết kiệm token)** mà vẫn giữ nguyên sức mạnh không?
