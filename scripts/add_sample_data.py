"""
Add realistic starter business data to TourAI (without touching existing data).

Adds exactly 10 items per category:
- 10 new destinations (Nha Trang, Hội An, Huế, ...)
- 10 new tours (one per new destination) + one departure schedule each
- 10 new CUSTOMER accounts (password: khachhang123)
- 10 bookings: 5 CONFIRMED, 2 PENDING, 3 CANCELLED - with linked payments
  (verified deposits/full payments, one pending transfer, two 90% refunds)
- 8 tour guides (biển, di sản, trekking...) + 10 LEAD_GUIDE assignments
  (sample schedules are 7 days apart -> no overlapping dates)

Idempotent: rows are detected by natural keys (name / slug / email / booking_code),
so re-running never duplicates or overwrites your real data.

Usage: python scripts/add_sample_data.py
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from werkzeug.security import generate_password_hash

from database.db import get_db, init_db
from services.tour_service import generate_slug

CUSTOMER_PASSWORD = "khachhang123"

IMG_CYCLE = [
    "https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1589394815804-964ed0be2eb5?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1570789210967-2cac24afeb00?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=800&q=80",
]

DESTINATIONS = [
    ("Nha Trang", "Miền Trung", "Thành phố biển với bãi tắm trong xanh, tháp Bà Ponagar và ẩm thực hải sản tuyệt vời."),
    ("Hội An", "Miền Trung", "Phố cổ đèn lồng yên bình bên sông Hoài, thương cảng một thời của thương thuyền Đông Nam Á."),
    ("Huế", "Miền Trung", "Cố đô với Kinh Thành Imperial, Đại Nội và lăng tẩm triều Nguyễn bên sông Hương."),
    ("Ninh Bình", "Miền Bắc", "Tràng An, Tam Cốc và Hang Múa - vịnh trên cỏ xanh tuyệt đẹp miền Bắc."),
    ("Quy Nhơn", "Miền Trung", "Bãi biển Kỳ Co, Eo Gió hùng vĩ và ghềnh đá Đĩa độc đáo của xứ Bình Định."),
    ("Phú Yên", "Miền Trung", "Gành Đá Đĩa, Mũi Đại Lãnh và cánh đồng Cỏ Mây - xứ hoa vàng trên cỏ xanh."),
    ("Vũng Tàu", "Miền Nam", "Thành phố biển gần Sài Gòn với Bạch Dinh, tượng Chúa Kitõ và hải sản tươi sống."),
    ("Côn Đảo", "Miền Nam", "Quần đảo thiêng liêng với hệ sinh thái hoang sơ, bãi Đầm Trầu và núi Non Nước."),
    ("Mộc Châu", "Miền Bắc", "Cao nguyên chè và hoa anh đào, bản làng người Mông và rừng thông Yên Môn."),
    ("Buôn Ma Thuột", "Tây Nguyên", "Thủ phủ cà phê với Thác Dray Nur, Hồ Lák và văn hóa cồng chiêng Tây Nguyên."),
]

# (dest_name, title, duration_days, duration_nights, base_price, transportation, description, itinerary)
TOURS = [
    ("Nha Trang", "Nha Trang - Bien Xanh Vinpearl 4 Ngay 3 Dem", 4, 3, 4_800_000,
     "Xe du lịch + cano",
     "Trải nghiệm biển Nha Trang trong vắt, vui chơi trọn ngày tại Vinpearl Land, lặn ngắm san hô và thưởng thức hải sản tươi sống.",
     "Ngày 1: TP.HCM/Nội Bài - Nha Trang - Bãi biển\nNgày 2: Vinpearl Land - Cáp treo\nNgày 3: Tháp Bà Ponagar - Hòn Chồng\nNgày 4: Chợ Đầm - Trở về"),
    ("Hội An", "Pho Co Ho An - Ngu Hanh Son 3 Ngay 2 Dem", 3, 2, 3_500_000,
     "Xe du lịch máy lạnh",
     "Dạo bước trong phố cổ đèn lồng, thăm Ngũ Hành Sơn và trải nghiệm thuyền thúng trên sông Hoài.",
     "Ngày 1: Đà Nẵng - Ngũ Hành Sơn - Biển An Bàng\nNgày 2: Phố cổ Hội An - Chùa Cầu - Lồng đèn\nNgày 3: Thanh Hà - Trở về"),
    ("Huế", "Co Do Hue - Dai Noi Thien Mu 3 Ngay 2 Dem", 3, 2, 3_200_000,
     "Xe du lịch + thuyền rồng",
     "Khám phá Kinh Thành Huế, Đại Nội, lăng Khải Định và chùa Thiên Mụ bên sông Hương.",
     "Ngày 1: Đại Nội - Chùa Thiên Mụ - Chè Huế\nNgày 2: Lăng Khải Định - Lăng Minh Mạng\nNgày 3: Chợ Đông Ba - Trở về"),
    ("Ninh Bình", "Trang An - Tam Coc Bich Dong 2 Ngay 1 Dem", 2, 1, 1_850_000,
     "Xe limousine 9 chỗ",
     "Chèo thuyền qua các hang xuyên thủy ở Tràng An, thăm Tam Cốc và leo Hang Múa ngắm toàn cảnh.",
     "Ngày 1: Tràng An - Chèo thuyền - Cố Vương Hoa Lư\nNgày 2: Tam Cốc - Hang Múa - Trở về"),
    ("Quy Nhơn", "Quy Nhon - Ky Co - Eo Gio 4 Ngay 3 Dem", 4, 3, 4_200_000,
     "Xe du lịch + cano",
     "Check-in Eo Gió hùng vĩ, tắm biển Kỳ Co trong veo và khám phá Ghềnh Đá Đĩa.",
     "Ngày 1: Quy Nhơn - Ghềnh Đá Đĩa\nNgày 2: Cano Kỳ Co - Eo Gió\nNgày 3: Tháp Đôi - Bãi Xép\nNgày 4: Chợ Quy Nhơn - Trở về"),
    ("Phú Yên", "Phu Yen - Ganh Da Dia - Dai Lanh 3 Ngay 2 Dem", 3, 2, 3_400_000,
     "Xe du lịch máy lạnh",
     "Một thước phim 'Đi để trở về' ngoài đời thực với Gành Đá Đĩa, Mũi Đại Lãnh và Bãi Môn.",
     "Ngày 1: Gành Đá Đĩa - Bãi Xép\nNgày 2: Mũi Đại Lãnh - Bãi Môn - Núi Đá Bia\nNgày 3: Chợ Pond - Trở về"),
    ("Vũng Tàu", "Vung Tau - Bien Duong 2 Ngay 1 Dem", 2, 1, 1_450_000,
     "Xe du lịch 45 chỗ",
     "Nghỉ dưỡng ngắn ngày bên biển, viếng tượng Chúa Kitõ, tham quan Bạch Dinh và ăn hải sản.",
     "Ngày 1: Bạch Dinh - Tượng Chúa - Biển Sao Mai\nNgày 2: Hòn Ngưu - Chợ hải sản - Trở về"),
    ("Côn Đảo", "Con Dao - Vuon Quoc Gia 3 Ngay 2 Dem", 3, 2, 5_600_000,
     "Máy bay + xe du lịch",
     "Khám phá quần đảo hoang sơ với bãi Đầm Trầu, đầm Sen và tìm hiểu lịch sử Côn Đảo.",
     "Ngày 1: Bay tới Côn Đảo - Bãi Đầm Trầu\nNgày 2: Vườn Quốc Gia - Hòn Bảy Cạnh\nNgày 3: Nghĩa Trang Hàng Dương - Trở về"),
    ("Mộc Châu", "Moc Chau - Doi Tra & Thac Dai Yem 3 Ngay 2 Dem", 3, 2, 2_900_000,
     "Xe du lịch 45 chỗ",
     "Mùa hoa cải, đồi chè Mộc Châu và thác Dải Yếm hùng vĩ trên cao nguyên Sơn La.",
     "Ngày 1: Sơn La - Đồi chè Mộc Châu\nNgày 2: Thác Dải Yếm - Bản người Mông\nNgày 3: Rừng thông Yên Môn - Trở về"),
    ("Buôn Ma Thuột", "Tay Nguyen - Dray Nur - Ho Lak 4 Ngay 3 Dem", 4, 3, 3_950_000,
     "Xe du lịch 45 chỗ",
     "Trải nghiệm cà phê Buôn Ma Thuột, thác Dray Nur hùng vĩ và hồ Lák êm ả giữa núi rừng.",
     "Ngày 1: Bảo tàng Cà phê - Làng đan lát\nNgày 2: Thác Dray Nur - Thác Dray Sáp\nNgày 3: Hồ Lák - Buôn Jun\nNgày 4: Chợ cà phê - Trở về"),
]

CUSTOMERS = [
    ("Nguyễn Văn An", "an.nguyen@gmail.com", "0912345678"),
    ("Lê Thị Bích", "bich.le@gmail.com", "0913456789"),
    ("Phạm Quốc Châu", "chau.pham@gmail.com", "0914567890"),
    ("Trần Văn Dũng", "dung.tran@gmail.com", "0915678901"),
    ("Hoàng Thu Hà", "ha.hoang@gmail.com", "0916789012"),
    ("Vũ Tuấn Minh", "minh.vu@gmail.com", "0917890123"),
    ("Đỗ Ngọc Mai", "mai.do@gmail.com", "0918901234"),
    ("Bùi Anh Khoa", "khoa.bui@gmail.com", "0919012345"),
    ("Ngô Thanh Thảo", "thao.ngo@gmail.com", "0910123456"),
    ("Đặng Văn Nam", "nam.dang@gmail.com", "0911234567"),
]

# payments: (payment_type, fraction_of_total, payment_status, verified)
# refunds:  (paid_fraction, refund_ratio) - only for CANCELLED bookings with prior payment
BOOKINGS = [
    dict(code="BK-SMP01", cust="an.nguyen@gmail.com", tour="Nha Trang - Bien Xanh Vinpearl 4 Ngay 3 Dem",
         a=2, c=0, status="CONFIRMED", note="Khách đặt cặp đôi, yêu cầu phòng view biển",
         pays=[("FULL", 1.0, "SUCCESS", True)]),
    dict(code="BK-SMP02", cust="bich.le@gmail.com", tour="Pho Co Ho An - Ngu Hanh Son 3 Ngay 2 Dem",
         a=1, c=1, status="CONFIRMED", note="Gia đình có 1 trẻ em 8 tuổi",
         pays=[("FULL", 1.0, "SUCCESS", True)]),
    dict(code="BK-SMP03", cust="chau.pham@gmail.com", tour="Co Do Hue - Dai Noi Thien Mu 3 Ngay 2 Dem",
         a=2, c=1, status="PENDING", note="Khách báo sẽ chuyển khoản trong hôm nay", pays=[]),
    dict(code="BK-SMP04", cust="dung.tran@gmail.com", tour="Trang An - Tam Coc Bich Dong 2 Ngay 1 Dem",
         a=1, c=0, status="CONFIRMED", note="Đã đặt cọc 50%", pays=[("DEPOSIT", 0.5, "SUCCESS", True)]),
    dict(code="BK-SMP05", cust="ha.hoang@gmail.com", tour="Quy Nhon - Ky Co - Eo Gio 4 Ngay 3 Dem",
         a=3, c=0, status="CONFIRMED", note="Nhóm bạn thân 3 người", pays=[("FULL", 1.0, "SUCCESS", True)]),
    dict(code="BK-SMP06", cust="minh.vu@gmail.com", tour="Phu Yen - Ganh Da Dia - Dai Lanh 3 Ngay 2 Dem",
         a=2, c=2, status="CONFIRMED", note="Khách đã CK, chờ kế toán xác nhận",
         pays=[("FULL", 1.0, "PENDING", False)]),
    dict(code="BK-SMP07", cust="mai.do@gmail.com", tour="Vung Tau - Bien Duong 2 Ngay 1 Dem",
         a=1, c=1, status="CANCELLED", note="Hủy trước 10 ngày - hoàn 90%",
         pays=[("FULL", 1.0, "SUCCESS", True)], refunds=[(1.0, 0.9)]),
    dict(code="BK-SMP08", cust="khoa.bui@gmail.com", tour="Con Dao - Vuon Quoc Gia 3 Ngay 2 Dem",
         a=2, c=0, status="PENDING", note="Đang giữ chỗ 24h chờ thanh toán", pays=[]),
    dict(code="BK-SMP09", cust="thao.ngo@gmail.com", tour="Moc Chau - Doi Tra & Thac Dai Yem 3 Ngay 2 Dem",
         a=1, c=0, status="CANCELLED", note="Hủy sau khi đặt cọc - hoàn 90% tiền cọc",
         pays=[("DEPOSIT", 0.5, "SUCCESS", True)], refunds=[(0.5, 0.9)]),
    dict(code="BK-SMP10", cust="nam.dang@gmail.com", tour="Tay Nguyen - Dray Nur - Ho Lak 4 Ngay 3 Dem",
         a=2, c=1, status="CANCELLED", note="Khách hủy trước khi thanh toán", pays=[]),
]

# 8 tour guides: (full_name, phone, email, languages, experience_years, bio)
GUIDES = [
    ("Lê Văn Hải", "0912111222", "hai.le@tourai.vn", "Tiếng Việt, Tiếng Anh", 5,
     "Nhiệt tình, am hiểu văn hóa vùng biển và di sản miền Trung."),
    ("Nguyễn Thị Mai", "0913333444", "mai.nguyen@tourai.vn", "Tiếng Việt, Tiếng Pháp", 4,
     "Chuyên dẫn các tour biển đảo và nghỉ dưỡng cao cấp."),
    ("Vàng A Súa", "0914555666", "sua.vang@tourai.vn", "Tiếng Việt, Tiếng Mông, Tiếng Anh", 6,
     "Người bản địa am hiểu văn hóa vùng cao và trekking."),
    ("Trần Đình Tuấn", "0915555777", "tuan.tran@tourai.vn", "Tiếng Việt, Tiếng Anh", 7,
     "Kỹ năng tổ chức tốt, chuyên các tour đô thị - di tích lịch sử."),
    ("Phạm Ngọc Lan", "0916666888", "lan.pham@tourai.vn", "Tiếng Việt, Tiếng Nhật", 3,
     "Tươi trẻ, nhiệt huyết, phù hợp nhóm khách gia đình và giới trẻ."),
    ("Đỗ Quang Huy", "0917777999", "huy.do@tourai.vn", "Tiếng Việt, Tiếng Hàn", 5,
     "Am hiểu ẩm thực địa phương, dẫn tốt tour trải nghiệm văn hóa."),
    ("Bùi Thị Kim Ngân", "0918888000", "ngan.bui@tourai.vn", "Tiếng Việt, Tiếng Anh", 4,
     "Chăm sóc khách chu đáo, chuyên tour nghỉ dưỡng."),
    ("Lý A Páo", "0919999111", "pao.ly@tourai.vn", "Tiếng Việt, Tiếng Tày, Tiếng Anh", 8,
     "HDV kỳ cựu, thông thạo trekking và các tuyến đường núi."),
]

# 10 assignments: (tour_title, guide_email, role_in_tour, notes)
# Sample schedules are 7 days apart -> no overlapping dates for any guide.
ASSIGNMENTS = [
    ("Nha Trang - Bien Xanh Vinpearl 4 Ngay 3 Dem", "hai.le@tourai.vn", "LEAD_GUIDE",
     "Dẫn đoàn tour biển Nha Trang"),
    ("Pho Co Ho An - Ngu Hanh Son 3 Ngay 2 Dem", "mai.nguyen@tourai.vn", "LEAD_GUIDE",
     "Dẫn đoàn phố cổ Hội An"),
    ("Co Do Hue - Dai Noi Thien Mu 3 Ngay 2 Dem", "tuan.tran@tourai.vn", "LEAD_GUIDE",
     "Dẫn đoàn di tích Cố Đô Huế"),
    ("Trang An - Tam Coc Bich Dong 2 Ngay 1 Dem", "lan.pham@tourai.vn", "LEAD_GUIDE",
     "Dẫn đoàn Ninh Bình (nhóm gia đình)"),
    ("Quy Nhon - Ky Co - Eo Gio 4 Ngay 3 Dem", "huy.do@tourai.vn", "LEAD_GUIDE",
     "Dẫn đoàn Quy Nhơn - ẩm thực Bình Định"),
    ("Phu Yen - Ganh Da Dia - Dai Lanh 3 Ngay 2 Dem", "ngan.bui@tourai.vn", "LEAD_GUIDE",
     "Dẫn đoàn Phú Yên"),
    ("Vung Tau - Bien Duong 2 Ngay 1 Dem", "lan.pham@tourai.vn", "LEAD_GUIDE",
     "Dẫn đoàn Vũng Tàu (cuối tuần)"),
    ("Con Dao - Vuon Quoc Gia 3 Ngay 2 Dem", "mai.nguyen@tourai.vn", "LEAD_GUIDE",
     "Dẫn đoàn Côn Đảo"),
    ("Moc Chau - Doi Tra & Thac Dai Yem 3 Ngay 2 Dem", "sua.vang@tourai.vn", "LEAD_GUIDE",
     "Dẫn đoàn Mộc Châu - am hiểu người Mông"),
    ("Tay Nguyen - Dray Nur - Ho Lak 4 Ngay 3 Dem", "pao.ly@tourai.vn", "LEAD_GUIDE",
     "Dẫn đoàn Tây Nguyên - văn hóa cồng chiêng"),
]


def main():
    init_db()
    stats = {"destinations": 0, "tours": 0, "schedules": 0, "customers": 0,
             "bookings": 0, "payments": 0, "refunds": 0,
             "guides": 0, "assignments": 0}

    with get_db() as conn:
        cur = conn.cursor()

        # --- 10 destinations ---
        for i, (name, region, desc) in enumerate(DESTINATIONS):
            cur.execute("SELECT id FROM destinations WHERE name = ?;", (name,))
            if cur.fetchone():
                continue
            cur.execute(
                "INSERT INTO destinations (name, region, description, image_url) VALUES (?, ?, ?, ?);",
                (name, region, desc, IMG_CYCLE[i % len(IMG_CYCLE)]),
            )
            stats["destinations"] += 1

        # --- 10 tours (+ 1 future schedule each; price linked: NL = base, TE = 70%) ---
        base_departure = date(2026, 10, 5)
        tour_ids = {}
        for i, (dest_name, title, days, nights, price, transport, desc, itinerary) in enumerate(TOURS):
            cur.execute("SELECT id FROM destinations WHERE name = ?;", (dest_name,))
            dest = cur.fetchone()
            if not dest:
                print(f"SKIP tour (missing destination): {dest_name}")
                continue
            slug = generate_slug(title)
            cur.execute("SELECT id FROM tours WHERE slug = ?;", (slug,))
            row = cur.fetchone()
            if row:
                tour_id = row["id"]
            else:
                cur.execute(
                    """INSERT INTO tours
                       (destination_id, title, slug, description, duration_days, duration_nights,
                        base_price, transportation, itinerary_text, image_url, is_active)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1);""",
                    (dest["id"], title, slug, desc, days, nights,
                     price, transport, itinerary, IMG_CYCLE[i % len(IMG_CYCLE)]),
                )
                tour_id = cur.lastrowid
                stats["tours"] += 1
            tour_ids[title] = tour_id

            cur.execute("SELECT id FROM tour_schedules WHERE tour_id = ?;", (tour_id,))
            if not cur.fetchone():
                dep = base_departure + timedelta(days=i * 7)
                ret = dep + timedelta(days=days - 1)
                cur.execute(
                    """INSERT INTO tour_schedules
                       (tour_id, departure_date, return_date, adult_price, child_price,
                        total_seats, available_seats, status)
                       VALUES (?, ?, ?, ?, ?, 20, 20, 'OPEN');""",
                    (tour_id, dep.isoformat(), ret.isoformat(), price, round(price * 0.7)),
                )
                stats["schedules"] += 1

        # --- 10 customers ---
        pw_hash = generate_password_hash(CUSTOMER_PASSWORD)
        cust_ids = {}
        for name, email, phone in CUSTOMERS:
            cur.execute("SELECT id FROM users WHERE email = ?;", (email,))
            row = cur.fetchone()
            if row:
                cust_ids[email] = row["id"]
                continue
            cur.execute(
                "INSERT INTO users (email, password_hash, full_name, phone, role) VALUES (?, ?, ?, ?, 'CUSTOMER');",
                (email, pw_hash, name, phone),
            )
            cust_ids[email] = cur.lastrowid
            stats["customers"] += 1

        # --- 8 guides + 10 assignments to sample schedules ---
        guide_ids = {}
        for gname, gphone, gemail, glangs, gyears, gbio in GUIDES:
            cur.execute("SELECT id FROM tour_guides WHERE email = ?;", (gemail,))
            row = cur.fetchone()
            if row:
                guide_ids[gemail] = row["id"]
                continue
            cur.execute(
                """INSERT INTO tour_guides
                   (full_name, phone, email, languages, experience_years, bio, is_active)
                   VALUES (?, ?, ?, ?, ?, ?, 1);""",
                (gname, gphone, gemail, glangs, gyears, gbio),
            )
            guide_ids[gemail] = cur.lastrowid
            stats["guides"] += 1

        for title, gemail, role, note in ASSIGNMENTS:
            if title not in tour_ids or gemail not in guide_ids:
                print(f"SKIP assignment: {title} / {gemail}")
                continue
            cur.execute(
                "SELECT id FROM tour_schedules WHERE tour_id = ? "
                "ORDER BY departure_date ASC LIMIT 1;",
                (tour_ids[title],),
            )
            sched = cur.fetchone()
            if not sched:
                continue
            cur.execute(
                "SELECT 1 FROM guide_assignments WHERE schedule_id = ? AND guide_id = ?;",
                (sched["id"], guide_ids[gemail]),
            )
            if cur.fetchone():
                continue
            cur.execute(
                """INSERT INTO guide_assignments (schedule_id, guide_id, role_in_tour, notes)
                   VALUES (?, ?, ?, ?);""",
                (sched["id"], guide_ids[gemail], role, note),
            )
            stats["assignments"] += 1

        # --- 10 bookings + linked payments/refunds ---
        seq = 0
        for b in BOOKINGS:
            cur.execute("SELECT id FROM bookings WHERE booking_code = ?;", (b["code"],))
            if cur.fetchone():
                continue
            if b["cust"] not in cust_ids or b["tour"] not in tour_ids:
                print(f"SKIP booking {b['code']}: missing customer/tour")
                continue
            cur.execute(
                """SELECT s.id, s.adult_price, s.child_price
                   FROM tour_schedules s WHERE s.tour_id = ?
                   ORDER BY s.departure_date ASC LIMIT 1;""",
                (tour_ids[b["tour"]],),
            )
            sched = cur.fetchone()
            if not sched:
                print(f"SKIP booking {b['code']}: no schedule")
                continue

            total = b["a"] * sched["adult_price"] + b["c"] * sched["child_price"]
            cur.execute(
                """INSERT INTO bookings
                   (booking_code, user_id, schedule_id, customer_name, customer_email, customer_phone,
                    num_adults, num_children, total_amount, status, notes)
                   VALUES (?, ?, ?, (SELECT full_name FROM users WHERE id = ?),
                           (SELECT email FROM users WHERE id = ?),
                           (SELECT phone FROM users WHERE id = ?), ?, ?, ?, ?, ?);""",
                (b["code"], cust_ids[b["cust"]], sched["id"], cust_ids[b["cust"]],
                 cust_ids[b["cust"]], cust_ids[b["cust"]],
                 b["a"], b["c"], total, b["status"], b["note"]),
            )
            booking_id = cur.lastrowid
            stats["bookings"] += 1

            # seats: only active bookings consume seats (cancelled = no deduction)
            if b["status"] != "CANCELLED":
                cur.execute(
                    "UPDATE tour_schedules SET available_seats = available_seats - ? WHERE id = ?;",
                    (b["a"] + b["c"], sched["id"]),
                )

            seq += 1
            for ptype, frac, pstatus, verified in b.get("pays", []):
                amount = round(round(total * frac))
                cur.execute(
                    """INSERT INTO payments
                       (booking_id, amount, payment_method, payment_type, transaction_id,
                        payment_status, verified_by, verified_at, notes)
                       VALUES (?, ?, 'BANK_TRANSFER', ?, ?, ?, ?, ?, ?);""",
                    (booking_id, amount, ptype, f"TXN-SMP-{seq:02d}", pstatus,
                     3 if verified else None,
                     "2026-09-24 10:00:00" if verified else None,
                     "Thanh toán dữ liệu mẫu - đã đối soát" if verified
                     else "Khách báo đã chuyển khoản, chờ kế toán duyệt"),
                )
                stats["payments"] += 1

            for paid_frac, ratio in b.get("refunds", []):
                amount = round(round(total * paid_frac) * ratio)
                cur.execute(
                    """INSERT INTO payments
                       (booking_id, amount, payment_method, payment_type, transaction_id,
                        payment_status, verified_by, verified_at, notes)
                       VALUES (?, ?, 'BANK_TRANSFER', 'REFUND', ?, 'SUCCESS', 3, ?, ?);""",
                    (booking_id, amount, f"REF-SMP-{seq:02d}", "2026-09-24 10:30:00",
                     f"Hoàn tiền hủy tour theo chính sách {int(ratio * 100)}%"),
                )
                stats["refunds"] += 1

    print("Added:")
    for k, v in stats.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()