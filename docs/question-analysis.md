# Đặc Tả Phân Tích Ý Định Câu Hỏi (Question Analysis Specification)

Tài liệu này quy định cấu trúc dữ liệu và các quy tắc bóc tách ý định người dùng (User Intent) từ ngôn ngữ tự nhiên sang định dạng JSON có cấu trúc.

---

## 1. Cấu trúc JSON Chuẩn (Structured Intent Schema)
```json
{
  "destinations": ["Hạ Long"],
  "regions": ["Miền Bắc"],
  "min_price": 2000000,
  "max_price": 5000000,
  "duration_days": 3,
  "keywords": ["du thuyền", "nghỉ dưỡng"],
  "sort_by": "price_asc"
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
3. **Chuẩn hóa Thời lượng:**
   - "2 ngày 1 đêm", "2N1Đ", "2 ngày" -> `duration_days = 2`.
   - "3 ngày 2 đêm", "3N2Đ", "3 ngày" -> `duration_days = 3`.
   - "4 ngày" -> `duration_days = 4`.
4. **Sở thích & Từ khóa:**
   - "đi biển", "tắm biển", "đảo" -> thêm từ khóa "biển".
   - "ngắm lúa", "ruộng bậc thang", "săn mây", "leo núi" -> thêm từ khóa "núi", "săn mây".

