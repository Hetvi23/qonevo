// Copyright (c) 2025, Qonevo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Barcode Generator', {
    refresh: function(frm) {
        // Add custom buttons
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__('Regenerate Barcode'), function() {
                frm.call('regenerate_barcode').then(() => {
                    frm.reload_doc();
                });
            });
            
            frm.add_custom_button(__('Print Barcode'), function() {
                frm.call('print_barcode').then((r) => {
                    if (r.message) {
                        // Open print dialog
                        const print_content = `
                            <div style="text-align: center; padding: 20px;">
                                <h3>${r.message.item_code} - ${r.message.item_name}</h3>
                                <p>Model: ${r.message.model_number || 'N/A'}</p>
                                <p>Serial: ${r.message.serial_number || 'N/A'}</p>
                                <div style="margin: 20px 0;">
                                    ${r.message.barcode_image}
                                </div>
                                <p><strong>Barcode:</strong> ${r.message.barcode_string}</p>
                            </div>
                        `;
                        
                        const print_window = window.open('', '_blank');
                        print_window.document.write(print_content);
                        print_window.document.close();
                        print_window.print();
                    }
                });
            });
        }
    },
    
    item_code: function(frm) {
        if (frm.doc.item_code) {
            // Fetch item details
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Item',
                    name: frm.doc.item_code
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('model_number', r.message.default_manufacturer_part_no || '');
                        frm.set_value('item_name', r.message.item_name);
                        frm.set_value('item_group', r.message.item_group);
                        frm.set_value('stock_uom', r.message.stock_uom);
                        frm.set_value('description', r.message.description);
                        frm.set_value('brand', r.message.brand);
                        frm.set_value('standard_rate', r.message.standard_rate);
                    }
                }
            });
        }
    },
    
    barcode_type: function(frm) {
        if (frm.doc.item_code && frm.doc.barcode_type) {
            // Regenerate barcode when type changes
            frm.save();
        }
    }
});

// Add barcode scanner functionality
frappe.ui.form.on('Item Barcode Generator', {
    setup: function(frm) {
        // Add barcode scanner button
        frm.add_custom_button(__('Scan Barcode'), function() {
            // This would integrate with a barcode scanner
            // For now, we'll show a prompt for manual entry
            frappe.prompt({
                fieldname: 'scanned_barcode',
                fieldtype: 'Data',
                label: __('Enter Barcode'),
                reqd: 1
            }, function(values) {
                if (values.scanned_barcode) {
                    // Process scanned barcode
                    frappe.call({
                        method: 'qonevo.barcode_utils.scan_item_barcode',
                        args: {
                            barcode_string: values.scanned_barcode
                        },
                        callback: function(r) {
                            if (r.message && r.message.success) {
                                frm.set_value('item_code', r.message.item_code);
                                frm.set_value('model_number', r.message.model_number);
                                frm.set_value('serial_number', r.message.serial_number);
                                frm.set_value('item_name', r.message.item_name);
                                frm.set_value('item_group', r.message.item_group);
                                frm.set_value('stock_uom', r.message.stock_uom);
                                frm.set_value('description', r.message.description);
                                frm.set_value('brand', r.message.brand);
                                frm.set_value('standard_rate', r.message.standard_rate);
                                frm.save();
                            } else {
                                frappe.msgprint(__('Invalid barcode or item not found'));
                            }
                        }
                    });
                }
            });
        });
    }
});
