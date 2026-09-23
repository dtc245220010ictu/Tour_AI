"""
Database Seeder for TourAI.
Populates initial rich sample data:
- Users with different roles (Admin, Staff, Accountant, Guide, Customer)
- Destinations (Hạ Long, Đà Nẵng, Phú Quốc, Sa Pa, Đà Lạt, Hà Giang)
- Tours with full details, duration, pricing, itinerary
- Tour Schedules with realistic future dates and seats
- Tour Guides & Assignments
- Bookings, Payments, Feedbacks
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from werkzeug.security import generate_password_hash
from database.db import get_db, init_db

def seed_all():
    init_db()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if already seeded
        cursor.execute("SELECT COUNT(*) FROM users;")
        if cursor.fetchone()[0] > 0:
            print("Database already contains data. Skipping seeder.")
            return

        print("Seeding Users...")
        users = [
            ("admin@tourai.vn", generate_password_hash("admin123"), "Nguyễn Quản Trị", "0901234567", "ADMIN"),
            ("staff@tourai.vn", generate_password_hash("staff123"), "Trần Tư Vấn", "0902345678", "STAFF"),
            ("accountant@tourai.vn", generate_password_hash("accountant123"), "Lê Kế Toán", "0903456789", "ACCOUNTANT"),
            ("guide@tourai.vn", generate_password_hash("guide123"), "Phạm Hướng Dẫn", "0904567890", "GUIDE"),
            ("customer@tourai.vn", generate_password_hash("customer123"), "Đỗ Khách Hàng", "0905678901", "CUSTOMER"),
        ]
        cursor.executemany(
            "INSERT INTO users (email, password_hash, full_name, phone, role) VALUES (?, ?, ?, ?, ?);",
            users
        )

        print("Seeding Destinations...")
        destinations = [
            ("Hạ Long", "Miền Bắc", "Kỳ quan thiên nhiên thế giới với hàng ngàn hòn đảo đá vôi kỳ vĩ và vịnh biển xanh ngắt.", "https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=800&q=80"),
            ("Đà Nẵng", "Miền Trung", "Thành phố đáng sống với bãi biển Mỹ Khê, bán đảo Sơn Trà và Bà Nà Hills cổ tích.", "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=800&q=80"),
            ("Phú Quốc", "Miền Nam", "Đảo ngọc thiên đường với những bãi cát trắng mịn, hoàng hôn rực rỡ và lặn ngắm san hô.", "https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?auto=format&fit=crop&w=800&q=80"),
            ("Sa Pa", "Miền Bắc", "Thị trấn trong sương, ruộng bậc thang kỳ vĩ và đỉnh Fansipan nóc nhà Đông Dương.", "https://images.unsplash.com/photo-1570789210967-2cac24afeb00?auto=format&fit=crop&w=800&q=80"),
            ("Đà Lạt", "Tây Nguyên", "Thành phố ngàn hoa với khí hậu mát mẻ quanh năm, rừng thông và hồ Tuyền Lâm thơ mộng.", "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"),
            ("Hà Giang", "Miền Bắc", "Cao nguyên đá Đồng Văn hùng vĩ, đèo Mã Pí Lèng và dòng sông Nho Quế màu xanh ngọc bích.", "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=800&q=80"),
        ]
        cursor.executemany(
            "INSERT INTO destinations (name, region, description, image_url) VALUES (?, ?, ?, ?);",
            destinations
        )

        print("Seeding Tours...")
        tours = [
            (
                1, "Hạ Long - Du Thuyền 5 Sao Sang Trọng", "ha-long-du-thuyen-5-sao",
                "Trải nghiệm nghỉ dưỡng đẳng cấp trên vịnh Hạ Long với du thuyền 5 sao sang trọng, chèo thuyền kayak qua hang Sửng Sốt, ngắm hoàng hôn vịnh biển và tiệc trà chiều cao cấp.",
                2, 1, 3200000, "Xe Limousine & Du thuyền 5 sao",
                "Ngày 1: Hà Nội - Tuần Châu - Vịnh Hạ Long - Thăm Hang Sửng Sốt - Chèo thuyền Kayak - Tiệc Sunset Party.\nNgày 2: Đón bình minh ngắm vịnh - Thăm Hang Luồn - Đảo Ti Tốp - Trả phòng du thuyền - Về lại Hà Nội.",
                "https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=800&q=80", 1
            ),
            (
                2, "Đà Nẵng - Hội An - Bà Nà Hills Cầu Vàng", "da-nang-hoi-an-ba-na-hills",
                "Khám phá thành phố đáng sống nhất Việt Nam: Check-in Cầu Vàng trên mây tại Bà Nà Hills, dạo phố cổ Hội An lung linh đèn lồng và tắm biển Mỹ Khê nước xanh cát trắng.",
                3, 2, 3850000, "Máy bay & Xe du lịch cao cấp",
                "Ngày 1: Đón sân bay Đà Nẵng - Bán đảo Sơn Trà - Chùa Linh Ứng - Tắm biển Mỹ Khê - Phố cổ Hội An về đêm.\nNgày 2: Khám phá Sun World Bà Nà Hills - Trải nghiệm cáp treo đạt kỷ lục - Check-in Cầu Vàng.\nNgày 3: Mua sắm đặc sản Chợ Hàn - Ngũ Hành Sơn - Tiễn sân bay Đà Nẵng.",
                "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=800&q=80", 1
            ),
            (
                3, "Phú Quốc - Thiên Đường Biển Đảo 4 Đảo Cano", "phu-quoc-thien-duong-bien-dao",
                "Hành trình khám phá Đảo Ngọc: Cano siêu tốc tham quan 4 đảo đẹp nhất Hòn Thơm, Hòn Móng Tay, lặn ngắm san hô tự nhiên, check-in Thị trấn Hoàng Hôn Sunset Town và VinWonders.",
                4, 3, 5200000, "Máy bay & Cano siêu tốc",
                "Ngày 1: Đón sân bay Phú Quốc - Check in resort - Ngắm hoàng hôn tại Sanato Beach Club.\nNgày 2: Tour Cano 4 đảo VIP - Lặn ngắm san hô công viên San Hô Namaste - Cáp treo Hòn Thơm.\nNgày 3: Khám phá Grand World Phú Quốc - Thành phố không ngủ - Xem show Tinh hoa Việt Nam.\nNgày 4: Thăm cơ sở nuôi cấy ngọc trai & vườn tiêu - Tiễn sân bay.",
                "https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?auto=format&fit=crop&w=800&q=80", 1
            ),
            (
                4, "Sa Pa - Chinh Phục Đỉnh Fansipan Nóc Nhà Đông Dương", "sa-pa-chinh-phuc-fansipan",
                "Chuyến đi đưa du khách đến xứ sở sương mù: Chinh phục đỉnh Fansipan 3.143m, khám phá bản Cát Cát thơ mộng của người H'Mông, thưởng thức ẩm thực thắng cố và lẩu cá hồi.",
                3, 2, 2800000, "Xe giường nằm VIP Cabin",
                "Ngày 1: Hà Nội đi Sa Pa - Check-in khách sạn trung tâm - Tham quan Bản Cát Cát và Thác Thủy Điện.\nNgày 2: Chinh phục đỉnh Fansipan bằng hệ thống cáp treo 3 dây hiện đại - Viếng quần thể tâm linh trên mây.\nNgày 3: Khám phá Núi Hàm Rồng - Vườn lan Châu Âu - Mua sắm quà lưu niệm - Về Hà Nội.",
                "https://images.unsplash.com/photo-1570789210967-2cac24afeb00?auto=format&fit=crop&w=800&q=80", 1
            ),
            (
                5, "Đà Lạt - Xứ Sở Sương Mù & Vườn Hoa Cẩm Tú Cầu", "da-lat-xu-so-suong-mu",
                "Tận hưởng không khí se lạnh, ngắm đồi chè Cầu Đất săn mây sáng sớm, thưởng thức cà phê ngắm thung lũng đèn lồng và hái dâu tây chín mọng tại vườn.",
                3, 2, 2600000, "Xe Limousine phòng nằm",
                "Ngày 1: TP.HCM - Đà Lạt - Quảng trường Lâm Viên - Hồ Xuân Hương thơ mộng.\nNgày 2: Đồi chè Cầu Đất săn mây - Vườn cẩm tú cầu - Thung lũng Tình Yêu - Chợ đêm Đà Lạt.\nNgày 3: Dinh Bảo Đại - Thiền Viện Trúc Lâm ngắm Hồ Tuyền Lâm - Khởi hành về TP.HCM.",
                "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80", 1
            ),
            (
                6, "Hà Giang - Hùng Vĩ Mã Pí Lèng & Sông Nho Quế", "ha-giang-hung-vi-ma-pi-leng",
                "Cung đường phượt huyền thoại: Vượt dốc Thẩm Mã, thăm Cột cờ Lũng Cú cực Bắc Tổ quốc, chinh phục một trong tứ đại đỉnh đèo Mã Pí Lèng và chèo thuyền hẻm Tu Sản.",
                3, 2, 3400000, "Xe Universe 29 chỗ đời mới",
                "Ngày 1: Hà Nội - Hà Giang - Cổng trời Quản Bạ - Núi Đôi Cô Tiên - Phố Cáo - Đồng Văn.\nNgày 2: Cột cờ Lũng Cú - Dinh Vua Mèo - Chinh phục Đèo Mã Pí Lèng - Du thuyền hẻm vực Tu Sản.\nNgày 3: Chợ phiên Đồng Văn - Làng dệt lanh Lùng Tám - Hà Giang - Về lại Hà Nội.",
                "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=800&q=80", 1
            ),
        ]
        cursor.executemany(
            """INSERT INTO tours 
            (destination_id, title, slug, description, duration_days, duration_nights, base_price, transportation, itinerary_text, image_url, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            tours
        )

        print("Seeding Tour Schedules...")
        schedules = [
            # Hạ Long
            (1, "2026-10-15", "2026-10-16", 3200000, 2240000, 20, 15, "OPEN"),
            (1, "2026-10-25", "2026-10-26", 3400000, 2380000, 20, 5, "OPEN"),
            # Đà Nẵng
            (2, "2026-10-18", "2026-10-20", 3850000, 2695000, 25, 12, "OPEN"),
            (2, "2026-11-05", "2026-11-07", 3950000, 2765000, 25, 0, "FULL"),
            # Phú Quốc
            (3, "2026-10-20", "2026-10-23", 5200000, 3640000, 20, 8, "OPEN"),
            (3, "2026-11-12", "2026-11-15", 5500000, 3850000, 20, 18, "OPEN"),
            # Sa Pa
            (4, "2026-10-16", "2026-10-18", 2800000, 1960000, 20, 10, "OPEN"),
            # Đà Lạt
            (5, "2026-10-22", "2026-10-24", 2600000, 1820000, 20, 14, "OPEN"),
            # Hà Giang
            (6, "2026-10-30", "2026-11-01", 3400000, 2380000, 16, 6, "OPEN"),
        ]
        cursor.executemany(
            """INSERT INTO tour_schedules 
            (tour_id, departure_date, return_date, adult_price, child_price, total_seats, available_seats, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
            schedules
        )

        print("Seeding Tour Guides...")
        guides = [
            ("Lê Văn Hải", "0912111222", "hai.le@tourai.vn", "Tiếng Việt, Tiếng Anh", 5, "Nhiệt tình, am hiểu văn hóa di sản miền Trung và vịnh Hạ Long."),
            ("Nguyễn Thị Mai", "0913333444", "mai.nguyen@tourai.vn", "Tiếng Việt, Tiếng Pháp", 4, "Chuyên viên hướng dẫn các tour biển đảo Phú Quốc và nghỉ dưỡng cao cấp."),
            ("Vàng A Súa", "0914555666", "sua.vang@tourai.vn", "Tiếng Việt, Tiếng Mông, Tiếng Anh", 6, "Người bản địa am hiểu sâu sắc văn hóa vùng cao Sa Pa và Hà Giang."),
        ]
        cursor.executemany(
            "INSERT INTO tour_guides (full_name, phone, email, languages, experience_years, bio) VALUES (?, ?, ?, ?, ?, ?);",
            guides
        )

        print("Seeding Guide Assignments...")
        assignments = [
            (1, 1, "LEAD_GUIDE", "Hướng dẫn chính đoàn khách Hạ Long."),
            (3, 1, "LEAD_GUIDE", "Hướng dẫn chính đoàn khách Đà Nẵng."),
            (5, 2, "LEAD_GUIDE", "Hướng dẫn đoàn cano đảo Phú Quốc."),
            (7, 3, "LEAD_GUIDE", "Hướng dẫn đoàn trekking Fansipan Sa Pa."),
        ]
        cursor.executemany(
            "INSERT INTO guide_assignments (schedule_id, guide_id, role_in_tour, notes) VALUES (?, ?, ?, ?);",
            assignments
        )

        print("Seeding Initial Bookings & Payments...")
        # 1 confirmed booking for customer
        cursor.execute(
            """INSERT INTO bookings 
            (booking_code, user_id, schedule_id, customer_name, customer_email, customer_phone, num_adults, num_children, total_amount, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            ("BK-20261001", 5, 1, "Đỗ Khách Hàng", "customer@tourai.vn", "0905678901", 2, 1, 8640000, "CONFIRMED", "Yêu cầu phòng tầng cao ngắm vịnh")
        )
        booking_id = cursor.lastrowid
        cursor.execute(
            """INSERT INTO payments (booking_id, amount, payment_method, transaction_id, payment_status)
            VALUES (?, ?, ?, ?, ?);""",
            (booking_id, 8640000, "ONLINE_MOCK", "TXN-998877", "SUCCESS")
        )

        print("Seeding Feedbacks...")
        feedbacks = [
            (5, 1, booking_id, 5, "Chuyến đi Hạ Long trên du thuyền 5 sao thực sự tuyệt vời! Phòng ốc sạch sẽ, đồ ăn ngon và hướng dẫn viên rất chu đáo."),
            (5, 2, None, 5, "Bà Nà Hills rất đẹp, check-in Cầu Vàng rất ấn tượng. Phố cổ Hội An buổi tối lung linh, dịch vụ công ty tổ chức rất chu đáo."),
            (5, 3, None, 4, "Tour cano Phú Quốc biển rất trong xanh, ngắm san hô đẹp. Giá cả rất hợp lý so với chất lượng phục vụ."),
            (5, 4, None, 5, "Chinh phục đỉnh Fansipan là trải nghiệm khó quên! Hướng dẫn viên địa phương rất hiểu biết và nhiệt huyết."),
        ]
        cursor.executemany(
            "INSERT INTO feedbacks (user_id, tour_id, booking_id, rating, comment) VALUES (?, ?, ?, ?, ?);",
            feedbacks
        )

        print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_all()
