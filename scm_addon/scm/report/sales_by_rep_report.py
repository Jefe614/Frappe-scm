# Copyright (c) 2026, VAPTECH and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    """Generate Sales By Rep report with date range filtering"""

    if not filters:
        filters = {}

    date_range = filters.get("date_range", "Today")
    sales_person = filters.get("sales_person")

    columns = get_columns()
    data = get_data(date_range, sales_person)

    return columns, data


def get_columns():
    """Define report columns"""
    return [
        {
            "label": _("Sales Person"),
            "fieldname": "sales_person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "width": 200
        },
        {
            "label": _("Sales Target"),
            "fieldname": "sales_target",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("Sales"),
            "fieldname": "sales",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": _("% of Target"),
            "fieldname": "sales_percentage",
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "label": _("Qty Target"),
            "fieldname": "qty_target",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("Qty Sold"),
            "fieldname": "qty_sold",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("Visits"),
            "fieldname": "visits",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": _("Customers"),
            "fieldname": "customers_in_route",
            "fieldtype": "Int",
            "width": 100
        }
    ]


def get_data(date_range, sales_person=None):
    """Fetch report data - shows all sales people regardless of stats"""
    from scm_addon.scm.doctype.sales_by_rep.sales_by_rep import get_date_range, refresh_single_sales_by_rep

    start_date, end_date = get_date_range(date_range)

    # Get all active sales people in the system
    all_sales_people = frappe.get_list(
        "Sales Person",
        filters={"enabled": 1},
        fields=["name"],
        pluck="name"
    )

    # If specific sales person is selected, filter to just that one
    if sales_person:
        if sales_person in all_sales_people:
            all_sales_people = [sales_person]
        else:
            all_sales_people = []

    # Ensure all sales people have records for the selected date range
    for sp in all_sales_people:
        try:
            refresh_single_sales_by_rep(sp, date_range)
        except Exception as e:
            frappe.log_error(f"Error refreshing Sales By Rep for {sp}: {str(e)}")

    # Get the Sales By Rep records (which now exist for all sales people)
    filters = {"sales_person": ["in", all_sales_people]}
    records = frappe.get_list(
        "Sales By Rep",
        filters=filters,
        fields=[
            "sales_person",
            "sales_target",
            "sales",
            "qty_target",
            "qty_sold",
            "visits",
            "customers_in_route"
        ]
    )

    # If no records found, create empty entries for all sales people
    if not records:
        records = []
        for sp in all_sales_people:
            records.append({
                "sales_person": sp,
                "sales_target": 0,
                "sales": 0,
                "qty_target": 0,
                "qty_sold": 0,
                "visits": 0,
                "customers_in_route": 0
            })

    # Process records and calculate percentages
    data = []
    for record in records:
        percentage = 0
        if record.get("sales_target") and record.get("sales_target") > 0:
            percentage = (record.get("sales", 0) / record.get("sales_target", 1)) * 100

        data.append({
            "sales_person": record["sales_person"],
            "sales_target": record.get("sales_target", 0),
            "sales": record.get("sales", 0),
            "sales_percentage": percentage,
            "qty_target": record.get("qty_target", 0),
            "qty_sold": record.get("qty_sold", 0),
            "visits": record.get("visits", 0),
            "customers_in_route": record.get("customers_in_route", 0)
        })

    return data
