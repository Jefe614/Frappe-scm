"""
scm_addon/config.py

Sidebar and desk configuration for SCM Addon module
Defines how the module appears in the ERPNext interface
"""

from frappe import _


def get_sidebar_config():
    """
    Returns the sidebar configuration for SCM Addon
    This makes the module appear in Awesome Bar and sidebar
    """

    return [
        {
            "app_name": "scm_addon",
            "module_name": "SCM Addon",
            "category": "Sales",
            "label": _("SCM Addon"),
            "color": "#3498db",
            "icon": "octicon octicon-organization",
            "type": "module",
            "description": "Route Planning, Territory Management, and Sales Rep Assignment",
        }
    ]


def get_config():
    """
    Returns the desk configuration for SCM Addon
    Configures module layout and shortcuts
    """

    return {
        "label": _("SCM Addon"),
        "items": [
            {
                "type": "doctype",
                "name": "Route Plan",
                "color": "#3498db",
                "icon": "octicon octicon-organization",
                "label": _("Route Plan"),
                "description": _("Plan sales routes by territory and day"),
            },
            {
                "type": "doctype",
                "name": "Territory",
                "color": "#2ecc71",
                "icon": "octicon octicon-location",
                "label": _("Territory"),
                "description": _("Sales territories"),
            },
            {
                "type": "doctype",
                "name": "Sales Person",
                "color": "#e74c3c",
                "icon": "octicon octicon-person",
                "label": _("Sales Person"),
                "description": _("Sales representatives"),
            },
            {
                "type": "doctype",
                "name": "Route Plan Territory",
                "label": _("Route Plan Territories"),
                "hidden": True,  # Hide child tables from main menu
            },
            {
                "type": "doctype",
                "name": "Route Plan Sales Reps",
                "label": _("Route Plan Sales Reps"),
                "hidden": True,  # Hide child tables from main menu
            },
            {
                "type": "doctype",
                "name": "Customer Visit",
                "color": "#9b59b6",
                "icon": "octicon octicon-map",
                "label": _("Customer Visit"),
                "description": _("Record of customer visits with location and order details"),
            },
            {
                "type": "doctype",
                "name": "Visit Order Item",
                "label": _("Visit Order Items"),
                "hidden": True,  # Hide child tables from main menu
            },
        ]
    }


# Alternative simpler configuration if above is too complex:
def get_config_simple():
    """
    Simpler configuration - just lists the main DocTypes
    """
    return {
        "label": _("SCM Addon"),
        "items": [
            {
                "type": "doctype",
                "name": "Route Plan",
            },
        ]
    }
