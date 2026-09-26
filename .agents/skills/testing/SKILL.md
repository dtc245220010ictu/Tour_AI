---
name: testing
description: Lập kế hoạch, viết và thực thi bộ kiểm thử tự động (unit, integration, kiểm tra sức chứa), bám sát yêu cầu, xác minh zero-hallucination và chống overbooking.
---
# Skill Kiểm Thử (Testing)

## Mục tiêu
Thiết lập quy trình đảm bảo chất lượng nghiêm ngặt, chuyển yêu cầu phần mềm thành kịch bản kiểm thử cụ thể, ca kiểm thử tự động và báo cáo thực thi.

## Quy trình làm việc
Yêu cầu (Requirements)
    ↓
Kịch bản kiểm thử (Test Scenario)
    ↓
Ca kiểm thử (Test Case)
    ↓
Kiểm thử tự động (pytest)
    ↓
Thực thi (Execution)
    ↓
Kết quả & chỉ số (Result & Metrics)
    ↓
Báo cáo lỗi (Defect Reporting)

## Đầu vào
Đọc:
- `docs/requirements.md`
- `docs/user-stories.md`
- `docs/acceptance-criteria.md`

## Quy trình
1. **Xây dựng kịch bản kiểm thử:** Ánh xạ từng Yêu cầu chức năng (FR-xxx) và Tiêu chí chấp nhận (AC-xxx) sang kịch bản kiểm thử.
2. **Thiết kế ca kiểm thử:** Mô tả chi tiết điều kiện tiên quyết, đầu vào, các bước thực thi, kết quả mong đợi và các giá trị biên.
3. **Triển khai kiểm thử tự động trong `tests/`:**
   - Unit test cho các service cốt lõi (Auth, Booking, khóa sức chứa, phân tích câu hỏi, truy xuất tour, Context Builder).
   - Integration test cho các endpoint Flask (`/tours`, `POST /booking/new/...`, `POST /api/chat`).
4. **Thực thi bộ kiểm thử:** Chạy qua `pytest -v`.
5. **Phân tích lỗi:** Không bao giờ sửa test chỉ để test PASS; xác minh xem lỗi có phải khiếm khuyết thật trong triển khai không.
6. **Tạo báo cáo kiểm thử:** Sinh kế hoạch kiểm thử và báo cáo thực thi có cấu trúc.

## Quy tắc
- KHÔNG sửa test chỉ để vượt qua; nếu phát hiện khiếm khuyết phải xử lý tận gốc trong mã ứng dụng.
- Đảm bảo bao phủ 100% cho logic nghiệp vụ quan trọng:
  - Trừ số chỗ và chống overbooking.
  - Zero-hallucination khi không có tour phù hợp.
  - Kháng SQL injection trong truy xuất tour.

## Đầu ra
Tạo:
- `docs/test-plan.md`
- `docs/test-report.md`
- Script kiểm thử tự động trong `tests/`
