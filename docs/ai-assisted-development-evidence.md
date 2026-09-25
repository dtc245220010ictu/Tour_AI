# Hồ Sơ AI-Assisted Development — TourAI

**Cập nhật:** 25/09/2026  
**Mục đích:** Cung cấp prompt tái lập và ma trận truy vết để minh chứng cách AI có thể hỗ trợ phân tích, thiết kế, sinh/kiểm tra mã cho KT1–KT3.

> **Minh bạch về bằng chứng:** Repository không lưu transcript, ảnh chụp màn hình hoặc lịch sử hội thoại AI gốc của các lần phát triển trước. Vì vậy tài liệu này **không khẳng định** các prompt dưới đây là transcript lịch sử. Đây là bộ prompt tái lập, được lập để giảng viên hoặc nhóm dự án có thể chạy lại quá trình AI-assisted development và đối chiếu trực tiếp với artifact, mã nguồn và test đang có.

---

## 1. Quy tắc sử dụng AI trong dự án

1. AI chỉ hỗ trợ phân tích, thiết kế, sinh gợi ý mã, review và tạo test; người phát triển kiểm tra lại trước khi tích hợp.
2. AI/LLM không được kết nối trực tiếp CSDL. RAG chỉ gửi context text đã được `ContextBuilder` chuẩn hóa cho Gemini.
3. Không đưa secret, API key, dữ liệu cá nhân nhạy cảm hoặc file `.env` vào prompt.
4. Mọi đề xuất AI liên quan số chỗ, thanh toán, hoàn tiền hoặc zero-hallucination phải được kiểm chứng bằng pytest.

---

## 2. KT1 — Phân tích đặt tour, thanh toán, hủy tour; Use Case và CSDL

### Prompt tái lập

```text
Bạn là Business Analyst và Database Designer cho hệ thống quản lý tour Flask.
Hãy phân tích ba nghiệp vụ: đặt tour, thanh toán/đặt cọc và hủy tour/hoàn tiền.

Yêu cầu đầu ra:
1. Liệt kê actor, tiền điều kiện, luồng chính, ngoại lệ và hậu điều kiện cho từng use case.
2. Đề xuất thực thể/tables tối thiểu và khóa ngoại giữa TourSchedule, Booking, Payment.
3. Nêu rõ invariant số chỗ và chính sách hoàn tiền phải được kiểm thử.
4. Không tự thêm cổng thanh toán thực tế hoặc chính sách tiền tệ chưa có yêu cầu.
Trả lời bằng tiếng Việt, Markdown có bảng.
```

### Artifact đối chiếu

| Kết quả cần có | Artifact trong repository |
|---|---|
| Yêu cầu đặt chỗ, thanh toán, hủy | `docs/requirements.md` — FR-012 đến FR-016 |
| User stories và truy vết | `docs/user-stories.md` — US-008 đến US-010 |
| Tiêu chí Given/When/Then | `docs/acceptance-criteria.md` — AC-003 đến AC-005 |
| Use case và activity flow | `docs/uml-diagrams.md` — UC-01, UC-02, UC-06, UC-07; Activity Diagram |
| Thiết kế bảng/khóa/ràng buộc | `docs/database-design.md`, `database/schema.sql` |
| Kiểm thử nghiệp vụ | `tests/test_booking_capacity.py`, `tests/test_accounting.py` |

---

## 3. KT2 — CRUD tour, lịch khởi hành, đặt chỗ; debug số chỗ còn

### Prompt tái lập

```text
Bạn là Python Flask engineer. Với kiến trúc Route -> Service -> SQLite/MySQL,
hãy review thiết kế CRUD Tour và TourSchedule, sau đó đề xuất cơ chế chống lệch
available_seats khi có booking.

Ràng buộc bắt buộc:
- Dùng parameterized SQL và transaction cho thao tác nhạy cảm.
- Booking PENDING đã giữ chỗ; CANCELLED không giữ chỗ.
- Khi sửa total_seats, available_seats phải được suy ra từ booking chưa hủy,
  không tin giá trị client gửi lên.
- Từ chối giảm total_seats thấp hơn số ghế đã giữ.
- Đề xuất unit/integration test cho booking, overbooking, cancel và edit schedule.
Không thay đổi quy tắc nghiệp vụ ngoài phạm vi trên.
```

### Artifact đối chiếu

| Kết quả cần có | Artifact trong repository |
|---|---|
| CRUD Tour | `routes/admin_routes.py`, `services/tour_service.py` (`create_tour`, `update_tour`, `delete_tour`) |
| CRUD Lịch khởi hành | `routes/admin_routes.py`, `services/tour_service.py` (`create_schedule`, `update_schedule`, `delete_schedule`) |
| Booking lifecycle | `routes/booking_routes.py`, `services/booking_service.py` |
| Atomic seat reservation | `BookingService.create_booking()` — `UPDATE ... available_seats >= ?` |
| Số chỗ khi sửa schedule | `TourService.update_schedule()` tính lại từ booking `PENDING`/`CONFIRMED`/`COMPLETED` |
| Regression tests | `tests/test_booking_capacity.py`, `tests/test_price_consistency.py` |

---

## 4. KT3 — Prompt tư vấn tour không bịa dữ liệu; kiểm thử yêu cầu mơ hồ

### Prompt tái lập

```text
Bạn là Prompt Engineer cho chatbot tư vấn tour theo mô hình RAG.
Viết system prompt tiếng Việt bảo đảm:
1. Chỉ dùng thông tin có trong CONTEXT được truy xuất từ CSDL.
2. Không bịa tên tour, giá, ngày khởi hành, thời lượng hoặc số chỗ.
3. Nếu không có tour đúng tiêu chí, phải nói rõ là không có; chỉ được giới thiệu
   tour thay thế nếu chúng xuất hiện trong CONTEXT.
4. Với câu hỏi mơ hồ, có thể giới thiệu tối đa các tour thực tế đang mở bán hoặc
   hỏi thêm ngân sách/điểm đến/thời lượng; không được suy đoán dữ liệu.
5. Đề xuất test cho câu rỗng, ngân sách bất khả thi, "khoảng 5 triệu", và các
   câu "Tư vấn cho tôi đi du lịch", "Có tour gì hay không?", "Tầm 5 triệu thì đi đâu?".
```

### Artifact đối chiếu

| Kết quả cần có | Artifact trong repository |
|---|---|
| Grounding prompt | `services/prompt_builder.py` |
| Structured intent | `services/question_analyzer.py`, `docs/question-analysis.md` |
| Parameterized retrieval chỉ lấy tour còn chỗ | `services/tour_retriever.py` |
| Fallback chỉ từ dữ liệu đã retrieve | `services/grounded_answer_builder.py`, `services/rag_service.py` |
| Test zero-hallucination | `tests/test_tour_retrieval.py`, `tests/test_grounded_answer_builder.py`, `tests/test_rag_pipeline.py` |
| Test yêu cầu mơ hồ chính thức | `tests/test_rag_pipeline.py` |

---

## 5. Checklist bằng chứng nộp/đánh giá

- [ ] Lưu prompt thực tế và phản hồi AI của mỗi thành viên (không chứa `.env`/secret).
- [ ] Lưu ảnh chụp hoặc export hội thoại AI nếu quy định môn học yêu cầu chứng minh lịch sử sử dụng.
- [ ] Ghi commit hash tương ứng với artifact đã review.
- [ ] Chạy `python -m pytest -q -p no:cacheprovider` và lưu output test trước khi nộp.
- [ ] Người phụ trách xác nhận đã review đề xuất AI và không tích hợp mã chưa được kiểm thử.