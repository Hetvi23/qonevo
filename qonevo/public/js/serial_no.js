frappe.ui.form.on('Serial No', {
    refresh(frm) {
        if (frm.is_new() && frm.doc.item_code) {
            frappe.db.get_doc('Item', frm.doc.item_code)
                .then(item => {
                    if (!frm.doc.custom_model_number && item.custom_default_model_number) {
                        frm.set_value('custom_model_number', item.custom_default_model_number);
                    }
                    if (!frm.doc.custom_size && item.custom_default_size) {
                        frm.set_value('custom_size', item.custom_default_size);
                    }
                });
        }
    },

    item_code(frm) {
        if (frm.doc.item_code) {
            frappe.db.get_doc('Item', frm.doc.item_code)
                .then(item => {
                    if (item.custom_default_model_number) {
                        frm.set_value('custom_model_number', item.custom_default_model_number);
                    }
                    if (item.custom_default_size) {
                        frm.set_value('custom_size', item.custom_default_size);
                    }
                });
        }
    }
});
