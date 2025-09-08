// Copyright (c) 2025, Hetvi Patel and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Requirement Gathering", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Requirement Gathering', {
    refresh: function(frm) {
        // Prevent infinite refresh loop by checking if we've already processed this refresh
        if (frm._refresh_processed) return;
        frm._refresh_processed = true;
        
        // Reset the flag after a short delay
        setTimeout(function() {
            frm._refresh_processed = false;
        }, 1000);
        
        // Show Create Purchase Order button if there are approved items and no PO exists
        let hasApprovedItems = false;
        if (frm.doc.requirement_item) {
            hasApprovedItems = frm.doc.requirement_item.some(item => item.select_ircl === 'Approved');
        }
        
        if (hasApprovedItems && !frm.doc.purchase_order_ref) {
            frm.add_custom_button(__('Create Purchase Order'), function() {
                createPurchaseOrder(frm);
            }, __('Actions'));
        }
        
        // Show Create Purchase Receipt button if PO exists but no PR exists
        if (frm.doc.purchase_order_ref && !frm.doc.purchase_receipt_ref) {
            frm.add_custom_button(__('Create Purchase Receipt'), function() {
                createPurchaseReceipt(frm);
            }, __('Actions'));
        }
        
        // Add Approve All button to Actions menu
        if (frm.doc.requirement_item && frm.doc.requirement_item.length > 0) {
            frm.add_custom_button(__('Approve All Items'), function() {
                approveAllItems(frm);
            }, __('Actions'));
        }
        
        // Add manual supplier details fetch button for testing
        if (frm.doc.supplier) {
            frm.add_custom_button(__('Refresh Supplier Details'), function() {
                fetchSupplierDetails(frm);
            }, __('Actions'));
        }
    },
    
    supplier: function(frm) {
        // Clear supplier-related fields when supplier changes
        frm.set_value('supplier_name', '');
        frm.set_value('supplier_address', '');
        frm.set_value('contact_person', '');
        frm.set_value('gstin', '');
        frm.set_value('payment_terms', '');
        frm.set_value('supply_terms', '');
        frm.set_value('transport_details', '');
        
        // Fetch supplier details if supplier is selected
        if (frm.doc.supplier) {
            fetchSupplierDetails(frm);
        }
    }
});

frappe.ui.form.on('Requirement Items', {
    
    item_code: function(frm, cdt, cdn) {
        // Clear item fields when item_code changes
        let row = locals[cdt][cdn];
        row.item_name = '';
        row.qty = '';
        row.rate = '';
        row.amount = '';
        frm.refresh_field('requirement_item');
        
        // Fetch item details if item_code is selected
        if (row.item_code) {
            fetchItemDetails(frm, cdt, cdn);
        }
    },
    
    qty: function(frm, cdt, cdn) {
        calculateRowAmount(frm, cdt, cdn);
    },
    
    rate: function(frm, cdt, cdn) {
        calculateRowAmount(frm, cdt, cdn);
    },
    
    gst: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        // Validate GST percentage (should be between 0 and 100)
        if (row.gst && (row.gst < 0 || row.gst > 100)) {
            frappe.msgprint(__('GST percentage should be between 0 and 100'));
            row.gst = 0;
        }
        calculateRowAmount(frm, cdt, cdn);
    }
});

function fetchSupplierDetails(frm) {
    // Don't call server method if document is not saved yet
    if (frm.doc.name && !frm.doc.name.startsWith('new-')) {
        frappe.call({
            method: 'qonevo.qonevo.doctype.requirement_gathering.requirement_gathering.fetch_supplier_details',
            args: {
                docname: frm.doc.name
            },
            callback: function(r) {
                if (r.exc) {
                    frappe.msgprint(__('Error: ') + r.exc);
                } else {
                    frm.refresh();
                }
            }
        });
    } else {
        // For new documents, fetch supplier details directly
        if (frm.doc.supplier) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Supplier',
                    name: frm.doc.supplier
                },
                callback: function(r) {
                    if (r.message) {
                        let supplier = r.message;
                        frm.set_value('supplier_name', supplier.supplier_name || '');
                        
                        // Fetch address if exists
                        if (supplier.supplier_primary_address) {
                            frappe.call({
                                method: 'frappe.client.get',
                                args: {
                                    doctype: 'Address',
                                    name: supplier.supplier_primary_address
                                },
                                callback: function(addr_r) {
                                    if (addr_r.message) {
                                        let address = addr_r.message;
                                        let address_parts = [];
                                        if (address.address_line1) address_parts.push(address.address_line1);
                                        if (address.city) address_parts.push(address.city);
                                        if (address.state) address_parts.push(address.state);
                                        if (address.pincode) address_parts.push(address.pincode);
                                        let address_str = address_parts.join(', ');
                                        frm.set_value('supplier_address', address_str);
                                    }
                                }
                            });
                        }
                        
                        // Fetch contact if exists
                        if (supplier.supplier_primary_contact) {
                            frappe.call({
                                method: 'frappe.client.get',
                                args: {
                                    doctype: 'Contact',
                                    name: supplier.supplier_primary_contact
                                },
                                callback: function(contact_r) {
                                    if (contact_r.message) {
                                        let contact = contact_r.message;
                                        let contact_name = contact.first_name || '';
                                        if (contact.last_name) contact_name += ' ' + contact.last_name;
                                        contact_name = contact_name.trim();
                                        frm.set_value('contact_person', contact_name);
                                    }
                                }
                            });
                        }
                        
                        // Set other fields
                        frm.set_value('gstin', supplier.tax_id || '');
                        frm.set_value('payment_terms', supplier.payment_terms || '');
                        frm.set_value('supply_terms', '');
                        frm.set_value('transport_details', '');
                    }
                }
            });
        }
    }
}

function fetchItemDetails(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    
    // For new rows that don't have a name yet, handle client-side
    if (!row.name || row.name.startsWith('new-')) {
        if (row.item_code) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Item',
                    name: row.item_code
                },
                callback: function(r) {
                    if (r.message) {
                        let item = r.message;
                        row.item_name = item.item_name || '';
                        
                        // Try to get default buying rate from Item Price
                        frappe.call({
                            method: 'frappe.client.get_list',
                            args: {
                                doctype: 'Item Price',
                                filters: {
                                    item_code: row.item_code,
                                    price_list: 'Standard Buying'
                                },
                                fields: ['price_list_rate'],
                                limit: 1
                            },
                            callback: function(price_r) {
                                if (price_r.message && price_r.message.length > 0) {
                                    row.rate = price_r.message[0].price_list_rate || 0;
                                } else {
                                    row.rate = item.standard_rate || 0;
                                }
                                
                                // Calculate amount (including GST)
                                calculateRowAmount(frm, cdt, cdn);
                                frm.refresh_field('requirement_item');
                            }
                        });
                    }
                }
            });
        }
    } else {
        // For existing rows, use server method
        frappe.call({
            method: 'qonevo.qonevo.doctype.requirement_items.requirement_items.fetch_item_details',
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
}

function calculateRowAmount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.qty && row.rate) {
        let base_amount = row.qty * row.rate;
        let gst_percentage = parseFloat(row.gst) || 0;
        let gst_amount = (base_amount * gst_percentage) / 100;
        row.gst_amount = gst_amount;
        row.amount = base_amount + gst_amount;
    } else {
        row.gst_amount = 0;
        row.amount = 0;
    }
    frm.refresh_field('requirement_item');
}













function approveAllItems(frm) {
    frappe.confirm(__('Are you sure you want to approve all items?'), function() {
        frappe.call({
            method: 'qonevo.qonevo.doctype.requirement_gathering.requirement_gathering.approve_items',
            args: {
                docname: frm.doc.name,
                all: true
            },
            callback: function(r) {
                if (r.exc) {
                    frappe.msgprint(__('Error: ') + r.exc);
                } else {
                    frm.reload_doc();
                    frappe.show_alert(__('All items approved successfully'), 3);
                }
            }
        });
    });
}

function rejectAllItems(frm) {
    frappe.confirm(__('Are you sure you want to reject all items?'), function() {
        frappe.call({
            method: 'qonevo.qonevo.doctype.requirement_gathering.requirement_gathering.reject_items',
            args: {
                docname: frm.doc.name,
                all: true
            },
            callback: function(r) {
                if (r.exc) {
                    frappe.msgprint(__('Error: ') + r.exc);
                } else {
                    frm.reload_doc();
                    frappe.show_alert(__('All items rejected successfully'), 3);
                }
            }
        });
    });
}

function createPurchaseOrder(frm) {
    frappe.confirm(__('Are you sure you want to create a Purchase Order?'), function() {
        // Save the document first to ensure GST calculations are saved
        frm.save().then(function() {
            frappe.call({
                method: 'qonevo.qonevo.doctype.requirement_gathering.requirement_gathering.create_purchase_order',
                args: {
                    docname: frm.doc.name
                },
                callback: function(r) {
                    if (r.exc) {
                        frappe.msgprint(__('Error: ') + r.exc);
                    } else {
                        frm.reload_doc();
                        frappe.show_alert(__('Purchase Order created successfully as Draft'), 3);
                    }
                }
            });
        });
    });
}

function createPurchaseReceipt(frm) {
    // Get PO items first
    frappe.call({
        method: 'qonevo.qonevo.doctype.requirement_gathering.requirement_gathering.get_purchase_order_items',
        args: {
            docname: frm.doc.name
        },
        callback: function(r) {
            if (r.exc) {
                frappe.msgprint(__('Error: ') + r.exc);
            } else {
                showPurchaseReceiptDialog(frm, r.message);
            }
        }
    });
}

function showPurchaseReceiptDialog(frm, po_items) {
    let dialog = new frappe.ui.Dialog({
        title: __('Create Purchase Receipt'),
        fields: [
            {
                fieldtype: 'HTML',
                fieldname: 'items_html',
                options: generateItemsHTML(po_items)
            },
            {
                fieldtype: 'Text Editor',
                fieldname: 'remarks',
                label: __('Remarks'),
                description: __('Optional remarks for the purchase receipt')
            }
        ],
        primary_action_label: __('Create Receipt'),
        primary_action: function() {
            let items_data = [];
            let $dialog = dialog.$wrapper;
            
            // Collect data from form
            po_items.forEach(function(item, idx) {
                let accepted_qty = parseFloat($dialog.find(`[data-fieldname="accepted_qty_${idx}"]`).val()) || 0;
                let rejected_qty = parseFloat($dialog.find(`[data-fieldname="rejected_qty_${idx}"]`).val()) || 0;
                
                items_data.push({
                    item_code: item.item_code,
                    item_name: item.item_name,
                    accepted_qty: accepted_qty,
                    rejected_qty: rejected_qty,
                    rate: item.rate,
                    po_item: item.po_item
                });
            });
            
            let remarks = $dialog.find('[data-fieldname="remarks"]').val();
            
            // Create purchase receipt
            frappe.call({
                method: 'qonevo.qonevo.doctype.requirement_gathering.requirement_gathering.create_purchase_receipt',
                args: {
                    docname: frm.doc.name,
                    items_data: items_data
                },
                callback: function(r) {
                    if (r.exc) {
                        frappe.msgprint(__('Error: ') + r.exc);
                    } else {
                        dialog.hide();
                        frm.reload_doc();
                        frappe.show_alert(__('Purchase Receipt created successfully'), 3);
                    }
                }
            });
        }
    });
    
    dialog.show();
}

function generateItemsHTML(po_items) {
    let html = `
        <div class="form-group">
            <label class="control-label">Items</label>
            <div class="table-responsive">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Item Code</th>
                            <th>Item Name</th>
                            <th>Ordered Qty</th>
                            <th>Rate</th>
                            <th>Accepted Qty</th>
                            <th>Rejected Qty</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    po_items.forEach(function(item, idx) {
        html += `
            <tr>
                <td>${item.item_code}</td>
                <td>${item.item_name}</td>
                <td>${item.ordered_qty}</td>
                <td>${item.rate}</td>
                <td>
                    <input type="number" class="form-control" 
                           data-fieldname="accepted_qty_${idx}" 
                           value="${item.ordered_qty}" 
                           min="0" max="${item.ordered_qty}">
                </td>
                <td>
                    <input type="number" class="form-control" 
                           data-fieldname="rejected_qty_${idx}" 
                           value="0" 
                           min="0" max="${item.ordered_qty}">
                </td>
            </tr>
        `;
    });
    
    html += `
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    return html;
}
