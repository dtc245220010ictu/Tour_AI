---
name: context-builder
description: Xây dựng đoạn ngữ cảnh gọn, chính xác, sạch từ bản ghi CSDL phục vụ prompt engineering — loại bỏ các trường không cần thiết và ngăn chặn thao túng dữ liệu.
---
# Skill Context Builder

## Mục tiêu
Chuyển bản ghi CSDL thô thành định dạng văn bản sạch, súc tích, có cấu trúc, được tối ưu riêng cho khả năng hiểu của LLM và bám sát dữ liệu thật (factual grounding).

## Đầu vào
- Danh sách bản ghi tour do `tour_retriever` trả về.

## Đầu ra
- Khối văn bản ngắn gọn, sạch biểu diễn các lựa chọn tour hiện có.

## Quy tắc
- KHÔNG thêm thông tin không có trong CSDL.
- KHÔNG thay đổi giá, giảm giá hoặc số chỗ.
- KHÔNG bịa khách sạn, chuyến bay hoặc chính sách không có thật.
- Định dạng giá theo chuẩn tiền Việt Nam rõ ràng (ví dụ `3.200.000 VNĐ`).
- Chỉ bao gồm các trường thiết yếu: Tên tour, Điểm đến, Thời lượng, Giá, Ngày khởi hành gần nhất, Số chỗ còn trống, Điểm nhấn.
- Nếu danh sách rỗng, xuất chỉ báo rõ ràng: `[KHÔNG TÌM THẤY TOUR NÀO THỎA MÃN TRONG CSDL]`.
