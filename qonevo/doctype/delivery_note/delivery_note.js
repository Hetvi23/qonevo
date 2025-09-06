frappe.ui.form.on('Delivery Note', {
    refresh: function(frm) {
        console.log("Delivery Note client script loaded!");
        // Add custom barcode scanning functionality
        if (frm.doc.docstatus === 0) { // Only for draft documents
            console.log("Adding custom barcode scanner...");
            add_custom_barcode_scanner(frm);
        }
    }
});

function add_custom_barcode_scanner(frm) {
    console.log("Adding custom barcode scanner function...");
    
    // Wait a bit for the form to be fully loaded
    setTimeout(function() {
        // Find the barcode input field
        let barcode_field = frm.fields_dict['scan_barcode'];
        console.log("Barcode field found:", barcode_field);
        
        if (barcode_field && barcode_field.$input) {
            console.log("Barcode input found, adding event listeners...");
            
            // Override the barcode scanning behavior
            barcode_field.$input.on('keypress', function(e) {
                if (e.which === 13) { // Enter key pressed
                    e.preventDefault();
                    let barcode_value = $(this).val();
                    console.log("Barcode entered:", barcode_value);
                    if (barcode_value) {
                        scan_custom_barcode(frm, barcode_value);
                        $(this).val(''); // Clear the input
                    }
                }
            });
            
            // Add a custom button for our barcode scanner
            if (frm.fields_dict['scan_barcode'].$wrapper) {
                console.log("Adding custom scan button...");
                let custom_btn = $(`<button class="btn btn-sm btn-primary" style="margin-left: 5px;">
                    <i class="fa fa-barcode"></i> Custom Scan
                </button>`);
                
                custom_btn.click(function() {
                    let barcode_value = barcode_field.get_value();
                    console.log("Custom scan button clicked, barcode:", barcode_value);
                    if (barcode_value) {
                        scan_custom_barcode(frm, barcode_value);
                        barcode_field.set_value('');
                    }
                });
                
                frm.fields_dict['scan_barcode'].$wrapper.append(custom_btn);
                console.log("Custom scan button added!");
            }
        } else {
            console.log("Barcode field not found or not ready");
        }
    }, 1000); // Wait 1 second for form to load
}

function scan_custom_barcode(frm, barcode_string) {
    // Call our custom barcode scanning API
    frappe.call({
        method: "qonevo.barcode_utils.scan_item_barcode",
        args: {
            barcode_string: barcode_string
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                // Add item to the table
                add_item_to_delivery_note(frm, r.message);
                frappe.show_alert({
                    message: `Item ${r.message.item_code} added successfully!`,
                    indicator: 'green'
                });
            } else {
                frappe.show_alert({
                    message: `Barcode not found: ${barcode_string}`,
                    indicator: 'red'
                });
            }
        }
    });
}

function add_item_to_delivery_note(frm, item_data) {
    // Check if item already exists in the table
    let existing_row = frm.doc.items.find(row => 
        row.item_code === item_data.item_code && 
        row.serial_no === item_data.serial_number
    );
    
    if (existing_row) {
        // Update quantity if item exists
        frappe.model.set_value(existing_row.doctype, existing_row.name, 'qty', 
            (existing_row.qty || 0) + 1);
    } else {
        // Add new item
        let new_row = frm.add_child('items');
        frappe.model.set_value(new_row.doctype, new_row.name, 'item_code', item_data.item_code);
        frappe.model.set_value(new_row.doctype, new_row.name, 'qty', 1);
        frappe.model.set_value(new_row.doctype, new_row.name, 'serial_no', item_data.serial_number);
        
        // Set model number if available
        if (item_data.model_number && item_data.model_number !== 'NO-MODEL') {
            frappe.model.set_value(new_row.doctype, new_row.name, 'description', 
                `${item_data.item_name} - Model: ${item_data.model_number}`);
        }
        
        // Trigger item code change to populate other fields
        frappe.model.trigger('item_code', new_row.doctype, new_row.name);
    }
    
    frm.refresh_field('items');
}
