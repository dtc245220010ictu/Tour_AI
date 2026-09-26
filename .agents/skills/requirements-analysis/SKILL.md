---
name: requirements-analysis
description: Phân tích yêu cầu phần mềm, chuyển yêu cầu ngôn ngữ tự nhiên thành yêu cầu chức năng, yêu cầu phi chức năng, user story, tiêu chí chấp nhận và thông tin truy xuất nguồn gốc (traceability) có cấu trúc.
---
# Skill Phân Tích Yêu Cầu

## Mục tiêu
Phân tích yêu cầu phần mềm một cách hệ thống và tạo ra đặc tả có cấu trúc, sẵn sàng cho các bước thiết kế kiến trúc, thiết kế CSDL, triển khai và kiểm thử tiếp theo.

## Đầu vào
Đọc các hồ sơ dự án sau khi có sẵn:
- yêu cầu khách hàng (`docs/customer-requirement.md`)
- yêu cầu nghiệp vụ
- tài liệu yêu cầu hiện có
- các ràng buộc của dự án

## Quy trình
### 1. Xác định các bên liên quan
Xác định tất cả các bên liên quan đến hệ thống (ví dụ: Đơn vị điều hành tour, Tư vấn viên du lịch, Kế toán, Hướng dẫn viên, Khách hàng).

### 2. Xác định các tác nhân
Xác định các tác nhân tương tác trực tiếp hoặc gián tiếp với hệ thống.

### 3. Xác định yêu cầu chức năng
Chuyển các nhu cầu nghiệp vụ đã nêu thành yêu cầu chức năng.
Sử dụng mã định danh có cấu trúc:
- FR-001
- FR-002
- FR-003...

### 4. Xác định yêu cầu phi chức năng
Xác định các yêu cầu liên quan đến:
- hiệu năng (performance)
- bảo mật (security)
- độ tin cậy (reliability)
- khả năng sử dụng (usability)
- khả năng bảo trì (maintainability)
- khả năng mở rộng (scalability)
Sử dụng mã định danh có cấu trúc:
- NFR-001
- NFR-002...

### 5. Xác định quy tắc nghiệp vụ
Liệt kê rõ các quy tắc nghiệp vụ được nêu trong yêu cầu (ví dụ: giới hạn số chỗ đặt, hạn chót hủy tour, ngưỡng đặt cọc).
Không được tự sáng tạo quy tắc nghiệp vụ.

### 6. Xác định giả định
Tách bạch giả định với yêu cầu thực tế.

### 7. Xác định điểm mơ hồ
Nhận diện các yêu cầu:
- mơ hồ
- thiếu thông tin
- mâu thuẫn
- không thể kiểm thử

### 8. Tạo user story
Sử dụng đúng định dạng chuẩn (giữ nguyên từ khóa để đồng bộ với `docs/user-stories.md`):
As a <vai trò>,
I want <khả năng>,
so that <lợi ích>.

### 9. Tạo tiêu chí chấp nhận
Mỗi user story quan trọng phải có tiêu chí chấp nhận kiểm thử được theo định dạng Gherkin (giữ nguyên từ khóa Given/When/Then):
Given <trạng thái ban đầu>
When <hành động được thực hiện>
Then <kết quả mong đợi>.

### 10. Truy xuất nguồn gốc (Traceability)
Mỗi user story phải truy xuất được tới một hoặc nhiều yêu cầu chức năng.

## Quy tắc
- Không viết mã nguồn.
- Không thiết kế CSDL.
- Không thiết kế kiến trúc.
- Không tự sáng tạo quy tắc nghiệp vụ không có trong tài liệu.
- Phân biệt rõ ràng giữa yêu cầu và giả định.
- Chỉ rõ các thông tin còn thiếu.

## Đầu ra
Tạo hoặc cập nhật:
- `docs/requirements.md`
- `docs/user-stories.md`
- `docs/acceptance-criteria.md`
- `docs/requirements-issues.md`

## Kiểm tra
Trước khi hoàn thành nhiệm vụ, xác minh:
- Mọi yêu cầu chức năng có mã định danh duy nhất;
- Mọi yêu cầu phi chức năng có mã định danh duy nhất;
- User story truy xuất được tới yêu cầu;
- Tiêu chí chấp nhận có thể kiểm thử được;
- Các điểm mơ hồ và giả định được ghi nhận rõ ràng.
