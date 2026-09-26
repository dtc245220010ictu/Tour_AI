---
name: uml-design
description: Skill chuẩn hóa tạo bộ biểu đồ UML và mô hình kiến trúc toàn diện gồm Use Case, Class, Sequence, Activity và Entity-Relationship (ERD) bằng Mermaid kèm đặc tả markdown.
---
# Skill Thiết Kế UML

## Mục tiêu
Chuyển yêu cầu phần mềm đã phê duyệt và mô hình miền thành các biểu đồ UML chính xác, chuẩn hóa và hồ sơ thiết kế trực quan, định hướng cho triển khai, thiết kế schema CSDL và tài liệu kỹ thuật.

## Đầu vào
Đọc các hồ sơ dự án sau:
- `docs/requirements.md`
- `docs/user-stories.md`
- `docs/acceptance-criteria.md`

## Quy trình
### 1. Xác định tác nhân & Use Case
- Ánh xạ tác nhân (Khách hàng, Admin, Nhân viên/Tư vấn viên, Kế toán, Hướng dẫn viên, AI Engine) sang các use case cấp cao.
- Nhóm use case theo phân hệ chức năng (Xác thực, Quản lý tour & lịch khởi hành, Đặt chỗ & kiểm soát sức chứa, Thanh toán, Phân công HDV, Phản hồi, Thống kê, Dịch vụ AI).
- Định nghĩa quan hệ include và extend khi phù hợp.

### 2. Thiết kế Class Diagram
- Mô hình hóa thực thể cốt lõi, mô hình miền, tầng service và lớp controller.
- Mô tả chi tiết thuộc tính (kèm kiểu và phạm vi truy cập), phương thức và quan hệ bản số (1-1, 1-N, N-M, kế thừa).

### 3. Thiết kế Sequence Diagram
- Mô tả từng bước các tương tác quan trọng:
  - Đặt tour & chống overbooking (Client → Route → BookingService → TourSchedule → DB).
  - Luồng Chatbot RAG (User → ChatAPI → QuestionAnalyzer → TourRetriever → ContextBuilder → GeminiService → Response).

### 4. Thiết kế Activity Diagram
- Vẽ sơ đồ luồng logic nghiệp vụ, điều kiện rẽ nhánh và trạng thái ngoại lệ (ví dụ: đặt tour kèm kiểm tra số chỗ, xác nhận thanh toán hoặc hoàn trả chỗ khi hủy).

### 5. Thiết kế Entity-Relationship Diagram (ERD)
- Định nghĩa toàn bộ bảng CSDL, cột, kiểu dữ liệu, khóa chính (PK), khóa ngoại (FK) và ràng buộc toàn vẹn tham chiếu.

## Quy tắc
- Dùng cú pháp Mermaid hợp lệ, được hỗ trợ bởi markdown previewer và công cụ sinh tài liệu.
- Đảm bảo nhất quán 100% với yêu cầu chức năng (FR-xxx) và tiêu chí chấp nhận (AC-xxx).
- Tránh thành phần mơ hồ hoặc rời rạc; mọi thực thể phải phục vụ một yêu cầu đã phê duyệt.

## Đầu ra
Tạo hoặc cập nhật:
- `docs/uml-diagrams.md`

## Kiểm tra
- Xác minh mọi tác nhân trong yêu cầu đều có use case tương ứng.
- Xác minh sequence diagram phản ánh đúng kiến trúc phân lớp.
- Xác minh ERD khớp với yêu cầu CSDL và các quy tắc ràng buộc sức chứa.
