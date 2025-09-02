## UC1: ĐẶT CÂU HỎI ĐƠN GIẢN, CHỈ NHẬN THÔNG TIN CÔNG KHAI

### **📋 Thông tin cơ bản**

- **ID**: UC-001
- **Tên**: Ask Simple Question (Public Content Only)
- **Actor chính**: Guest User
- **Mức độ**: Primary
- **Phạm vi**: Core System

### **🎯 Mục tiêu**

Cho phép khách truy cập đặt câu hỏi và nhận câu trả lời dựa trên tài liệu công khai mà không cần đăng nhập.

### **📝 Mô tả**

Guest có thể tương tác với chatbot để hỏi về thông tin công ty, sản phẩm, dịch vụ, và các thông tin khác được phân loại là "public". Hệ thống sẽ chỉ truy xuất và trả lời dựa trên dữ liệu có mức độ truy cập công khai.

### **🔗 Điều kiện tiên quyết (Preconditions)**

- Hệ thống chatbot đang hoạt động
- Có ít nhất một tài liệu public trong database
- Guest interface có thể truy cập được
- Session tracking được khởi tạo

### **✅ Điều kiện hậu (Postconditions)**

- **Thành công**: Câu trả lời được hiển thị với citations từ tài liệu public
- **Thất bại**: Thông báo lỗi hoặc "không tìm thấy thông tin phù hợp"
- Session được cập nhật với câu hỏi và câu trả lời
- Metrics được ghi nhận (response time, query type)

### **🏃‍♂️ Luồng chính (Main Flow)**

| Bước | Actor | Hành động |
| --- | --- | --- |
| 1   | Guest | Truy cập giao diện chatbot |
| 2   | System | Hiển thị giao diện chat với placeholder "Hãy đặt câu hỏi..." |
| 3   | Guest | Nhập câu hỏi vào text box và nhấn Send hoặc Enter |
| 4   | System | Validate input (không rỗng, độ dài hợp lệ ≤ 1000 ký tự) |
| 5   | System | Hiển thị loading indicator "Đang xử lý..." |
| 6   | System | Gọi RAG Core Engine với query + access_level="public" |
| 7   | System | RAG Engine thực hiện semantic search trong public documents |
| 8   | System | LLM sinh câu trả lời dựa trên retrieved context |
| 9   | System | Validate câu trả lời (không chứa nội dung sensitive) |
| 10  | System | Hiển thị câu trả lời kèm theo references |
| 11  | System | Lưu câu hỏi/trả lời vào session history |
| 12  | Guest | Đọc câu trả lời và có thể đặt câu hỏi tiếp theo |

### **🔄 Luồng thay thế (Alternative Flows)**

**AF1 - Không tìm thấy thông tin phù hợp:**

- Bước 7-8: RAG Engine không tìm thấy documents relevent
- System hiển thị: "Xin lỗi, tôi không tìm thấy thông tin phù hợp về câu hỏi của bạn. Bạn có thể thử đặt câu hỏi khác hoặc liên hệ với nhân viên để được hỗ trợ."
- System suggest một số câu hỏi phổ biến

**AF2 - Lỗi kết nối LLM:**

- Bước 8: LLM API trả về error hoặc timeout
- System hiển thị: "Hệ thống đang bận, vui lòng thử lại sau ít phút."
- System ghi log error để admin xử lý

**AF3 - Query quá dài:**

- Bước 4: Input validation fail (>1000 ký tự)
- System hiển thị: "Câu hỏi quá dài. Vui lòng rút gọn câu hỏi (tối đa 1000 ký tự)."

### **❌ Luồng ngoại lệ (Exception Flows)**

**EF1 - Hệ thống overload:**

- System trả về HTTP 503 Service Unavailable
- Hiển thị: "Hệ thống đang quá tải. Vui lòng thử lại sau 5 phút."

**EF2 - Database không khả dụng:**

- Vector DB hoặc PostgreSQL down
- Hiển thị: "Dịch vụ tạm thời không khả dụng. Vui lòng thử lại sau."

### **🎯 Yêu cầu đặc biệt**

- **Hiệu suất**: Response time ≤ 60 giây
- **Bảo mật**: Chỉ truy cập documents có access_level="public"
- **Usability**: Giao diện intuitive, không cần hướng dẫn
- **Scalability**: Hỗ trợ 50+ concurrent guest users

### **📊 Tiêu chí chấp nhận**

- [ ] Guest có thể đặt câu hỏi mà không cần đăng nhập
- [ ] Chỉ nhận được thông tin từ tài liệu public
- [ ] Response time trung bình < 45 giây
- [ ] UI responsive trên desktop và mobile
- [ ] Error messages rõ ràng và hữu ích
- [ ] Session được maintain trong suốt interaction
---
# HƯỚNG DẪN IMPLEMENTATION UC1 - ĐẶT CÂU HỎI ĐƠN GIẢN (GUEST USER)

Với UC1 đã được định nghĩa rõ ràng, đây là hướng dẫn chi tiết để implement use case này trong hệ thống đã tích hợp:

## 🔧 **1. BACKEND IMPLEMENTATION**

### **Step 1.1: Guest Query Endpoint**

```python
# routers/guest_router.py
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, validator
from typing import Optional
import structlog
from datetime import datetime

router = APIRouter(prefix="/api/v1/guest", tags=["Guest Access"])

class GuestQueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    
    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Câu hỏi không được để trống')
        if len(v) > 1000:
            raise ValueError('Câu hỏi quá dài (tối đa 1000 ký tự)')
        return v.strip()

class GuestQueryResponse(BaseModel):
    answer: str
    references: list
    session_id: str
    response_time: float
    confidence: float
    suggestions: list
    metadata: dict

@router.post("/ask", response_model=GuestQueryResponse)
async def guest_ask_question(
    request: GuestQueryRequest,
    http_request: Request,
    system_state = Depends(get_system_state)
):
    """
    UC1: Guest user asks simple question (public content only)
    
    Implementation của main flow UC1
    """
    
    logger = structlog.get_logger()
    start_time = datetime.now()
    
    try:
        # Step 4: Validate input (đã validate trong Pydantic model)
        
        # Step 5: Show loading (handled by frontend)
        logger.info(
            "guest_query_started",
            query_length=len(request.query),
            session_id=request.session_id,
            client_ip=http_request.client.host
        )
        
        # Step 6-8: Call RAG Core Engine với guest permissions
        guest_user_context = {
            "user_id": "guest",
            "role": "guest",
            "accessible_resources": ["public"],  # Chỉ public content
            "department": None,
            "session_id": request.session_id or generate_guest_session_id()
        }
        
        # Sử dụng RAG engine với permission filtering
        rag_response = await system_state.rag_engine.process_guest_query(
            query=request.query,
            user_context=guest_user_context
        )
        
        # Step 9: Validate response (không chứa nội dung sensitive)
        validated_response = await validate_guest_response(rag_response)
        
        # Step 10-11: Format response và save session
        formatted_response = await format_guest_response(
            rag_response=validated_response,
            query=request.query,
            session_id=guest_user_context["session_id"]
        )
        
        # Calculate response time
        response_time = (datetime.now() - start_time).total_seconds()
        formatted_response["response_time"] = response_time
        
        # Log successful interaction
        logger.info(
            "guest_query_completed",
            session_id=guest_user_context["session_id"],
            response_time=response_time,
            confidence=formatted_response["confidence"],
            references_count=len(formatted_response["references"])
        )
        
        # Update metrics
        await update_guest_metrics(
            query=request.query,
            response_time=response_time,
            success=True,
            confidence=formatted_response["confidence"]
        )
        
        return GuestQueryResponse(**formatted_response)
        
    except ValueError as e:
        # Input validation error (AF3)
        raise HTTPException(status_code=400, detail=str(e))
        
    except ConnectionError as e:
        # LLM connection error (AF2)
        logger.error("llm_connection_error", error=str(e))
        raise HTTPException(
            status_code=503, 
            detail="Hệ thống đang bận, vui lòng thử lại sau ít phút."
        )
        
    except Exception as e:
        # General system error (EF1, EF2)
        logger.error(
            "guest_query_error",
            error=str(e),
            session_id=request.session_id
        )
        
        await update_guest_metrics(
            query=request.query,
            response_time=(datetime.now() - start_time).total_seconds(),
            success=False,
            error=str(e)
        )
        
        raise HTTPException(
            status_code=503,
            detail="Dịch vụ tạm thời không khả dụng. Vui lòng thử lại sau."
        )

async def validate_guest_response(rag_response: dict) -> dict:
    """Step 9: Validate response không chứa sensitive content."""
    
    answer = rag_response.get("answer", "")
    
    # Check for sensitive keywords
    sensitive_keywords = [
        "password", "api_key", "secret", "token", 
        "internal_only", "confidential", "salary", "budget"
    ]
    
    answer_lower = answer.lower()
    
    for keyword in sensitive_keywords:
        if keyword in answer_lower:
            # Replace với generic message
            rag_response["answer"] = (
                "Xin lỗi, tôi không thể cung cấp thông tin này. "
                "Vui lòng liên hệ với nhân viên để được hỗ trợ."
            )
            rag_response["confidence"] = 0
            rag_response["references"] = []
            break
    
    # Validate references are only public
    public_references = []
    for ref in rag_response.get("references", []):
        if ref.get("access_level") == "public":
            public_references.append(ref)
    
    rag_response["references"] = public_references
    
    return rag_response

async def format_guest_response(rag_response: dict, query: str, session_id: str) -> dict:
    """Step 10: Format response for guest user."""
    
    # Handle case when no relevant documents found (AF1)
    if not rag_response.get("answer") or rag_response.get("confidence", 0) < 0.3:
        return {
            "answer": (
                "Xin lỗi, tôi không tìm thấy thông tin phù hợp về câu hỏi của bạn. "
                "Bạn có thể thử đặt câu hỏi khác hoặc liên hệ với nhân viên để được hỗ trợ."
            ),
            "references": [],
            "session_id": session_id,
            "confidence": 0,
            "suggestions": generate_guest_suggestions(),
            "metadata": {
                "query_type": "no_match",
                "access_level": "public"
            }
        }
    
    # Format successful response
    formatted_references = []
    for ref in rag_response.get("references", []):
        formatted_references.append({
            "title": ref.get("title", "Tài liệu"),
            "excerpt": ref.get("excerpt", "")[:150] + "...",
            "source": ref.get("source", ""),
            "confidence": ref.get("confidence", 0)
        })
    
    # Add confidence indicator
    confidence = rag_response.get("confidence", 0)
    answer = rag_response.get("answer", "")
    
    if confidence >= 0.8:
        confidence_text = "\n\n*Tôi khá tự tin về thông tin này.*"
    elif confidence >= 0.6:
        confidence_text = "\n\n*Đây là thông tin tôi tìm được, bạn có thể tham khảo thêm.*"
    else:
        confidence_text = "\n\n*Thông tin này có thể chưa đầy đủ, vui lòng liên hệ trực tiếp để được hỗ trợ chính xác hơn.*"
    
    return {
        "answer": answer + confidence_text,
        "references": formatted_references,
        "session_id": session_id,
        "confidence": confidence,
        "suggestions": generate_contextual_suggestions(query, rag_response),
        "metadata": {
            "query_type": "public_search",
            "access_level": "public",
            "documents_searched": len(rag_response.get("references", []))
        }
    }

def generate_guest_suggestions() -> list:
    """Generate default suggestions for guests."""
    return [
        "Công ty làm về lĩnh vực gì?",
        "Sản phẩm chính của công ty là gì?",
        "Thông tin liên hệ của công ty?",
        "Công ty có các chi nhánh ở đâu?",
        "Chính sách bảo hành sản phẩm?"
    ]

def generate_contextual_suggestions(query: str, rag_response: dict) -> list:
    """Generate contextual suggestions based on query and response."""
    
    # Analyze query content to suggest related questions
    query_lower = query.lower()
    suggestions = []
    
    if "sản phẩm" in query_lower:
        suggestions.extend([
            "Giá cả sản phẩm như thế nào?",
            "Sản phẩm có bảo hành không?",
            "Cách mua sản phẩm?"
        ])
    elif "dịch vụ" in query_lower:
        suggestions.extend([
            "Quy trình sử dụng dịch vụ?",
            "Chi phí dịch vụ?",
            "Thời gian xử lý?"
        ])
    elif "liên hệ" in query_lower:
        suggestions.extend([
            "Giờ làm việc của công ty?",
            "Địa chỉ các chi nhánh?",
            "Email hỗ trợ khách hàng?"
        ])
    else:
        suggestions = generate_guest_suggestions()
    
    return suggestions[:3]  # Limit to 3 suggestions

def generate_guest_session_id() -> str:
    """Generate unique session ID for guest users."""
    import uuid
    return f"guest_{uuid.uuid4().hex[:12]}"

async def update_guest_metrics(query: str, response_time: float, 
                              success: bool, confidence: float = 0, error: str = None):
    """Update metrics for guest queries."""
    # Implementation tùy thuộc vào metrics system được sử dụng
    pass
```

### **Step 1.2: Enhanced RAG Engine for Guest Queries**

```python
# modules/rag_engine/guest_processor.py
import structlog
from typing import Dict, Any, List

class GuestQueryProcessor:
    """Specialized processor for guest queries với public content only."""
    
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
        self.logger = structlog.get_logger()
    
    async def process_guest_query(self, query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process guest query với strict public content filtering.
        
        Implements UC1 steps 6-8
        """
        
        try:
            # Step 6: RAG Core Engine call
            self.logger.info("processing_guest_query", query_length=len(query))
            
            # Step 7: Semantic search trong public documents only
            public_documents = await self.search_public_documents(query)
            
            if not public_documents:
                return {
                    "answer": "",
                    "references": [],
                    "confidence": 0,
                    "query_type": "no_public_content"
                }
            
            # Step 8: LLM generates answer từ public context
            response = await self.generate_public_response(query, public_documents, user_context)
            
            # Additional safety check
            response = await self.ensure_public_only_content(response)
            
            return response
            
        except Exception as e:
            self.logger.error("guest_query_processing_error", error=str(e))
            raise
    
    async def search_public_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search only in public documents."""
        
        # Create embedding for query
        query_embedding = await self.rag_engine.embedding_module.create_embedding(query)
        
        # Search trong public collection only
        search_results = await self.rag_engine.database_module.vector_db.similarity_search(
            collection_name="documents_public",
            query_vector=query_embedding,
            top_k=top_k,
            threshold=0.7  # Higher threshold for public content
        )
        
        # Filter và validate results
        public_documents = []
        for result in search_results:
            metadata = result.get("metadata", {})
            
            # Double-check access level
            if metadata.get("access_level") == "public":
                public_documents.append({
                    "id": metadata.get("document_id"),
                    "title": metadata.get("document_title", ""),
                    "content": result.get("text", ""),
                    "access_level": "public",
                    "confidence": result.get("similarity", 0),
                    "source": metadata.get("source", ""),
                    "excerpt": result.get("text", "")[:200]
                })
        
        return public_documents
    
    async def generate_public_response(self, query: str, documents: List[Dict], 
                                     user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response using only public documents."""
        
        # Build context from public documents
        context_texts = []
        references = []
        
        for doc in documents:
            context_texts.append(f"Tài liệu: {doc['title']}\nNội dung: {doc['content']}")
            references.append({
                "document_id": doc["id"],
                "title": doc["title"],
                "excerpt": doc["excerpt"],
                "confidence": doc["confidence"],
                "access_level": "public",
                "source": doc["source"]
            })
        
        context = "\n\n".join(context_texts)
        
        # Create prompt for public content only
        system_prompt = """
        Bạn là trợ lý AI của công ty, chuyên trả lời câu hỏi cho khách hàng và khách thăm quan.
        
        QUY TẮC QUAN TRỌNG:
        - Chỉ sử dụng thông tin từ tài liệu công khai được cung cấp
        - Không bao giờ tiết lộ thông tin nội bộ, bí mật, hoặc nhạy cảm
        - Nếu không có thông tin phù hợp, hãy thừa nhận và đề xuất liên hệ trực tiếp
        - Giữ câu trả lời thân thiện và chuyên nghiệp
        - Không suy đoán hoặc tạo ra thông tin không có trong tài liệu
        
        Thông tin tài liệu công khai:
        {context}
        """
        
        user_prompt = f"Câu hỏi của khách: {query}"
        
        # Call LLM
        llm_response = await self.rag_engine.llm_client.generate_response(
            system_prompt=system_prompt.format(context=context),
            user_prompt=user_prompt,
            max_tokens=500,
            temperature=0.3  # Lower temperature for more factual responses
        )
        
        # Calculate confidence based on document relevance
        avg_doc_confidence = sum(doc["confidence"] for doc in documents) / len(documents)
        response_confidence = min(avg_doc_confidence * 1.2, 1.0)  # Boost slightly but cap at 1.0
        
        return {
            "answer": llm_response.get("text", ""),
            "references": references,
            "confidence": response_confidence,
            "query_type": "public_search",
            "processing_time": llm_response.get("processing_time", 0)
        }
    
    async def ensure_public_only_content(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Final safety check to ensure only public content."""
        
        # Keywords that might indicate non-public content
        restricted_indicators = [
            "nội bộ", "internal", "confidential", "secret", "password",
            "salary", "wage", "budget", "cost", "profit", "revenue",
            "employee id", "personal", "private", "restricted"
        ]
        
        answer = response.get("answer", "").lower()
        
        # Check if answer contains restricted indicators
        for indicator in restricted_indicators:
            if indicator in answer:
                self.logger.warning(
                    "potential_restricted_content_detected",
                    indicator=indicator,
                    answer_preview=answer[:100]
                )
                
                # Replace with safe response
                response["answer"] = (
                    "Tôi không thể cung cấp thông tin chi tiết về vấn đề này. "
                    "Vui lòng liên hệ trực tiếp với công ty để được hỗ trợ tốt nhất."
                )
                response["confidence"] = 0
                response["references"] = []
                break
        
        return response
```

---

## 🖥️ **2. FRONTEND IMPLEMENTATION**

### **Step 2.1: Guest Chat Interface Component**

```jsx
// components/GuestChatInterface.jsx
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const GuestChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [suggestions, setSuggestions] = useState([]);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        // Step 2: Initialize interface với welcome message
        const welcomeMessage = {
            id: 'welcome',
            type: 'assistant',
            text: 'Xin chào! Tôi là trợ lý AI của công ty. Bạn có thể hỏi tôi về sản phẩm, dịch vụ và thông tin công ty. Hãy đặt câu hỏi nhé!',
            timestamp: new Date(),
            suggestions: [
                'Công ty làm về lĩnh vực gì?',
                'Sản phẩm chính của công ty là gì?',
                'Thông tin liên hệ của công ty?'
            ]
        };
        
        setMessages([welcomeMessage]);
        setSuggestions(welcomeMessage.suggestions);
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    // Step 3: Handle user input
    const handleSendMessage = async (messageText = null) => {
        const query = messageText || inputText.trim();
        
        // Step 4: Validate input
        if (!query) return;
        
        if (query.length > 1000) {
            alert('Câu hỏi quá dài. Vui lòng rút gọn câu hỏi (tối đa 1000 ký tự).');
            return;
        }

        // Add user message to chat
        const userMessage = {
            id: Date.now(),
            type: 'user',
            text: query,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputText('');
        setIsLoading(true);

        // Step 5: Show loading indicator
        const loadingMessage = {
            id: `loading_${Date.now()}`,
            type: 'loading',
            text: 'Đang xử lý...',
            timestamp: new Date()
        };
        
        setMessages(prev => [...prev, loadingMessage]);

        try {
            // Step 6-12: Call backend API
            const response = await axios.post('/api/v1/guest/ask', {
                query: query,
                session_id: sessionId
            });

            const data = response.data;
            
            // Update session ID
            if (!sessionId && data.session_id) {
                setSessionId(data.session_id);
            }

            // Remove loading message and add response
            setMessages(prev => prev.filter(msg => msg.id !== loadingMessage.id));

            // Step 10: Display answer with references
            const assistantMessage = {
                id: Date.now() + 1,
                type: 'assistant',
                text: data.answer,
                timestamp: new Date(),
                references: data.references,
                confidence: data.confidence,
                responseTime: data.response_time,
                suggestions: data.suggestions
            };

            setMessages(prev => [...prev, assistantMessage]);
            setSuggestions(data.suggestions);

        } catch (error) {
            // Handle errors (AF2, EF1, EF2)
            setMessages(prev => prev.filter(msg => msg.id !== loadingMessage.id));

            let errorMessage = 'Có lỗi xảy ra. Vui lòng thử lại.';
            
            if (error.response) {
                const status = error.response.status;
                const detail = error.response.data.detail;
                
                if (status === 400) {
                    errorMessage = detail; // Input validation error
                } else if (status === 503) {
                    errorMessage = detail; // Service unavailable
                }
            } else if (error.request) {
                errorMessage = 'Không thể kết nối tới server. Vui lòng kiểm tra kết nối mạng.';
            }

            const errorMsg = {
                id: Date.now() + 1,
                type: 'error',
                text: errorMessage,
                timestamp: new Date()
            };

            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const handleSuggestionClick = (suggestion) => {
        handleSendMessage(suggestion);
    };

    return (
        <div className="guest-chat-container">
            {/* Header */}
            <div className="chat-header">
                <h3>💬 Hỗ Trợ Khách Hàng</h3>
                <p>Hỏi tôi về sản phẩm và dịch vụ của công ty</p>
            </div>

            {/* Messages Area */}
            <div className="messages-container">
                {messages.map((message) => (
                    <MessageComponent key={message.id} message={message} />
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Suggestions */}
            {suggestions.length > 0 && !isLoading && (
                <div className="suggestions-container">
                    <p>💡 Câu hỏi gợi ý:</p>
                    <div className="suggestions-list">
                        {suggestions.map((suggestion, index) => (
                            <button
                                key={index}
                                className="suggestion-button"
                                onClick={() => handleSuggestionClick(suggestion)}
                                disabled={isLoading}
                            >
                                {suggestion}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Input Area */}
            <div className="input-container">
                <div className="input-wrapper">
                    <textarea
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Hãy đặt câu hỏi..."
                        disabled={isLoading}
                        rows={1}
                        maxLength={1000}
                    />
                    <button
                        onClick={handleSendMessage}
                        disabled={isLoading || !inputText.trim()}
                        className="send-button"
                    >
                        {isLoading ? '⏳' : '➤'}
                    </button>
                </div>
                <div className="character-count">
                    {inputText.length}/1000
                </div>
            </div>
        </div>
    );
};

// Message Component
const MessageComponent = ({ message }) => {
    const { type, text, references, confidence, responseTime, timestamp } = message;

    return (
        <div className={`message ${type}`}>
            {type === 'loading' && (
                <div className="loading-indicator">
                    <div className="spinner"></div>
                    <span>{text}</span>
                </div>
            )}

            {type === 'user' && (
                <div className="user-message">
                    <div className="message-text">{text}</div>
                    <div className="message-time">
                        {timestamp.toLocaleTimeString()}
                    </div>
                </div>
            )}

            {(type === 'assistant' || type === 'error') && (
                <div className="assistant-message">
                    <div className="message-text">
                        {text}
                        {type === 'error' && <span className="error-icon">⚠️</span>}
                    </div>

                    {/* References (Step 10) */}
                    {references && references.length > 0 && (
                        <div className="references">
                            <h5>📚 Nguồn tham khảo:</h5>
                            {references.map((ref, index) => (
                                <div key={index} className="reference-item">
                                    <strong>{ref.title}</strong>
                                    <p>{ref.excerpt}</p>
                                    <span className="confidence">
                                        Độ tin cậy: {Math.round(ref.confidence * 100)}%
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Metadata */}
                    {confidence !== undefined && (
                        <div className="message-metadata">
                            <span className="confidence-badge">
                                Độ tin cậy: {Math.round(confidence * 100)}%
                            </span>
                            {responseTime && (
                                <span className="response-time">
                                    Thời gian: {responseTime.toFixed(1)}s
                                </span>
                            )}
                            <span className="timestamp">
                                {timestamp.toLocaleTimeString()}
                            </span>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default GuestChatInterface;
```

---

## 🧪 **3. TESTING IMPLEMENTATION**

### **Step 3.1: UC1 Specific Tests**

```python
# tests/test_uc1_guest_query.py
import pytest
from httpx import AsyncClient
import asyncio

class TestUC1GuestQuery:
    """Test UC1: Đặt câu hỏi đơn giản, chỉ nhận thông tin công khai"""
    
    async def test_main_flow_success(self, client: AsyncClient):
        """Test main flow UC1 - successful case"""
        
        # Setup: Ensure có public documents
        await self.seed_public_document(client)
        
        # Step 3: Guest nhập câu hỏi
        response = await client.post("/api/v1/guest/ask", json={
            "query": "Công ty làm về lĩnh vực gì?"
        })
        
        # Step 4-12: Validate response
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "answer" in data
        assert "references" in data
        assert "session_id" in data
        assert "confidence" in data
        assert "suggestions" in data
        
        # Check only public content
        for ref in data["references"]:
            assert ref.get("access_level") == "public"
        
        # Check performance requirement
        assert data["response_time"] < 60
        
        # Check session ID is generated
        assert data["session_id"].startswith("guest_")
        
        print(f"✅ Main flow test passed - Response time: {data['response_time']:.2f}s")
    
    async def test_af1_no_relevant_info(self, client: AsyncClient):
        """Test AF1: Không tìm thấy thông tin phù hợp"""
        
        response = await client.post("/api/v1/guest/ask", json={
            "query": "Thông tin về xe tăng và máy bay chiến đấu"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return polite no-match message
        assert "không tìm thấy thông tin phù hợp" in data["answer"]
        assert len(data["references"]) == 0
        assert len(data["suggestions"]) > 0
        assert data["confidence"] == 0
        
        print("✅ AF1 test passed - No relevant info handled gracefully")
    
    async def test_af2_system_overload(self, client: AsyncClient):
        """Test AF2: System overload simulation"""
        
        # Simulate overload với concurrent requests
        tasks = []
        for i in range(20):  # Send 20 concurrent requests
            task = client.post("/api/v1/guest/ask", json={
                "query": f"Test overload query {i}"
            })
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # At least some should succeed, some might get 503
        success_count = 0
        overload_count = 0
        
        for response in responses:
            if hasattr(response, 'status_code'):
                if response.status_code == 200:
                    success_count += 1
                elif response.status_code == 503:
                    overload_count += 1
        
        print(f"✅ AF2 test - Success: {success_count}, Overload: {overload_count}")
        assert success_count > 0  # At least some should succeed
    
    async def test_af3_query_too_long(self, client: AsyncClient):
