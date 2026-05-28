frappe.listview_settings['Sales By Rep'] = {
    hide_name_column: true,

    get_indicator: function(doc) {
        const pct = doc.sales_target > 0
            ? (doc.sales / doc.sales_target) * 100
            : 0;

        if (pct >= 100) return [__('Target Met'), 'green', 'sales,>=,sales_target'];
        if (pct >= 50)  return [__('On Track'),   'orange', ''];
        return [__('Below Target'), 'red', ''];
    },

    formatters: {
        sales: function(value) {
            return `<b>Sh ${frappe.format(value, {fieldtype: 'Currency'})}</b>`;
        },
        sales_target: function(value) {
            return `Sh ${frappe.format(value, {fieldtype: 'Currency'})}`;
        },
        visits: function(value) {
            return `<span class="badge" style="background:#e3f2fd;color:#1565c0;padding:2px 8px;border-radius:10px;">${value || 0}</span>`;
        },
        customers_in_route: function(value) {
            return `<span class="badge" style="background:#f3e5f5;color:#6a1b9a;padding:2px 8px;border-radius:10px;">${value || 0}</span>`;
        },
        qty_sold: function(value) {
            return value ? value.toFixed(0) : '0';
        },
        qty_target: function(value) {
            return value ? value.toFixed(0) : '0';
        }
    },

    onload: function(listview) {
        // Hide the ID/name column in both header and rows
        setTimeout(function() {
            $(
                '.list-row-head .list-row-col:first-child, ' +
                '.list-row-container .list-row-col:first-child, ' +
                '.list-row-head .list-row-col:contains("ID"), ' +
                '.list-subject .ellipsis, ' +
                '.list-row-check'
            ).hide();
        }, 300);

        // Refresh button
        listview.page.add_inner_button(__('Refresh All'), function() {
            frappe.call({
                method: 'scm_addon.scm.doctype.sales_by_rep.sales_by_rep.refresh_all_sales_by_rep',
                freeze: true,
                freeze_message: __('Refreshing Sales By Rep data...'),
                callback: function() {
                    listview.refresh();
                    frappe.show_alert({message: __('Sales By Rep refreshed'), indicator: 'green'});
                }
            });
        }, __('Actions'));
    }
};
