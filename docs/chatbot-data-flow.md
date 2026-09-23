# Luồng Dữ Liệu Của Chatbot (Chatbot Data Flow)

Tài liệu này minh họa chi tiết sự chuyển đổi dữ liệu qua từng bước xử lý trong pipeline RAG của TourAI.

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
  "regions": ["Miền Bắc", "Miền Trung"],
  "max_price": 4000000,
  "min_price": null,
  "duration_days": [2, 3],
  "preferences": ["cuối tuần"],
  "keywords": ["du lịch", "còn chỗ"]
}
```

### Bước 3: Tour Retriever -> Parameterized SQL Query
```sql
SELECT t.id, t.title, t.slug, t.description, t.duration_days, t.duration_nights,
       t.base_price, t.transportation, t.image_url, d.name AS destination_name,
       MIN(s.departure_date) AS next_departure,
       SUM(s.available_seats) AS total_available_seats
FROM tours t
JOIN destinations d ON t.destination_id = d.id
JOIN tour_schedules s ON t.id = s.tour_id
WHERE t.is_active = 1
  AND s.status = 'OPEN'
  AND s.available_seats > 0
  AND (d.name LIKE '%Hạ Long%' OR d.name LIKE '%Đà Nẵng%')
  AND t.base_price <= 4000000
  AND t.duration_days IN (2, 3)
GROUP BY t.id
ORDER BY t.base_price ASC
LIMIT 5;
```

### Bước 4: Tour Retriever Result (Raw Database Records)
```json
[
  {
    "id": 1,
    "title": "Hạ Long - Du Thuyền 5 Sao Sang Trọng",
    "destination_name": "Hạ Long",
    "base_price": 3200000,
    "duration_days": 2,
    "duration_nights": 1,
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
    "next_departure": "2026-10-18",
    "total_available_seats": 12
  }
]
```

### Bước 5: Context Builder -> Clean Compact Text Context
```text
[DANH SÁCH TOUR CÒN CHỖ TRONG HỆ THỐNG]:
1. Tour: Hạ Long - Du Thuyền 5 Sao Sang Trọng
   - Điểm đến: Hạ Long
   - Giá tour: 3.200.000 VNĐ / khách
   - Thời lượng: 2 ngày 1 đêm
   - Phương tiện: Xe Limousine & Du thuyền 5 sao
   - Ngày khởi hành gần nhất: 15/10/2026 (Còn 20 chỗ)
   - Điểm nổi bật: Nghỉ đêm du thuyền 5 sao, chèo kayak hang Sửng Sốt.

2. Tour: Đà Nẵng - Hội An - Bà Nà Hills Cầu Vàng
   - Điểm đến: Đà Nẵng
   - Giá tour: 3.850.000 VNĐ / khách
   - Thời lượng: 3 ngày 2 đêm
   - Phương tiện: Máy bay & Xe du lịch cao cấp
   - Ngày khởi hành gần nhất: 18/10/2026 (Còn 12 chỗ)
   - Điểm nổi bật: Check-in Cầu Vàng Bà Nà Hills, dạo phố cổ Hội An.
```

### Bước 6: Prompt Builder -> Final Prompt to Gemini
```text
Bạn là Trợ lý Tư vấn Tour Du lịch của công ty du lịch TourAI.

QUY TẮC BẮT BUỘC:
1. CHỈ sử dụng thông tin trong mục CONTEXT bên dưới. Tuyệt đối KHÔNG tự sáng tạo ra tour, giá tiền, ngày đi hoặc địa điểm không có trong CONTEXT.
2. Nếu mục CONTEXT không có tour phù hợp, hãy thông báo lịch sự rằng hiện chưa có tour đáp ứng chính xác yêu cầu và hướng dẫn khách hàng thay đổi tiêu chí hoặc liên hệ hotline.
3. Luôn trả lời bằng tiếng Việt thân thiện, nhiệt tình, chuyên nghiệp.
4. Nêu rõ giá tiền, thời lượng và ngày khởi hành còn chỗ để khách hàng dễ lựa chọn.

CONTEXT:
{context}

CÂU HỎI CỦA KHÁCH HÀNG:
"Tôi có khoảng 4 triệu, muốn đi du lịch Hạ Long hoặc Đà Nẵng tầm 2-3 ngày cuối tuần này còn chỗ không?"
```

### Bước 7: Phản hồi cuối cùng gửi tới Client (API Response)
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

