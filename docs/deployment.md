# Triển khai TourAI hiện tại (SQLite, Gunicorn và Nginx)

Tài liệu này phản ánh mã nguồn đang có. `database/db.py` chỉ sử dụng SQLite; dự án **chưa có** backend MySQL, cấu hình `DATABASE_URL` hay Docker deployment. Không dùng các hướng dẫn MySQL cũ cho phiên bản này.

## 1. Điều kiện chạy

- Ubuntu Server có Python 3.10 trở lên và Nginx.
- Một thư mục dữ liệu có quyền ghi cho tiến trình ứng dụng.
- Một worker Gunicorn. SQLite phù hợp cho quy mô nhỏ hoặc demo; tăng nhiều worker ghi đồng thời có thể gây lock database.

## 2. Cài đặt ứng dụng

```bash
sudo apt update
sudo apt install -y python3 python3-venv nginx
sudo useradd --system --create-home --shell /usr/sbin/nologin tourai
sudo mkdir -p /var/www/tourai /var/lib/tourai
sudo chown -R tourai:www-data /var/www/tourai /var/lib/tourai
```

Sao chép mã nguồn vào `/var/www/tourai`, sau đó cài dependency:

```bash
cd /var/www/tourai
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn
```

## 3. Cấu hình biến môi trường và SQLite

Tạo `/var/www/tourai/.env`, thay các giá trị mẫu bằng secret thực tế:

```ini
SECRET_KEY=replace-with-a-long-random-secret
FLASK_DEBUG=0
PORT=5000
SQLITE_DB_PATH=/var/lib/tourai/tour_ai.db
ENABLE_DEMO_QUICK_LOGIN=0
SEED_DEMO_DATA=0

# Tùy chọn: chatbot/sinh nội dung AI sẽ dùng fallback nếu không có key.
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.6-flash
```

`SECRET_KEY` phải được đặt khi triển khai. Giá trị fallback trong mã chỉ dành cho môi trường local/demo và không phù hợp production.

Khởi tạo schema SQLite bằng chính mã ứng dụng:

```bash
cd /var/www/tourai
source venv/bin/activate
python -c "from database.db import init_db; init_db()"
```

Không bật `SEED_DEMO_DATA` trên môi trường chứa dữ liệu thật. Nếu cần dữ liệu minh họa cho môi trường demo riêng, chạy `python database/seeder.py` một lần.

## 4. Systemd và Gunicorn

Tạo `/etc/systemd/system/tourai.service`:

```ini
[Unit]
Description=TourAI Flask application
After=network.target

[Service]
User=tourai
Group=www-data
WorkingDirectory=/var/www/tourai
Environment="PATH=/var/www/tourai/venv/bin"
EnvironmentFile=/var/www/tourai/.env
ExecStart=/var/www/tourai/venv/bin/gunicorn --workers 1 --bind 127.0.0.1:5000 app:app
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

## 6. Sao lưu và vận hành

Sao lưu định kỳ cả cơ sở dữ liệu và ảnh tải lên; hai nơi này đều là dữ liệu người dùng:

```bash
sudo -u tourai mkdir -p /var/backups/tourai
sudo -u tourai cp /var/lib/tourai/tour_ai.db /var/backups/tourai/tour_ai-$(date +%F).db
sudo -u tourai tar -czf /var/backups/tourai/uploads-$(date +%F).tar.gz -C /var/www/tourai/static uploads
```

Kiểm tra log khi có sự cố:

```bash
sudo journalctl -u tourai -f
```

Khi cần quy mô ghi đồng thời lớn hoặc triển khai nhiều instance, cần triển khai và kiểm thử một data-access backend MySQL/PostgreSQL trước; không chỉ thay biến môi trường.
