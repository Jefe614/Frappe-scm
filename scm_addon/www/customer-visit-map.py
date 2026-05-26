import frappe


def get_context(context):
    """Generate context for customer visit map page"""
    context.no_cache = 1
    context.show_sidebar = False
    return context
