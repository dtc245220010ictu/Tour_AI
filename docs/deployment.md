# Hướng Dẫn Triển Khai Hệ Thống (Production Deployment Guide) - TourAI

Tài liệu này hướng dẫn chi tiết quy trình đưa ứng dụng **TourAI (Đề tài 17)** lên môi trường máy chủ sản phẩm (Ubuntu Server, Nginx, Gunicorn, MySQL 8).

---

## 1. Yêu Cầu Hạ Tầng Môi Trường
- **Hệ điều hành:** Ubuntu 22.04 LTS hoặc 24.04 LTS.
- **Python:** 3.10 trở lên.
- **Cơ sở dữ liệu:** MySQL 8.0+.
- **Web Server & Reverse Proxy:** Nginx 1.18+.
- **WSGI Application Server:** Gunicorn.

---

## 2. Cài Đặt Cơ Sở Dữ Liệu MySQL Trên Server

1. **Cài đặt MySQL Server:**
   ```bash
   sudo apt update
   sudo apt install -y mysql-server
   sudo mysql_secure_installation
   ```

2. **Tạo CSDL và cấp quyền:**
   ```sql
   CREATE DATABASE tour_ai_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'tourai_user'@'localhost' IDENTIFIED BY 'MatKhauBaoMatCuaBan2026!';
   GRANT ALL PRIVILEGES ON tour_ai_db.* TO 'tourai_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

3. **Nạp Schema và Dữ liệu mẫu:**
   ```bash
   mysql -u tourai_user -p tour_ai_db < database/schema.sql
   ```

---

## 3. Cài Đặt Ứng Dụng & Cấu Hình Biến Môi Trường

1. **Clone mã nguồn:**
   ```bash
   cd /var/www
   git clone https://github.com/your-org/TourAI.git tourai
   cd tourai
   ```

2. **Tạo môi trường ảo và cài đặt thư viện:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install gunicorn pymysql cryptography
   ```

3. **Tạo file `.env` sản phẩm:**
   ```ini
   SECRET_KEY=kHOA_bAO_mAT_pROD_2026_sUPER_sECURE
   FLASK_ENV=production
   FLASK_DEBUG=0
   PORT=5000

   # Kết nối MySQL Production
   DATABASE_URL=mysql+pymysql://tourai_user:MatKhauBaoMatCuaBan2026!@localhost:3306/tour_ai_db
   
   # Google Gemini API Key
   GEMINI_API_KEY=AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   GEMINI_MODEL=gemini-1.5-flash
   ```

---

## 4. Cấu Hình Systemd Service (Quản lý tiến trình chạy ngầm)

Tạo file dịch vụ: `/etc/systemd/system/tourai.service`:
```ini
[Unit]
Description=TourAI Flask Application
After=network.target mysql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/tourai
Environment="PATH=/var/www/tourai/venv/bin"
EnvironmentFile=/var/www/tourai/.env
ExecStart=/var/www/tourai/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 app:app

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Kích hoạt và khởi chạy service:
```bash
sudo systemctl daemon-reload
sudo systemctl start tourai
sudo systemctl enable tourai
sudo systemctl status tourai
```

---

## 5. Cấu Hình Nginx Reverse Proxy & SSL (HTTPS)

1. **Tạo file cấu hình Nginx:** `/etc/nginx/sites-available/tourai.conf`:
   ```nginx
   server {
       listen 80;
       server_name tourai.vn www.tourai.vn;

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
           add_header Cache-Control "public, no-transform";
       }
   }
   ```

2. **Kích hoạt site và kiểm tra cú pháp:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/tourai.conf /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

3. **Cài đặt chứng chỉ SSL miễn phí qua Certbot:**
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d tourai.vn -d www.tourai.vn
   ```

