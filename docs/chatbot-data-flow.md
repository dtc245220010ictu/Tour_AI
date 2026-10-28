# Luồng Dữ Liệu Của Chatbot (Chatbot Data Flow)

Tài liệu này mô tả chi tiết dữ liệu đi qua pipeline RAG của TourAI. Các giá trị
tour cụ thể bên dưới chỉ minh họa cấu trúc phản hồi; dữ liệu thực tế luôn được
truy xuất từ SQLite tại thời điểm người dùng gửi câu hỏi.

---

## 1. Ví dụ Chuyển đổi Dữ liệu Thực tế

### Bước 1: Câu hỏi Người dùng (User Input)
```text
"Tôi có khoảng 4 triệu, muốn đi du lịch Hạ Long hoặc Đà Nẵng tầm 2-3 ngày cuối tuần này còn chỗ không?"
```

### Bước 2: Question Analyzer -> Structured Intent JSON
```json
{
  "destinations": ["Hạ Long", "Đà Nẵng"],
  "max_price": 4000000,
  "min_price": null,
  "duration_days": [2, 3],
  "keywords": [],
  "sort_by": null,
  "raw_question": "Tôi có khoảng 4 triệu, muốn đi du lịch Hạ Long hoặc Đà Nẵng tầm 2-3 ngày cuối tuần này còn chỗ không?"
}
```

`QuestionAnalyzer` hiện không tạo các khóa `regions` hoặc `preferences`; cụm
“cuối tuần này” chưa trở thành bộ lọc ngày khởi hành. Từ khóa được nhận diện
có thể ánh xạ sang điểm đến nếu người dùng chưa nêu điểm đến trực tiếp.

### Bước 3: Tour Retriever -> Parameterized SQL Query
```sql
SELECT t.id, t.title, t.slug, t.description, t.duration_days, t.duration_nights,
       t.base_price, t.transportation, t.image_url, d.name AS destination_name,
       d.region AS destination_region,
       MIN(s.departure_date) AS next_departure,
       SUM(s.available_seats) AS total_available_seats
FROM tours t
JOIN destinations d ON t.destination_id = d.id
JOIN tour_schedules s ON t.id = s.tour_id
WHERE t.is_active = 1
  AND s.status = 'OPEN'
  AND s.available_seats > 0
  AND d.name IN (?, ?)
  AND t.base_price <= ?
  AND t.duration_days BETWEEN ? AND ?
GROUP BY t.id
ORDER BY next_departure ASC, t.base_price ASC
LIMIT ?;
```

```text
params = ["Hạ Long", "Đà Nẵng", 4000000.0, 2, 3, 4]
```

Nếu `sort_by` là `price_asc` hoặc `price_desc`, truy vấn sắp xếp theo giá; nếu
không, dùng thứ tự lịch khởi hành gần nhất rồi giá. Mọi giá trị lọc đi qua
placeholder SQLite `?`, không ghép trực tiếp từ câu hỏi.

### Bước 4: Tour Retriever Result (bản ghi CSDL)

Ví dụ dưới đây chỉ thể hiện các trường trả về; không khẳng định các tour, giá,
ngày hoặc số chỗ này đang tồn tại trong CSDL hiện hành.
```json
[
  {
    "id": 1,
    "title": "Hạ Long - Du Thuyền 5 Sao Sang Trọng",
    "destination_name": "Hạ Long",
    "base_price": 3200000,
    "duration_days": 2,
    "duration_nights": 1,
    "destination_region": "Bắc",
    "next_departure": "2026-10-15",
    "total_available_seats": 20
  },
  {
    "id": 2,
    "title": "Đà Nẵng - Hội An - Bà Nà Hills Cầu Vàng",
    "destination_name": "Đà Nẵng",
    "base_price": 3850000,
    "duration_days": 3,
    "duration_nights": 2,
    "destination_region": "Trung",
    "next_departure": "2026-10-18",
    "total_available_seats": 12
  }
]
```

### Bước 5: Context Builder -> Clean Compact Text Context
```text
[=== DANH SÁCH TOUR THỎA MÃN YÊU CẦU TRONG CƠ SỞ DỮ LIỆU ===]
1. Tên tour: Hạ Long - Du Thuyền 5 Sao Sang Trọng
   - Điểm đến: Hạ Long (Bắc)
   - Giá tiêu chuẩn: 3.200.000 VNĐ / khách
   - Thời lượng: 2 ngày 1 đêm
   - Phương tiện: Xe Limousine & Du thuyền 5 sao
   - Lịch khởi hành gần nhất: 2026-10-15 (Số chỗ còn lại: 20 chỗ)
   - Điểm nhấn: Nghỉ đêm du thuyền 5 sao, chèo kayak hang Sửng Sốt...

2. Tên tour: Đà Nẵng - Hội An - Bà Nà Hills Cầu Vàng
   - Điểm đến: Đà Nẵng (Trung)
   - Giá tiêu chuẩn: 3.850.000 VNĐ / khách
   - Thời lượng: 3 ngày 2 đêm
   - Phương tiện: Máy bay & Xe du lịch cao cấp
   - Lịch khởi hành gần nhất: 2026-10-18 (Số chỗ còn lại: 12 chỗ)
   - Điểm nhấn: Check-in Cầu Vàng Bà Nà Hills, dạo phố cổ Hội An...
```

Khi không có kết quả khớp, context dùng tiêu đề nêu rõ “KHÔNG CÓ TOUR ĐÚNG
TIÊU CHÍ” rồi chỉ liệt kê tour thay thế do CSDL trả về. Nếu không có cả tour
thay thế, context là `[KHÔNG TÌM THẤY TOUR THỎA MÃN TIÊU CHÍ TRONG CƠ SỞ DỮ
LIỆU]`.

### Bước 6: Prompt Builder -> Final Prompt to Gemini
```text
Bạn là Trợ lý Tư vấn Tour Du lịch của công ty du lịch TourAI.

QUY TẮC BẮT BUỘC:
1. CHỈ sử dụng thông tin trong mục CONTEXT bên dưới. Tuyệt đối KHÔNG tự sáng tạo ra tour, giá tiền, ngày đi hoặc địa điểm không có trong CONTEXT.
2. Nếu CONTEXT cho biết không có tour đúng tiêu chí, hãy thông báo lịch sự, trung thực. Nếu CONTEXT có tour thay thế, phải giới thiệu các tour đó với dữ liệu có sẵn; nếu không có tour nào thì hướng dẫn đổi tiêu chí hoặc liên hệ hotline.
3. Luôn trả lời bằng tiếng Việt thân thiện, nhiệt tình, chuyên nghiệp.
4. Khi context có tour, nêu giá, thời lượng, ngày khởi hành và số chỗ đúng như context; không được bổ sung dữ kiện ngoài context.

CONTEXT:
{context}

CÂU HỎI CỦA KHÁCH HÀNG:
"Tôi có khoảng 4 triệu, muốn đi du lịch Hạ Long hoặc Đà Nẵng tầm 2-3 ngày cuối tuần này còn chỗ không?"
```

### Bước 7: Phản hồi cuối cùng gửi tới Client (API Response)

Route `POST /api/chat` chỉ trả `answer` và `tours`; `intent` là dữ liệu nội bộ
và được ghi log. Nội dung cụ thể dưới đây chỉ minh họa định dạng: Gemini hoặc
grounded fallback có thể diễn đạt khác, nhưng chỉ được dựa trên các bản ghi đã
truy xuất.
```json
{
  "answer": "Chào bạn! Với ngân sách 4 triệu và mong muốn đi du lịch 2-3 ngày, hệ thống TourAI hiện có 2 tour rất phù hợp và đang còn chỗ cho bạn lựa chọn:\n\n1. **Hạ Long - Du Thuyền 5 Sao Sang Trọng** (2 ngày 1 đêm): Giá chỉ **3.200.000 VNĐ/khách**, khởi hành ngày 15/10/2026 (còn 20 chỗ). Bạn sẽ được trải nghiệm nghỉ đêm trên du thuyền 5 sao đẳng cấp và chèo thuyền kayak.\n\n2. **Đà Nẵng - Hội An - Bà Nà Hills Cầu Vàng** (3 ngày 2 đêm): Giá **3.850.000 VNĐ/khách**, khởi hành ngày 18/10/2026 (còn 12 chỗ). Tour bao gồm vé cáp treo check-in Cầu Vàng và dạo chơi phố cổ Hội An.\n\nBạn có thể nhấn vào thẻ tour bên dưới để xem chi tiết lịch trình và đặt chỗ ngay nhé!",
  "tours": [
    {
      "id": 1,
      "title": "Hạ Long - Du Thuyền 5 Sao Sang Trọng",
      "slug": "ha-long-du-thuyen-5-sao",
      "base_price": 3200000,
      "duration_days": 2,
      "destination_name": "Hạ Long",
      "image_url": "https://images.unsplash.com/photo-1528127269322-539801943592..."
    },
    {
      "id": 2,
      "title": "Đà Nẵng - Hội An - Bà Nà Hills Cầu Vàng",
      "slug": "da-nang-hoi-an-ba-na-hills",
      "base_price": 3850000,
      "duration_days": 3,
      "destination_name": "Đà Nẵng",
      "image_url": "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b..."
    }
  ]
}
```

Sau phản hồi tư vấn, `RAGService` cố gắng ghi `session_id`, câu hỏi, intent
JSON, các ID tour đã dùng và câu trả lời vào bảng `chat_logs`. Lỗi ghi log
không làm thất bại phản hồi chat.

## 2. Nhánh tổng hợp phản hồi khách hàng

Khi câu hỏi đồng thời có động từ tổng hợp (ví dụ “tóm tắt”, “báo cáo”) và danh
từ phản hồi (ví dụ “đánh giá”, “review”), hệ thống không chạy truy xuất tour.
Chỉ tài khoản `ADMIN` được đọc tối đa 50 phản hồi thật để tạo báo cáo; vai trò
khác nhận thông báo không có quyền. Nhánh này luôn trả mảng `tours` rỗng và
cũng ghi nhật ký vào `chat_logs`.

