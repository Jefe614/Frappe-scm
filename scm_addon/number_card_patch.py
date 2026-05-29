# Copyright (c) 2026, VAPTECH
# For license information, please see license.txt

"""Small patch to make Number Card percentage visible when previous period is 0.

Frappe's default behavior returns `None` when previous_result == 0, which means the
UI only renders the count (no percentage). For the SCM dashboard we prefer:
- previous = 0, current > 0 => show 100%
- previous = 0, current = 0 => show 0%

This module is designed to be imported from hooks.py / init patching.
"""

import frappe
from frappe.utils import flt



@frappe.whitelist()
def get_percentage_difference_with_zero_previous(doc, filters, result):
    """Compatibility wrapper for Frappe Number Card percentage computation."""
    # Import inside the function to avoid hard dependency at import time.
    number_card = frappe.get_module("frappe.desk.doctype.number_card.number_card")

    doc = frappe.parse_json(doc)
    doc_name = doc.get("name")
    if not doc_name:
        # In some call paths `doc` is already the Number Card name.
        doc_name = frappe.parse_json(doc).get("name")

    number_card_doc = frappe.get_doc("Number Card", doc_name)

    # If the standard flag isn't enabled, keep default behavior.
    if not number_card_doc.get("show_percentage_stats"):
        return None

    previous_result = flt(number_card.calculate_previous_result(number_card_doc, filters))
    result = flt(result)

    # If previous is 0: if current is also 0, return 0.
    # If current > 0, return None so we don't trigger UI math that caused
    # the TypeError, while still allowing the UI to display something neutral.
    if previous_result == 0:
        return 0 if result == 0 else None

    # Otherwise, preserve default behavior.
    if result == previous_result:
        return 0

    return ((result / previous_result) - 1) * 100.0


