"""
Comprehensive test suite for the Accounting & Finance Module in TourAI.
Tests the 4 accounting pillars:
1. Customer Payments Reconciliation & Debt Tracking
2. Tour Operational Expenses & P&L Calculations
3. Cancellation Refund Policy & Refund Processing
4. Cashflow Summary & Role-Based Access Control (RBAC)
"""

import re
import pytest
from datetime import date, datetime
from database.db import execute_query, get_db
from services.accounting_service import AccountingService
from services.booking_service import BookingService


def _page_text(resp):
    """Decodes an HTML response and collapses whitespace runs to single spaces.

    Template source lines may be wrapped by the IDE formatter, so text nodes can
    contain newlines / extra indentation between words. Normalizing whitespace
    keeps content assertions robust without weakening them.
    """
    return re.sub(r"\s+", " ", resp.data.decode("utf-8"))


def test_record_and_verify_payment():
    """
    Kế toán duyệt giao dịch chuyển khoản:
    - Giao dịch PENDING xuất hiện trong danh sách đối soát.
    - Sau khi xác nhận: payment_status = SUCCESS, verified_by/verified_at được ghi.
    - Booking PENDING chuyển sang CONFIRMED.
    - Duyệt lại lần hai phải báo lỗi.
    """
    booking = BookingService.create_booking(
        user_id=5,
        schedule_id=2,
        customer_name="Test Reconciliation Customer",
        customer_email="recon@test.com",
        customer_phone="0912000111",
        num_adults=1,
        num_children=0
    )
    booking_id = booking["id"]
    total_amount = booking["total_amount"]

    # Insert a pending bank transfer payment (khách báo đã chuyển khoản)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO payments (booking_id, amount, payment_method, payment_type, transaction_id, payment_status, notes)
               VALUES (?, ?, 'BANK_TRANSFER', 'FULL', 'TXN-TEST-RECON-1', 'PENDING', 'Khách báo đã CK');""",
            (booking_id, total_amount)
        )
        payment_id = cursor.lastrowid

    # Payment appears in the pending reconciliation list
    pending_list = AccountingService.get_payment_reconciliation_list(status="PENDING")
    pending_ids = [p["id"] for p in pending_list]
    assert payment_id in pending_ids

    # Accountant (user_id=3) confirms the payment
    res = AccountingService.confirm_payment(payment_id=payment_id, accountant_user_id=3)
    assert res is True

    # Payment is now SUCCESS and verified
    payment = execute_query("SELECT * FROM payments WHERE id = ?;", (payment_id,), fetch_one=True)
    assert payment["payment_status"] == "SUCCESS"
    assert payment["verified_by"] == 3
    assert payment["verified_at"] is not None

    # Booking status was updated to CONFIRMED
    updated_booking = BookingService.get_booking_by_id(booking_id)
    assert updated_booking["status"] == "CONFIRMED"

    # Confirming again should raise ValueError
    with pytest.raises(ValueError) as exc:
        AccountingService.confirm_payment(payment_id=payment_id, accountant_user_id=3)
    assert "đã được xác nhận" in str(exc.value)


def test_debt_calculation():
    """
    Tính công nợ khách hàng khi khách mới đặt cọc một phần:
    Công nợ = Tổng tiền tour - Tiền đã thanh toán thành công.
    """
    # Seeded booking BK-20261002: total 7,700,000, deposit 3,000,000 -> debt 4,700,000
    debt_list = AccountingService.get_booking_debt_list()
    assert len(debt_list) > 0

    target = next((d for d in debt_list if d["booking_code"] == "BK-20261002"), None)
    assert target is not None
    assert target["remaining_debt"] == 4700000
    assert target["paid_amount"] == 3000000
    assert target["debt_status"] == "PARTIAL_PAID"

    # Paying more than remaining debt raises ValueError
    with pytest.raises(ValueError) as exc:
        AccountingService.record_debt_payment(
            booking_id=target["booking_id"],
            amount=5000000,  # greater than 4.7M
            payment_method="BANK_TRANSFER",
            accountant_user_id=3,
            notes="Quá số nợ"
        )
    assert "vượt quá số nợ còn lại" in str(exc.value)

    # Pay partial debt (2,000,000 VND)
    AccountingService.record_debt_payment(
        booking_id=target["booking_id"],
        amount=2000000,
        payment_method="BANK_TRANSFER",
        accountant_user_id=3,
        notes="Khách thanh toán đợt 2"
    )

    # Check updated debt
    debt_list_updated = AccountingService.get_booking_debt_list()
    updated_target = next(d for d in debt_list_updated if d["booking_id"] == target["booking_id"])
    assert updated_target["paid_amount"] == 5000000
    assert updated_target["remaining_debt"] == 2700000


def test_tour_expense_and_pnl():
    """
    Ghi nhận chi phí vận hành tour và kiểm tra công thức P&L:
    Lợi nhuận gộp = Doanh thu - Tổng chi phí; Margin % = Lợi nhuận / Doanh thu * 100.
    """
    today_str = date.today().strftime("%Y-%m-%d")

    # --- Validation ---
    with pytest.raises(ValueError) as exc:
        AccountingService.record_tour_expense(
            schedule_id=1, category="INVALID_CAT", title="Chi phí sai",
            amount=500000, supplier_name="Đối tác", invoice_code="HD-01",
            expense_date=today_str, created_by=3
        )
    assert "Loại chi phí không hợp lệ" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        AccountingService.record_tour_expense(
            schedule_id=1, category="HOTEL", title="Khách sạn âm tiền",
            amount=-100, supplier_name="KS", invoice_code="HD-02",
            expense_date=today_str, created_by=3
        )
    assert "lớn hơn 0" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        AccountingService.record_tour_expense(
            schedule_id=1, category="TRANSPORT", title="   ",
            amount=1000000, supplier_name="Xe", invoice_code="HD-03",
            expense_date=today_str, created_by=3
        )
    assert "Vui lòng nhập tên khoản chi" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        AccountingService.record_tour_expense(
            schedule_id=99999, category="MEAL", title="Ăn uống",
            amount=1000000, supplier_name="Nhà hàng", invoice_code="HD-04",
            expense_date=today_str, created_by=3
        )
    assert "Không tìm thấy lịch khởi hành" in str(exc.value)

    # --- Successful insert ---
    exp_id = AccountingService.record_tour_expense(
        schedule_id=1,
        category="MEAL",
        title="Tiệc gala dinner đêm cuối trên vịnh",
        amount=2500000,
        supplier_name="Nhà hàng Biển Đông",
        invoice_code="HD-GALA-01",
        expense_date=today_str,
        created_by=3,
        notes="Bao gồm rượu vang khai vị"
    )
    assert exp_id is not None

    expenses = AccountingService.get_tour_expenses(schedule_id=1)
    titles = [e["title"] for e in expenses]
    assert "Tiệc gala dinner đêm cuối trên vịnh" in titles

    # --- P&L math consistency for schedule 1 ---
    pnl = AccountingService.get_schedule_pnl(schedule_id=1)
    assert pnl is not None
    assert {"revenue", "expenses", "gross_profit", "profit_margin", "expenses_breakdown"} <= set(pnl.keys())

    assert pnl["gross_profit"] == pnl["revenue"] - pnl["expenses"]
    if pnl["revenue"] > 0:
        expected_margin = round((pnl["gross_profit"] / pnl["revenue"] * 100), 1)
        assert pnl["profit_margin"] == expected_margin

    # Full P&L list (per departure schedule)
    all_pnl = AccountingService.get_schedule_pnl()
    assert isinstance(all_pnl, list)
    assert len(all_pnl) >= 1


def test_cancellation_refund_policy_and_processing():
    """
    Chính sách hoàn tiền theo số ngày trước khởi hành và lập phiếu chi hoàn tiền.
    """
    refunds = AccountingService.get_refund_requests()
    assert len(refunds) >= 1

    # Seeded cancelled booking BK-20261004 (Schedule 1, paid 3,200,000)
    target = next((r for r in refunds if r["booking_code"] == "BK-20261004"), None)
    assert target is not None
    assert target["paid_amount"] == 3200000
    assert target["suggested_percent"] in [90, 50, 0]
    assert target["suggested_amount"] == (3200000 * target["suggested_percent"]) / 100

    # Refund exceeding paid amount must fail
    with pytest.raises(ValueError) as exc:
        AccountingService.process_refund(
            booking_id=target["booking_id"],
            refund_amount=4000000,  # > 3.2M
            accountant_user_id=3,
            notes="Vượt số tiền đã trả"
        )
    assert "không thể vượt quá" in str(exc.value)

    # Successful refund
    refund_val = target["suggested_amount"] if target["suggested_amount"] > 0 else 1000000
    res = AccountingService.process_refund(
        booking_id=target["booking_id"],
        refund_amount=refund_val,
        accountant_user_id=3,
        notes="Hoàn trả qua Vietcombank số TK 001100..."
    )
    assert res is True

    refund_txn = execute_query(
        "SELECT * FROM payments WHERE booking_id = ? AND payment_type = 'REFUND';",
        (target["booking_id"],),
        fetch_one=True
    )
    assert refund_txn is not None
    assert refund_txn["amount"] == refund_val
    assert refund_txn["payment_status"] == "SUCCESS"
    assert refund_txn["verified_by"] == 3

    # Refunding more than the remainder should now fail
    with pytest.raises(ValueError):
        AccountingService.process_refund(
            booking_id=target["booking_id"],
            refund_amount=3200000,
            accountant_user_id=3
        )


def test_cashflow_summary_metrics():
    """
    Sổ quỹ dòng tiền: Tổng thực thu - Tổng thực chi = Tồn quỹ ròng.
    """
    cashflow = AccountingService.get_cashflow_summary()
    assert cashflow["total_inflow"] >= 0
    assert cashflow["total_outflow"] >= 0
    assert cashflow["net_cash"] == cashflow["total_inflow"] - cashflow["total_outflow"]
    assert "total_debts" in cashflow
    assert "pending_payments_count" in cashflow
    assert "pending_refunds_count" in cashflow


def test_unauthorized_access(client):
    """
    RBAC trên các route /accounting/*:
    - Khách ẩn danh: chuyển hướng về /login (302).
    - CUSTOMER / GUIDE: bị từ chối truy cập (302).
    - ACCOUNTANT / ADMIN: 200 OK và render đúng nội dung.
    """
    # 1. Anonymous access
    resp = client.get("/accounting/dashboard")
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]

    resp = client.get("/accounting/expenses")
    assert resp.status_code == 302

    # 2. Customer access (user_id=5, role=CUSTOMER)
    with client.session_transaction() as sess:
        sess["user_id"] = 5
        sess["user_name"] = "Khách Hàng"
        sess["role"] = "CUSTOMER"

    resp = client.get("/accounting/dashboard")
    assert resp.status_code == 302
    assert "/" in resp.headers["Location"]

    resp = client.get("/accounting/tours-pnl")
    assert resp.status_code == 302

    # 3. Guide access (user_id=4, role=GUIDE)
    with client.session_transaction() as sess:
        sess["user_id"] = 4
        sess["user_name"] = "Hướng Dẫn Viên"
        sess["role"] = "GUIDE"

    resp = client.get("/accounting/debts")
    assert resp.status_code == 302

    # 4. Accountant access (user_id=3, role=ACCOUNTANT)
    with client.session_transaction() as sess:
        sess["user_id"] = 3
        sess["user_name"] = "Kế Toán Viên"
        sess["role"] = "ACCOUNTANT"

    resp = client.get("/accounting/dashboard")
    assert resp.status_code == 200
    assert "Quản Lý Kế Toán & Tài Chính" in _page_text(resp)

    resp = client.get("/accounting/transactions")
    assert resp.status_code == 200
    assert "Đối Soát Thanh Toán" in _page_text(resp)

    resp = client.get("/accounting/debts")
    assert resp.status_code == 200
    assert "Quản Lý Công Nợ" in _page_text(resp)

    resp = client.get("/accounting/expenses")
    assert resp.status_code == 200
    assert "Sổ Chi Phí Vận Hành" in _page_text(resp)

    resp = client.get("/accounting/tours-pnl")
    assert resp.status_code == 200
    assert "Báo Cáo Lợi Nhuận (P&L)" in _page_text(resp)

    resp = client.get("/accounting/refunds")
    assert resp.status_code == 200
    assert "Quản Lý Hoàn Tiền Khi Hủy Tour" in _page_text(resp)

    # 5. Admin access (user_id=1, role=ADMIN)
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_name"] = "Quản Trị Viên"
        sess["role"] = "ADMIN"

    resp = client.get("/accounting/dashboard")
    assert resp.status_code == 200