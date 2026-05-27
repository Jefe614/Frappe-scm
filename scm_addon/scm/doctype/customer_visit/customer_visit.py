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
    if hasattr(doc, "sales_person") and doc.sales_person:
        doc.sales_person = None


def get_default_warehouse():
    """Get default warehouse from Stock Settings or first available warehouse."""
    warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")
    if warehouse:
        return warehouse

    return frappe.db.get_value(
        "Warehouse",
        {"is_group": 0, "disabled": 0},
        "name"
    )


