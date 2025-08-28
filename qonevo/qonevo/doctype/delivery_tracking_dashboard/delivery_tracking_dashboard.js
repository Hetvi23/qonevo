// Copyright (c) 2025, Qonevo and contributors
// License: MIT. See LICENSE

frappe.ui.form.on("Delivery Tracking Dashboard", {
    refresh: function (frm) {
        frm.add_custom_button(__("Show Dashboard"), () =>
            frappe.set_route("delivery-tracking-dashboard", frm.doc.name)
        );

        if (!frappe.boot.developer_mode && frm.doc.is_standard) {
            frm.disable_form();
        }

        frm.set_query("chart", "charts", function () {
            return {
                filters: {
                    is_public: 1,
                },
            };
        });

        frm.set_query("card", "cards", function () {
            return {
                filters: {
                    is_public: 1,
                },
            };
        });
    },
}); 