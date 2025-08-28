frappe.ui.form.on('Requirement Items', {
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code) {
            fetchItemDetails(frm, cdt, cdn);
        } else {
            // Clear item fields
            row.item_name = '';
            row.qty = '';
            row.rate = '';
            row.amount = '';
            frm.refresh_field('requirement_item');
        }
    },
    
    qty: function(frm, cdt, cdn) {
        calculateRowAmount(frm, cdt, cdn);
    },
    
    rate: function(frm, cdt, cdn) {
        calculateRowAmount(frm, cdt, cdn);
    }
});

function fetchItemDetails(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    frappe.call({
        method: 'qonevo.requirement_items.requirement_items.fetch_item_details',
        args: {
            docname: row.name
        },
        callback: function(r) {
            if (r.exc) {
                frappe.msgprint(__('Error: ') + r.exc);
            } else {
                frm.refresh_field('requirement_item');
            }
        }
    });
}

function calculateRowAmount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.qty && row.rate) {
        row.amount = row.qty * row.rate;
    } else {
        row.amount = 0;
    }
    frm.refresh_field('requirement_item');
} 