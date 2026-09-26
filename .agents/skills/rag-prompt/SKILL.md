---
name: rag-prompt
description: Xây dựng prompt hệ thống và prompt người dùng vững chắc, bám dữ liệu thật; áp đặt chính sách zero-hallucination nghiêm ngặt và văn phong tư vấn du lịch tiếng Việt chuyên nghiệp.
---
# Skill Prompt Engineering Cho RAG

## Mục tiêu
Lắp ghép các thành phần prompt thành mẫu "bất khả xâm phạm", hướng dẫn mô hình AI đưa ra tư vấn tour chính xác, lịch sự, thuyết phục — chỉ dựa trên ngữ cảnh (context) đã truy xuất.

## Cấu trúc
Vai trò hệ thống (System Role)
    ↓
Quy tắc bám dữ liệu (ràng buộc zero-hallucination)
    ↓
Ngữ cảnh (dữ liệu thật từ CSDL)
    ↓
Câu hỏi người dùng
    ↓
Hướng dẫn định dạng phản hồi

## Quy tắc
- Chỉ thị rõ cho mô hình: "CHỈ sử dụng thông tin trong mục CONTEXT. Tuyệt đối không tự suy diễn hoặc bịa đặt tour/giá tiền".
- Yêu cầu mô hình thông báo lịch sự khi không có tour phù hợp.
- Yêu cầu mô hình trả lời bằng tiếng Việt tự nhiên, lịch thiệp.
- Yêu cầu mô hình trích dẫn chi tiết cụ thể từ CONTEXT (tên tour, giá, thời lượng, ngày khởi hành) thay vì nói chung chung.
- Cấm trả lời các câu hỏi chung không liên quan danh mục tour khi đang tư vấn sản phẩm.
- Luôn tính trước `fallback_answer` bằng `GroundedAnswerBuilder` (chỉ từ dữ liệu truy xuất có cấu trúc) để khi LLM/API offline, chat vẫn trả lời đủ giàu thông tin mà không bịa đặt.
