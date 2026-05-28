# Copyright (c) 2026, VAPTECH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_days, get_first_day, get_last_day, now
from datetime import datetime, timedelta
import calendar


class SalesByRep(Document):
    pass


def get_today_range():
    """Returns (start_date, end_date) for today."""
    today = datetime.now().date()
    return (today, today)


# ─────────────────────────────────────────
# Customer Visit Hooks
# ─────────────────────────────────────────

def refresh_single_sales_by_rep_from_visit(doc, method):
    """Update Sales By Rep when a Customer Visit is saved/cancelled."""
    sales_person = doc.get("sales_person")
    if sales_person:
        try:
            refresh_single_sales_by_rep(sales_person)
        except Exception as e:
            frappe.log_error(f"Error updating Sales By Rep for {sales_person}: {str(e)}")


# ─────────────────────────────────────────
# Sales Order Hooks
# ─────────────────────────────────────────

def update_sales_by_rep_from_sales_order(doc, method):
    """Update Sales By Rep when a Sales Order is submitted/cancelled."""
    sales_person_names = set()

    # 1. Find sales person via Customer Visit -> order_number link
    cv_sales_person = frappe.db.get_value(
        "Customer Visit",
        {"order_number": doc.name},
        "sales_person"
    )
    if cv_sales_person:
        sales_person_names.add(cv_sales_person)

    # 2. Get sales people from Sales Team child table
    if not sales_person_names and hasattr(doc, "sales_team") and doc.sales_team:
        for member in doc.sales_team:
            if member.sales_person:
                sales_person_names.add(member.sales_person)

    # 3. Final fallback: user -> employee -> sales person
    if not sales_person_names:
        sp = get_sales_person_for_user(frappe.session.user)
        if sp:
            sales_person_names.add(sp)

    for sp_name in sales_person_names:
        try:
            refresh_single_sales_by_rep(sp_name)
        except Exception as e:
            frappe.log_error(f"Error updating Sales By Rep for {sp_name}: {str(e)}")


def get_sales_person_for_user(user):
    """Find Sales Person linked to a User via Employee."""
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    if employee:
        return frappe.db.get_value(
            "Sales Person",
            {"employee": employee, "enabled": 1},
            "name"
        )
    return None


# ─────────────────────────────────────────
# Sales By Rep Aggregation
# ─────────────────────────────────────────

def refresh_single_sales_by_rep(sales_person_name):
    """Refresh one Sales By Rep record for today's data.
    Uses raw SQL UPDATE to avoid ORM hook triggers and lock contention.
    """

    # Get date range for today
    start_date, end_date = get_today_range()

    # 1. Count visits and unique customers (with date filter)
    # NOTE: Field is called "date" in Customer Visit, not "visit_date"
    visits_data = frappe.db.sql("""
        SELECT
            COUNT(DISTINCT cv.name)     AS total_visits,
            COUNT(DISTINCT cv.customer) AS total_customers
        FROM `tabCustomer Visit` cv
        WHERE cv.sales_person = %s
          AND DATE(cv.date) >= %s
          AND DATE(cv.date) <= %s
    """, (sales_person_name, start_date, end_date), as_dict=True)

    # 2. Sum Sales Orders linked via Customer Visit.order_number (with date filter)
    orders_data = frappe.db.sql("""
        SELECT
            COALESCE(SUM(so.grand_total), 0) AS total_order_amount,
            COALESCE(SUM(so.total_qty), 0)   AS total_order_qty
        FROM `tabSales Order` so
        INNER JOIN `tabCustomer Visit` cv
            ON cv.order_number = so.name
        WHERE cv.sales_person = %s
          AND DATE(cv.date) >= %s
          AND DATE(cv.date) <= %s
          AND so.docstatus IN (0, 1)
    """, (sales_person_name, start_date, end_date), as_dict=True)

    data_v = visits_data[0] if visits_data else {}
    data_o = orders_data[0] if orders_data else {}

    # 3. Get targets from Sales Person Target Detail table (always use current fiscal year)
    targets = get_sales_person_targets(sales_person_name)

    # 4. Check if record already exists for this sales person
    existing = frappe.db.get_value(
        "Sales By Rep",
        {"sales_person": sales_person_name},
        "name"
    )

    if existing:
        now_ts = now()
        # Raw SQL — bypasses hooks and avoids lock wait timeout
        # IMPORTANT: manually set modified so the list view detects changes
        frappe.db.sql("""
            UPDATE `tabSales By Rep`
            SET visits             = %s,
                customers_in_route = %s,
                sales              = %s,
                qty_sold           = %s,
                sales_target       = %s,
                qty_target         = %s,
                modified           = %s,
                modified_by        = %s
            WHERE name = %s
        """, (
            data_v.get("total_visits", 0),
            data_v.get("total_customers", 0),
            data_o.get("total_order_amount", 0.0),
            data_o.get("total_order_qty", 0.0),
            targets.get("sales_target", 0.0),
            targets.get("qty_target", 0.0),
            now_ts,
            frappe.session.user,
            existing
        ))
        frappe.db.commit()
    else:
        # Insert new record via ORM (only runs once per new sales person)
        doc = frappe.new_doc("Sales By Rep")
        doc.sales_person       = sales_person_name
        doc.visits             = data_v.get("total_visits", 0)
        doc.customers_in_route = data_v.get("total_customers", 0)
        doc.sales              = data_o.get("total_order_amount", 0.0)
        doc.qty_sold           = data_o.get("total_order_qty", 0.0)
        doc.sales_target       = targets.get("sales_target", 0.0)
        doc.qty_target         = targets.get("qty_target", 0.0)
        doc.insert(ignore_permissions=True)

    # ── Real-time notification to all connected clients ──
    frappe.publish_realtime(
        event="sales_by_rep_updated",
        message={
            "sales_person": sales_person_name,
            "visits": data_v.get("total_visits", 0),
            "customers": data_v.get("total_customers", 0),
            "sales": data_o.get("total_order_amount", 0.0),
            "qty_sold": data_o.get("total_order_qty", 0.0),
        },
        after_commit=True
    )


def get_sales_person_targets(sales_person_name):
    """Get current fiscal year targets for a Sales Person."""
    current_fiscal_year = frappe.db.get_value(
        "Fiscal Year",
        {
            "year_start_date": ("<=", nowdate()),
            "year_end_date":   (">=", nowdate()),
        },
        "name"
    )

    if not current_fiscal_year:
        return {"sales_target": 0.0, "qty_target": 0.0}

    targets = frappe.db.sql("""
        SELECT
            COALESCE(SUM(target_amount), 0) AS total_target_amount,
            COALESCE(SUM(target_qty), 0)    AS total_target_qty
        FROM `tabTarget Detail`
        WHERE parent      = %s
          AND parenttype  = 'Sales Person'
          AND fiscal_year = %s
    """, (sales_person_name, current_fiscal_year), as_dict=True)

    t = targets[0] if targets else {}
    return {
        "sales_target": t.get("total_target_amount", 0.0),
        "qty_target":   t.get("total_target_qty", 0.0),
    }


def refresh_all_sales_by_rep():
    """Refresh Sales By Rep for all reps who have Customer Visit data."""
    active_reps = frappe.db.sql("""
        SELECT DISTINCT sales_person
        FROM `tabCustomer Visit`
        WHERE sales_person IS NOT NULL
          AND sales_person != ''
    """, pluck="sales_person")

    for sp in active_reps:
        try:
            refresh_single_sales_by_rep(sp)
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Sales By Rep refresh failed for {sp}"
            )


def ensure_all_sales_people_initialized():
    """Ensure all enabled Sales People have Sales By Rep records.
    Called during installation to bootstrap the system."""

    # Get all enabled Sales People
    all_sales_people = frappe.get_list(
        "Sales Person",
        filters={"enabled": 1},
        fields=["name"],
        pluck="name"
    )

    for sales_person in all_sales_people:
        try:
            # Check if record exists
            existing = frappe.db.get_value(
                "Sales By Rep",
                {"sales_person": sales_person},
                "name"
            )

            if not existing:
                # Create record for this sales person
                refresh_single_sales_by_rep(sales_person)
        except Exception as e:
            frappe.log_error(f"Error initializing Sales By Rep for {sales_person}: {str(e)}")
