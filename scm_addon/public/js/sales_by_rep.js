// Sales By Realtime Auto-Refresh
// Listens for real-time events pushed from the backend when Customer Visits
// are created/updated, and auto-refreshes the list view so data is always current.

frappe.realtime.on("sales_by_rep_updated", function(data) {
    console.log("📊 Sales By Rep updated:", data.sales_person, data.date_range);

    // If we are on the Sales By Rep list view, refresh it
    if (
        frappe.get_route &&
        frappe.get_route()[0] === "List" &&
        frappe.get_route()[1] === "Sales By Rep"
    ) {
        // Throttle refreshes - only refresh if no recent refresh happened
        let now = Date.now();
        if (!frappe._last_sbr_refresh || (now - frappe._last_sbr_refresh) > 3000) {
            frappe._last_sbr_refresh = now;

            // Trigger list view refresh
            let listview = frappe.get_listview && frappe.get_listview("Sales By Rep");
            if (listview) {
                listview.refresh();
            } else {
                // Fallback: reload the current route
                frappe.ui.toolbar.clear_cache_and_reload();
            }
        }
    }
});
