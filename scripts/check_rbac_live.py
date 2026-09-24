"""
Quick live check: verify RBAC changes are active on the running server.
Run: python scripts/check_rbac_live.py
"""
import sys
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar

BASE = "http://127.0.0.1:5000"


def make_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj)), cj


def login(opener, email, password):
    data = urllib.parse.urlencode({"email": email, "password": password}).encode()
    req = urllib.request.Request(f"{BASE}/login", data=data)
    try:
        opener.open(req)
    except urllib.error.HTTPError:
        pass  # redirects handled automatically


def get(opener, path, allow_error=False):
    try:
        resp = opener.open(urllib.request.Request(f"{BASE}{path}"))
        return resp.status, resp.geturl(), resp.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        if allow_error:
            return e.code, e.geturl(), ""
        raise


def main():
    results = []

    # --- STAFF ---
    o, _ = make_opener()
    login(o, "staff@tourai.vn", "staff123")
    code, url, body = get(o, "/admin/dashboard", allow_error=True)
    staff_blocked = "/admin/dashboard" not in url
    results.append(("STAFF bị chặn /admin/dashboard (CN8)", staff_blocked, f"final_url={url}"))

    code, url, body = get(o, "/admin/tours")
    results.append(("STAFF vào được /admin/tours (CN2)", code == 200, f"status={code}"))
    results.append(("STAFF thấy nav trỏ /admin/tours",
                    'href="/admin/tours"' in body and "Quản trị" in body, ""))

    code, url, body = get(o, "/admin/feedbacks", allow_error=True)
    results.append(("STAFF bị chặn /admin/feedbacks (CN7)",
                    "/admin/feedbacks" not in url, f"final_url={url}"))

    # --- ACCOUNTANT ---
    o, _ = make_opener()
    login(o, "accountant@tourai.vn", "accountant123")
    code, url, body = get(o, "/admin/dashboard")
    results.append(("ACCOUNTANT xem được /admin/dashboard (CN8)",
                    code == 200, f"status={code}"))
    results.append(("ACCOUNTANT không thấy bảng 'Đơn Đặt Chỗ Gần Đây'",
                    "Đơn Đặt Chỗ Gần Đây" not in body, ""))
    code, url, body = get(o, "/admin/bookings", allow_error=True)
    results.append(("ACCOUNTANT bị chặn /admin/bookings (CN4)",
                    "/admin/bookings" not in url, f"final_url={url}"))

    # --- ADMIN ---
    o, _ = make_opener()
    login(o, "admin@tourai.vn", "admin123")
    code, url, body = get(o, "/admin/dashboard")
    results.append(("ADMIN vào dashboard bình thường", code == 200, f"status={code}"))
    results.append(("ADMIN thấy bảng 'Đơn Đặt Chỗ Gần Đây'",
                    "Đơn Đặt Chỗ Gần Đây" in body, ""))
    code, url, body = get(o, "/admin/feedbacks")
    results.append(("ADMIN vào được /admin/feedbacks", code == 200, f"status={code}"))

    # --- GUIDE (read-only) ---
    o, _ = make_opener()
    login(o, "guide@tourai.vn", "guide123")
    code, url, body = get(o, "/admin/tours", allow_error=True)
    results.append(("GUIDE bị chặn /admin/tours", "/admin/tours" not in url, f"final_url={url}"))

    # --- GUIDE dedicated interface (CN6) ---
    o, _ = make_opener()
    login(o, "guide@tourai.vn", "guide123")
    code, url, body = get(o, "/guide/schedule")
    results.append(("GUIDE có trang riêng /guide/schedule", code == 200, f"status={code}"))
    results.append(("GUIDE thấy bảng phân công (HDV đồng nghiệp)", "Lê Văn Hải" in body, ""))
    results.append(("GUIDE thấy nav 'Lịch Phân Công'", "Lịch Phân Công" in body, ""))
    code, url, body = get(o, "/admin/guides", allow_error=True)
    results.append(("GUIDE bị chặn /admin/guides", "/admin/guides" not in url, f"final_url={url}"))

    # --- ADMIN guide management (CN6) ---
    o, _ = make_opener()
    login(o, "admin@tourai.vn", "admin123")
    code, url, body = get(o, "/admin/guides")
    results.append(("ADMIN vào được /admin/guides", code == 200, f"status={code}"))
    results.append(("ADMIN thấy danh sách HDV seed", "Nguyễn Thị Mai" in body, ""))

    # --- STAFF blocked from guide management (CN6) ---
    o, _ = make_opener()
    login(o, "staff@tourai.vn", "staff123")
    code, url, body = get(o, "/admin/guides", allow_error=True)
    results.append(("STAFF bị chặn /admin/guides", "/admin/guides" not in url, f"final_url={url}"))

    # --- CUSTOMER views guides on public tour detail (CN6) ---
    o, _ = make_opener()
    code, url, body = get(o, "/tours/ha-long-du-thuyen-5-sao")
    results.append(("KH xem được HDV ở trang chi tiết tour",
                    code == 200 and "Hướng Dẫn Viên Đồng Hành" in body, ""))

    # --- Print ---
    ok = 0
    for name, passed, extra in results:
        mark = "PASS" if passed else "FAIL"
        if passed:
            ok += 1
        print(f"[{mark}] {name}  {extra}")
    print(f"\n{ok}/{len(results)} checks passed")
    sys.exit(0 if ok == len(results) else 1)


if __name__ == "__main__":
    main()
