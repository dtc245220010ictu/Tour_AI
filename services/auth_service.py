"""
Authentication and User Management Service.
Handles registration, secure login, password hashing, and user role lookups.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from database.db import execute_query

class AuthService:
    @staticmethod
    def register_user(email: str, password: str, full_name: str, phone: str, role: str = "CUSTOMER"):
        email = email.strip().lower()
        if not email or not password or not full_name:
            raise ValueError("Vui lòng điền đầy đủ email, mật khẩu và họ tên.")
        
        if len(password) < 6:
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự.")
            
        existing = execute_query(
            "SELECT id FROM users WHERE email = ?;",
            (email,),
            fetch_one=True
        )
        if existing:
            raise ValueError("Email này đã được sử dụng. Vui lòng chọn email khác.")
            
        password_hash = generate_password_hash(password)
        user_id = execute_query(
            """INSERT INTO users (email, password_hash, full_name, phone, role) 
            VALUES (?, ?, ?, ?, ?);""",
            (email, password_hash, full_name.strip(), phone.strip(), role),
            commit=True
        )
        return AuthService.get_user_by_id(user_id)

    @staticmethod
    def login_user(email: str, password: str):
        email = email.strip().lower()
        user = execute_query(
            "SELECT * FROM users WHERE email = ?;",
            (email,),
            fetch_one=True
        )
        if not user:
            return None
        
        if not check_password_hash(user["password_hash"], password):
            return None
            
        return user

    @staticmethod
    def get_user_by_id(user_id: int):
        return execute_query(
            "SELECT id, email, full_name, phone, role, created_at FROM users WHERE id = ?;",
            (user_id,),
            fetch_one=True
        )

    @staticmethod
    def get_user_by_email(email: str):
        return execute_query(
            "SELECT id, email, full_name, phone, role, created_at FROM users WHERE email = ?;",
            (email.strip().lower(),),
            fetch_one=True
        )

    # ==============================================================
    # Quản lý khách hàng (ADMIN: Thêm/Sửa/Xóa; STAFF: Chỉ xem)
    # ==============================================================
    @staticmethod
    def get_all_customers():
        """Danh sách khách hàng (role=CUSTOMER) kèm số đơn đã đặt - dùng cho trang Quản lý khách hàng."""
        return execute_query(
            """SELECT u.id, u.email, u.full_name, u.phone, u.role, u.created_at,
                      COUNT(b.id) AS booking_count
               FROM users u
               LEFT JOIN bookings b ON b.user_id = u.id
               WHERE u.role = 'CUSTOMER'
               GROUP BY u.id
               ORDER BY u.created_at DESC, u.id DESC;""",
            fetch_all=True
        )

    @staticmethod
    def get_customer_by_id(user_id: int):
        """Lấy thông tin một khách hàng; trả về None nếu không phải tài khoản CUSTOMER."""
        return execute_query(
            "SELECT id, email, full_name, phone, role, created_at FROM users WHERE id = ? AND role = 'CUSTOMER';",
            (user_id,),
            fetch_one=True
        )

    @staticmethod
    def update_customer(user_id: int, full_name: str, phone: str, email: str, password: str = ""):
        """ADMIN cập nhật thông tin khách hàng. Không cho phép đổi role qua chức năng này."""
        customer = AuthService.get_customer_by_id(user_id)
        if not customer:
            raise ValueError("Không tìm thấy khách hàng.")

        email = (email or "").strip().lower()
        full_name = (full_name or "").strip()
        phone = (phone or "").strip()
        if not email or not full_name or not phone:
            raise ValueError("Vui lòng điền đầy đủ họ tên, email và số điện thoại.")

        duplicate = execute_query(
            "SELECT id FROM users WHERE email = ? AND id != ?;",
            (email, user_id),
            fetch_one=True
        )
        if duplicate:
            raise ValueError("Email này đã được sử dụng. Vui lòng chọn email khác.")

        if password:
            if len(password) < 6:
                raise ValueError("Mật khẩu phải có ít nhất 6 ký tự.")
            execute_query(
                """UPDATE users SET full_name = ?, phone = ?, email = ?, password_hash = ?
                   WHERE id = ? AND role = 'CUSTOMER';""",
                (full_name, phone, email, generate_password_hash(password), user_id),
                commit=True
            )
        else:
            execute_query(
                """UPDATE users SET full_name = ?, phone = ?, email = ?
                   WHERE id = ? AND role = 'CUSTOMER';""",
                (full_name, phone, email, user_id),
                commit=True
            )
        return AuthService.get_user_by_id(user_id)

    @staticmethod
    def delete_customer(user_id: int):
        """ADMIN xóa khách hàng. Chỉ xóa được tài khoản có role=CUSTOMER."""
        customer = AuthService.get_customer_by_id(user_id)
        if not customer:
            raise ValueError("Không tìm thấy khách hàng.")
        execute_query(
            "DELETE FROM users WHERE id = ? AND role = 'CUSTOMER';",
            (user_id,),
            commit=True
        )
        return True

