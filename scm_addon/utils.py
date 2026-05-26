import frappe


def sanitize_sales_order_request():
    """Strip invalid fields from Sales Order POST requests before Frappe processes them."""
    request = frappe.local.request
    if request.method != "POST":
        return
    if "Sales%20Order" not in request.path and "Sales Order" not in request.path:
        return

    try:
        import json
        import io

        body = request.get_data(as_text=True)
        if not body:
            return

        data = json.loads(body)
        modified = False

        # Remove sales_person — Sales Order uses Sales Team child table
        if "sales_person" in data:
            del data["sales_person"]
            modified = True

        if modified:
            new_body = json.dumps(data).encode("utf-8")
            request._cached_data = new_body
            request.environ["wsgi.input"] = io.BytesIO(new_body)
            request.environ["CONTENT_LENGTH"] = str(len(new_body))

    except Exception as e:
        frappe.log_error(title="sanitize_sales_order_request error", message=str(e))
