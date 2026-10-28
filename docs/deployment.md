# Triển khai TourAI với MySQL 8, Gunicorn và Nginx

Tài liệu này phản ánh runtime hiện tại: Flask kết nối trực tiếp **MySQL 8** qua `mysql-connector-python`. SQLite không còn là backend của ứng dụng. Trước khi triển khai, cần có một database MySQL và tài khoản ứng dụng có quyền trên database đó.

## 1. Điều kiện chạy

- Ubuntu Server có Python 3.10+, MySQL 8.0+ và Nginx.
- Tài khoản hệ điều hành `tourai` để chạy ứng dụng.
- Tài khoản MySQL riêng cho ứng dụng. Tài khoản bootstrap có quyền tạo database/schema; tài khoản chạy Gunicorn chỉ cần các quyền DML cần thiết sau khi schema đã được khởi tạo. Không dùng tài khoản `root` cho Gunicorn.

## 2. Cài đặt ứng dụng

```bash
sudo apt update
sudo apt install -y python3 python3-venv nginx mysql-server
sudo useradd --system --create-home --shell /usr/sbin/nologin tourai
sudo mkdir -p /var/www/tourai
sudo chown -R tourai:www-data /var/www/tourai
```

Sao chép mã nguồn vào `/var/www/tourai`, sau đó cài dependencies:

```bash
cd /var/www/tourai
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn
```

## 3. Cấu hình MySQL và biến môi trường

Tạo database và tài khoản ứng dụng bằng quản trị viên MySQL. Đổi mật khẩu mẫu trước khi dùng:

```sql
CREATE DATABASE tourai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'tourai_app'@'127.0.0.1' IDENTIFIED BY 'replace-with-a-strong-password';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES
    ON tourai.* TO 'tourai_app'@'127.0.0.1';
FLUSH PRIVILEGES;
```

Tạo `/var/www/tourai/.env` và thay toàn bộ giá trị mẫu:

```ini
SECRET_KEY=replace-with-a-long-random-secret
FLASK_DEBUG=0
PORT=5000
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=tourai_app
MYSQL_PASSWORD=replace-with-a-strong-password
MYSQL_DB=tourai
ENABLE_DEMO_QUICK_LOGIN=0
SEED_DEMO_DATA=0

# Không bắt buộc: thiếu key thì AI dùng fallback an toàn.
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.6-flash
```

Khởi tạo bảng và chỉ mục từ `database/schema.sql`:

```bash
cd /var/www/tourai
source venv/bin/activate
python -c "from database.db import init_db; init_db()"
```

Nếu database chưa tồn tại và tài khoản có quyền tạo database, dùng lệnh sau thay cho lệnh trên:

```bash
python -c "from database.db import create_database_if_missing, init_db; create_database_if_missing(); init_db()"
```

Không bật `SEED_DEMO_DATA` trên môi trường chứa dữ liệu thật. Với môi trường demo riêng, chạy `python database/seeder.py` một lần sau khi khởi tạo schema.

## 4. Systemd và Gunicorn

Tạo `/etc/systemd/system/tourai.service`:

```ini
[Unit]
Description=TourAI Flask application
After=network.target mysql.service

[Service]
User=tourai
Group=www-data
WorkingDirectory=/var/www/tourai
Environment="PATH=/var/www/tourai/venv/bin"
EnvironmentFile=/var/www/tourai/.env
ExecStart=/var/www/tourai/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tourai
sudo systemctl status tourai
```

Số worker phải được điều chỉnh theo CPU, dung lượng MySQL và tải thực tế. Booking vẫn dùng cập nhật có điều kiện trong transaction để bảo vệ số chỗ.

## 5. Nginx reverse proxy

Tạo `/etc/nginx/sites-available/tourai`:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/tourai/static/;
        expires 30d;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/tourai /etc/nginx/sites-enabled/tourai
sudo nginx -t
sudo systemctl reload nginx
```

## 6. Sao lưu, khôi phục và kiểm thử

Sao lưu database bằng `mysqldump` và sao lưu ảnh tải lên. Bảo quản bản sao ở vị trí khác máy chủ:

```bash
sudo mkdir -p /var/backups/tourai
mysqldump --single-transaction --routines --triggers -h 127.0.0.1 -u tourai_app -p tourai > /var/backups/tourai/tourai-$(date +%F).sql
sudo -u tourai tar -czf /var/backups/tourai/uploads-$(date +%F).tar.gz -C /var/www/tourai/static uploads
```

Kiểm thử khôi phục định kỳ vào một database tách biệt, ví dụ `tourai_restore_test`; không khôi phục đè database vận hành.

Để chạy pytest, khai báo `MYSQL_TEST_DB=tourai_test`. Fixture sẽ **xóa và tạo lại** database này ở đầu phiên. Database test phải kết thúc bằng `_test` và tuyệt đối không trỏ tới `tourai`.

Do fixture thực hiện `DROP DATABASE` và `CREATE DATABASE`, chỉ chạy pytest với tài khoản phát triển/test chuyên dụng có quyền đó; không cấp quyền này cho tài khoản Gunicorn production.

```bash
python -m pytest -v
```

Theo dõi log khi có sự cố:

```bash
sudo journalctl -u tourai -f
```
