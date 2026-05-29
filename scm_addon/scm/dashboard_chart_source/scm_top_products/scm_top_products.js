// /* Copyright (c) 2026, VAPTECH */

// frappe.provide("frappe.dashboards.chart_sources");

// (function () {
//     function safeParse(data) {
//         try {
//             return typeof data === "string" ? JSON.parse(data) : data;
//         } catch (e) {
//             return data;
//         }
//     }

//     frappe.dashboards.chart_sources["SCM Top Products"] = {
//         method: "scm_addon.chart_data.get_top_products_with_percent",

//         filters: [
//             {
//                 fieldname: "time_range",
//                 label: __("Time Range"),
//                 fieldtype: "Select",
//                 options: [
//                     "Today",
//                     "Yesterday",
//                     "This Week",
//                     "Last Week",
//                     "This Month",
//                     "Last Month",
//                     "This Quarter",
//                     "This Year",
//                     "Last Year",
//                     "Custom",
//                 ].join("\n"),
//                 default: "Today",
//             },
//             {
//                 fieldname: "from_date",
//                 label: __("From Date"),
//                 fieldtype: "Date",
//             },
//             {
//                 fieldname: "to_date",
//                 label: __("To Date"),
//                 fieldtype: "Date",
//             },
//         ],

//         render: function (chart_container, data, chart_args) {
//             data = safeParse(data);

//             const labels   = data.labels || [];
//             const datasets = data.datasets || [];
//             const quantities = data.quantities || [];




//             const COLORS = [
//                 "#4463F0","#29CD42","#FF6B6B","#FFA500",
//                 "#9B59B6","#1ABC9C","#E74C3C","#3498DB",
//                 "#F39C12","#2ECC71"
//             ];

//             // Clear container
//             chart_container.innerHTML = "";

//             if (!labels.length) {
//                 chart_container.innerHTML = `
//                     <div style="display:flex;align-items:center;justify-content:center;height:200px;color:#888;">
//                         No data available
//                     </div>`;
//                 return;
//             }

//             // Build list
//             const list = document.createElement("div");
//             list.style.cssText = `
//                 display: flex;
//                 flex-direction: column;
//                 gap: 10px;
//                 padding: 8px 4px;
//                 max-height: 340px;
//                 overflow-y: auto;
//             `;

//             labels.forEach(function (label, i) {
//                 const color   = COLORS[i % COLORS.length];
//                 const qty     = quantities[i] || 0;


//                 const row = document.createElement("div");
//                 row.style.cssText = `
//                     display: flex;
//                     align-items: center;
//                     gap: 10px;
//                     padding: 6px 8px;
//                     border-radius: 6px;
//                     background: #f9f9f9;
//                 `;

//                 // Donut SVG (no percentage)
//                 const radius = 14;
//                 const donut  = `
//                     <svg width="36" height="36" viewBox="0 0 36 36">
//                         <circle cx="18" cy="18" r="${radius}"
//                             fill="none" stroke="#e0e0e0" stroke-width="4"/>
//                         <circle cx="18" cy="18" r="${radius}"
//                             fill="none" stroke="${color}" stroke-width="4"/>
//                     </svg>`;


//                 // Info block
//                 const info = `
//                     <div style="flex:1; min-width:0;">
//                         <div style="font-weight:600; font-size:13px; color:#333;
//                                     white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"
//                              title="${label}">${label}</div>
//                         <div style="font-size:11px; color:#888; margin-top:1px;">
//                             Quantity ${qty.toLocaleString()}
//                         </div>
//                     </div>`;

//                 row.innerHTML = donut + info;

//                 list.appendChild(row);
//             });

//             chart_container.appendChild(list);
//         },
//     };
// })();
