# Copyright (c) 2026, VAPTECH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class CustomerVisit(Document):
    def validate(self):
        pass


# ─────────────────────────────────────────
# Sales Order Hook
# ─────────────────────────────────────────

def set_sales_order_defaults(doc, method):
    """Auto-set warehouse on Sales Order items before insert.
    Fixes mobile app submissions that don't include warehouse.
    Also strips invalid fields the mobile app may send.
    """
    default_warehouse = get_default_warehouse()

    if not default_warehouse:
        frappe.log_error(
            title="SCM - No Default Warehouse",
            message=(
                "No default warehouse found. "
                "Please set one in Stock Settings > Default Warehouse."
            )
        )
        return

    for item in doc.items:
        if not item.warehouse:
            item.warehouse = default_warehouse
        if not item.delivery_date:
            item.delivery_date = doc.delivery_date or nowdate()

    # Sales Order uses Sales Team child table, not a direct sales_person field.
    # Remove it if mobile app sends it to avoid LinkValidationError.
    if hasattr(doc, "sales_person") and doc.sales_person:
        doc.sales_person = None


def get_default_warehouse():
    """Get default warehouse from Stock Settings or first available warehouse."""
    # ERPNext stores default warehouse in Stock Settings
    warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
    if warehouse:
        return warehouse

    # Fallback: first active non-group warehouse
    return frappe.db.get_value(
        "Warehouse",
        {"is_group": 0, "disabled": 0},
        "name"
    )


# ─────────────────────────────────────────
# Customer Visit Hooks
# ─────────────────────────────────────────

def update_sales_by_rep(doc, method):
    """Update Sales By Rep when a Customer Visit is submitted/cancelled."""
    refresh_sales_by_rep()


# ─────────────────────────────────────────
# Sales By Rep Aggregation
# ─────────────────────────────────────────

def refresh_sales_by_rep():
    """Refresh Sales By Rep — one cumulative record per sales person across ALL dates."""
    sales_people = frappe.get_all("Sales Person", pluck="name")

    for sp in sales_people:
        existing = frappe.db.get_value("Sales By Rep", {"sales_person": sp}, "name")

        if existing:
            doc = frappe.get_doc("Sales By Rep", existing)
        else:
            doc = frappe.new_doc("Sales By Rep")
            doc.sales_person = sp

        # Aggregate ALL submitted visits for this sales person
        visits_data = frappe.db.sql("""
            SELECT
                COUNT(DISTINCT cv.name)      AS total_visits,
                COUNT(DISTINCT cv.customer)  AS total_customers,
                COALESCE(SUM(voi.amount), 0) AS total_sales_amount,
                COALESCE(SUM(voi.qty), 0)    AS total_qty_sold
            FROM `tabCustomer Visit` cv
            LEFT JOIN `tabVisit Order Item` voi ON voi.parent = cv.name
            WHERE cv.sales_person = %s
              AND cv.docstatus = 1
        """, (sp,), as_dict=True)

        data = visits_data[0] if visits_data else {}

        doc.sales             = data.get("total_sales_amount", 0.0)
        doc.qty_sold          = data.get("total_qty_sold", 0.0)
        doc.customers_in_route = data.get("total_customers", 0)
        doc.visits            = data.get("total_visits", 0)

        doc.save(ignore_permissions=True)


def refresh_all_sales_by_rep():
    """Scheduled job to refresh all Sales By Rep records."""
    refresh_sales_by_rep()
