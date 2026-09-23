# Tài Liệu Đặc Tả Giao Diện Lập Trình (API Specification) - TourAI

Tài liệu này đặc tả toàn bộ các endpoints của hệ thống TourAI, bao gồm Chatbot RAG API và các công cụ AI.

---

## 1. Chatbot & Tư Vấn AI API

### 1.1 Gửi câu hỏi tư vấn tour (RAG Pipeline)
- **Endpoint:** `POST /api/chat`
- **Headers:** `Content-Type: application/json`
- **Mô tả:** Tiếp nhận câu hỏi ngôn ngữ tự nhiên từ người dùng, chạy pipeline RAG bóc tách intent, truy vấn CSDL và trả về câu trả lời tư vấn kèm danh sách các tour phù hợp.
- **Quy tắc an toàn:** Không bao giờ trả về API key hoặc exception stack trace khi gặp sự cố.

#### Request Body
```json
{
  "question": "Có tour nào đi biển dưới 5 triệu không?"
}
```

#### Response Success (HTTP 200 OK)
```json
{
  "answer": "Chào bạn! Với ngân sách dưới 5 triệu và sở thích đi biển, TourAI hiện có chuyến du lịch rất phù hợp đang còn chỗ...",
  "tours": [
    {
      "id": 1,
      "title": "Hạ Long - Du Thuyền 5 Sao Sang Trọng",
      "slug": "ha-long-du-thuyen-5-sao",
      "destination_name": "Hạ Long",
      "base_price": 3200000,
      "duration_days": 2,
      "duration_nights": 1,
      "transportation": "Xe Limousine & Du thuyền 5 sao",
      "image_url": "https://images.unsplash.com/...",
      "next_departure": "2026-10-15",
      "total_available_seats": 15
    }
  ]
}
```

#### Response Error (HTTP 400 Bad Request)
```json
{
  "error": "Vui lòng nhập câu hỏi của bạn."
}
```

---

## 2. Công Cụ Nội Bộ AI Cho Nhân Viên (Staff AI Tools)

### 2.1 Sinh mô tả tour & lịch trình tự động
- **Endpoint:** `POST /api/ai/generate-description`
- **Xác thực:** Yêu cầu quyền `ADMIN` hoặc `STAFF`.
- **Headers:** `Content-Type: application/json`

#### Request Body
```json
{
  "title": "Tour Khám Phá Cố Đô Huế",
  "destination": "Huế",
  "highlights": "Đại Nội, chùa Thiên Mụ, lăng Khải Định, ca Huế trên sông Hương",
  "duration_days": 3
}
```

#### Response Success (HTTP 200 OK)
```json
{
  "description": "Hành trình đưa du khách trở về miền di sản Cố Đô cổ kính...",
  "itinerary": "Ngày 1: Đón sân bay Phú Bài - Đại Nội Huế...\nNgày 2: Chùa Thiên Mụ - Lăng Khải Định - Nghe ca Huế...\nNgày 3: Chợ Đông Ba mua đặc sản mè xửng, nón bài thơ - Tiễn khách.",
  "full_content": "..."
}
```

### 2.2 Phân tích và tóm tắt phản hồi khách hàng
- **Endpoint:** `POST /api/ai/summarize-feedbacks`
- **Xác thực:** Yêu cầu quyền `ADMIN` hoặc `STAFF`.
- **Response Success (HTTP 200 OK):**
```json
{
  "summary": "1. ĐIỂM KHEN NGỢI:\n- Hướng dẫn viên rất nhiệt tình và am hiểu văn hóa...\n2. ĐIỂM CẦN CẢI THIỆN:\n- Một số bữa ăn cần đa dạng món hơn...\n3. ĐỀ XUẤT HÀNH ĐỘNG:\n- Làm việc lại với thực đơn nhà hàng tại điểm đến..."
}
```

---

## 3. Quản Lý Đặt Chỗ (Booking API / Endpoints)

| Phương thức | Đường dẫn URL | Mô tả chức năng | Quyền hạn |
|---|---|---|---|
| `GET` | `/tours` | Lấy danh sách tour, hỗ trợ lọc theo `destination_id`, `max_price`, `duration`, `keyword` | Public |
| `GET` | `/tours/<slug>` | Xem chi tiết tour, lịch trình, bảng lịch khởi hành còn chỗ | Public |
| `POST` | `/booking/new/<schedule_id>` | Tạo đơn đặt tour mới, trừ chỗ khả dụng nguyên tử | `CUSTOMER`, `ADMIN` |
| `POST` | `/booking/<id>/pay` | Xác nhận thanh toán (mô phỏng hoặc chuyển khoản) | `CUSTOMER`, `ACCOUNTANT` |
| `POST` | `/booking/<id>/cancel` | Hủy đơn đặt tour, tự động hoàn trả số chỗ | `CUSTOMER`, `ADMIN` |
| `POST` | `/feedback/new` | Gửi đánh giá sao (1-5) và nhận xét | `CUSTOMER` |

---

## 4. Quản Lý Kế Toán & Tài Chính (Accounting Module Endpoints)

Tất cả các endpoints kế toán đều được bảo vệ bằng cơ chế RBAC (`@roles_required("ADMIN", "ACCOUNTANT")`).

| Phương thức | Đường dẫn URL | Mô tả chức năng & Nghiệp vụ | Payload / Tham số |
|---|---|---|---|
| `GET` | `/accounting/dashboard` | Dashboard tài chính: Sổ quỹ dòng tiền (Inflow, Outflow, Net Cash), cảnh báo giao dịch chờ duyệt, top nợ khách hàng, tóm tắt P&L | Không |
| `GET` | `/accounting/transactions` | Danh sách phiếu thu, lịch sử giao dịch và đối soát chuyển khoản ngân hàng | Query: `?status=PENDING` hoặc `?status=SUCCESS` |
| `POST` | `/accounting/transactions/<id>/verify` | Kế toán xác nhận tiền đã vào tài khoản ngân hàng, chuyển đơn sang `CONFIRMED` | Không |
| `GET` | `/accounting/debts` | Quản lý công nợ khách hàng (Total - Paid = Remaining Debt) | Không |
| `POST` | `/accounting/debts/<booking_id>/pay` | Lập phiếu thu thanh toán nợ / đợt tiếp theo của khách hàng | Form: `amount`, `payment_method`, `notes` |
| `GET` | `/accounting/expenses` | Xem danh sách chi phí vận hành đoàn tour (xe, phòng KS, ăn uống, vé, thù lao HDV) | Query: `?schedule_id=<id>` |
| `POST` | `/accounting/expenses` | Lập phiếu chi mới gắn với Lịch khởi hành đoàn tour | Form: `schedule_id`, `category`, `title`, `amount`, `supplier_name`, `invoice_code`, `expense_date`, `notes` |
| `GET` | `/accounting/tours-pnl` | Báo cáo Lợi nhuận (P&L): Doanh thu - Chi phí = Lợi nhuận gộp & Biên lợi nhuận (%) theo từng chuyến đi | Query: `?schedule_id=<id>` |
| `GET` | `/accounting/refunds` | Danh sách đơn hủy tour, đối soát theo chính sách hoàn tiền 3 mốc (>=7 ngày: 90%, 3-6 ngày: 50%, <3 ngày: 0%) | Không |
| `POST` | `/accounting/refunds` | Lập phiếu chi xuất quỹ hoàn tiền hủy tour cho khách hàng | Form: `booking_id`, `refund_amount`, `notes` |


