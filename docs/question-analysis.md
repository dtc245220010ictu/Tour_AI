# Đặc Tả Phân Tích Ý Định Câu Hỏi (Question Analysis Specification)

Tài liệu này quy định cấu trúc dữ liệu và các quy tắc bóc tách ý định người dùng (User Intent) từ ngôn ngữ tự nhiên sang định dạng JSON có cấu trúc.

---

## 1. Cấu trúc JSON Chuẩn (Structured Intent Schema)
```json
{
  "destinations": ["Hạ Long"],
  "min_price": 2000000,
  "max_price": 5000000,
  "duration_days": [2, 3],
  "keywords": ["du thuyền", "nghỉ dưỡng"],
  "sort_by": "price_asc",
  "raw_question": "Tôi muốn đi Hạ Long 2-3 ngày, giá từ 2 đến 5 triệu"
}
```

---

## 2. Quy tắc Chuẩn hóa Dữ liệu (Normalization Rules)
1. **Chuẩn hóa Tiền tệ (VND):**
   - Cụm từ chứa "triệu", "tr", "củ", "m" được nhân với `1,000,000`.
   - Cụm từ chứa "nghìn", "k", "ngàn" được nhân với `1,000`.
   - Tiền tố "dưới", "tối đa", "không quá", "<=" gán vào `max_price`.
   - Tiền tố "trên", "tối thiểu", "từ", ">=" gán vào `min_price`.
   - Khoảng giá "từ X đến Y" / "tầm X - Y" gán `min_price = X, max_price = Y`.
2. **Chuẩn hóa Điểm đến:**
   - So khớp không phân biệt hoa thường và hỗ trợ cả tiếng Việt không dấu:
     - "ha long" -> "Hạ Long"
     - "da nang" -> "Đà Nẵng"
     - "phu quoc" -> "Phú Quốc"
     - "sa pa" / "sapa" -> "Sa Pa"
     - "da lat" / "dalat" -> "Đà Lạt"
     - "ha giang" -> "Hà Giang"
   - Bộ từ điển hiện tại cũng nhận diện Nha Trang, Ninh Bình, Huế, Quy Nhơn,
     Phú Yên, Vũng Tàu, Côn Đảo, Mộc Châu và Buôn Ma Thuột, cùng các tên điểm
     tham quan như Hội An, Fansipan, Đồng Văn, Mã Pí Lèng, Tràng An và Tam Cốc.
3. **Chuẩn hóa Thời lượng:**
   - "2 ngày 1 đêm", "2N1Đ", "2 ngày" -> `duration_days = 2`.
   - "3 ngày 2 đêm", "3N2Đ", "3 ngày" -> `duration_days = 3`.
   - "4 ngày" -> `duration_days = 4`.
   - "2-3 ngày", "từ 2 đến 3 ngày" hoặc "2~3 ngày" ->
     `duration_days = [2, 3]`; truy xuất dùng khoảng bao gồm cả hai đầu mút.
4. **Sở thích & Từ khóa:**
   - Các từ khóa đã hỗ trợ gồm `biển`, `đảo`, `cano`, `du thuyền`, `núi`,
     `săn mây`, `đèo`, `hoa`. Nếu người dùng chưa nêu điểm đến trực tiếp,
     mỗi từ khóa sẽ ánh xạ sang danh sách điểm đến gợi ý trong mã nguồn.
   - `keywords` hiện được dùng để diễn đạt tiêu chí/cung cấp điểm đến gợi ý;
     `TourRetriever` không tạo điều kiện SQL tìm toàn văn theo trường này.
5. **Sắp xếp:**
   - "rẻ nhất", "thấp nhất", "tiết kiệm nhất" -> `sort_by = "price_asc"`.
   - "cao cấp", "sang trọng nhất", "đắt nhất", "VIP nhất" ->
     `sort_by = "price_desc"`.
   - Nếu không có từ khóa sắp xếp, kết quả được xếp theo lịch khởi hành gần
     nhất, rồi theo giá tăng dần.

## 3. Phạm vi intent hiện tại

`QuestionAnalyzer` trả về đúng các khóa `destinations`, `min_price`,
`max_price`, `duration_days`, `keywords`, `sort_by` và `raw_question`.
Không có khóa `regions` hoặc `preferences`; các cụm như "cuối tuần" chưa được
chuyển thành điều kiện ngày khởi hành. Truy xuất chỉ lọc điểm đến, khoảng giá,
thời lượng và sắp xếp; mọi giá trị SQL đều được truyền qua tham số hóa.

