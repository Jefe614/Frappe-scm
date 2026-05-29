// /* Copyright (c) 2026, VAPTECH */
// frappe.provide("frappe.dashboards.chart_sources");

// frappe.dashboards.chart_sources["SCM Top Products"] = {
//     method: "scm_addon.chart_data.get_top_products_with_percent",
//     filters: [
//         {
//             fieldname: "time_range", label: __("Time Range"), fieldtype: "Select",
//             options: ["Today","Yesterday","This Week","Last Week","This Month",
//                       "Last Month","This Quarter","This Year","Last Year","Custom"].join("\n"),
//             default: "Today",
//         },
//         { fieldname: "from_date", label: __("From Date"), fieldtype: "Date" },
//         { fieldname: "to_date",   label: __("To Date"),   fieldtype: "Date" },
//     ],
// };

// // Hook into frappe.call to intercept dashboard chart data responses
// (function() {
//     var _original_call = frappe.call.bind(frappe);
//     frappe.call = function(opts) {
//         var method = opts.method || (opts && opts.method);
//         if (method && method.indexOf("get_chart_data") !== -1) {
//             var _original_callback = opts.callback;
//             opts.callback = function(r) {
//                 if (_original_callback) _original_callback(r);
//                 // After data loads, try to replace chart rendering
//                 setTimeout(function() {
//                     scm_replace_charts();
//                 }, 300);
//             };
//         }
//         return _original_call(opts);
//     };
// })();

// function scm_replace_charts() {
//     document.querySelectorAll(".widget").forEach(function(widget) {
//         var titleEl = widget.querySelector(".widget-title, .chart-title");
//         if (!titleEl) return;
//         var title = titleEl.textContent.trim();
//         if (title !== "Top 10 Selling Products") return;
//         if (widget.dataset.scmDone) return;

//         frappe.call({
//             method: "scm_addon.chart_data.get_top_products_with_percent",
//             args: { time_range: "Today" },
//             callback: function(r) {
//                 if (!r.message) return;
//                 widget.dataset.scmDone = "1";
//                 scm_render(widget, r.message);
//             }
//         });

//     });
// }

// function scm_render(widget, data) {
//     var labels    = data.labels || [];
//     var quantities = data.quantities || [];

//     var COLORS = ["#4463F0","#29CD42","#FF6B6B","#FFA500","#9B59B6",
//                   "#1ABC9C","#E74C3C","#3498DB","#F39C12","#2ECC71"];

//     // Target the SVG/canvas area specifically
//     var targets = widget.querySelectorAll("svg, canvas, .frappe-chart, .chart-container");
//     var chartArea = targets.length ? targets[targets.length - 1].parentElement : widget.querySelector(".widget-body");
//     if (!chartArea) return;

//     chartArea.innerHTML = "";
//     chartArea.style.padding = "8px";

//     labels.forEach(function(label, i) {
//         var color   = COLORS[i % COLORS.length];
//         var qty     = quantities[i] || 0;
//         var r = 14;


//         var row = document.createElement("div");
//         row.style.cssText = "display:flex;align-items:center;gap:10px;padding:6px 8px;margin-bottom:6px;border-radius:6px;background:#f9f9f9;";
//         row.innerHTML =
//             '<svg width="36" height="36" viewBox="0 0 36 36">' +
//               '<circle cx="18" cy="18" r="' + r + '" fill="none" stroke="#e0e0e0" stroke-width="4"/>' +
//             '<circle cx="18" cy="18" r="' + r + '" fill="none" stroke="' + color + '" stroke-width="4"/>' +
//             '</svg>' +

//             '<div style="flex:1;min-width:0;">' +
//               '<div style="font-weight:600;font-size:13px;color:#333;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" title="' + label + '">' + label + '</div>' +
//               '<div style="font-size:11px;color:#888;">Quantity ' + Number(qty).toLocaleString() + '</div>' +
//             '</div>' +

//         chartArea.appendChild(row);
//     });
// }

// // Also trigger on route change
// frappe.router && frappe.router.on && frappe.router.on("change", function() {
//     setTimeout(scm_replace_charts, 1500);
// });
// setTimeout(scm_replace_charts, 2000);
