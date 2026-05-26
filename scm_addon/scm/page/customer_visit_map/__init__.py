"""
Customer Visit Map Page
Registers a custom page for displaying customer visits on a map
"""
import frappe
from frappe.desk.page.page import Page


class CustomerVisitMapPage(Page):
    def __init__(self):
        super().__init__()
        self.name = "customer-visit-map"
        self.title = "Customer Visit Map"
        self.module = "scm"


# Register the page
def get_page(name):
    """Get page by name"""
    if name == "customer-visit-map":
        return {
            "name": "customer-visit-map",
            "title": "Customer Visit Map",
            "module": "scm",
            "doctype": "Page",
            "icon": "icon-map-marker",
        }
    return None
