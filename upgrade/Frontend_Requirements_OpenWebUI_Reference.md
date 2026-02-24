# YÊU CẦU XÂY DỰNG GIAO DIỆN CHATBOT - OPEN WEBUI REFERENCE

## THÔNG TIN TÀI LIỆU

**Dự án**: Hệ thống Hỗ trợ Tư vấn Tài liệu Pháp lý  
**Module**: Frontend - Giao diện Chat  
**Phiên bản**: 2.0 (Open WebUI Referenced)  
**Ngày**: 15/01/2026  
**Đối tượng**: Đội Phát triển Frontend (Outsource)

---

## 1. TỔNG QUAN

### 1.1 Mục tiêu
Xây dựng giao diện chat thông minh cho hệ thống tư vấn tài liệu pháp lý với:
- ✅ **UI/UX Reference**: Open WebUI (https://github.com/open-webui/open-webui)
- ✅ **Build from scratch**: Không fork, tự xây dựng hoàn toàn mới
- ✅ **Tính năng tùy chỉnh**: Citations display, Vietnamese optimization, Export enhancements

### 1.2 Phạm vi công việc

**Đội Outsource sẽ:**
1. Build giao diện chat với thiết kế tham khảo Open WebUI
2. Implement streaming response với progress indicators
3. Tích hợp API backend (do đội nội bộ cung cấp)
4. Tùy chỉnh cho tiếng Việt và tài liệu pháp lý
5. Bàn giao source code + documentation

**Không thuộc phạm vi:**
- ❌ Backend API development
- ❌ Database design
- ❌ AI/ML models
- ❌ Server deployment

---

## 2. UI/UX DESIGN REFERENCE

### 2.1 Tham khảo chính: Open WebUI

**Link:** https://github.com/open-webui/open-webui  
**Demo:** https://docs.openwebui.com

**Yêu cầu:** Giao diện cần giống Open WebUI về:

#### Layout & Structure
```
┌─────────────────────────────────────────────────────────┐
│  Header: [Logo] [Model] [Settings] [User]              │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│ Sidebar  │           Chat Area                         │
│          │                                              │
│ [+ New]  │  User: Question here                        │
│          │                                              │
│ History: │  AI: [Streaming response with typing...]   │
│ • Chat 1 │      [Content appears gradually]            │
│ • Chat 2 │                                              │
│ • Chat 3 │  📚 Citations (CUSTOM - see section 3)      │
│          │                                              │
│          │  👍 👎 📋 Copy  📥 Export                   │
├──────────┴──────────────────────────────────────────────┤
│  💬 [Type your message here...]          [Send ➤]      │
└─────────────────────────────────────────────────────────┘
```

#### UI Components giống Open WebUI
- **Chat bubbles**: User (right, blue), AI (left, gray)
- **Sidebar**: Collapsible, chat history with search
- **Input box**: Multi-line với auto-resize
- **Buttons**: Copy, Export, Like/Dislike
- **Animations**: Smooth transitions, fade-in effects
- **Dark/Light mode**: Toggle theme

**LƯU Ý:** Đội outsource tự implement code, KHÔNG copy code từ Open WebUI. Chỉ tham khảo giao diện.

### 2.2 Branding Customization

| Element | Open WebUI | Customization cho Dự án |
|---------|------------|-------------------------|
| Logo | Open WebUI logo | Logo công ty (sẽ cung cấp) |
| Primary Color | Purple/Blue | **#0066CC** (Blue) |
| Secondary Color | Gray | **#FF6B00** (Orange) |
| Font | Inter | **Inter** (giữ nguyên OK) |
| Language | English default | **Tiếng Việt** default |
| App Name | "Open WebUI" | "Trợ lý Tài liệu Pháp lý" |

### 2.3 Screenshots Reference

**Đội outsource vui lòng:**
1. Cài đặt Open WebUI local để xem demo
2. Screenshot các màn hình chính để confirm với team nội bộ
3. Implement UI tương tự với branding đã customize

---

## 3. TÍNH NĂNG CẦN IMPLEMENT

### 3.1 Core Features (Giống Open WebUI)

#### 3.1.1 Chat Interface ✅
- User gửi tin nhắn
- AI trả lời với streaming response (văn bản hiện từng phần)
- Hiển thị typing indicator khi đang xử lý
- Copy response, regenerate response

**API Integration:**
```typescript
// POST /api/v1/chat/stream
interface ChatRequest {
  query: string;
  session_id: string;
  language: 'vi' | 'en';
}

// Server-Sent Events Response
event: message
data: {"chunk": "Theo ", "isComplete": false}

event: message
data: {"chunk": "Quyết định 635...", "isComplete": false}

event: complete
data: {"messageId": "msg-123"}
```

#### 3.1.2 Chat History ✅
- Sidebar hiển thị danh sách conversations
- Group by date: Hôm nay, Tuần này, Tháng này
- Search conversations
- Delete conversation
- Rename conversation

**API Integration:**
```typescript
// GET /api/v1/chat/history
interface ChatHistory {
  id: string;
  title: string;
  last_message: string;
  timestamp: string;
  message_count: number;
}
```

#### 3.1.3 Multi-language Support ✅
- Language switcher (flag icon)
- Default: Tiếng Việt
- Support: Vietnamese, English
- Persist user preference

#### 3.1.4 Responsive Design ✅
- Desktop: Full layout với sidebar
- Tablet: Collapsible sidebar
- Mobile: Drawer sidebar, full-width chat

---

### 3.2 Custom Features (KHÁC Open WebUI - Cần spec kỹ)

#### 3.2.1 Citations Display (NEW FEATURE) 🆕

**Mục đích:** Hiển thị nguồn tài liệu pháp lý kèm câu trả lời

**UI Design:**
```
┌─────────────────────────────────────────────────────┐
│ AI Response:                                        │
│ Theo Quyết định 635/QĐ-ATTECH về chế độ lương,    │
│ mức lương cơ bản được áp dụng theo Bảng lương...   │
├─────────────────────────────────────────────────────┤
│ 📚 Nguồn tham khảo (3):                            │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ 📄 Quyết định 635/QĐ-ATTECH        [Xem] ↗ │   │
│ │ Trang 5 • Độ liên quan: ████████░░ 95%     │   │
│ │ "Điều 3. Chế độ lương cơ bản áp dụng..."   │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ 📄 Thông tư 120/TT-BTC             [Xem] ↗ │   │
│ │ Trang 12 • Độ liên quan: ███████░░░ 87%    │   │
│ │ "Phụ cấp trách nhiệm được tính theo..."    │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ 📄 Công văn 045/CV-ATTECH          [Xem] ↗ │   │
│ │ Trang 3 • Độ liên quan: ██████░░░░ 78%     │   │
│ │ "Về việc điều chỉnh mức lương năm 2026..." │   │
│ └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**Data Structure:**
```typescript
interface Citation {
  document_id: string;
  document_title: string;
  page: number;
  excerpt: string;              // Đoạn trích dẫn
  relevance_score: number;       // 0.0 - 1.0
  download_url?: string;         // Link tải tài liệu
}

interface AIMessageWithCitations {
  message_id: string;
  text: string;
  citations: Citation[];
  timestamp: string;
}
```

**API Response:**
```json
{
  "message_id": "msg-456",
  "text": "Theo Quyết định 635/QĐ-ATTECH...",
  "citations": [
    {
      "document_id": "QD635_2024",
      "document_title": "Quyết định 635/QĐ-ATTECH",
      "page": 5,
      "excerpt": "Điều 3. Chế độ lương cơ bản áp dụng theo Bảng lương Nhà nước...",
      "relevance_score": 0.95,
      "download_url": "https://api.example.com/documents/QD635_2024.pdf"
    },
    {
      "document_id": "TT120_2023",
      "document_title": "Thông tư 120/TT-BTC",
      "page": 12,
      "excerpt": "Phụ cấp trách nhiệm được tính theo vị trí công việc...",
      "relevance_score": 0.87
    }
  ]
}
```

**Yêu cầu Implementation:**
- Component: `<CitationPanel citations={citations} />`
- Hiển thị dưới mỗi AI response
- Click vào citation → Open document viewer (modal hoặc new tab)
- Responsive: Stack vertically trên mobile
- Loading state khi citations đang được fetch
- Empty state: "Không tìm thấy tài liệu tham khảo"

#### 3.2.2 Progress Indicators (ENHANCEMENT) 🔄

**Mục đích:** Cho người dùng biết hệ thống đang xử lý gì (tránh cảm giác "lag")

**UI Design:**
```
┌─────────────────────────────────────────┐
│ 🔍 Đang tìm kiếm tài liệu...            │
│ ████████░░░░░░░░░░░░░░░░░░░ 30%        │
└─────────────────────────────────────────┘

[2 giây sau...]

┌─────────────────────────────────────────┐
│ 🧠 Đang phân tích nội dung...           │
│ ████████████████░░░░░░░░░░░ 60%        │
└─────────────────────────────────────────┘

[2 giây sau...]

┌─────────────────────────────────────────┐
│ ✍️ Đang tổng hợp câu trả lời...        │
│ ████████████████████████░░░ 90%        │
└─────────────────────────────────────────┘
```

**3 Giai đoạn:**
```typescript
type ProgressStage = 'searching' | 'analyzing' | 'synthesizing' | 'complete';

interface ProgressUpdate {
  stage: ProgressStage;
  percentage: number;        // 0-100
  message: string;
}

// Ví dụ progress events từ API
event: progress
data: {"stage": "searching", "percentage": 20, "message": "Đang tìm kiếm tài liệu..."}

event: progress
data: {"stage": "analyzing", "percentage": 60, "message": "Đang phân tích nội dung..."}

event: progress
data: {"stage": "synthesizing", "percentage": 90, "message": "Đang tổng hợp câu trả lời..."}
```

**Yêu cầu Implementation:**
- Component: `<ProgressIndicator stage={stage} percentage={percentage} />`
- Hiển thị trước khi streaming response bắt đầu
- Animation: Progress bar fill smooth (duration: 0.5s)
- Icon rotation khi đang xử lý
- Tự động ẩn khi streaming bắt đầu

#### 3.2.3 Export with Citations (ENHANCEMENT) 📥

**Mục đích:** Export conversation kèm nguồn tài liệu (khác Open WebUI chỉ export markdown)

**Formats hỗ trợ:**
- **PDF**: Formatted report với header công ty + citations
- **JSON**: Raw data cho integration
- **TXT**: Plain text cho đọc nhanh
- **DOCX**: Word document (optional, ưu tiên thấp)

**Export PDF Layout:**
```
┌─────────────────────────────────────────┐
│ [Logo Công ty]                          │
│ HỆ THỐNG TƯ VẤN TÀI LIỆU PHÁP LÝ       │
│ Báo cáo Hội thoại                       │
│ Ngày: 15/01/2026 10:30                  │
├─────────────────────────────────────────┤
│                                         │
│ NGƯỜI DÙNG:                             │
│ Quyết định 635 quy định gì về lương?   │
│                                         │
│ TRỢ LÝ AI:                              │
│ Theo Quyết định 635/QĐ-ATTECH...       │
│                                         │
│ NGUỒN THAM KHẢO:                        │
│ 1. Quyết định 635/QĐ-ATTECH - Trang 5  │
│    "Điều 3. Chế độ lương..."           │
│                                         │
│ 2. Thông tư 120/TT-BTC - Trang 12      │
│    "Phụ cấp trách nhiệm..."            │
├─────────────────────────────────────────┤
│ [Footer: Tên công ty - Hotline]        │
└─────────────────────────────────────────┘
```

**API Integration:**
```typescript
// POST /api/v1/chat/export
interface ExportRequest {
  session_id: string;
  format: 'pdf' | 'json' | 'txt' | 'docx';
  include_citations: boolean;
  include_metadata: boolean;
}

interface ExportResponse {
  download_url: string;      // Pre-signed URL
  file_size: number;         // Bytes
  expires_at: string;        // ISO timestamp
}
```

**Yêu cầu Implementation:**
- Dropdown menu: [📥 Tải xuống ▼] → PDF / JSON / TXT
- Loading state khi đang generate file
- Download automatically sau khi generate xong
- Error handling: "Không thể tạo file, vui lòng thử lại"

#### 3.2.4 Vietnamese Optimization 🇻🇳

**Mục đích:** Tối ưu trải nghiệm cho người dùng Việt Nam

**Yêu cầu:**

1. **Default Language: Tiếng Việt**
   - UI labels, buttons, placeholders đều là tiếng Việt
   - Language switcher có thể chuyển sang English

2. **Date/Time Format:**
   ```
   Open WebUI:    "Jan 15, 2026 10:30 AM"
   Customized:    "15/01/2026 10:30 Sáng"
                  "Hôm nay 10:30"
                  "Hôm qua 14:20"
   ```

3. **Input Placeholder:**
   ```
   Open WebUI:    "Send a message..."
   Customized:    "💬 Nhập câu hỏi về văn bản pháp lý..."
   ```

4. **Empty States:**
   ```
   Open WebUI:    "No conversations yet"
   Customized:    "Chưa có hội thoại nào. Bắt đầu bằng cách hỏi một câu hỏi!"
   ```

5. **Error Messages:**
   ```
   Open WebUI:    "Network error"
   Customized:    "❌ Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng."
   ```

**Translation File:**
```typescript
// i18n/vi.ts
export const vi = {
  chat: {
    input_placeholder: "Nhập câu hỏi về văn bản pháp lý...",
    send_button: "Gửi",
    new_chat: "Hội thoại mới",
    search_placeholder: "Tìm kiếm hội thoại...",
  },
  citations: {
    title: "Nguồn tham khảo",
    relevance: "Độ liên quan",
    view_document: "Xem tài liệu",
    page: "Trang",
  },
  export: {
    button: "Tải xuống",
    pdf: "PDF",
    json: "JSON", 
    txt: "Text",
    generating: "Đang tạo file...",
  },
  errors: {
    network: "Không thể kết nối đến server",
    timeout: "Yêu cầu quá lâu, vui lòng thử lại",
    server: "Lỗi server, vui lòng thử lại sau",
  }
};
```

---

## 4. TECH STACK

### 4.1 Recommend Tech Stack (Có thể dùng giống Open WebUI)

Open WebUI sử dụng:
- **Frontend**: Svelte + SvelteKit
- **Styling**: Tailwind CSS
- **Icons**: Lucide Icons
- **Deployment**: Docker

**Đội outsource có thể:**
- ✅ **Option A**: Dùng stack giống Open WebUI (Svelte + SvelteKit + Tailwind)
- ✅ **Option B**: Dùng React/Next.js + TypeScript + Tailwind (nếu team quen hơn)

**Yêu cầu bắt buộc:**
- TypeScript (type safety)
- Tailwind CSS (styling như Open WebUI)
- SSE (Server-Sent Events) cho streaming
- Responsive framework
- i18n library (multi-language)

### 4.2 Dependencies

**Core:**
```json
{
  "dependencies": {
    "svelte": "^4.0.0" (hoặc "react": "^18.2.0"),
    "tailwindcss": "^3.3.0",
    "typescript": "^5.0.0",
    "axios": "^1.6.0"
  }
}
```

**Utilities:**
```json
{
  "dependencies": {
    "date-fns": "^2.30.0",          // Date formatting
    "i18next": "^23.0.0",           // Internationalization
    "jspdf": "^2.5.1",              // PDF generation
    "framer-motion": "^10.16.0"     // Animations (optional)
  }
}
```

### 4.3 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx/svelte
│   │   │   ├── MessageBubble.tsx/svelte
│   │   │   ├── StreamingMessage.tsx/svelte
│   │   │   ├── ProgressIndicator.tsx/svelte
│   │   │   └── CitationPanel.tsx/svelte     ← NEW
│   │   ├── sidebar/
│   │   │   ├── Sidebar.tsx/svelte
│   │   │   └── ChatHistory.tsx/svelte
│   │   └── ui/
│   │       ├── Button.tsx/svelte
│   │       ├── Input.tsx/svelte
│   │       └── Modal.tsx/svelte
│   ├── services/
│   │   ├── api.ts                           ← API calls
│   │   ├── streaming.ts                     ← SSE handling
│   │   └── export.ts                        ← Export logic
│   ├── i18n/
│   │   ├── vi.ts                            ← Vietnamese
│   │   └── en.ts                            ← English
│   ├── utils/
│   │   ├── dateFormat.ts
│   │   └── textUtils.ts
│   └── types/
│       ├── chat.types.ts
│       └── citation.types.ts
├── public/
│   └── logo.svg                             ← Company logo
├── package.json
├── tsconfig.json
└── tailwind.config.js
```

---

## 5. API INTEGRATION SPECS

### 5.1 Base URL

```
Development:  http://localhost:8000/api/v1
Production:   https://api.example.com/api/v1  (sẽ cung cấp sau)
```

### 5.2 Authentication

```typescript
// Headers required for all requests
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

**Note:** Token sẽ được lấy từ login flow (do đội nội bộ cung cấp mock)

### 5.3 Core Endpoints

#### 5.3.1 Chat Streaming

```typescript
// POST /api/v1/chat/stream
// Content-Type: application/json

Request:
{
  "query": "Quyết định 635 quy định gì về lương?",
  "session_id": "uuid-xxx",
  "language": "vi"
}

Response: Server-Sent Events (SSE)
----------------------------------
// Event 1: Progress update
event: progress
data: {"stage": "searching", "percentage": 20, "message": "Đang tìm kiếm tài liệu..."}

// Event 2: Progress update
event: progress
data: {"stage": "analyzing", "percentage": 60, "message": "Đang phân tích nội dung..."}

// Event 3: Start streaming message
event: message
data: {"chunk": "Theo ", "isComplete": false}

// Event 4: Continue streaming
event: message
data: {"chunk": "Quyết định 635/QĐ-ATTECH ", "isComplete": false}

// Event N: Last chunk
event: message
data: {"chunk": "...điều khoản cuối.", "isComplete": true}

// Final Event: Citations
event: citations
data: [
  {
    "document_id": "QD635_2024",
    "document_title": "Quyết định 635/QĐ-ATTECH",
    "page": 5,
    "excerpt": "Điều 3. Chế độ lương...",
    "relevance_score": 0.95,
    "download_url": "https://..."
  }
]

// Complete Event
event: complete
data: {"message_id": "msg-123", "timestamp": "2026-01-15T10:30:00Z"}
```

#### 5.3.2 Chat History

```typescript
// GET /api/v1/chat/history
Response:
{
  "conversations": [
    {
      "id": "session-1",
      "title": "Quyết định 635 - Lương",
      "last_message": "Cảm ơn!",
      "timestamp": "2026-01-15T10:30:00Z",
      "message_count": 8
    },
    {
      "id": "session-2",
      "title": "Thông tư 120",
      "last_message": "Đã hiểu",
      "timestamp": "2026-01-14T15:20:00Z",
      "message_count": 5
    }
  ]
}
```

#### 5.3.3 Get Conversation Messages

```typescript
// GET /api/v1/chat/conversation/{session_id}
Response:
{
  "session_id": "session-1",
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "Quyết định 635 quy định gì?",
      "timestamp": "2026-01-15T10:00:00Z"
    },
    {
      "id": "msg-2",
      "role": "assistant",
      "content": "Theo Quyết định 635/QĐ-ATTECH...",
      "citations": [...],
      "timestamp": "2026-01-15T10:00:05Z"
    }
  ]
}
```

#### 5.3.4 Export

```typescript
// POST /api/v1/chat/export
Request:
{
  "session_id": "session-1",
  "format": "pdf",
  "include_citations": true,
  "include_metadata": true
}

Response:
{
  "download_url": "https://api.example.com/files/export-123.pdf",
  "file_size": 2048576,
  "expires_at": "2026-01-15T23:59:59Z"
}
```

#### 5.3.5 Feedback

```typescript
// POST /api/v1/chat/feedback
Request:
{
  "message_id": "msg-2",
  "session_id": "session-1",
  "feedback_type": "thumbs_up",  // or "thumbs_down"
  "comment": "Rất hữu ích!"      // Optional
}

Response:
{
  "success": true,
  "feedback_id": "fb-789"
}
```

### 5.4 Error Handling

```typescript
// Error Response Format
{
  "error": {
    "code": "NETWORK_ERROR",
    "message": "Không thể kết nối đến server",
    "details": {...}  // Optional
  }
}

// Error Codes
- NETWORK_ERROR: Lỗi kết nối
- AUTH_ERROR: Lỗi xác thực (token hết hạn)
- VALIDATION_ERROR: Dữ liệu không hợp lệ
- SERVER_ERROR: Lỗi server (500)
- TIMEOUT_ERROR: Timeout
```

---

## 6. MOCK DATA CHO DEVELOPMENT

### 6.1 Mock Server (Tùy chọn)

**Option A:** Đội outsource tự viết mock server đơn giản
**Option B:** Đội nội bộ cung cấp mock server (Docker image)

Nếu chọn Option A, đây là ví dụ simple mock:

```javascript
// mock-server.js (Node.js + Express)
const express = require('express');
const app = express();

app.post('/api/v1/chat/stream', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  
  // Mock progress
  res.write('event: progress\n');
  res.write('data: {"stage":"searching","percentage":20,"message":"Đang tìm kiếm..."}\n\n');
  
  setTimeout(() => {
    res.write('event: progress\n');
    res.write('data: {"stage":"analyzing","percentage":60,"message":"Đang phân tích..."}\n\n');
  }, 1000);
  
  // Mock streaming chunks
  const chunks = ['Theo ', 'Quyết định ', '635/QĐ-ATTECH ', '...'];
  chunks.forEach((chunk, i) => {
    setTimeout(() => {
      res.write('event: message\n');
      res.write(`data: {"chunk":"${chunk}","isComplete":false}\n\n`);
    }, 2000 + i * 500);
  });
  
  // Mock citations
  setTimeout(() => {
    res.write('event: citations\n');
    res.write('data: [{"document_id":"QD635","page":5,...}]\n\n');
    res.write('event: complete\n');
    res.write('data: {"message_id":"msg-123"}\n\n');
    res.end();
  }, 5000);
});

app.listen(8000);
```

### 6.2 Mock Conversations Data

```json
{
  "conversations": [
    {
      "id": "session-1",
      "title": "Quyết định 635 - Chế độ lương",
      "messages": [
        {
          "role": "user",
          "content": "Quyết định 635 quy định gì về chế độ lương?"
        },
        {
          "role": "assistant",
          "content": "Theo Quyết định 635/QĐ-ATTECH ngày 15/01/2024, chế độ lương được quy định như sau:\n\n1. Mức lương cơ bản áp dụng theo Bảng lương Nhà nước\n2. Phụ cấp bao gồm: phụ cấp trách nhiệm, phụ cấp khu vực, phụ cấp độc hại\n3. Thưởng dựa trên hiệu quả công việc",
          "citations": [
            {
              "document_id": "QD635_2024",
              "document_title": "Quyết định 635/QĐ-ATTECH",
              "page": 5,
              "excerpt": "Điều 3. Chế độ lương cơ bản áp dụng theo Bảng lương Nhà nước...",
              "relevance_score": 0.95
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 7. TESTING REQUIREMENTS

### 7.1 Unit Testing
- Test coverage: **≥ 70%** (không cần 80% như ban đầu)
- Focus: Core components (ChatInterface, CitationPanel, ProgressIndicator)

### 7.2 Integration Testing
- User flow: Send message → Receive streaming response → View citations
- Export flow: Click export → Download file

### 7.3 E2E Testing (Optional - Nice to have)
- Full user journey với mock API

### 7.4 Manual Testing Checklist
```
✅ Streaming response hoạt động mượt mà
✅ Progress indicators hiển thị đúng
✅ Citations panel hiển thị đầy đủ
✅ Export PDF thành công
✅ Vietnamese labels hiển thị đúng
✅ Responsive trên mobile/tablet/desktop
✅ Dark/Light mode toggle
✅ Chat history search
✅ Error handling (network error, timeout)
```

---

## 8. DELIVERABLES & TIMELINE

### 8.1 Deliverables

**1. Source Code:**
- Git repository (GitHub/GitLab)
- Clean code với comments
- README.md với hướng dẫn setup

**2. Documentation:**
- Component documentation
- API integration guide
- Deployment guide (Docker)

**3. Build Artifacts:**
- Production build
- Docker image (optional)

**4. Demo:**
- Live demo với mock API
- Screenshot các features chính

### 8.2 Timeline

| Week | Tasks | Deliverables |
|------|-------|--------------|
| **Week 1** | Setup + Core UI | Chat interface, Sidebar, Responsive layout |
| **Week 2** | Streaming + Progress | SSE integration, Progress indicators, Citations panel |
| **Week 3** | Export + Vietnamese | Export PDF/JSON, i18n Vietnamese, Testing |
| **Week 4** | Testing + Polish | Bug fixes, Documentation, Final delivery |

**Total:** 4 tuần (thay vì 3 tuần - để có thời gian polish hơn)

### 8.3 Milestones

**Milestone 1 (End of Week 1):**
- ✅ UI giống Open WebUI
- ✅ Chat bubbles, sidebar working
- ✅ Responsive layout

**Milestone 2 (End of Week 2):**
- ✅ Streaming response hoạt động
- ✅ Progress indicators
- ✅ Citations panel

**Milestone 3 (End of Week 3):**
- ✅ Export PDF/JSON
- ✅ Vietnamese UI
- ✅ All features integrated

**Milestone 4 (End of Week 4):**
- ✅ Testing complete
- ✅ Documentation ready
- ✅ Ready for production

---

## 9. ACCEPTANCE CRITERIA

### 9.1 Functional Requirements

**Core Features:**
- [x] User có thể gửi/nhận tin nhắn
- [x] Streaming response hiển thị từng phần
- [x] Chat history lưu và hiển thị đúng
- [x] Language switcher (VI/EN)
- [x] Dark/Light mode toggle
- [x] Responsive trên mobile/tablet/desktop

**Custom Features:**
- [x] Citations panel hiển thị nguồn tài liệu
- [x] Progress indicators (3 stages)
- [x] Export PDF kèm citations
- [x] Vietnamese UI/UX đầy đủ

### 9.2 Performance Requirements

| Metric | Target |
|--------|--------|
| Initial load | < 3 seconds |
| Message send | < 100ms |
| Streaming start | < 500ms |
| Bundle size | < 800KB gzipped |

### 9.3 Quality Requirements

- [x] Code tuân thủ ESLint rules
- [x] TypeScript không có errors
- [x] Test coverage ≥ 70%
- [x] UI giống Open WebUI ≥ 90%
- [x] Works on Chrome, Firefox, Safari, Edge

---

## 10. SUPPORT & COMMUNICATION

### 10.1 Communication Channels

**Daily Standup:** 9:00 AM (Zoom/Google Meet)  
**Weekly Review:** Thứ 5 hàng tuần  
**Issue Tracking:** GitHub Issues  
**Chat:** Slack #frontend-project

### 10.2 Point of Contact

**Technical Lead:** [Tên] - [Email] - [Phone]  
**Product Owner:** [Tên] - [Email]  
**Designer:** [Tên] - [Email] (nếu có)

### 10.3 Questions & Clarifications

Nếu có thắc mắc về:
- UI/UX design → Screenshot từ Open WebUI và hỏi confirm
- API specs → Check section 5 hoặc email technical lead
- Timeline → Thảo luận trong weekly review

**Response SLA:**
- Urgent issues: < 4 hours
- Normal questions: < 24 hours

---

## 11. APPENDIX

### 11.1 Open WebUI Resources

**Main Repository:**  
https://github.com/open-webui/open-webui

**Documentation:**  
https://docs.openwebui.com

**Demo (Live):**  
https://chat.openwebui.com

**Video Demo:**  
https://www.youtube.com/watch?v=... (search "Open WebUI demo")

### 11.2 Design Assets (Sẽ cung cấp)

- Company logo (SVG, PNG)
- Color palette details
- Custom fonts (nếu có)
- Brand guidelines

### 11.3 Tech Stack References

**Svelte/SvelteKit:**  
https://svelte.dev  
https://kit.svelte.dev

**React/Next.js (Alternative):**  
https://react.dev  
https://nextjs.org

**Tailwind CSS:**  
https://tailwindcss.com

**Server-Sent Events (SSE):**  
https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events

---

## 12. NOTES FOR OUTSOURCE TEAM

### 12.1 Quan trọng ⚠️

1. **UI Reference = Open WebUI**
   - KHÔNG copy code từ Open WebUI
   - CHỈ tham khảo giao diện
   - Tự implement từ đầu với tech stack của team

2. **Focus on Custom Features**
   - Citations Panel (quan trọng nhất!)
   - Progress Indicators (UX improvement)
   - Export with Citations
   - Vietnamese Optimization

3. **API Backend = Black Box**
   - Không cần biết backend dùng công nghệ gì
   - Chỉ cần integrate đúng API specs
   - Mock API để development/testing

### 12.2 Tips

✅ **DO:**
- Screenshot Open WebUI để confirm design với team
- Hỏi khi không chắc chắn
- Test thường xuyên với mock API
- Commit code nhỏ, thường xuyên
- Document code rõ ràng

❌ **DON'T:**
- Copy code từ Open WebUI (license issues)
- Thay đổi API contract tự ý
- Bỏ qua testing
- Hardcode credentials/tokens
- Skip documentation

---

## VERSION HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 15/01/2026 | Technical Lead | Initial version - 50 pages detailed |
| **2.0** | **15/01/2026** | **Technical Lead** | **Simplified - Open WebUI reference** |

---

**END OF DOCUMENT**

---

## 📌 SUMMARY - Điểm khác biệt so với Version 1.0

| Aspect | Version 1.0 (50 pages) | Version 2.0 (This doc) |
|--------|------------------------|------------------------|
| **Design Specs** | 30 trang wireframes, colors, fonts chi tiết | "Giống Open WebUI" (5 dòng) |
| **Code Examples** | Chi tiết từng component | Chỉ custom features |
| **Timeline** | 3 tuần | 4 tuần (realistic) |
| **Tech Stack** | React specified | Flexible (Svelte or React) |
| **Focus** | Everything from scratch | Custom features only |
| **Pages** | 50 pages | ~20 pages |
| **Clarity** | High detail, may overwhelm | Clear direction, easier to start |

**Kết luận:** Version 2.0 đơn giản hơn, rõ ràng hơn, ít overwhelm hơn cho outsource team! ✅
