import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields as _create_custom_fields


def after_install():
    from scm_addon.scm.doctype.sales_by_rep.sales_by_rep import refresh_all_sales_by_rep, ensure_all_sales_people_initialized
    try:
        ensure_all_sales_people_initialized()
        refresh_all_sales_by_rep()
    except Exception as e:
        frappe.log_error(f"Failed to seed Sales By Rep: {e}", "SCM Install")

    setup_custom_fields()
    seed_weekdays()


def after_migrate():
    """Re-run setup on migrate to ensure fields/config exist."""
    from scm_addon.scm.doctype.sales_by_rep.sales_by_rep import ensure_all_sales_people_initialized

    setup_custom_fields()
    seed_weekdays()

    try:
        ensure_all_sales_people_initialized()
    except Exception as e:
        frappe.log_error(f"Failed to initialize Sales By Rep: {e}", "SCM Migrate")


def setup_custom_fields():
    _create_custom_fields({
        "Customer": [
            {
                "fieldname": "custom_latitude",
                "fieldtype": "Float",
                "label": "Latitude",
                "insert_after": "address_html",
                "precision": "6",
            },
            {
                "fieldname": "custom_longitude",
                "fieldtype": "Float",
                "label": "Longitude",
                "insert_after": "custom_latitude",
                "precision": "6",
            },
        ]
    })
    frappe.clear_cache(doctype="Customer")


def seed_weekdays():
    """Pre-create the 7 days of the week as Weekdays records."""
    days = [
        "Sunday", "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday"
    ]
    for day in days:
        if not frappe.db.exists("Weekday", day):
            doc = frappe.get_doc({
                "doctype": "Weekday",
                "day_name": day,
            })
            doc.insert()
