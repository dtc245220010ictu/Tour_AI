# Tài Liệu Thiết Kế Kiến Trúc Chatbot RAG (Chatbot Architecture)

Tài liệu này đặc tả kiến trúc thành phần của hệ thống con RAG Chatbot theo `architecture-design` skill.

---

## 1. Sơ đồ Kiến trúc Pipeline RAG

```mermaid
flowchart TD
    Client["👤 Khách hàng (Trình duyệt)"]
    ChatUI["💻 Chatbot UI (chat.js & chat.css)"]
    Endpoint["🌐 Flask API: POST /api/chat"]
    RAG["🧠 RAGService (Điều phối chính)"]
    
    QA["1. Question Analyzer (services/question_analyzer.py)"]
    TR["2. Tour Retriever (services/tour_retriever.py)"]
    DB[("🗄️ MySQL / SQLite (Bảng tours, schedules)")]
    CB["3. Context Builder (services/context_builder.py)"]
    PB["4. Prompt Builder (services/prompt_builder.py)"]
    GS["5. Gemini Service (services/gemini_service.py)"]
    ExtAI["☁️ Google Gemini API"]
    
    Client -->|Nhập câu hỏi tiếng Việt| ChatUI
    ChatUI -->|Fetch POST JSON| Endpoint
    Endpoint -->|Gọi answer_question| RAG
    
    RAG -->|Bước 1: Phân tích intent| QA
    QA -->|Structured Intent JSON| RAG
    
    RAG -->|Bước 2: Truy xuất tour| TR
    TR -->|Parameterized SQL query| DB
    DB -->|Tour records còn chỗ| TR
    TR -->|List Tour Objects| RAG
    
    alt Không tìm thấy tour nào (Zero Results)
        RAG -->|Trả thông báo lịch sự không bịa| Endpoint
    else Tìm thấy tour phù hợp
        RAG -->|Bước 3: Chuẩn hóa context| CB
        CB -->|Clean Compact Context| RAG
        
        RAG -->|Bước 4: Tạo Prompt Grounded| PB
        PB -->|System + Grounding + User Prompt| RAG
        
        RAG -->|Bước 5: Gọi AI Engine| GS
        GS -->|REST HTTPS| ExtAI
        ExtAI -->|Phản hồi văn bản| GS
        GS -->|Answer Text| RAG
    end
    
    RAG -->|Trả {answer, tours}| Endpoint
    Endpoint -->|HTTP 200 JSON| ChatUI
    ChatUI -->|Render Text + Product Cards| Client
```

---

## 2. Chi tiết các module thành phần
1. **Chatbot API (`routes/chat_routes.py`):**
   - Tiếp nhận câu hỏi, kiểm tra tính hợp lệ (`question` không rỗng), bắt ngoại lệ, không lộ stack trace.
2. **Question Analyzer (`services/question_analyzer.py`):**
   - Trích xuất điểm đến, ngân sách tối đa/tối thiểu, số ngày đi, từ khóa sở thích.
   - Nhận diện ý định đặc biệt **tổng hợp phản hồi khách hàng** (động từ tóm tắt + danh từ phản hồi) để rẽ nhánh pipeline.
3. **Tour Retriever (`services/tour_retriever.py`):**
   - Xây dựng SQL có tham số, lọc các tour đang hoạt động (`is_active = 1`) và có lịch trình còn chỗ (`available_seats > 0`).
4. **Context Builder (`services/context_builder.py`):**
   - Chuyển đổi dữ liệu bản ghi CSDL thành văn bản mô tả ngắn gọn, trung thực, bao gồm tên tour, giá, điểm đến, thời lượng và ngày khởi hành gần nhất.
5. **Prompt Builder (`services/prompt_builder.py`):**
   - Đặt vai trò chuyên gia tư vấn du lịch, ban hành các quy tắc cấm bịa đặt (Grounding Rules) và hướng dẫn cách so sánh, gợi ý cho khách hàng.
6. **Gemini Service (`services/gemini_service.py`):**
   - Giao tiếp với Google Gemini API (model `gemini-1.5-flash`), xử lý timeout, bảo mật key và cơ chế fallback.
7. **RAG Service (`services/rag_service.py`):**
   - Điều phối tuần tự các bước trên và ghi log vào bảng `chat_logs`.
   - Nhánh đặc biệt: nếu câu hỏi là yêu cầu tổng hợp phản hồi khách hàng → bỏ qua truy xuất tour; `ADMIN` nhận báo cáo dựng từ bảng `feedbacks` (số lượng, điểm trung bình, phân tích AI), các vai trò khác nhận thông báo dành cho Quản trị viên.

