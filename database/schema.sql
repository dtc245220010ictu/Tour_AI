-- ==========================================================
-- Schema Database cho Hệ Thống Quản Lý Tour Du Lịch (TourAI)
-- Đề tài 17: Hệ thống quản lý tour du lịch có tích hợp AI
-- Tương thích: MySQL 8.0+ và SQLite 3
-- ==========================================================

-- 1. Bảng USERS (Quản lý người dùng và phân quyền)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'CUSTOMER', -- 'ADMIN', 'STAFF', 'ACCOUNTANT', 'GUIDE', 'CUSTOMER'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Bảng DESTINATIONS (Điểm đến du lịch)
CREATE TABLE IF NOT EXISTS destinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    region VARCHAR(50) NOT NULL, -- 'Miền Bắc', 'Miền Trung', 'Miền Nam', 'Tây Nguyên', 'Quốc tế'
    description TEXT,
    image_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bảng TOURS (Sản phẩm tour du lịch)
CREATE TABLE IF NOT EXISTS tours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(220) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    duration_days INTEGER NOT NULL DEFAULT 1,
    duration_nights INTEGER NOT NULL DEFAULT 0,
    base_price DECIMAL(12, 2) NOT NULL,
    transportation VARCHAR(100) DEFAULT 'Xe du lịch máy lạnh',
    itinerary_text TEXT,
    image_url VARCHAR(255),
    is_active INTEGER DEFAULT 1, -- 1: Active, 0: Inactive
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (destination_id) REFERENCES destinations (id) ON DELETE RESTRICT
);

-- 4. Bảng TOUR_SCHEDULES (Lịch khởi hành & Kiểm soát số chỗ)
CREATE TABLE IF NOT EXISTS tour_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id INTEGER NOT NULL,
    departure_date DATE NOT NULL,
    return_date DATE NOT NULL,
    adult_price DECIMAL(12, 2) NOT NULL,
    child_price DECIMAL(12, 2) NOT NULL,
    total_seats INTEGER NOT NULL DEFAULT 20,
    available_seats INTEGER NOT NULL DEFAULT 20,
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN', -- 'OPEN', 'FULL', 'CLOSED', 'CANCELLED'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tour_id) REFERENCES tours (id) ON DELETE CASCADE,
    CHECK (available_seats >= 0 AND available_seats <= total_seats)
);

-- 5. Bảng BOOKINGS (Đơn đặt tour)
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_code VARCHAR(30) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    schedule_id INTEGER NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(120) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    num_adults INTEGER NOT NULL DEFAULT 1,
    num_children INTEGER NOT NULL DEFAULT 0,
    total_amount DECIMAL(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED'
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES tour_schedules (id) ON DELETE RESTRICT
);

-- 6. Bảng PAYMENTS (Thanh toán & Đặt cọc)
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method VARCHAR(30) NOT NULL DEFAULT 'BANK_TRANSFER', -- 'CASH', 'BANK_TRANSFER', 'ONLINE'
    transaction_id VARCHAR(100),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'SUCCESS', -- 'PENDING', 'SUCCESS', 'FAILED', 'REFUNDED'
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings (id) ON DELETE CASCADE
);

-- 7. Bảng TOUR_GUIDES (Hồ sơ hướng dẫn viên)
CREATE TABLE IF NOT EXISTS tour_guides (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    languages VARCHAR(100) DEFAULT 'Tiếng Việt',
    experience_years INTEGER DEFAULT 1,
    bio TEXT,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 8. Bảng GUIDE_ASSIGNMENTS (Phân công hướng dẫn viên)
CREATE TABLE IF NOT EXISTS guide_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER NOT NULL,
    guide_id INTEGER NOT NULL,
    role_in_tour VARCHAR(50) DEFAULT 'LEAD_GUIDE',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (schedule_id) REFERENCES tour_schedules (id) ON DELETE CASCADE,
    FOREIGN KEY (guide_id) REFERENCES tour_guides (id) ON DELETE RESTRICT
);

-- 9. Bảng FEEDBACKS (Đánh giá sau chuyến đi)
CREATE TABLE IF NOT EXISTS feedbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    booking_id INTEGER,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (tour_id) REFERENCES tours (id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES bookings (id) ON DELETE SET NULL
);

-- 10. Bảng CHAT_LOGS (Nhật ký tư vấn AI)
CREATE TABLE IF NOT EXISTS chat_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(100) NOT NULL,
    user_message TEXT NOT NULL,
    intent_json TEXT,
    retrieved_tour_ids VARCHAR(255),
    bot_response TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES TỐI ƯU HÓA TÌM KIẾM VÀ RETRIEVAL CỦA RAG CHATBOT
CREATE INDEX IF NOT EXISTS idx_tours_destination ON tours (destination_id);
CREATE INDEX IF NOT EXISTS idx_tours_price ON tours (base_price);
CREATE INDEX IF NOT EXISTS idx_tours_duration ON tours (duration_days);
CREATE INDEX IF NOT EXISTS idx_schedules_tour ON tour_schedules (tour_id);
CREATE INDEX IF NOT EXISTS idx_schedules_lookup ON tour_schedules (tour_id, departure_date, available_seats);
CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings (user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_schedule ON bookings (schedule_id);
CREATE INDEX IF NOT EXISTS idx_feedbacks_tour ON feedbacks (tour_id);

