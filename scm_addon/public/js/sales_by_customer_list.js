frappe.listview_settings['Sales By Customer'] = {
    hide_name_column: true,
    add_fields: ['latitude', 'longitude', 'last_visit'],

    formatters: {
        customer: function(value) {
            return `<b>${frappe.format(value, {fieldtype: 'Data'})}</b>`;
        },

        visited: function(value, df, options, doc) {
            const count = parseInt(value) || 0;

            if (count === 0) {
                return `<span class="badge" style="background:#f8d7da;color:#721c24;padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600;">Not visited</span>`;
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

            return `<span class="badge" style="background:${bg};color:${color};padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600;">${label}</span>`;
        },

        total_sales: function(value) {
            return `<b>Sh ${frappe.format(value || 0, {fieldtype: 'Currency'})}</b>`;
        },

        first_visit: function(value) {
            return value ? frappe.datetime.str_to_user(value) : '<span style="color:#aaa;">N/A</span>';
        },

        last_visit: function(value) {
            return value ? frappe.datetime.str_to_user(value) : '<span style="color:#aaa;">N/A</span>';
        }
    },

    onload: function(listview) {
        // Inject CSS to hide ID/name column and make table full width
        if (!document.getElementById('sbc-custom-style')) {
            const style = document.createElement('style');
            style.id = 'sbc-custom-style';
            style.textContent = `
                .list-row-col[data-fieldname="name"],
                .list-header-col[data-fieldname="name"] {
                    display: none !important;
                }
                .frappe-list .list-row,
                .frappe-list .list-headers {
                    width: 100% !important;
                }
            `;
            document.head.appendChild(style);
        }
    }
};
