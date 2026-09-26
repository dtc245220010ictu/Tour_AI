---
name: code-review
description: Đánh giá mã nguồn theo mẫu kiến trúc, mức độ tuân thủ yêu cầu, chất lượng mã, khả năng bảo trì, hiệu năng, xử lý lỗi và độ đầy đủ của kiểm thử.
---
# Skill Đánh Giá Mã Nguồn (Code Review)

## Mục tiêu
Đánh giá một cách hệ thống toàn bộ mã nguồn nhằm phát hiện lỗi, thiếu sót so với yêu cầu, lệch kiến trúc, điểm nghẽn hiệu năng và code smell — mà KHÔNG chỉnh sửa mã nguồn.

## Tiêu chí đánh giá
1. **Tính đúng đắn:** Mã nguồn có thực hiện đúng chức năng dự kiến?
2. **Tuân thủ yêu cầu:** Tất cả yêu cầu chức năng và tiêu chí chấp nhận có được đáp ứng? Có chức năng nào tự thêm ngoài đặc tả không?
3. **Tuân thủ kiến trúc:** Các ranh giới phân lớp có được tôn trọng? Route có gọi Service? Service có gọi tầng truy cập dữ liệu? LLM có được cô lập khỏi CSDL?
4. **Khả năng bảo trì & Clean Code:** Quy ước đặt tên, kích thước hàm, tính mô-đun, type hints, docstrings.
5. **Trùng lặp mã:** Mức độ tuân thủ nguyên tắc DRY (Don't Repeat Yourself).
6. **Xử lý lỗi:** Quản lý ngoại lệ an toàn, không rò rỉ stack trace nội bộ.
7. **Truy cập CSDL:** Truy vấn tham số hóa an toàn, tính nguyên tử của giao dịch, đóng kết nối đúng cách.
8. **Chất lượng kiểm thử:** Kiểm thử tự động độc lập, lặp lại được và bao phủ toàn diện.

## Phân loại lỗi
Phân loại mọi vấn đề phát hiện được vào 4 mức độ nghiêm trọng:
- **CRITICAL:** Gây hỏng dữ liệu, lỗ hổng bảo mật hoặc sập toàn bộ hệ thống.
- **HIGH:** Yêu cầu cốt lõi bị hỏng, rò rỉ overbooking hoặc ảo giác AI không kiểm soát.
- **MEDIUM:** Hiệu năng chưa tối ưu, thiếu index hoặc phản hồi lỗi không nhất quán.
- **LOW:** Không nhất quán phong cách mã, lỗi định dạng nhỏ hoặc lỗi chính tả tài liệu.

## Quy tắc
- KHÔNG chỉnh sửa mã ứng dụng trong quá trình đánh giá.
- Cung cấp bằng chứng cụ thể (đường dẫn file và số dòng) cho mỗi nhận xét.
- Đề xuất giải pháp khắc phục cụ thể, có thể hành động được cho từng vấn đề.

## Đầu ra
Tạo hoặc cập nhật:
- `docs/code-review.md`
