/* Copyright (c) 2026, VAPTECH */

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
                ].join("\n"),
                default: "This Month",
            },
        ],

        get: function (values) {
            return new Promise(function (resolve, reject) {
                var args = {};
                if (values && values.time_range) args.time_range = values.time_range;
                if (values && values.from_date)  args.from_date = values.from_date;
                if (values && values.to_date)    args.to_date = values.to_date;
                frappe.call({
                    method: "scm_addon.chart_data.get_daily_sales_rep_performance",
                    args: args,
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

        render: function (chart_container, data, chart_args) {
            data = safeParse(data);

            chart_container.innerHTML = "";

            var labels = data.labels || [];
            var datasets = data.datasets || [];

            if (!labels.length || !datasets.length) {
                chart_container.innerHTML = `
                    <div style="display:flex;align-items:center;justify-content:center;height:200px;color:#888;">
                        No data available
                    </div>`;
                return;
            }

            // Create a canvas element for Frappe's built-in chart renderer
            var canvas = document.createElement("canvas");
            canvas.style.width = "100%";
            canvas.style.height = "100%";
            chart_container.appendChild(canvas);

            // Build compatible data format and render with Frappe chart
            var chartData = {
                labels: labels,
                datasets: datasets
            };

            try {
                new frappe.Chart(canvas, {
                    data: chartData,
                    type: "bar",
                    height: 220,
                    colors: ["#4463F0", "#29CD42", "#FF6B6B"],
                    truncateLegends: 1,
                    axisOptions: {
                        xIsSeries: true
                    }
                });
            } catch (e) {
                chart_container.innerHTML = `
                    <div style="display:flex;align-items:center;justify-content:center;height:200px;color:#888;">
                        No data available
                    </div>`;
            }
        },
    };
})();
