# Copyright (c) 2026, VAPTECH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, now


class SalesByCustomer(Document):
    pass


# ─────────────────────────────────────────
# Customer Visit Hooks
# ─────────────────────────────────────────

def refresh_sales_by_customer_from_visit(doc, method):
    """Update Sales By Customer when a Customer Visit is saved/cancelled."""
    customer = doc.get("customer")
    sales_person = doc.get("sales_person")
    if customer:
        try:
            refresh_single_sales_by_customer(customer, sales_person)
        except Exception as e:
            frappe.log_error(f"Error updating Sales By Customer for {customer}: {str(e)}")


# ─────────────────────────────────────────
# Sales Order Hooks
# ─────────────────────────────────────────

def update_sales_by_customer_from_sales_order(doc, method):
    """Update Sales By Customer when a Sales Order is submitted/cancelled."""
    customer = doc.get("customer")
    if customer:
        try:
            # Get the sales person from linked Customer Visit
            sales_person = frappe.db.get_value(
                "Customer Visit",
                {"order_number": doc.name},
                "sales_person"
            )
            refresh_single_sales_by_customer(customer, sales_person)
        except Exception as e:
            frappe.log_error(f"Error updating Sales By Customer for {customer}: {str(e)}")


# ─────────────────────────────────────────
# Sales By Customer Aggregation
# ─────────────────────────────────────────

def refresh_single_sales_by_customer(customer_name, sales_person=None):
    """Refresh one Sales By Customer record for all-time data."""

    # 1. Get visit info: first visit date, last visit date, visit count
    visit_data = frappe.db.sql("""
        SELECT
            MIN(DATE(cv.date))           AS first_visit_date,
            MAX(DATE(cv.date))           AS last_visit_date,
            COUNT(DISTINCT cv.name)      AS total_visits
        FROM `tabCustomer Visit` cv
        WHERE cv.customer = %s
    """, customer_name, as_dict=True)

    data_v = visit_data[0] if visit_data else {}

    # 2. Get total sales from Sales Orders linked via Customer Visit
    sales_data = frappe.db.sql("""
        SELECT
            COALESCE(SUM(so.grand_total), 0) AS total_sales_amount
        FROM `tabSales Order` so
        INNER JOIN `tabCustomer Visit` cv
            ON cv.order_number = so.name
        WHERE cv.customer = %s
          AND so.docstatus IN (0, 1)
    """, customer_name, as_dict=True)

    data_s = sales_data[0] if sales_data else {}

    # 3. Get customer location (from Customer custom fields or last visit geolocation)
    location = "—"
    latitude = 0.0
    longitude = 0.0

    # Try Customer custom fields first
    customer_loc = frappe.db.get_value(
        "Customer", customer_name,
        ["custom_latitude", "custom_longitude"], as_dict=True
    )
    if customer_loc:
        lat = customer_loc.get("custom_latitude")
        lng = customer_loc.get("custom_longitude")
        if lat and lng and lat != 0.0 and lng != 0.0:
            latitude = lat
            longitude = lng
            location = f"{lat}, {lng}"

    # If no customer coordinates, try last visit's stop location
    if latitude == 0.0 and longitude == 0.0:
        last_geo = frappe.db.sql("""
            SELECT stop_latitude, stop_longitude
            FROM `tabCustomer Visit`
            WHERE customer = %s
              AND stop_latitude IS NOT NULL
              AND stop_longitude IS NOT NULL
              AND stop_latitude != 0
              AND stop_longitude != 0
            ORDER BY creation DESC
            LIMIT 1
        """, customer_name, as_dict=True)

        if last_geo:
            lg = last_geo[0]
            lat = lg.get("stop_latitude", 0)
            lng = lg.get("stop_longitude", 0)
            if lat and lng:
                latitude = lat
                longitude = lng
                location = f"{lat}, {lng}"

    # 4. Check if record already exists for this customer
    existing = frappe.db.get_value(
        "Sales By Customer",
        {"customer": customer_name},
        "name"
    )

    if existing:
        now_ts = now()
        frappe.db.sql("""
            UPDATE `tabSales By Customer`
            SET location      = %s,
                latitude      = %s,
                longitude     = %s,
                first_visit   = %s,
                last_visit    = %s,
                visited       = %s,
                total_sales   = %s,
                modified      = %s,
                modified_by   = %s
            WHERE name = %s
        """, (
            location,
            latitude,
            longitude,
            data_v.get("first_visit_date"),
            data_v.get("last_visit_date"),
            data_v.get("total_visits", 0),
            data_s.get("total_sales_amount", 0.0),
            now_ts,
            frappe.session.user,
            existing
        ))
        frappe.db.commit()
    else:
        # Insert new record
        doc = frappe.new_doc("Sales By Customer")
        doc.customer     = customer_name
        doc.location     = location
        doc.latitude     = latitude
        doc.longitude    = longitude
        doc.first_visit  = data_v.get("first_visit_date")
        doc.last_visit   = data_v.get("last_visit_date")
        doc.visited      = data_v.get("total_visits", 0)
        doc.total_sales  = data_s.get("total_sales_amount", 0.0)
        doc.insert(ignore_permissions=True)

    # ── Real-time notification to all connected clients ──
    frappe.publish_realtime(
        event="sales_by_customer_updated",
        message={
            "customer": customer_name,
            "visited": data_v.get("total_visits", 0),
            "total_sales": data_s.get("total_sales_amount", 0.0),
        },
        after_commit=True
    )


def refresh_all_sales_by_customer():
    """Refresh Sales By Customer for all customers who have visit data."""
    active_customers = frappe.db.sql("""
        SELECT DISTINCT customer
        FROM `tabCustomer Visit`
        WHERE customer IS NOT NULL
          AND customer != ''
    """, pluck="customer")

    for cust in active_customers:
        try:
            refresh_single_sales_by_customer(cust)
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Sales By Customer refresh failed for {cust}"
            )


def ensure_all_customers_initialized():
    """Ensure all visited customers have Sales By Customer records.
    Called during installation to bootstrap the system."""
    active_customers = frappe.db.sql("""
        SELECT DISTINCT customer
        FROM `tabCustomer Visit`
        WHERE customer IS NOT NULL
          AND customer != ''
    """, pluck="customer")

    for customer in active_customers:
        try:
            existing = frappe.db.get_value(
                "Sales By Customer",
                {"customer": customer},
                "name"
            )

            if not existing:
                refresh_single_sales_by_customer(customer)
        except Exception as e:
            frappe.log_error(f"Error initializing Sales By Customer for {customer}: {str(e)}")
