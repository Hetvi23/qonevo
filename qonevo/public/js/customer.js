// Copyright (c) 2025, Qonevo and contributors

frappe.ui.form.on('Customer', {
    refresh: function (frm) {
        if (!frm.is_new()) {
            frm.trigger('render_connection_dashboard');
        }
    },

    render_connection_dashboard: function (frm) {
        frappe.call({
            method: 'qonevo.api.get_customer_connections_html',
            args: {
                customer: frm.doc.name
            },
            callback: function (r) {
                if (r.message) {
                    if (frm.fields_dict.connection && frm.fields_dict.connection.wrapper) {
                        $(frm.fields_dict.connection.wrapper).html(r.message);
                    }
                }
            }
        });
    }
});
