// frappe.listview_settings['Driver Report'] = {
//     hide_name_column: true,

//     get_indicator: function(doc) {
//         if (doc.trips > 0 && doc.completed_trips === doc.trips) {
//             return [__('All Completed'), 'green', 'trips,>,'];
//         }
//         if (doc.trips > doc.completed_trips) {
//             return [__('Pending'), 'orange', ''];
//         }
//         return [__('No Activity'), 'light-gray', ''];
//     },

//     formatters: {
//         driver: function(value) {
//             return value || __('Unnamed');
//         },
//         trips: function(value) {
//             return `<span class="badge" style="background:#e8f5e9;color:#2e7d32;padding:2px 8px;border-radius:10px;">${value || 0}</span>`;
//         },
//         completed_trips: function(value) {
//             return `<span class="badge" style="background:#e3f2fd;color:#1565c0;padding:2px 8px;border-radius:10px;">${value || 0}</span>`;
//         },
//         deliveries: function(value) {
//             return `<span class="badge" style="background:#fff3e0;color:#e65100;padding:2px 8px;border-radius:10px;">${value || 0}</span>`;
//         },
//         completed_deliveries: function(value) {
//             return `<span class="badge" style="background:#f3e5f5;color:#6a1b9a;padding:2px 8px;border-radius:10px;">${value || 0}</span>`;
//         },
//         distance_covered: function(value) {
//             return value ? `${value.toFixed(2)} km` : '0 km';
//         }
//     },

//     onload: function(listview) {
//         // Hide the ID/name column in both header and rows
//         setTimeout(function() {
//             $(
//                 '.list-row-head .list-row-col:first-child, ' +
//                 '.list-row-container .list-row-col:first-child, ' +
//                 '.list-row-head .list-row-col:contains("ID"), ' +
//                 '.list-subject .ellipsis, ' +
//                 '.list-row-check'
//             ).hide();
//         }, 300);

//         // Refresh All button
//         listview.page.add_inner_button(__('Refresh All'), function() {
//             frappe.call({
//                 method: 'scm_addon.scm.doctype.driver_report.driver_report.refresh_all_driver_reports',
//                 freeze: true,
//                 freeze_message: __('Refreshing Driver Reports...'),
//                 callback: function(r) {
//                     listview.refresh();
//                     frappe.show_alert({
//                         message: r.message && r.message.message
//                             ? r.message.message
//                             : __('Driver Reports refreshed'),
//                         indicator: 'green'
//                     });
//                 }
//             });
//         }, __('Actions'));
//     }
// };
