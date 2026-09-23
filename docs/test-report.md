# Báo Cáo Kết Quả Kiểm Thử (Automated Test Report) - TourAI

Tài liệu này ghi nhận kết quả thực thi bộ kiểm thử tự động toàn diện cho hệ thống **TourAI (Đề tài 17)** theo tiêu chuẩn `testing` skill.

---

## 1. Tóm tắt kết quả kiểm thử (Executive Summary)

- **Thời điểm thực thi:** 23/09/2026
- **Test Framework:** `pytest 9.1.1`
- **Môi trường:** Python 3.14 (Windows)
- **Tổng số ca kiểm thử:** **20/20 PASSED**
- **Tỷ lệ thành công:** **100.0%**
- **Thời gian thực thi:** 1.19 giây
- **Tình trạng:** **PASSED - READY FOR PRODUCTION**

```text
============================= test session starts =============================
rootdir: F:\TourAI
collected 20 items

tests/test_auth.py::test_register_and_login_success PASSED               [  5%]
tests/test_auth.py::test_login_invalid_password PASSED                   [ 10%]
tests/test_auth.py::test_register_duplicate_email_fails PASSED           [ 15%]
tests/test_booking_capacity.py::test_booking_successful_and_seats_deducted PASSED [ 20%]
tests/test_booking_capacity.py::test_overbooking_prevention_rejected PASSED [ 25%]
tests/test_booking_capacity.py::test_cancellation_restores_seats PASSED  [ 30%]
tests/test_context_builder.py::test_build_context_with_tours PASSED      [ 35%]
tests/test_context_builder.py::test_build_context_empty PASSED           [ 40%]
tests/test_question_analyzer.py::test_analyze_ha_long_under_4_million PASSED [ 45%]
tests/test_question_analyzer.py::test_analyze_da_nang_3_days_under_5_tr PASSED [ 50%]
tests/test_question_analyzer.py::test_analyze_beach_preference PASSED    [ 55%]
tests/test_question_analyzer.py::test_analyze_cheapest_sorting PASSED    [ 60%]
tests/test_question_analyzer.py::test_analyze_empty_or_whitespace PASSED [ 65%]
tests/test_rag_pipeline.py::test_rag_service_ha_long_query PASSED        [ 70%]
tests/test_rag_pipeline.py::test_api_chat_success PASSED                 [ 75%]
tests/test_rag_pipeline.py::test_api_chat_empty_question_returns_400 PASSED [ 80%]
tests/test_rag_pipeline.py::test_api_chat_zero_hallucination_impossible_price PASSED [ 85%]
tests/test_tour_retrieval.py::test_retrieve_ha_long_under_4_million PASSED [ 90%]
tests/test_tour_retrieval.py::test_retrieve_impossible_budget_returns_empty PASSED [ 95%]
tests/test_tour_retrieval.py::test_retrieve_alternative_tours_when_none_match PASSED [100%]

============================= 20 passed in 1.19s ==============================
```

---

## 2. Chi tiết các module kiểm thử

| STT | Tên Test File | Số ca test | Kết quả | Trọng tâm kiểm thử |
|---|---|---|---|---|
| 1 | `test_auth.py` | 3 | 3/3 PASS | Mật khẩu băm an toàn, đăng ký trùng email bị từ chối, đăng nhập chính xác |
| 2 | `test_booking_capacity.py` | 3 | 3/3 PASS | Trừ số chỗ nguyên tử, chặn đứng Overbooking, hoàn trả số chỗ khi hủy tour |
| 3 | `test_question_analyzer.py` | 5 | 5/5 PASS | Bóc tách ngân sách (triệu, tr, nghìn), số ngày, điểm đến, sở thích biển/núi |
| 4 | `test_tour_retrieval.py` | 3 | 3/3 PASS | Parameterized SQL query an toàn, không có tour giá ảo trả về empty list |
| 5 | `test_context_builder.py` | 2 | 2/2 PASS | Định dạng ngữ cảnh ngắn gọn, thông báo rỗng chuẩn mực |
| 6 | `test_rag_pipeline.py` | 4 | 4/4 PASS | Toàn trình RAG, API POST /api/chat, kiểm tra Zero Hallucination |

---

## 3. Đánh giá tính tuân thủ các quy tắc cốt lõi

### 3.1 Quy tắc Phòng Chống Đặt Vượt Chỗ (Overbooking Prevention)
- Khi lịch khởi hành có `available_seats = 15`, khách đặt 3 chỗ -> `available_seats` giảm còn đúng 12 chỗ.
- Khách đặt vượt quá số chỗ còn lại -> Hệ thống ném ngoại lệ `OverbookingError` và rollback giao dịch CSDL ngay lập tức.
- Khi đơn đặt chỗ bị hủy -> Số chỗ được cộng trả chính xác về lịch trình tương ứng.
- **Đánh giá: ĐẠT 100%.**

### 3.2 Quy tắc Không Bịa Đặt Dữ Liệu (Zero Hallucination Policy)
- Khi khách hỏi tour với mức giá không tưởng (ví dụ: "Dưới 100 nghìn"), Tour Retriever trả về danh sách rỗng `[]`.
- Context Builder sinh thông báo rỗng.
- Chatbot API trả về thông báo lịch sự rằng không tìm thấy tour phù hợp, tuyệt đối không bịa ra tour hay mức giá giả.
- **Đánh giá: ĐẠT 100%.**
