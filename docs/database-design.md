# Tài Liệu Thiết Kế Cơ Sở Dữ Liệu (Database Design Specification)

Tài liệu này đặc tả thiết kế cơ sở dữ liệu quan hệ cho hệ thống TourAI (Đề tài 17) đạt chuẩn chuẩn hóa 3NF, hỗ trợ cả MySQL và SQLite.

---

## 1. Danh sách các thực thể & Bảng dữ liệu

### 1.1 Bảng `users` (Quản lý người dùng & Phân quyền)
Lưu thông tin tài khoản của khách hàng, nhân viên tư vấn, kế toán, hướng dẫn viên và quản trị viên.
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `email` VARCHAR(120) NOT NULL UNIQUE
- `password_hash` VARCHAR(255) NOT NULL
- `full_name` VARCHAR(100) NOT NULL
- `phone` VARCHAR(20) NOT NULL
- `role` VARCHAR(20) NOT NULL DEFAULT 'CUSTOMER' (`ADMIN`, `STAFF`, `ACCOUNTANT`, `GUIDE`, `CUSTOMER`)
- `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP

### 1.2 Bảng `destinations` (Điểm đến du lịch)
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `name` VARCHAR(100) NOT NULL UNIQUE
- `region` VARCHAR(50) NOT NULL (`Miền Bắc`, `Miền Trung`, `Miền Nam`, `Tây Nguyên`, `Quốc tế`)
- `description` TEXT
- `image_url` VARCHAR(255)
- `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP

### 1.3 Bảng `tours` (Thông tin sản phẩm tour)
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `destination_id` INT NOT NULL (FK -> `destinations.id`)
- `title` VARCHAR(200) NOT NULL
- `slug` VARCHAR(220) NOT NULL UNIQUE
- `description` TEXT NOT NULL
- `duration_days` INT NOT NULL DEFAULT 1
- `duration_nights` INT NOT NULL DEFAULT 0
- `base_price` DECIMAL(12,2) NOT NULL
- `transportation` VARCHAR(100) DEFAULT 'Xe du lịch / Máy bay'
- `itinerary_text` TEXT
- `image_url` VARCHAR(255)
- `is_active` BOOLEAN DEFAULT TRUE
- `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP

### 1.4 Bảng `tour_schedules` (Lịch khởi hành & Kiểm soát chỗ)
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `tour_id` INT NOT NULL (FK -> `tours.id`)
- `departure_date` DATE NOT NULL
- `return_date` DATE NOT NULL
- `adult_price` DECIMAL(12,2) NOT NULL
- `child_price` DECIMAL(12,2) NOT NULL
- `total_seats` INT NOT NULL DEFAULT 20
- `available_seats` INT NOT NULL DEFAULT 20
- `status` VARCHAR(20) NOT NULL DEFAULT 'OPEN' (`OPEN`, `FULL`, `CLOSED`, `CANCELLED`)
- `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP

*Ràng buộc toàn vẹn:* `CHECK (available_seats <= total_seats AND available_seats >= 0)`

### 1.5 Bảng `bookings` (Quản lý đơn đặt tour)
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `booking_code` VARCHAR(30) NOT NULL UNIQUE
- `user_id` INT NOT NULL (FK -> `users.id`)
- `schedule_id` INT NOT NULL (FK -> `tour_schedules.id`)
- `customer_name` VARCHAR(100) NOT NULL
- `customer_email` VARCHAR(120) NOT NULL
- `customer_phone` VARCHAR(20) NOT NULL
- `num_adults` INT NOT NULL DEFAULT 1
- `num_children` INT NOT NULL DEFAULT 0
- `total_amount` DECIMAL(12,2) NOT NULL
- `status` VARCHAR(20) NOT NULL DEFAULT 'PENDING' (`PENDING`, `CONFIRMED`, `COMPLETED`, `CANCELLED`)
- `notes` TEXT
- `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP

### 1.6 Bảng `payments` (Lịch sử thanh toán & Đặt cọc)
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `booking_id` INT NOT NULL (FK -> `bookings.id`)
- `amount` DECIMAL(12,2) NOT NULL
- `payment_method` VARCHAR(30) NOT NULL (`CASH`, `BANK_TRANSFER`, `ONLINE_MOCK`)
- `transaction_id` VARCHAR(100)
- `payment_status` VARCHAR(20) NOT NULL DEFAULT 'SUCCESS' (`PENDING`, `SUCCESS`, `FAILED`, `REFUNDED`)
- `payment_date` DATETIME DEFAULT CURRENT_TIMESTAMP

### 1.7 Bảng `tour_guides` (Hồ sơ hướng dẫn viên)
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `full_name` VARCHAR(100) NOT NULL
- `phone` VARCHAR(20) NOT NULL UNIQUE
- `email` VARCHAR(120) NOT NULL UNIQUE
- `languages` VARCHAR(100) DEFAULT 'Tiếng Việt'
- `experience_years` INT DEFAULT 1
- `bio` TEXT
- `is_active` BOOLEAN DEFAULT TRUE

### 1.8 Bảng `guide_assignments` (Phân công hướng dẫn viên theo lịch)
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `schedule_id` INT NOT NULL (FK -> `tour_schedules.id`)
- `guide_id` INT NOT NULL (FK -> `tour_guides.id`)
- `role_in_tour` VARCHAR(50) DEFAULT 'LEAD_GUIDE'
- `notes` TEXT
- `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP

### 1.9 Bảng `feedbacks` (Đánh giá chất lượng sau chuyến đi)
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `user_id` INT NOT NULL (FK -> `users.id`)
- `tour_id` INT NOT NULL (FK -> `tours.id`)
- `booking_id` INT (FK -> `bookings.id`)
- `rating` INT NOT NULL CHECK (rating >= 1 AND rating <= 5)
- `comment` TEXT NOT NULL
- `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP

### 1.10 Bảng `chat_logs` (Nhật ký tư vấn Chatbot)
- `id` INT PRIMARY KEY AUTO_INCREMENT
- `session_id` VARCHAR(100) NOT NULL
- `user_message` TEXT NOT NULL
- `intent_json` TEXT
- `retrieved_tour_ids` VARCHAR(255)
- `bot_response` TEXT NOT NULL
- `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP

---

## 2. Chuẩn hóa dữ liệu (Database Normalization Analysis)
- **1NF (Dạng chuẩn 1):** Mọi thuộc tính đều mang giá trị nguyên tử (atomic), không chứa mảng lồng nhau. Lịch khởi hành và danh sách đặt chỗ được tách thành các bảng độc lập.
- **2NF (Dạng chuẩn 2):** Toàn bộ các bảng đều có khóa chính đơn thuộc tính (`id`), loại bỏ hoàn toàn phụ thuộc một phần vào khóa chính phức hợp.
- **3NF (Dạng chuẩn 3):** Không có phụ thuộc bắc cầu (transitive dependency). Thông tin khách hàng của tài khoản được liên kết qua `user_id`; thông tin điểm đến được liên kết qua `destination_id`.

---

## 3. Chiến lược chỉ mục (Indexing Strategy)

1. `idx_tours_destination` trên `tours(destination_id)`
2. `idx_tours_price` trên `tours(base_price)`
3. `idx_tours_duration` trên `tours(duration_days)`
4. `idx_schedules_lookup` trên `tour_schedules(tour_id, departure_date, available_seats)`
5. `idx_bookings_user` trên `bookings(user_id)`
6. `idx_bookings_schedule` trên `bookings(schedule_id)`
7. `idx_feedbacks_tour` trên `feedbacks(tour_id)`

Các chỉ mục trên tối ưu hóa đặc biệt cho RAG Tour Retriever khi thực hiện câu lệnh lọc:
`WHERE available_seats > 0 AND base_price <= ? AND duration_days = ?`.

