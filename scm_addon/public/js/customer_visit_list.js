frappe.listview_settings["Customer Visit"] = {
    onload: function(listview) {
        console.log("LIST JS LOADED ✓");

        // Remove Add Customer Visit button
        listview.page.clear_primary_action();
        $(".btn-primary:contains('Add Customer Visit')").hide();

        setTimeout(function() {
            $(`<style>
                .frappe-list {
                    overflow-x: auto !important;
                    display: block !important;
                }
                .list-row-head,
                .list-row-container,
                .list-row {
                    min-width: 1400px !important;
                    flex-wrap: nowrap !important;
                }
                .list-row-col.hidden-xs,
                .list-row-head .list-row-col.hidden-xs {
                    display: flex !important;
                    visibility: visible !important;
                }
                .list-row-col {
                    flex-shrink: 0 !important;
                    min-width: 120px !important;
                }
                .list-row-col.list-subject {
                    min-width: 180px !important;
                }
                .list-row-col.tag-col,
                .list-row-head .list-row-col.tag-col {
                    display: none !important;
                    width: 0 !important;
                    min-width: 0 !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    overflow: hidden !important;
                }
                .btn-orders {
                    font-size: 11px;
                    padding: 2px 8px;
                    border-radius: 4px;
                    margin-right: 8px;
                }
                .so-status-badge {
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 600;
                }
                .so-status-draft     { background:#f0f0f0; color:#666; }
                .so-status-pending   { background:#fff3cd; color:#856404; }
                .so-status-to-deliver { background:#cce5ff; color:#004085; }
                .so-status-completed { background:#d4edda; color:#155724; }
                .so-status-cancelled { background:#f8d7da; color:#721c24; }
            </style>`).appendTo("head");

            // ✅ Add Orders column header
            $(".list-row-head .list-row-activity").before(
                `<div class="list-row-col hidden-xs" style="min-width:120px; font-weight:600;">Orders</div>`
            );

            // Add Orders button to each row
            $(".list-row-container").each(function() {
                let row = $(this);
                let href = row.find("a.ellipsis").attr("href") || "";
                let name = href.split("/").pop();

                if (name && name.startsWith("CUST-VISIT-")) {
                    let btn = $(`<button class="btn btn-default btn-sm btn-orders"
                        data-name="${name}">Orders</button>`);

                    btn.on("click", function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        show_orders_modal(name);
                    });

                    row.find(".list-row-activity").before(btn);
                }
            });

        }, 800);

        listview.page.add_inner_button(__("Map View"), function() {
            frappe.set_route("app", "customer-visit-map");
        });
    },

    hide_name_column: true
};

// Form view — read only, no edit/create
frappe.ui.form.on("Customer Visit", {
    refresh: function(frm) {
        frm.disable_form();
        frm.page.clear_primary_action();
        frm.page.clear_secondary_action();
        $(".btn-edit").hide();
        $(".page-actions .btn-primary").hide();
    }
});

function get_status_badge(status) {
    let cls = "so-status-" + (status || "draft").toLowerCase().replace(/ /g, "-");
    return `<span class="so-status-badge ${cls}">${status || "Draft"}</span>`;
}

function show_orders_modal(docname) {
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Customer Visit",
            name: docname
        },
        callback: function(r) {
            if (!r.message) return;

            let doc = r.message;
            let customer = doc.customer;
            let order_number = doc.order_number;

            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Sales Order",
                    filters: [
                        ["customer", "=", customer],
                        ["name", "=", order_number]
                    ],
                    fields: ["name", "transaction_date", "customer", "status", "grand_total"],
                    limit: 50,
                    order_by: "transaction_date desc"
                },
                callback: function(res) {
                    let orders = res.message || [];

                    if (orders.length === 0 && order_number) {
                        frappe.call({
                            method: "frappe.client.get_list",
                            args: {
                                doctype: "Sales Order",
                                filters: [["customer", "=", customer]],
                                fields: ["name", "transaction_date", "customer", "status", "grand_total"],
                                limit: 50,
                                order_by: "transaction_date desc"
                            },
                            callback: function(res2) {
                                render_orders_modal(docname, res2.message || []);
                            }
                        });
                    } else {
                        render_orders_modal(docname, orders);
                    }
                }
            });
        }
    });
}

function render_orders_modal(docname, orders) {
    let rows = "";

    if (orders.length === 0) {
        rows = `<tr>
            <td colspan="5" class="text-center text-muted" style="padding:20px;">
                No Sales Orders found
            </td>
        </tr>`;
    } else {
        orders.forEach(function(so) {
            rows += `
                <tr>
                    <td>${frappe.datetime.str_to_user(so.transaction_date) || "—"}</td>
                    <td>
                        <a href="/app/sales-order/${so.name}" target="_blank">
                            ${so.name}
                        </a>
                    </td>
                    <td>${so.customer || "—"}</td>
                    <td>${get_status_badge(so.status)}</td>
                    <td style="text-align:right">
                        ${frappe.format(so.grand_total, {fieldtype: "Currency"})}
                    </td>
                </tr>`;
        });
    }

    let d = new frappe.ui.Dialog({
        title: __("Sales Orders"),
        size: "large",
        fields: [{ fieldtype: "HTML", fieldname: "orders_html" }],
        primary_action_label: __("OK"),
        primary_action: function() { d.hide(); },
        secondary_action_label: __("Cancel"),
        secondary_action: function() { d.hide(); }
    });

    d.fields_dict.orders_html.$wrapper.html(`
        <table class="table table-bordered" style="margin-bottom:0">
            <thead style="background:#f8f9fa;">
                <tr>
                    <th>Date</th>
                    <th>Voucher No.</th>
                    <th>Customer</th>
                    <th>Status</th>
                    <th style="text-align:right">Total</th>
                </tr>
            </thead>
            <tbody>${rows}</tbody>
        </table>
    `);

    d.show();
}
