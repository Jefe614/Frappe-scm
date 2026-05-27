# Copyright (c) 2026, VAPTECH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_days, get_first_day, get_last_day
from datetime import datetime, timedelta
import calendar


class SalesByRep(Document):
    pass


# ─────────────────────────────────────────
# Date Range Utility Functions
# ─────────────────────────────────────────

def get_date_range(date_range_type):
    """
    Returns a tuple of (start_date, end_date) based on the selected date range.
    Supports: Today, Yesterday, This Month, Last Month, Last Week, Last Quarter, Last Year, This Year, Yearly
    """
    today = datetime.now().date()

    if date_range_type == "Today":
        return (today, today)

    elif date_range_type == "Yesterday":
        yesterday = today - timedelta(days=1)
        return (yesterday, yesterday)

    elif date_range_type == "This Month":
        first_day = get_first_day(today)
        return (first_day, today)

    elif date_range_type == "Last Month":
        first_day_this_month = get_first_day(today)
        last_day_prev_month = first_day_this_month - timedelta(days=1)
        first_day_prev_month = get_first_day(last_day_prev_month)
        return (first_day_prev_month, last_day_prev_month)

    elif date_range_type == "Last Week":
        # Last 7 days
        start = today - timedelta(days=7)
        return (start, today)

    elif date_range_type == "Last Quarter":
        # Get the current quarter
        month = today.month
        year = today.year

        # Determine current quarter
        if month <= 3:
            current_quarter = 1
        elif month <= 6:
            current_quarter = 2
        elif month <= 9:
            current_quarter = 3
        else:
            current_quarter = 4

        # Previous quarter
        if current_quarter == 1:
            prev_quarter = 4
            prev_year = year - 1
        else:
            prev_quarter = current_quarter - 1
            prev_year = year

        # Calculate start and end of previous quarter
        quarter_months = {
            1: (1, 3),
            2: (4, 6),
            3: (7, 9),
            4: (10, 12)
        }

        start_month, end_month = quarter_months[prev_quarter]
        start_date = datetime(prev_year, start_month, 1).date()
        last_day_end_month = calendar.monthrange(prev_year, end_month)[1]
        end_date = datetime(prev_year, end_month, last_day_end_month).date()
        return (start_date, end_date)

    elif date_range_type == "Last Year":
        last_year = today.year - 1
        start_date = datetime(last_year, 1, 1).date()
        end_date = datetime(last_year, 12, 31).date()
        return (start_date, end_date)

    elif date_range_type == "This Year":
        start_date = datetime(today.year, 1, 1).date()
        return (start_date, today)

    elif date_range_type == "Yearly":
        # Current year to date
        start_date = datetime(today.year, 1, 1).date()
        return (start_date, today)

    else:
        # Default to This Month
        first_day = get_first_day(today)
        return (first_day, today)


# ─────────────────────────────────────────
# Customer Visit Hooks
# ─────────────────────────────────────────

def refresh_single_sales_by_rep_from_visit(doc, method):
    """Update Sales By Rep when a Customer Visit is saved/cancelled.
    Updates records for all relevant date ranges."""
    sales_person = doc.get("sales_person")
    if sales_person:
        # Update for all date ranges when a visit changes
        date_ranges = ["Today", "Yesterday", "This Month", "Last Month", "Last Week", "Last Quarter", "Last Year", "This Year"]
        for date_range in date_ranges:
            try:
                refresh_single_sales_by_rep(sales_person, date_range)
            except Exception as e:
                frappe.log_error(f"Error updating Sales By Rep for {sales_person} with date range {date_range}: {str(e)}")


# ─────────────────────────────────────────
# Sales Order Hooks
# ─────────────────────────────────────────

def update_sales_by_rep_from_sales_order(doc, method):
    """Update Sales By Rep when a Sales Order is submitted/cancelled.
    Updates records for all relevant date ranges."""
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

    # Update all date ranges for affected sales persons
    date_ranges = ["Today", "Yesterday", "This Month", "Last Month", "Last Week", "Last Quarter", "Last Year", "This Year"]
    for sp_name in sales_person_names:
        for date_range in date_ranges:
            try:
                refresh_single_sales_by_rep(sp_name, date_range)
            except Exception as e:
                frappe.log_error(f"Error updating Sales By Rep for {sp_name} with date range {date_range}: {str(e)}")


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

def refresh_single_sales_by_rep(sales_person_name, date_range="Today"):
    """Refresh one Sales By Rep record with optional date filtering.
    Uses raw SQL UPDATE to avoid ORM hook triggers and lock contention.
    """

    # Get date range based on the selected filter
    start_date, end_date = get_date_range(date_range)

    # 1. Count visits and unique customers (with date filter)
    visits_data = frappe.db.sql("""
        SELECT
            COUNT(DISTINCT cv.name)     AS total_visits,
            COUNT(DISTINCT cv.customer) AS total_customers
        FROM `tabCustomer Visit` cv
        WHERE cv.sales_person = %s
          AND DATE(cv.visit_date) >= %s
          AND DATE(cv.visit_date) <= %s
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
          AND DATE(cv.visit_date) >= %s
          AND DATE(cv.visit_date) <= %s
          AND so.docstatus IN (0, 1)
    """, (sales_person_name, start_date, end_date), as_dict=True)

    data_v = visits_data[0] if visits_data else {}
    data_o = orders_data[0] if orders_data else {}

    # 3. Get targets from Sales Person Target Detail table (always use current fiscal year)
    targets = get_sales_person_targets(sales_person_name)

    # 4. Check if record already exists
    existing = frappe.db.get_value(
        "Sales By Rep", {"sales_person": sales_person_name}, "name"
    )

    if existing:
        # Raw SQL — bypasses hooks and avoids lock wait timeout
        frappe.db.sql("""
            UPDATE `tabSales By Rep`
            SET visits             = %s,
                customers_in_route = %s,
                sales              = %s,
                qty_sold           = %s,
                sales_target       = %s,
                qty_target         = %s,
                date_range         = %s
            WHERE name = %s
        """, (
            data_v.get("total_visits", 0),
            data_v.get("total_customers", 0),
            data_o.get("total_order_amount", 0.0),
            data_o.get("total_order_qty", 0.0),
            targets.get("sales_target", 0.0),
            targets.get("qty_target", 0.0),
            date_range,
            existing
        ))
    else:
        # Insert new record via ORM (only runs once per new sales person)
        doc = frappe.new_doc("Sales By Rep")
        doc.sales_person       = sales_person_name
        doc.date_range         = date_range
        doc.visits             = data_v.get("total_visits", 0)
        doc.customers_in_route = data_v.get("total_customers", 0)
        doc.sales              = data_o.get("total_order_amount", 0.0)
        doc.qty_sold           = data_o.get("total_order_qty", 0.0)
        doc.sales_target       = targets.get("sales_target", 0.0)
        doc.qty_target         = targets.get("qty_target", 0.0)
        doc.insert(ignore_permissions=True)


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


def refresh_sales_by_rep(date_range="Today"):
    """Refresh Sales By Rep for all reps who have Customer Visit data."""
    active_reps = frappe.db.sql("""
        SELECT DISTINCT sales_person
        FROM `tabCustomer Visit`
        WHERE sales_person IS NOT NULL
          AND sales_person != ''
    """, pluck="sales_person")

    for sp in active_reps:
        try:
            refresh_single_sales_by_rep(sp, date_range)
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Sales By Rep refresh failed for {sp}"
            )


def refresh_all_sales_by_rep():
    """Scheduled job entry point."""
    # Refresh for all date ranges to ensure data is current
    date_ranges = ["Today", "Yesterday", "This Month", "Last Month", "Last Week", "Last Quarter", "Last Year", "This Year"]
    for dr in date_ranges:
        try:
            refresh_sales_by_rep(dr)
        except Exception:
            frappe.log_error(frappe.get_traceback(), f"Sales By Rep refresh failed for date range: {dr}")


def ensure_all_sales_people_initialized():
    """Ensure all enabled Sales People have Sales By Rep records for all date ranges.
    Called during installation to bootstrap the system."""

    # Get all enabled Sales People
    all_sales_people = frappe.get_list(
        "Sales Person",
        filters={"enabled": 1},
        fields=["name"],
        pluck="name"
    )

    date_ranges = ["Today", "Yesterday", "This Month", "Last Month", "Last Week", "Last Quarter", "Last Year", "This Year"]

    for sales_person in all_sales_people:
        for date_range in date_ranges:
            try:
                # Check if record exists
                existing = frappe.db.get_value(
                    "Sales By Rep",
                    {"sales_person": sales_person, "date_range": date_range},
                    "name"
                )

                if not existing:
                    # Create record for this date range
                    refresh_single_sales_by_rep(sales_person, date_range)
            except Exception as e:
                frappe.log_error(f"Error initializing Sales By Rep for {sales_person} ({date_range}): {str(e)}")

