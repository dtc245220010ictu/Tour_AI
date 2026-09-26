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

### 1.2 Hỏi Trợ Lý AI tổng hợp phản hồi khách hàng (Feedback Summary Intent)
- **Endpoint:** `POST /api/chat` (dùng chung endpoint 1.1 — hệ thống tự nhận diện ý định từ nội dung câu hỏi).
- **Mô tả:** Khi câu hỏi chứa cặp *"động từ tóm tắt + danh từ phản hồi"* (ví dụ: *"Tóm tắt phản hồi khách hàng"*, *"Phân tích đánh giá của khách"*, *"Tổng hợp nhận xét khách hàng"*), pipeline **bỏ qua bước truy xuất tour** và trả về **Báo cáo tổng hợp chất lượng dịch vụ** dựng từ dữ liệu thật trong bảng `feedbacks`: số lượng phản hồi, điểm trung bình sao và 3 mục 1. ĐIỂM KHEN NGỢI / 2. ĐIỂM CẦN CẢI THIỆN / 3. ĐỀ XUẤT HÀNH ĐỘNG. Trường `tours` trả về `[]` (không trả thẻ tour).
- **Quyền hạn:** Báo cáo chỉ dành cho `ADMIN` (đồng nhất với `/admin/feedbacks` và `/api/ai/summarize-feedbacks`). Các vai trò khác nhận thông báo lịch sự rằng chức năng dành cho Quản trị viên — không rò rỉ nội dung phản hồi.
- **Fallback:** Nếu Gemini không khả dụng hoặc hết quota, hệ thống trả về bản tổng hợp luật theo thang điểm sao — không bao giờ trả câu chào mẫu chung chung hay thông tin bịa đặt.

#### Response Success (HTTP 200 OK) — ví dụ với tài khoản ADMIN
```json
{
  "answer": "📊 **Báo cáo tổng hợp phản hồi khách hàng** — 4 phản hồi, điểm trung bình 4.8/5 ⭐\n\n1. ĐIỂM KHEN NGỢI:\n- Hướng dẫn viên rất nhiệt tình và chu đáo...\n2. ĐIỂM CẦN CẢI THIỆN:\n- ...\n3. ĐỀ XUẤT HÀNH ĐỘNG:\n- ...",
  "tours": []
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
  "full_content": "...",
  "source": "ai"
}
```
- `source`: `"ai"` nếu Gemini sinh nội dung; `"template"` nếu AI không khả dụng/trả về nội dung không hợp lệ → hệ thống tự động tạo mô tả & lịch trình theo mẫu cấu trúc (không bao giờ trả về câu chào mẫu chung chung).

### 2.2 Phân tích và tóm tắt phản hồi khách hàng
- **Endpoint:** `POST /api/ai/summarize-feedbacks`
- **Xác thực:** Yêu cầu quyền `ADMIN` (xem và xử lý phản hồi là quyền quản trị - Nhân viên tư vấn không có quyền).
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
| `POST` | `/booking/new/<schedule_id>` | Tạo đơn đặt tour mới, trừ chỗ khả dụng nguyên tử | `CUSTOMER`, `STAFF`, `ADMIN` |
| `POST` | `/booking/<id>/pay` | Xác nhận thanh toán (mô phỏng hoặc chuyển khoản); `CUSTOMER` chỉ với đơn của chính mình | `CUSTOMER` (đơn của mình), `ACCOUNTANT`, `ADMIN` |
| `POST` | `/booking/<id>/cancel` | Hủy đơn đặt tour (PENDING hoặc CONFIRMED), tự động hoàn trả số chỗ; `CUSTOMER` tự hủy đơn của chính mình không cần qua nhân viên; đơn COMPLETED bị chặn | `CUSTOMER` (đơn của mình), `ADMIN` |
| `POST` | `/feedback/new` | Gửi đánh giá sao (1-5) và nhận xét | `CUSTOMER`, `ADMIN` |

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

---

## 5. Upload Ảnh Cho Form Admin

### 5.1 Tải ảnh đại diện (tour / điểm đến)
- **Endpoint:** `POST /admin/upload-image`
- **Xác thực:** Yêu cầu quyền `ADMIN` hoặc `STAFF`.
- **Headers:** `Content-Type: multipart/form-data`
- **Body:** trường `file` — file ảnh (JPG, PNG, WEBP, GIF; tối đa 5MB).
- **Mô tả:** Được form admin gọi AJAX khi người dùng dán ảnh (Ctrl+V) vào ô URL hoặc chọn file. Ảnh được validate và lưu vào `static/uploads/` với tên duy nhất (UUID).

#### Response Success (HTTP 200 OK)
```json
{ "ok": true, "url": "/static/uploads/3f9c8a...b1.png" }
```

#### Response Error (HTTP 400 Bad Request)
```json
{ "ok": false, "error": "Định dạng ảnh không hợp lệ. Chỉ chấp nhận: gif, jpeg, jpg, png, webp." }
```

> Các form tạo/sửa tour & điểm đến (`POST /admin/tours`, `/admin/tours/<id>/edit`, `/admin/destinations`, `/admin/destinations/<id>/edit`) nhận thêm trường `image_file` (multipart). Nếu có file tải lên thì **ưu tiên dùng file**, ngược lại dùng giá trị trường `image_url`.

> Ô nhập URL trên form là `type="text"` (không dùng `type="url"`): hệ thống lưu ảnh upload dưới dạng đường dẫn tương đối `/static/uploads/...`, nếu dùng `type="url"` trình duyệt sẽ chặn submit và bắt người dùng nhập lại URL mỗi khi mở form Sửa tour/điểm đến đã có ảnh.


