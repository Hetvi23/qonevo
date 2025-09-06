// Custom Barcode Scanner for ERPNext - Intercepts existing barcode field
frappe.provide("qonevo.custom_barcode_scanner");

qonevo.custom_barcode_scanner = {
    // Override the existing barcode scanning functionality
    override_barcode_scanner: function(frm, child_table = 'items') {
        console.log("Overriding barcode scanner for", frm.doctype);
        
        // Find the barcode input field - it's usually in the items table grid
        let barcode_field = null;
        
        // Try to find the scan_barcode field first
        if (frm.fields_dict['scan_barcode']) {
            barcode_field = frm.fields_dict['scan_barcode'];
            console.log("Found scan_barcode field");
        } else {
            // Try to find the barcode field in the items table grid
            let items_table = frm.fields_dict['items'];
            if (items_table && items_table.grid) {
                barcode_field = items_table.grid.get_field('barcode');
                console.log("Found barcode field in items grid");
            }
        }
        
        if (!barcode_field || !barcode_field.$input) {
            console.log("Barcode field not found, trying to find any input with barcode in name...");
            // Try to find any input field that might be the barcode field
            $('input[placeholder*="barcode"], input[placeholder*="Barcode"], input[name*="barcode"], input[name*="Barcode"]').each(function() {
                if ($(this).is(':visible')) {
                    barcode_field = { $input: $(this) };
                    console.log("Found barcode field by placeholder/name");
                    return false; // break the loop
                }
            });
        }
        
        if (!barcode_field || !barcode_field.$input) {
            console.log("Barcode field not found in any location");
            return;
        }
        
        console.log("Barcode field found, setting up event handlers");
        
        // Override the barcode input behavior
        barcode_field.$input.off('keypress.barcode').on('keypress.barcode', function(e) {
            if (e.which === 13) { // Enter key pressed
                e.preventDefault();
                e.stopPropagation();
                
                let barcode_value = $(this).val();
                console.log("Barcode scanned:", barcode_value);
                
                if (barcode_value) {
                    // Check if it's our custom format (contains |)
                    if (barcode_value.includes('|')) {
                        console.log("Custom barcode format detected, processing...");
                        qonevo.custom_barcode_scanner.process_barcode(frm, barcode_value, child_table);
                        $(this).val(''); // Clear the input
                        return false; // Prevent further processing
                    } else {
                        console.log("Standard barcode format, using original handler");
                        // Let the original ERPNext handler process it
                        // We don't interfere with standard barcodes
                    }
                }
            }
        });
        
        // Also override the change event to catch barcode scanning
        barcode_field.$input.off('change.barcode').on('change.barcode', function(e) {
            let barcode_value = $(this).val();
            if (barcode_value && barcode_value.includes('|')) {
                console.log("Custom barcode detected on change:", barcode_value);
                qonevo.custom_barcode_scanner.process_barcode(frm, barcode_value, child_table);
                $(this).val(''); // Clear the input
                return false; // Prevent further processing
            }
        });
        
        // Override the input event as well to catch all barcode scanning
        barcode_field.$input.off('input.barcode').on('input.barcode', function(e) {
            let barcode_value = $(this).val();
            if (barcode_value && barcode_value.includes('|') && barcode_value.length > 10) {
                console.log("Custom barcode detected on input:", barcode_value);
                qonevo.custom_barcode_scanner.process_barcode(frm, barcode_value, child_table);
                $(this).val(''); // Clear the input
                return false; // Prevent further processing
            }
        });
        
        
        console.log("Barcode scanner override applied successfully");
    },
    
    // Process the scanned barcode
    process_barcode: function(frm, barcode_string, child_table) {
        console.log("Processing barcode:", barcode_string);
        
        // Call our barcode scanning API
        frappe.call({
            method: "qonevo.barcode_utils.scan_item_barcode",
            args: {
                barcode_string: barcode_string
            },
            callback: function(r) {
                console.log("API Response:", r);
                if (r.message && r.message.success) {
                    console.log("Success! Adding item to table...");
                    qonevo.custom_barcode_scanner.add_item_to_table(frm, child_table, r.message);
                    frappe.show_alert({
                        message: `Item ${r.message.item_code} added successfully!`,
                        indicator: 'green'
                    });
                } else {
                    console.log("API failed:", r.message);
                    frappe.show_alert({
                        message: `Barcode not found: ${barcode_string}`,
                        indicator: 'red'
                    });
                }
            },
            error: function(err) {
                console.log("API Error:", err);
                frappe.show_alert({
                    message: `Error scanning barcode: ${err.message || 'Unknown error'}`,
                    indicator: 'red'
                });
            }
        });
    },
    
    // Add item to the specified table
    add_item_to_table: function(frm, child_table, item_data) {
        console.log("Adding item to table:", child_table, item_data);
        
        // Check if item already exists in the table
        let existing_row = frm.doc[child_table].find(row => 
            row.item_code === item_data.item_code && 
            row.serial_no === item_data.serial_number
        );
        
        if (existing_row) {
            // Update quantity if item exists
            frappe.model.set_value(existing_row.doctype, existing_row.name, 'qty', 
                (existing_row.qty || 0) + 1);
            console.log("Updated existing item quantity");
        } else {
            // Add new item
            let new_row = frm.add_child(child_table);
            frappe.model.set_value(new_row.doctype, new_row.name, 'item_code', item_data.item_code);
            frappe.model.set_value(new_row.doctype, new_row.name, 'qty', 1);
            
            // Add serial number if available
            if (item_data.serial_number) {
                frappe.model.set_value(new_row.doctype, new_row.name, 'serial_no', item_data.serial_number);
            }
            
            // Add model number to description if available
            if (item_data.model_number && item_data.model_number !== 'NO-MODEL') {
                frappe.model.set_value(new_row.doctype, new_row.name, 'description', 
                    `${item_data.item_name} - Model: ${item_data.model_number}`);
            }
            
            // Trigger item code change to populate other fields
            frappe.model.trigger('item_code', new_row.doctype, new_row.name);
            console.log("Added new item to table");
        }
        
        frm.refresh_field(child_table);
    }
};

// Override barcode scanner for Delivery Note
frappe.ui.form.on('Delivery Note', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            // Wait a bit for the form to be fully loaded
            setTimeout(function() {
                qonevo.custom_barcode_scanner.override_barcode_scanner(frm, 'items');
            }, 1000);
        }
    }
});

// Override barcode scanner for Purchase Receipt
frappe.ui.form.on('Purchase Receipt', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            setTimeout(function() {
                qonevo.custom_barcode_scanner.override_barcode_scanner(frm, 'items');
            }, 1000);
        }
    }
});

// Override barcode scanner for Stock Entry
frappe.ui.form.on('Stock Entry', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            setTimeout(function() {
                qonevo.custom_barcode_scanner.override_barcode_scanner(frm, 'items');
            }, 1000);
        }
    }
});

// Override barcode scanner for Material Request
frappe.ui.form.on('Material Request', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            setTimeout(function() {
                qonevo.custom_barcode_scanner.override_barcode_scanner(frm, 'items');
            }, 1000);
        }
    }
});

// Override barcode scanner for Purchase Order
frappe.ui.form.on('Purchase Order', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            setTimeout(function() {
                qonevo.custom_barcode_scanner.override_barcode_scanner(frm, 'items');
            }, 1000);
        }
    }
});

// Override barcode scanner for Sales Order
frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            setTimeout(function() {
                qonevo.custom_barcode_scanner.override_barcode_scanner(frm, 'items');
            }, 1000);
        }
    }
});
