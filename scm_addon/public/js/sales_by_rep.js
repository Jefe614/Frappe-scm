frappe.listview_settings['Sales By Rep'] = {
	add_fields: ["date_range", "sales_person", "sales", "qty_sold", "visits", "customers_in_route"],
	onload: function(listview) {
		// Add custom filtering for date range
		listview.page.add_inner_button(__('Refresh Data'), function() {
			frappe.call({
				method: 'scm_addon.scm.doctype.sales_by_rep.sales_by_rep.refresh_all_sales_by_rep',
				callback: function(r) {
					frappe.msgprint(__('Sales By Rep data refreshed successfully'));
					listview.refresh();
				}
			});
		});
	}
};

// Custom report view for Sales By Rep
if (frappe.views.ReportView) {
	frappe.views.ReportView = frappe.views.ReportView.extend({
		setup: function() {
			this._super();

			// Add date range filter to report
			if (this.doctype === 'Sales By Rep') {
				this.add_date_range_filter();
			}
		},

		add_date_range_filter: function() {
			const self = this;

			// This will be called when the report is loaded
			setTimeout(function() {
				if (cur_list && cur_list.doctype === 'Sales By Rep') {
					// Add filter dropdown for date ranges
					const date_ranges = [
						{ label: 'Today', value: 'Today' },
						{ label: 'Yesterday', value: 'Yesterday' },
						{ label: 'This Month', value: 'This Month' },
						{ label: 'Last Month', value: 'Last Month' },
						{ label: 'Last Week', value: 'Last Week' },
						{ label: 'Last Quarter', value: 'Last Quarter' },
						{ label: 'Last Year', value: 'Last Year' },
						{ label: 'This Year', value: 'This Year' },
						{ label: 'Yearly', value: 'Yearly' }
					];
				}
			}, 500);
		}
	});
}

// Customize the report columns and filtering
frappe.ui.form.on('Sales By Rep', {
	refresh: function(frm) {
		// Add real-time update button
		if (!frm.is_new()) {
			frm.add_custom_button(__('Refresh Report'), function() {
				frappe.call({
					method: 'frappe.client.get',
					args: {
						doctype: 'Sales By Rep',
						name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							frm.reload_doc();
							frappe.msgprint(__('Report refreshed'));
						}
					}
				});
			});
		}
	}
});
