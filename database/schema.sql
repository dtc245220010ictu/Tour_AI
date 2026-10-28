-- TourAI MySQL 8 schema
-- Character set: utf8mb4. All tables use InnoDB for transactions and foreign keys.

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'CUSTOMER',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_users_role CHECK (role IN ('ADMIN', 'STAFF', 'ACCOUNTANT', 'GUIDE', 'CUSTOMER'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS destinations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    region VARCHAR(50) NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tours (
    id INT AUTO_INCREMENT PRIMARY KEY,
    destination_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(220) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    duration_days INT NOT NULL DEFAULT 1,
    duration_nights INT NOT NULL DEFAULT 0,
    base_price DECIMAL(12, 2) NOT NULL,
    transportation VARCHAR(100) NOT NULL DEFAULT 'Xe du lịch máy lạnh',
    itinerary_text TEXT,
    image_url VARCHAR(255),
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_tours_duration CHECK (duration_days >= 1 AND duration_nights >= 0),
    CONSTRAINT chk_tours_price CHECK (base_price >= 0),
    CONSTRAINT fk_tours_destination FOREIGN KEY (destination_id)
        REFERENCES destinations (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tour_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tour_id INT NOT NULL,
    departure_date DATE NOT NULL,
    return_date DATE NOT NULL,
    adult_price DECIMAL(12, 2) NOT NULL,
    child_price DECIMAL(12, 2) NOT NULL,
    total_seats INT NOT NULL DEFAULT 20,
    available_seats INT NOT NULL DEFAULT 20,
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
    postpone_reason TEXT,
    postponed_at DATETIME NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_schedules_dates CHECK (return_date >= departure_date),
    CONSTRAINT chk_schedules_prices CHECK (adult_price >= 0 AND child_price >= 0),
    CONSTRAINT chk_schedules_capacity CHECK (total_seats > 0 AND available_seats BETWEEN 0 AND total_seats),
    CONSTRAINT chk_schedules_status CHECK (status IN ('OPEN', 'FULL', 'CLOSED', 'CANCELLED', 'POSTPONED')),
    CONSTRAINT fk_schedules_tour FOREIGN KEY (tour_id)
        REFERENCES tours (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_code VARCHAR(30) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    schedule_id INT NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(120) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    num_adults INT NOT NULL DEFAULT 1,
    num_children INT NOT NULL DEFAULT 0,
    total_amount DECIMAL(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_bookings_passengers CHECK (num_adults >= 0 AND num_children >= 0 AND num_adults + num_children > 0),
    CONSTRAINT chk_bookings_total CHECK (total_amount >= 0),
    CONSTRAINT chk_bookings_status CHECK (status IN ('PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED')),
    CONSTRAINT fk_bookings_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_bookings_schedule FOREIGN KEY (schedule_id)
        REFERENCES tour_schedules (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method VARCHAR(30) NOT NULL DEFAULT 'BANK_TRANSFER',
    payment_type VARCHAR(30) NOT NULL DEFAULT 'FULL',
    transaction_id VARCHAR(100),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'SUCCESS',
    payment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verified_by INT NULL,
    verified_at DATETIME NULL,
    notes TEXT,
    CONSTRAINT chk_payments_amount CHECK (amount > 0),
    CONSTRAINT chk_payments_type CHECK (payment_type IN ('DEPOSIT', 'FULL', 'REMAINING', 'REFUND')),
    CONSTRAINT chk_payments_status CHECK (payment_status IN ('PENDING', 'SUCCESS', 'FAILED', 'REFUNDED')),
    CONSTRAINT fk_payments_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (id) ON DELETE CASCADE,
    CONSTRAINT fk_payments_verifier FOREIGN KEY (verified_by)
        REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS refund_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL UNIQUE,
    paid_amount DECIMAL(12, 2) NOT NULL,
    request_amount DECIMAL(12, 2) NOT NULL,
    reason TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    requested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_by INT NULL,
    processed_at DATETIME NULL,
    decision_amount DECIMAL(12, 2) NULL,
    decision_notes TEXT,
    CONSTRAINT chk_refunds_amount CHECK (paid_amount >= 0 AND request_amount > 0 AND request_amount <= paid_amount),
    CONSTRAINT chk_refunds_status CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    CONSTRAINT fk_refunds_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (id) ON DELETE CASCADE,
    CONSTRAINT fk_refunds_processor FOREIGN KEY (processed_by)
        REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tour_guides (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    languages VARCHAR(100) NOT NULL DEFAULT 'Tiếng Việt',
    experience_years INT NOT NULL DEFAULT 1,
    bio TEXT,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_guides_experience CHECK (experience_years >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS guide_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NOT NULL,
    guide_id INT NOT NULL,
    role_in_tour VARCHAR(50) NOT NULL DEFAULT 'LEAD_GUIDE',
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_guide_schedule UNIQUE (schedule_id, guide_id),
    CONSTRAINT fk_assignments_schedule FOREIGN KEY (schedule_id)
        REFERENCES tour_schedules (id) ON DELETE CASCADE,
    CONSTRAINT fk_assignments_guide FOREIGN KEY (guide_id)
        REFERENCES tour_guides (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    tour_id INT NOT NULL,
    booking_id INT NULL,
    rating INT NOT NULL,
    comment TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_feedback_rating CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT fk_feedbacks_user FOREIGN KEY (user_id)
        REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_feedbacks_tour FOREIGN KEY (tour_id)
        REFERENCES tours (id) ON DELETE CASCADE,
    CONSTRAINT fk_feedbacks_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS chat_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    user_message TEXT NOT NULL,
    intent_json JSON NULL,
    retrieved_tour_ids VARCHAR(255),
    bot_response TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tour_expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    schedule_id INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    supplier_name VARCHAR(150),
    invoice_code VARCHAR(50),
    expense_date DATE NOT NULL,
    created_by INT NULL,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_expenses_amount CHECK (amount > 0),
    CONSTRAINT fk_expenses_schedule FOREIGN KEY (schedule_id)
        REFERENCES tour_schedules (id) ON DELETE CASCADE,
    CONSTRAINT fk_expenses_creator FOREIGN KEY (created_by)
        REFERENCES users (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_tours_destination ON tours (destination_id);
CREATE INDEX idx_tours_price ON tours (base_price);
CREATE INDEX idx_tours_duration ON tours (duration_days);
CREATE INDEX idx_schedules_tour ON tour_schedules (tour_id);
CREATE INDEX idx_schedules_lookup ON tour_schedules (tour_id, departure_date, available_seats);
CREATE INDEX idx_bookings_user ON bookings (user_id);
CREATE INDEX idx_bookings_schedule ON bookings (schedule_id);
CREATE INDEX idx_feedbacks_tour ON feedbacks (tour_id);
CREATE INDEX idx_expenses_schedule ON tour_expenses (schedule_id);
CREATE INDEX idx_payments_booking ON payments (booking_id);
CREATE INDEX idx_payments_status ON payments (payment_status);
CREATE INDEX idx_refund_requests_status ON refund_requests (status);
CREATE INDEX idx_refund_requests_booking ON refund_requests (booking_id);
