"""
Accounting and Finance Routes for TourAI.
Exposes endpoints for cashflow, payment reconciliation, customer debts,
tour operational expenses, P&L reporting, and cancellation refunds.
Restricted to ADMIN and ACCOUNTANT roles.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import roles_required
from services.accounting_service import AccountingService
from services.tour_service import TourService

accounting_bp = Blueprint("accounting", __name__, url_prefix="/accounting")

@accounting_bp.route("/dashboard")
@roles_required("ADMIN", "ACCOUNTANT")
def dashboard():
    cashflow = AccountingService.get_cashflow_summary()
    pending_payments = AccountingService.get_payment_reconciliation_list(status="PENDING")[:5]
    top_debts = AccountingService.get_booking_debt_list()[:5]
    recent_pnl = AccountingService.get_schedule_pnl()[:5]

    return render_template(
        "accounting/dashboard.html",
        cashflow=cashflow,
        pending_payments=pending_payments,
        top_debts=top_debts,
        recent_pnl=recent_pnl
    )

@accounting_bp.route("/transactions")
@roles_required("ADMIN", "ACCOUNTANT")
def transactions():
    status = request.args.get("status")
    payments = AccountingService.get_payment_reconciliation_list(status=status)
    return render_template("accounting/transactions.html", payments=payments, current_status=status)

@accounting_bp.route("/transactions/<int:payment_id>/verify", methods=["POST"])
@roles_required("ADMIN", "ACCOUNTANT")
def verify_transaction(payment_id):
    try:
        AccountingService.confirm_payment(payment_id, accountant_user_id=session["user_id"])
        flash("Đã xác nhận tiền vào tài khoản và duyệt giao dịch thành công!", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("accounting.transactions"))

@accounting_bp.route("/debts")
@roles_required("ADMIN", "ACCOUNTANT")
def debts():
    debt_list = AccountingService.get_booking_debt_list()
    return render_template("accounting/debts.html", debts=debt_list)

@accounting_bp.route("/debts/<int:booking_id>/pay", methods=["POST"])
@roles_required("ADMIN", "ACCOUNTANT")
def record_debt_collection(booking_id):
    amount = request.form.get("amount", 0, type=float)
    payment_method = request.form.get("payment_method", "BANK_TRANSFER")
    notes = request.form.get("notes", "").strip()

    try:
        AccountingService.record_debt_payment(
            booking_id=booking_id,
            amount=amount,
            payment_method=payment_method,
            accountant_user_id=session["user_id"],
            notes=notes
        )
        flash("Đã ghi nhận thanh toán công nợ thành công!", "success")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("accounting.debts"))

@accounting_bp.route("/expenses", methods=["GET", "POST"])
@roles_required("ADMIN", "ACCOUNTANT")
def expenses():
    if request.method == "POST":
        schedule_id = request.form.get("schedule_id", type=int)
        category = request.form.get("category", "OTHER").strip()
        title = request.form.get("title", "").strip()
        amount = request.form.get("amount", 0, type=float)
        supplier_name = request.form.get("supplier_name", "").strip()
        invoice_code = request.form.get("invoice_code", "").strip()
        expense_date = request.form.get("expense_date", "").strip()
        notes = request.form.get("notes", "").strip()

        try:
            AccountingService.record_tour_expense(
                schedule_id=schedule_id,
                category=category,
                title=title,
                amount=amount,
                supplier_name=supplier_name,
                invoice_code=invoice_code,
                expense_date=expense_date,
                created_by=session["user_id"],
                notes=notes
            )
            flash("Đã ghi nhận chi phí vận hành đoàn tour thành công!", "success")
            return redirect(url_for("accounting.expenses", schedule_id=schedule_id))
        except ValueError as e:
            flash(str(e), "danger")

    schedule_id_filter = request.args.get("schedule_id", type=int)
    expense_list = AccountingService.get_tour_expenses(schedule_id=schedule_id_filter)
    schedules = TourService.get_tour_schedules(tour_id=None) if hasattr(TourService, "get_all_schedules") else []

    # Get available schedules for select dropdown
    from database.db import execute_query
    schedules_dropdown = execute_query(
        """SELECT s.id, s.departure_date, s.return_date, t.title AS tour_title
           FROM tour_schedules s
           JOIN tours t ON s.tour_id = t.id
           ORDER BY s.departure_date DESC;""",
        fetch_all=True
    )

    return render_template(
        "accounting/expenses.html",
        expenses=expense_list,
        schedules=schedules_dropdown,
        selected_schedule=schedule_id_filter
    )

@accounting_bp.route("/tours-pnl")
@roles_required("ADMIN", "ACCOUNTANT")
def tours_pnl():
    schedule_id = request.args.get("schedule_id", type=int)
    pnl_data = AccountingService.get_schedule_pnl(schedule_id=schedule_id)
    pnl_records = [pnl_data] if schedule_id and pnl_data else (pnl_data if not schedule_id else [])

    from database.db import execute_query
    schedules_dropdown = execute_query(
        """SELECT s.id, s.departure_date, t.title AS tour_title
           FROM tour_schedules s
           JOIN tours t ON s.tour_id = t.id
           ORDER BY s.departure_date DESC;""",
        fetch_all=True
    )

    return render_template(
        "accounting/pnl_report.html",
        pnl_records=pnl_records,
        schedules=schedules_dropdown,
        selected_schedule=schedule_id
    )

@accounting_bp.route("/refunds", methods=["GET", "POST"])
@roles_required("ADMIN", "ACCOUNTANT")
def refunds():
    if request.method == "POST":
        booking_id = request.form.get("booking_id", type=int)
        refund_amount = request.form.get("refund_amount", 0, type=float)
        notes = request.form.get("notes", "").strip()

        try:
            AccountingService.process_refund(
                booking_id=booking_id,
                refund_amount=refund_amount,
                accountant_user_id=session["user_id"],
                notes=notes
            )
            flash("Đã lập phiếu chi hoàn tiền cho khách hàng thành công!", "success")
        except ValueError as e:
            flash(str(e), "danger")
        return redirect(url_for("accounting.refunds"))

    refund_requests = AccountingService.get_refund_requests()
    return render_template("accounting/refunds.html", refund_requests=refund_requests)

