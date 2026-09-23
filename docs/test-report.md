# Báo Cáo Kết Quả Kiểm Thử (Automated Test Report) - TourAI

Tài liệu này ghi nhận kết quả thực thi bộ kiểm thử tự động toàn diện cho hệ thống **TourAI (Đề tài 17)** theo tiêu chuẩn `testing` skill.

---

## 1. Tóm tắt kết quả kiểm thử (Executive Summary)

- **Thời điểm thực thi:** 23/09/2026
- **Test Framework:** `pytest 9.1.1`
- **Môi trường:** Python 3.14 (Windows)
- **Tổng số ca kiểm thử:** **27/27 PASSED**
- **Tỷ lệ thành công:** **100.0%**
- **Thời gian thực thi:** 1.34 giây
- **Tình trạng:** **PASSED - READY FOR PRODUCTION**

```text
============================= test session starts =============================
rootdir: F:\TourAI
collected 27 items

tests/test_accounting.py::test_payment_reconciliation_and_confirmation PASSED [  3%]
tests/test_accounting.py::test_booking_debts_and_collection PASSED       [  7%]
tests/test_accounting.py::test_record_tour_expense_and_validation PASSED [ 11%]
tests/test_accounting.py::test_schedule_pnl_calculation PASSED           [ 14%]
tests/test_accounting.py::test_cancellation_refund_policy_and_processing PASSED [ 18%]
tests/test_accounting.py::test_cashflow_summary_metrics PASSED           [ 22%]
tests/test_accounting.py::test_accounting_rbac_protection PASSED         [ 25%]
tests/test_auth.py::test_register_and_login_success PASSED               [ 29%]
tests/test_auth.py::test_login_invalid_password PASSED                   [ 33%]
tests/test_auth.py::test_register_duplicate_email_fails PASSED           [ 37%]
tests/test_booking_capacity.py::test_booking_successful_and_seats_deducted PASSED [ 40%]
tests/test_booking_capacity.py::test_overbooking_prevention_rejected PASSED [ 44%]
tests/test_booking_capacity.py::test_cancellation_restores_seats PASSED  [ 48%]
tests/test_context_builder.py::test_build_context_with_tours PASSED      [ 51%]
tests/test_context_builder.py::test_build_context_empty PASSED           [ 55%]
tests/test_question_analyzer.py::test_analyze_ha_long_under_4_million PASSED [ 59%]
tests/test_question_analyzer.py::test_analyze_da_nang_3_days_under_5_tr PASSED [ 62%]
tests/test_question_analyzer.py::test_analyze_beach_preference PASSED    [ 66%]
tests/test_question_analyzer.py::test_analyze_cheapest_sorting PASSED    [ 70%]
tests/test_question_analyzer.py::test_analyze_empty_or_whitespace PASSED [ 74%]
tests/test_rag_pipeline.py::test_rag_service_ha_long_query PASSED        [ 77%]
tests/test_rag_pipeline.py::test_api_chat_success PASSED                 [ 81%]
tests/test_rag_pipeline.py::test_api_chat_empty_question_returns_400 PASSED [ 85%]
tests/test_rag_pipeline.py::test_api_chat_zero_hallucination_impossible_price PASSED [ 88%]
tests/test_tour_retrieval.py::test_retrieve_ha_long_under_4_million PASSED [ 92%]
tests/test_tour_retrieval.py::test_retrieve_impossible_budget_returns_empty PASSED [ 96%]
tests/test_tour_retrieval.py::test_retrieve_alternative_tours_when_none_match PASSED [100%]

============================= 27 passed in 1.34s ==============================
```

---

## 2. Chi tiết các module kiểm thử

| STT | Tên Test File | Số ca test | Kết quả | Trọng tâm kiểm thử |
|---|---|---|---|---|
| 1 | `test_accounting.py` | 7 | 7/7 PASS | Đối soát thanh toán, công nợ, chi phí tour, P&L, hoàn tiền hủy tour, RBAC |
| 2 | `test_auth.py` | 3 | 3/3 PASS | Mật khẩu băm an toàn, đăng ký trùng email bị từ chối, đăng nhập chính xác |
| 3 | `test_booking_capacity.py` | 3 | 3/3 PASS | Trừ số chỗ nguyên tử, chặn đứng Overbooking, hoàn trả số chỗ khi hủy tour |
| 4 | `test_question_analyzer.py` | 5 | 5/5 PASS | Bóc tách ngân sách (triệu, tr, nghìn), số ngày, điểm đến, sở thích biển/núi |
| 5 | `test_tour_retrieval.py` | 3 | 3/3 PASS | Parameterized SQL query an toàn, không có tour giá ảo trả về empty list |
| 6 | `test_context_builder.py` | 2 | 2/2 PASS | Định dạng ngữ cảnh ngắn gọn, thông báo rỗng chuẩn mực |
| 7 | `test_rag_pipeline.py` | 4 | 4/4 PASS | Toàn trình RAG, API POST /api/chat, kiểm tra Zero Hallucination |

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

### 3.3 Phân Hệ Kế Toán & Tài Chính (Accounting Module)
- **Đối soát thanh toán:** Kế toán xác nhận giao dịch chuyển khoản PENDING → SUCCESS, đơn tour tự động CONFIRMED. Xác nhận lại giao dịch đã duyệt bị từ chối đúng.
- **Công nợ khách hàng:** Tính đúng `Debt = Total Amount - Paid Amount`. Thanh toán vượt quá nợ còn lại bị từ chối.
- **Chi phí vận hành:** Validate hạng mục chi phí, số tiền > 0, tiêu đề không rỗng, schedule tồn tại. Ghi nhận thành công.
- **Báo cáo P&L:** Tính đúng `Gross Profit = Revenue - Expenses`, `Margin % = (Gross Profit / Revenue) × 100`.
- **Hoàn tiền hủy tour:** Áp dụng chính sách 3 mốc (90% / 50% / 0%). Hoàn vượt tiền đã trả bị từ chối.
- **Sổ quỹ dòng tiền:** Tổng hợp đúng `Net Cash = Total Inflow - Total Outflow`.
- **RBAC:** Anonymous → redirect login. CUSTOMER/GUIDE → redirect denied. ACCOUNTANT/ADMIN → 200 OK.
- **Đánh giá: ĐẠT 100%.**
