/* Copyright (c) 2026, VAPTECH */
// Dashboard Chart Source JS

frappe.provide("frappe.dashboards.chart_sources");

(function () {
    function safeParse(data) {
        try {
            return typeof data === "string" ? JSON.parse(data) : data;
        } catch (e) {
            return data;
        }
    }

    frappe.dashboards.chart_sources["SCM Daily Sales Rep"] = {
        method: "scm_addon.chart_data.get_daily_sales_rep_performance",

        filters: [
            {
                fieldname: "time_range",
                label: __("Time Range"),
                fieldtype: "Select",
                options: [
                    "Today",
                    "Yesterday",
                    "This Week",
                    "Last Week",
                    "This Month",
                    "Last Month",
                    "This Quarter",
                    "This Year",
                    "Last Year",
                    "Custom",
                ].join("\n"),
                default: "Today",
            },
            {
                fieldname: "from_date",
                label: __("From Date"),
                fieldtype: "Date",
                default: frappe.datetime.get_today(),
                depends_on: "eval:filters.time_range === 'Custom'",
            },
            {
                fieldname: "to_date",
                label: __("To Date"),
                fieldtype: "Date",
                default: frappe.datetime.get_today(),
                depends_on: "eval:filters.time_range === 'Custom'",
            },
        ],

        get: function (values) {
            return new Promise(function (resolve, reject) {
                frappe.call({
                    method: "scm_addon.chart_data.get_daily_sales_rep_performance",
                    args: {
                        chart_name: values && values.chart_name,
                        time_range: values && values.time_range,
                        from_date:  values && values.from_date,
                        to_date:    values && values.to_date,
                    },
                    callback: function (r) {
                        if (r && r.message) {
                            resolve(safeParse(r.message));
                        } else {
                            resolve({ labels: [], datasets: [] });
                        }
                    },
                    error: function (err) {
                        reject(err);
                    },
                });
            });
        },
    };
})();
