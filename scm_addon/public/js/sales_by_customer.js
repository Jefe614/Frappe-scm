// Sales By Customer - Report View Settings
frappe.report_settings['Sales By Customer'] = {
    formatters: {
        visited: function(value, df, doc) {
            const count = parseInt(value) || 0;

            if (count === 0) {
                return `<span style="background:#f8d7da;color:#721c24;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;">Not visited</span>`;
            }

            const last_visit = doc && doc.last_visit ? doc.last_visit : null;
            let daysSince = null;
            if (last_visit) {
                const diffMs = new Date() - new Date(last_visit);
                daysSince = Math.floor(diffMs / (1000 * 60 * 60 * 24));
            }

            let bg, color, label;
            if (daysSince !== null && daysSince <= 1) {
                bg = '#d4edda'; color = '#155724'; label = 'Today';
            } else if (daysSince !== null && daysSince <= 7) {
                bg = '#fff3cd'; color = '#856404'; label = `${daysSince}d ago`;
            } else if (daysSince !== null && daysSince <= 30) {
                bg = '#ffd8a8'; color = '#7c4a00'; label = `${daysSince} days ago`;
            } else {
                bg = '#e2e3e5'; color = '#383d41'; label = daysSince ? `${daysSince} days ago` : `${count}`;
            }

            return `<span style="background:${bg};color:${color};padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600;">${label}</span>`;
        }
    }
};

// Real-time Auto-Refresh
frappe.realtime.on("sales_by_customer_updated", function(data) {
    if (
        frappe.get_route &&
        frappe.get_route()[0] === "List" &&
        frappe.get_route()[1] === "Sales By Customer"
    ) {
        let now = Date.now();
        if (!frappe._last_sbc_refresh || (now - frappe._last_sbc_refresh) > 3000) {
            frappe._last_sbc_refresh = now;
            let listview = frappe.get_listview && frappe.get_listview("Sales By Customer");
            if (listview) listview.refresh();
        }
    }
});
