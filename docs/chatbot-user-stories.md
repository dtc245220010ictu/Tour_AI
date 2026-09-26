# User Stories Cho Chatbot AI (Chatbot User Stories)

## Danh sách User Stories

- **US-CHAT-001 (Tư vấn tour theo ngân sách và điểm đến):**
  - *As a* khách hàng muốn lên kế hoạch du lịch,
  - *I want to* nhập câu hỏi tự nhiên như "Có tour Phú Quốc nào dưới 6 triệu không?",
  - *so that* tôi nhận được gợi ý tour chính xác và phù hợp với túi tiền.
  - *Traceability:* `FR-CHAT-001`, `FR-CHAT-002`, `FR-CHAT-003`, `FR-CHAT-006`

- **US-CHAT-002 (Gợi ý tour theo sở thích & thời lượng):**
  - *As a* khách hàng bận rộn,
  - *I want to* hỏi tour theo thời gian và sở thích (ví dụ: "Cuối tuần muốn đi biển 2-3 ngày"),
  - *so that* AI gợi ý các điểm đến biển đảo thích hợp có lịch khởi hành phù hợp.
  - *Traceability:* `FR-CHAT-002`, `FR-CHAT-003`, `FR-CHAT-006`

- **US-CHAT-003 (Chính sách Không Ảo giác - Zero Hallucination):**
  - *As a* khách hàng tìm kiếm chuyến đi,
  - *I want* AI chỉ giới thiệu những tour thực sự có trong hệ thống và có lịch trình còn chỗ,
  - *so that* tôi không bị lừa dối bởi những thông tin và mức giá ảo.
  - *Traceability:* `FR-CHAT-004`, `FR-CHAT-005`, `FR-CHAT-007`

- **US-CHAT-004 (Xem nhanh chi tiết tour qua thẻ giao diện):**
  - *As a* khách hàng,
  - *I want* câu trả lời của AI kèm các thẻ tour trực quan có ảnh, giá và nút bấm xem chi tiết,
  - *so that* tôi có thể nhấn vào để đặt chỗ ngay lập tức.
  - *Traceability:* `FR-CHAT-006`

- **US-CHAT-005 (Bảo mật & Độ sẵn sàng cao):**
  - *As an* quản trị viên hệ thống,
  - *I want* API key được bảo vệ an toàn trên server và chatbot vẫn trả lời được dù không kết nối được dịch vụ bên ngoài,
  - *so that* hệ thống luôn an toàn và ổn định.
  - *Traceability:* `FR-CHAT-008`, `FR-CHAT-009`

- **US-CHAT-006 (Tổng hợp phản hồi khách hàng qua Trợ lý AI):**
  - *As an* quản trị viên công ty du lịch,
  - *I want to* hỏi trợ lý AI *"Tóm tắt phản hồi khách hàng"* và nhận ngay Báo cáo chất lượng dịch vụ dựng từ dữ liệu đánh giá thật,
  - *so that* tôi không bị trả lời lạc hướng bằng tư vấn/giới thiệu tour và nhanh chóng nắm được điểm khen, điểm chê cùng đề xuất hành động.
  - *Traceability:* `FR-CHAT-010`

