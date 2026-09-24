"""
Accounting and Financial Management Service for TourAI.
Handles Payment Reconciliation, Customer Debts, Tour Operating Expenses,
P&L (Profit & Loss) by Schedule, and Cashflow Management.
"""

from datetime import datetime, date
from database.db import get_db, execute_query

class AccountingService:
    @staticmethod
    def get_payment_reconciliation_list(status: str | None = None):
        """
        Retrieves payment transactions for accountant review and reconciliation.
        Includes booking details, tour info, and verifier info.
        """
        query = """
            SELECT p.*, b.booking_code, b.customer_name, b.customer_email, b.customer_phone,
                   b.total_amount AS booking_total, b.status AS booking_status,
                   t.title AS tour_title, s.departure_date,
                   u.full_name AS accountant_name
            FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            JOIN tour_schedules s ON b.schedule_id = s.id
            JOIN tours t ON s.tour_id = t.id
            LEFT JOIN users u ON p.verified_by = u.id
        """
        params = []
        if status:
            query += " WHERE p.payment_status = ?"
            params.append(status)
        query += " ORDER BY p.payment_date DESC;"

        return execute_query(query, params, fetch_all=True)

    @staticmethod
    def confirm_payment(payment_id: int, accountant_user_id: int):
        """
        Accountant verifies and confirms a bank transfer/cash payment.
        Updates payment status to SUCCESS and verifies booking.
        """
        with get_db() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM payments WHERE id = ?;", (payment_id,))
            payment = cursor.fetchone()
            if not payment:
                raise ValueError("Không tìm thấy giao dịch thanh toán.")

            if payment["payment_status"] == "SUCCESS":
                raise ValueError("Giao dịch thanh toán này đã được xác nhận trước đó.")

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 1. Update payment status to SUCCESS and set verifier
            cursor.execute(
                """UPDATE payments 
                   SET payment_status = 'SUCCESS', verified_by = ?, verified_at = ?
                   WHERE id = ?;""",
                (accountant_user_id, now_str, payment_id)
            )

            # 2. Check total successful payments for the booking
            booking_id = payment["booking_id"]
            cursor.execute("SELECT * FROM bookings WHERE id = ?;", (booking_id,))
            booking = cursor.fetchone()

            if booking and booking["status"] == "PENDING":
                cursor.execute(
                    """SELECT COALESCE(SUM(amount), 0) AS total_paid
                       FROM payments 
                       WHERE booking_id = ? AND payment_status = 'SUCCESS' AND payment_type != 'REFUND';""",
                    (booking_id,)
                )
                paid_row = cursor.fetchone()
                total_paid = paid_row["total_paid"] if paid_row else 0

                # If paid amount covers or is at least a deposit, confirm the booking
                if total_paid > 0:
                    cursor.execute("UPDATE bookings SET status = 'CONFIRMED' WHERE id = ?;", (booking_id,))

        return True

    @staticmethod
    def get_booking_debt_list():
        """
        Calculates accounts receivable (Công nợ khách hàng) for active bookings.
        Debt = Total Amount - Total Successful Paid Amount.
        """
        query = """
            SELECT b.id AS booking_id, b.booking_code, b.customer_name, b.customer_email,
                   b.customer_phone, b.total_amount, b.status AS booking_status, b.created_at,
                   t.title AS tour_title, s.departure_date, s.return_date,
                   COALESCE(p.paid_amount, 0) AS paid_amount,
                   (b.total_amount - COALESCE(p.paid_amount, 0)) AS remaining_debt
            FROM bookings b
            JOIN tour_schedules s ON b.schedule_id = s.id
            JOIN tours t ON s.tour_id = t.id
            LEFT JOIN (
                SELECT booking_id, SUM(amount) AS paid_amount
                FROM payments
                WHERE payment_status = 'SUCCESS' AND payment_type != 'REFUND'
                GROUP BY booking_id
            ) p ON b.id = p.booking_id
            WHERE b.status IN ('PENDING', 'CONFIRMED')
              AND (b.total_amount - COALESCE(p.paid_amount, 0)) > 0
            ORDER BY remaining_debt DESC, s.departure_date ASC;
        """
        debts = execute_query(query, fetch_all=True)
        for d in debts:
            if d["paid_amount"] > 0:
                d["debt_status"] = "PARTIAL_PAID" # Đã cọc một phần
            else:
                d["debt_status"] = "UNPAID" # Chưa thanh toán đồng nào
        return debts

    @staticmethod
    def record_debt_payment(booking_id: int, amount: float, payment_method: str,
                            accountant_user_id: int, notes: str = ""):
        """
        Records an installment payment against customer debt.
        """
        if amount <= 0:
            raise ValueError("Số tiền thanh toán phải lớn hơn 0.")

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookings WHERE id = ?;", (booking_id,))
            booking = cursor.fetchone()
            if not booking:
                raise ValueError("Không tìm thấy đơn đặt tour.")

            cursor.execute(
                """SELECT COALESCE(SUM(amount), 0) AS total_paid
                   FROM payments 
                   WHERE booking_id = ? AND payment_status = 'SUCCESS' AND payment_type != 'REFUND';""",
                (booking_id,)
            )
            paid_row = cursor.fetchone()
            total_paid = paid_row["total_paid"] if paid_row else 0
            remaining_debt = booking["total_amount"] - total_paid

            if amount > remaining_debt:
                raise ValueError(f"Số tiền thanh toán ({amount:,.0f} đ) không thể vượt quá số nợ còn lại ({remaining_debt:,.0f} đ).")

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            txn_id = f"TXN-REM-{booking['booking_code']}-{int(datetime.now().timestamp())}"

            cursor.execute(
                """INSERT INTO payments 
                (booking_id, amount, payment_method, payment_type, transaction_id, payment_status,
                 payment_date, verified_by, verified_at, notes)
                VALUES (?, ?, ?, 'REMAINING', ?, 'SUCCESS', ?, ?, ?, ?);""",
                (booking_id, amount, payment_method, txn_id, now_str, accountant_user_id, now_str, notes)
            )

            if booking["status"] == "PENDING":
                cursor.execute("UPDATE bookings SET status = 'CONFIRMED' WHERE id = ?;", (booking_id,))

        return True

    @staticmethod
    def record_tour_expense(schedule_id: int, category: str, title: str, amount: float,
                            supplier_name: str, invoice_code: str, expense_date: str,
                            created_by: int, notes: str = ""):
        """
        Records a tour operational expense linked to a specific departure schedule.
        """
        valid_categories = ["HOTEL", "TRANSPORT", "MEAL", "TICKETS", "GUIDE_FEE", "OTHER"]
        if category not in valid_categories:
            raise ValueError(f"Loại chi phí không hợp lệ. Cho phép: {valid_categories}")

        if amount <= 0:
            raise ValueError("Số tiền chi phí phải lớn hơn 0.")

        if not title or not title.strip():
            raise ValueError("Vui lòng nhập tên khoản chi.")

        schedule = execute_query("SELECT id FROM tour_schedules WHERE id = ?;", (schedule_id,), fetch_one=True)
        if not schedule:
            raise ValueError("Không tìm thấy lịch khởi hành đã chọn.")

        return execute_query(
            """INSERT INTO tour_expenses 
            (schedule_id, category, title, amount, supplier_name, invoice_code, expense_date, created_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            (schedule_id, category, title.strip(), amount, supplier_name.strip() if supplier_name else None,
             invoice_code.strip() if invoice_code else None, expense_date, created_by, notes.strip() if notes else None),
            commit=True
        )

    @staticmethod
    def get_tour_expenses(schedule_id: int | None = None):
        """
        Retrieves list of tour expenses with schedule and creator info.
        """
        query = """
            SELECT e.*, t.title AS tour_title, s.departure_date, s.return_date,
                   u.full_name AS creator_name
            FROM tour_expenses e
            JOIN tour_schedules s ON e.schedule_id = s.id
            JOIN tours t ON s.tour_id = t.id
            LEFT JOIN users u ON e.created_by = u.id
        """
        params = []
        if schedule_id:
            query += " WHERE e.schedule_id = ?"
            params.append(schedule_id)
        query += " ORDER BY e.expense_date DESC, e.id DESC;"

        return execute_query(query, params, fetch_all=True)

    @staticmethod
    def get_schedule_pnl(schedule_id: int | None = None):
        """
        Calculates Profit & Loss (P&L) statement per schedule.
        Revenue = Total confirmed successful payments for bookings in this schedule.
        Expenses = Total expenses recorded for this schedule.
        Gross Profit = Revenue - Expenses.
        Margin % = (Gross Profit / Revenue) * 100.
        """
        # Fetch schedules
        sched_query = """
            SELECT s.id AS schedule_id, s.departure_date, s.return_date,
                   s.adult_price, s.child_price, s.total_seats, s.available_seats, s.status,
                   t.id AS tour_id, t.title AS tour_title, d.name AS destination_name
            FROM tour_schedules s
            JOIN tours t ON s.tour_id = t.id
            JOIN destinations d ON t.destination_id = d.id
        """
        params = []
        if schedule_id:
            sched_query += " WHERE s.id = ?"
            params.append(schedule_id)
        sched_query += " ORDER BY s.departure_date DESC;"

        schedules = execute_query(sched_query, params, fetch_all=True)

        pnl_list = []
        for s in schedules:
            sid = s["schedule_id"]
            # 1. Calculate confirmed revenue from bookings in this schedule
            rev_row = execute_query(
                """SELECT COALESCE(SUM(p.amount), 0) AS total_revenue
                   FROM payments p
                   JOIN bookings b ON p.booking_id = b.id
                   WHERE b.schedule_id = ? AND p.payment_status = 'SUCCESS' AND p.payment_type != 'REFUND';""",
                (sid,),
                fetch_one=True
            )
            revenue = rev_row["total_revenue"] if rev_row else 0

            # 2. Calculate expenses grouped by category
            exp_rows = execute_query(
                """SELECT category, COALESCE(SUM(amount), 0) AS cat_total
                   FROM tour_expenses
                   WHERE schedule_id = ?
                   GROUP BY category;""",
                (sid,),
                fetch_all=True
            )
            expenses_by_cat = {row["category"]: row["cat_total"] for row in exp_rows}
            total_expenses = sum(expenses_by_cat.values())

            # 3. P&L metrics
            gross_profit = revenue - total_expenses
            profit_margin = round((gross_profit / revenue * 100), 1) if revenue > 0 else 0
            booked_seats = s["total_seats"] - s["available_seats"]

            pnl_list.append({
                "schedule_id": sid,
                "tour_title": s["tour_title"],
                "destination_name": s["destination_name"],
                "departure_date": s["departure_date"],
                "return_date": s["return_date"],
                "status": s["status"],
                "total_seats": s["total_seats"],
                "booked_seats": booked_seats,
                "revenue": revenue,
                "expenses": total_expenses,
                "expenses_breakdown": expenses_by_cat,
                "gross_profit": gross_profit,
                "profit_margin": profit_margin
            })

        return pnl_list if not schedule_id else (pnl_list[0] if pnl_list else None)

    @staticmethod
    def get_cashflow_summary(from_date: str | None = None, to_date: str | None = None):
        """
        Summarizes Cashflow Journal (Sổ quỹ thu / chi):
        Total Inflow (Thực thu), Total Outflow (Thực chi: expenses + refunds), Net Cash.
        """
        # Inflows: All successful non-refund payments
        inflow_query = "SELECT COALESCE(SUM(amount), 0) AS total_inflow FROM payments WHERE payment_status = 'SUCCESS' AND payment_type != 'REFUND';"
        inflow_row = execute_query(inflow_query, fetch_one=True)
        total_inflow = inflow_row["total_inflow"] if inflow_row else 0

        # Outflows 1: Tour expenses
        exp_query = "SELECT COALESCE(SUM(amount), 0) AS total_expenses FROM tour_expenses;"
        exp_row = execute_query(exp_query, fetch_one=True)
        total_expenses = exp_row["total_expenses"] if exp_row else 0

        # Outflows 2: Refunds
        refund_query = "SELECT COALESCE(SUM(amount), 0) AS total_refunds FROM payments WHERE payment_status = 'SUCCESS' AND payment_type = 'REFUND';"
        refund_row = execute_query(refund_query, fetch_one=True)
        total_refunds = refund_row["total_refunds"] if refund_row else 0

        total_outflow = total_expenses + total_refunds
        net_cash = total_inflow - total_outflow

        # Total accounts receivable (debts)
        debts = AccountingService.get_booking_debt_list()
        total_debts = sum(d["remaining_debt"] for d in debts)

        # Pending items requiring accountant action
        pending_payments_row = execute_query(
            "SELECT COUNT(*) AS count FROM payments WHERE payment_status = 'PENDING';",
            fetch_one=True
        )
        pending_payments_count = pending_payments_row["count"] if pending_payments_row else 0

        pending_refunds_row = execute_query(
            """SELECT COUNT(DISTINCT b.id) AS count 
               FROM bookings b
               JOIN payments p ON b.id = p.booking_id AND p.payment_status = 'SUCCESS' AND p.payment_type != 'REFUND'
               WHERE b.status = 'CANCELLED'
                 AND b.id NOT IN (
                     SELECT DISTINCT booking_id FROM payments WHERE payment_type = 'REFUND' AND payment_status = 'SUCCESS'
                 );""",
            fetch_one=True
        )
        pending_refunds_count = pending_refunds_row["count"] if pending_refunds_row else 0

        return {
            "total_inflow": total_inflow,
            "total_outflow": total_outflow,
            "total_expenses": total_expenses,
            "total_refunds": total_refunds,
            "net_cash": net_cash,
            "total_debts": total_debts,
            "pending_payments_count": pending_payments_count,
            "pending_refunds_count": pending_refunds_count
        }

    @staticmethod
    def get_refund_requests():
        """
        Lists cancelled bookings and calculates suggested refund amounts based on policy.
        Policy:
        - Cancellation >= 7 days before departure: 90% of paid amount.
        - Cancellation 3 to 6 days before departure: 50% of paid amount.
        - Cancellation < 3 days before departure: 0% refund.
        """
        query = """
            SELECT b.id AS booking_id, b.booking_code, b.customer_name, b.customer_email,
                   b.customer_phone, b.total_amount, b.created_at AS booking_date,
                   t.title AS tour_title, s.departure_date,
                   COALESCE(p.paid_amount, 0) AS paid_amount,
                   COALESCE(r.refunded_amount, 0) AS refunded_amount
            FROM bookings b
            JOIN tour_schedules s ON b.schedule_id = s.id
            JOIN tours t ON s.tour_id = t.id
            JOIN (
                SELECT booking_id, SUM(amount) AS paid_amount
                FROM payments
                WHERE payment_status = 'SUCCESS' AND payment_type != 'REFUND'
                GROUP BY booking_id
            ) p ON b.id = p.booking_id
            LEFT JOIN (
                SELECT booking_id, SUM(amount) AS refunded_amount
                FROM payments
                WHERE payment_status = 'SUCCESS' AND payment_type = 'REFUND'
                GROUP BY booking_id
            ) r ON b.id = r.booking_id
            WHERE b.status = 'CANCELLED'
            ORDER BY b.id DESC;
        """
        rows = execute_query(query, fetch_all=True)
        today = date.today()

        for row in rows:
            try:
                dep_date = datetime.strptime(row["departure_date"], "%Y-%m-%d").date()
                days_diff = (dep_date - today).days
            except Exception:
                days_diff = 7

            if days_diff >= 7:
                row["suggested_percent"] = 90
            elif days_diff >= 3:
                row["suggested_percent"] = 50
            else:
                row["suggested_percent"] = 0

            suggested_amount = (row["paid_amount"] * row["suggested_percent"]) / 100
            row["suggested_amount"] = suggested_amount
            row["is_refunded"] = (row["refunded_amount"] > 0)

        return rows

    @staticmethod
    def process_refund(booking_id: int, refund_amount: float, accountant_user_id: int, notes: str = ""):
        """
        Executes refund payout voucher for a cancelled booking.
        """
        if refund_amount <= 0:
            raise ValueError("Số tiền hoàn trả phải lớn hơn 0.")

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookings WHERE id = ?;", (booking_id,))
            booking = cursor.fetchone()
            if not booking:
                raise ValueError("Không tìm thấy đơn đặt tour.")

            if booking["status"] != "CANCELLED":
                raise ValueError("Chỉ có thể hoàn tiền cho các đơn tour đã ở trạng thái CANCELLED.")

            cursor.execute(
                """SELECT COALESCE(SUM(amount), 0) AS total_paid
                   FROM payments 
                   WHERE booking_id = ? AND payment_status = 'SUCCESS' AND payment_type != 'REFUND';""",
                (booking_id,)
            )
            total_paid = cursor.fetchone()["total_paid"]

            cursor.execute(
                """SELECT COALESCE(SUM(amount), 0) AS already_refunded
                   FROM payments 
                   WHERE booking_id = ? AND payment_status = 'SUCCESS' AND payment_type = 'REFUND';""",
                (booking_id,)
            )
            already_refunded = cursor.fetchone()["already_refunded"]

            if refund_amount > (total_paid - already_refunded):
                raise ValueError(f"Số tiền hoàn trả ({refund_amount:,} đ) không thể vượt quá số tiền khách đã trả còn lại ({total_paid - already_refunded:,} đ).")

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            txn_id = f"REF-{booking['booking_code']}-{int(datetime.now().timestamp())}"

            cursor.execute(
                """INSERT INTO payments 
                (booking_id, amount, payment_method, payment_type, transaction_id, payment_status,
                 payment_date, verified_by, verified_at, notes)
                VALUES (?, ?, 'BANK_TRANSFER', 'REFUND', ?, 'SUCCESS', ?, ?, ?, ?);""",
                (booking_id, refund_amount, txn_id, now_str, accountant_user_id, now_str, notes)
            )

        return True
