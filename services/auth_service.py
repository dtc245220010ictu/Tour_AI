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

