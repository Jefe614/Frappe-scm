import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields as _create_custom_fields


def after_install():
    from scm_addon.scm.doctype.sales_by_rep.sales_by_rep import refresh_all_sales_by_rep, ensure_all_sales_people_initialized
    from scm_addon.scm.doctype.sales_by_customer.sales_by_customer import refresh_all_sales_by_customer, ensure_all_customers_initialized
    from scm_addon.scm.doctype.driver_report.driver_report import ensure_all_drivers_initialized
    try:
        ensure_all_sales_people_initialized()
        refresh_all_sales_by_rep()
        ensure_all_customers_initialized()
        refresh_all_sales_by_customer()
        ensure_all_drivers_initialized()
    except Exception as e:
        frappe.log_error(f"Failed to seed reports: {e}", "SCM Install")

    setup_custom_fields()
    seed_weekdays()


def after_migrate():
    """Re-run setup on migrate to ensure fields/config exist."""
    from scm_addon.scm.doctype.sales_by_rep.sales_by_rep import ensure_all_sales_people_initialized, refresh_all_sales_by_rep
    from scm_addon.scm.doctype.sales_by_customer.sales_by_customer import ensure_all_customers_initialized, refresh_all_sales_by_customer
    from scm_addon.scm.doctype.driver_report.driver_report import ensure_all_drivers_initialized, refresh_all_driver_reports

    setup_custom_fields()
    seed_weekdays()

    try:
        ensure_all_sales_people_initialized()
        refresh_all_sales_by_rep()
        ensure_all_customers_initialized()
        refresh_all_sales_by_customer()
        ensure_all_drivers_initialized()
        refresh_all_driver_reports()
    except Exception as e:
        frappe.log_error(f"Failed to initialize reports: {e}", "SCM Migrate")


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
