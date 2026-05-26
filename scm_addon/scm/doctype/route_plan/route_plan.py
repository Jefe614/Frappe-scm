# Copyright (c) 2026, VAPTECH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RoutePlan(Document):

    def as_dict(self, *args, **kwargs):
        data = super().as_dict(*args, **kwargs)

        data["route"] = [{"territory": r.get("territory")} for r in data.pop("route", [])]
        data["days"] = [{"days": d.get("day")} for d in data.pop("select_days", [])]

        # Remove fields not in mobile data class
        data.pop("salesmen", None)
        data.pop("territory", None)
        data.pop("sales_reps", None)

        return data


@frappe.whitelist()
def get_route_plans():
    """Return route plans in mobile-friendly format."""
    plans = frappe.get_all(
        "Route Plan",
        fields=["name", "route_plan_name", "owner", "status", "start_date", "end_date"],
        filters={"status": 1}
    )

    result = []
    for plan in plans:
        doc = frappe.get_doc("Route Plan", plan["name"])

        result.append({
            "id": doc.name,
            "company": doc.status or 0,
            "route_plan_name": doc.route_plan_name,
            "start_date": str(doc.start_date) if doc.start_date else None,
            "end_date": str(doc.end_date) if doc.end_date else None,
            "route": [{"territory": r.territory} for r in doc.route],
            "days": [{"days": d.day} for d in doc.select_days],
        })

    return result
