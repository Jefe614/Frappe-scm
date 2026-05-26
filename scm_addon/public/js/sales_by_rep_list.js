// frappe.listview_settings["Sales By Rep"] = {
//     hide_name_column: true,

//     // Explicitly define which fields to show and their widths
//     add_fields: ["sales_person", "sales_target", "qty_target", "sales", "qty_sold", "customers_in_route", "visits"],

//     onload: function(listview) {
//         // Remove the Tags filter from sidebar
//         listview.filter_area && listview.filter_area.$filter_list_wrapper &&
//             listview.filter_area.$filter_list_wrapper.find('[data-fieldname="_user_tags"]').closest('.form-group').remove();

//         applyStyles();

//         // Re-apply after Frappe re-renders
//         [300, 700, 1500].forEach(t => setTimeout(applyStyles, t));

//         listview.page.wrapper.on("after-refresh", applyStyles);
//     },

//     formatters: {
//         sales_target: (value) => format_currency(value, "KES"),
//         sales: (value) => format_currency(value, "KES"),
//     }
// };

// function applyStyles() {
//     $("#sbr-style").remove();
//     $("head").append(`
//         <style id="sbr-style">
//             /* ── Scrollable container ── */
//             [data-list-renderer="Sales By Rep"] .frappe-list,
//             .frappe-list {
//                 overflow-x: auto !important;
//             }

//             /* ── No wrapping on rows ── */
//             .list-row-head .level-left,
//             .list-row .level-left {
//                 flex-wrap: nowrap !important;
//                 display: flex !important;
//                 align-items: center !important;
//                 width: 100% !important;
//             }

//             /* ── Column sizing ── */
//             .list-row-col {
//                 flex: 1 1 120px !important;
//                 min-width: 110px !important;
//                 max-width: 200px !important;
//                 padding: 8px 12px !important;
//                 white-space: nowrap !important;
//                 overflow: hidden !important;
//                 text-overflow: ellipsis !important;
//                 border-right: 1px solid var(--border-color) !important;
//             }
//             .list-row-col:last-child { border-right: none !important; }

//             /* ── Header styling ── */
//             .list-row-head {
//                 background: var(--control-bg) !important;
//                 border-bottom: 2px solid var(--border-color) !important;
//                 font-weight: 600 !important;
//             }

//             /* ── Row hover ── */
//             .list-row-container:hover {
//                 background: var(--bg-light-blue) !important;
//             }

//             /* ── Hide Tags column (both header & data cells) ── */
//             .list-row-head .list-row-col:has(.tag-col),
//             .list-row-col.tag-col,
//             .list-row-col[data-col="tag"],
//             .column-tag,
//             .list-header-subject + .list-row-col:nth-child(2) {
//                 display: none !important;
//             }

//             /* ── Hide indicator pills ── */
//             .list-row-col .indicator-pill,
//             .list-row-col .indicator {
//                 display: none !important;
//             }

//             /* ── Ensure hidden-xs cols are visible on desktop ── */
//             @media (min-width: 768px) {
//                 .list-row-col.hidden-xs {
//                     display: flex !important;
//                     visibility: visible !important;
//                 }
//             }

//             /* ── Table border ── */
//             .frappe-list .list-row-container {
//                 border-bottom: 1px solid var(--border-color) !important;
//             }
//         </style>
//     `);

//     // Directly hide tag-related elements via jQuery
//     $(".list-row-col").each(function() {
//         const text = $(this).find(".list-row-col-info, span").text().trim().toLowerCase();
//         if ($(this).hasClass("tag-col") || $(this).find(".tag-col").length) {
//             $(this).hide();
//         }
//     });

//     $(".list-row-head .list-row-col").each(function() {
//         if ($(this).find(".tag-col, [data-fieldname='_user_tags']").length) {
//             $(this).hide();
//         }
//     });
// }
