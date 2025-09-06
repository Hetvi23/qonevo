// Clean Barcode Scanner for ERPNext - Override original scanner
frappe.provide("qonevo.clean_barcode_scanner");

qonevo.clean_barcode_scanner = {
    // Override the original scan barcode field behavior
    override_scan_barcode_field: function(frm, child_table = 'items') {
        console.log("Overriding scan barcode field for", frm.doctype);
        
        // Wait for the form to be fully loaded
        setTimeout(function() {
            // Find the original scan barcode field
            let scan_barcode_field = frm.fields_dict['scan_barcode'];
            if (scan_barcode_field) {
                console.log("Found original scan barcode field, overriding...");
                
                // Update the placeholder text to show our format
                scan_barcode_field.$input.attr('placeholder', 'Scan or type: ITEM_CODE|MODEL|SERIAL_NUMBER');
                
                // Add help text and scanner button below the field
                let help_text = `
                    <div class="help-block" style="margin-top: 5px; font-size: 12px; color: #666;">
                        <i class="fa fa-info-circle"></i> 
                        Format: <code>ITEM_CODE|MODEL|SERIAL_NUMBER</code> | 
                        Example: <code>TEST-ITEM-001|MODEL-123|SERIAL-456</code>
                    </div>
                    <div style="margin-top: 8px;">
                        <button type="button" class="btn btn-primary btn-sm" id="open-camera-scanner">
                            <i class="fa fa-camera"></i> Open Scanner
                        </button>
                    </div>
                `;
                
                // Add help text if not already present
                if (!scan_barcode_field.$wrapper.find('.help-block').length) {
                    scan_barcode_field.$wrapper.append(help_text);
                }
                
                // Override the original field's behavior
                scan_barcode_field.$input.off('keypress').on('keypress', function(e) {
                    if (e.which === 13) { // Enter key
                        e.preventDefault();
                        e.stopPropagation();
                        let barcode_value = $(this).val().trim();
                        if (barcode_value) {
                            qonevo.clean_barcode_scanner.process_barcode_direct(frm, child_table, barcode_value);
                            $(this).val(''); // Clear after processing
                        }
                        return false;
                    }
                });
                
                // Override change event
                scan_barcode_field.$input.off('change').on('change', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    let barcode_value = $(this).val().trim();
                    if (barcode_value) {
                        qonevo.clean_barcode_scanner.process_barcode_direct(frm, child_table, barcode_value);
                        $(this).val(''); // Clear after processing
                    }
                    return false;
                });
                
                // Override input event
                scan_barcode_field.$input.off('input').on('input', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                });
                
                // Add camera scanner event handler
                $('#open-camera-scanner').on('click', function() {
                    qonevo.clean_barcode_scanner.open_camera_scanner(frm, child_table);
                });
                
                console.log("Original scan barcode field overridden successfully");
            } else {
                console.log("Original scan barcode field not found, trying alternative approach...");
                // Fallback: add a simple input field near the items table
                qonevo.clean_barcode_scanner.add_fallback_scanner(frm, child_table);
            }
        }, 1000);
    },
    
    // Fallback method if original field not found
    add_fallback_scanner: function(frm, child_table) {
        if (frm.fields_dict[child_table]) {
            let fallback_html = `
                <div class="form-group" style="margin: 10px 0; padding: 15px; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #007bff;">
                    <label style="font-weight: 500; margin-bottom: 10px; display: block; color: #007bff;">
                        <i class="fa fa-barcode"></i> Custom Barcode Scanner
                    </label>
                    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 10px;">
                        <input type="text" 
                               class="form-control" 
                               id="fallback-barcode-input" 
                               placeholder="Scan or type: ITEM_CODE|MODEL|SERIAL_NUMBER"
                               style="flex: 1; font-family: monospace; font-size: 14px;">
                        <button class="btn btn-primary btn-sm" id="fallback-scan-btn">
                            <i class="fa fa-search"></i> Scan
                        </button>
                    </div>
                    <div style="text-align: center;">
                        <button class="btn btn-primary btn-sm" id="fallback-camera-btn">
                            <i class="fa fa-camera"></i> Open Scanner
                        </button>
                    </div>
                    <small style="color: #666; margin-top: 10px; display: block; text-align: center;">
                        Format: <code>ITEM_CODE|MODEL|SERIAL_NUMBER</code> | 
                        Example: <code>TEST-ITEM-001|MODEL-123|SERIAL-456</code>
                    </small>
                </div>
            `;
            
            frm.fields_dict[child_table].$wrapper.before(fallback_html);
            
            // Add event handlers
            $('#fallback-barcode-input').on('keypress', function(e) {
                if (e.which === 13) {
                    let barcode_value = $(this).val().trim();
                    if (barcode_value) {
                        qonevo.clean_barcode_scanner.process_barcode_direct(frm, child_table, barcode_value);
                        $(this).val('');
                    }
                }
            });
            
            $('#fallback-scan-btn').on('click', function() {
                let barcode_value = $('#fallback-barcode-input').val().trim();
                if (barcode_value) {
                    qonevo.clean_barcode_scanner.process_barcode_direct(frm, child_table, barcode_value);
                    $('#fallback-barcode-input').val('');
                }
            });
            
            $('#fallback-camera-btn').on('click', function() {
                qonevo.clean_barcode_scanner.open_camera_scanner(frm, child_table);
            });
        }
    },
    
    // Open camera scanner
    open_camera_scanner: function(frm, child_table) {
        console.log("Opening camera scanner...");
        
        // Check if camera is available
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            frappe.show_alert({
                message: __('Camera not available. Please use manual input or ensure HTTPS connection.'),
                indicator: 'orange'
            });
            return;
        }
        
        // Create camera scanner dialog
        let camera_dialog = new frappe.ui.Dialog({
            title: __('Camera Barcode Scanner'),
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'camera_container',
                    options: `
                        <div style="text-align: center; padding: 20px;">
                            <div id="camera-preview" style="width: 100%; max-width: 500px; height: 300px; background: #000; border-radius: 8px; margin: 0 auto; position: relative; overflow: hidden;">
                                <video id="camera-video" autoplay playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>
                                <div id="camera-overlay" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 200px; height: 100px; border: 2px solid #007bff; border-radius: 8px; pointer-events: none;">
                                    <div style="position: absolute; top: -20px; left: 50%; transform: translateX(-50%); color: #007bff; font-weight: bold; background: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">
                                        Position barcode here
                                    </div>
                                </div>
                            </div>
                            <div style="margin-top: 15px;">
                                <button class="btn btn-primary" id="start-camera-btn">
                                    <i class="fa fa-camera"></i> Start Camera
                                </button>
                                <button class="btn btn-default" id="stop-camera-btn" style="display: none;">
                                    <i class="fa fa-stop"></i> Stop Camera
                                </button>
                            </div>
                            <div id="scan-result" style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 4px; display: none;">
                                <strong>Scanned:</strong> <span id="scanned-barcode"></span>
                                <button class="btn btn-success btn-sm" id="process-scanned-barcode" style="margin-left: 10px;">
                                    <i class="fa fa-check"></i> Add Item
                                </button>
                            </div>
                        </div>
                    `
                }
            ],
            primary_action_label: __('Close'),
            primary_action: function() {
                qonevo.clean_barcode_scanner.stop_camera();
                camera_dialog.hide();
            }
        });
        
        camera_dialog.show();
        
        // Add event handlers
        $('#start-camera-btn').on('click', function() {
            qonevo.clean_barcode_scanner.start_camera(camera_dialog, frm, child_table);
        });
        
        $('#stop-camera-btn').on('click', function() {
            qonevo.clean_barcode_scanner.stop_camera();
        });
        
        $('#process-scanned-barcode').on('click', function() {
            let scanned_barcode = $('#scanned-barcode').text();
            if (scanned_barcode) {
                qonevo.clean_barcode_scanner.process_barcode_direct(frm, child_table, scanned_barcode);
                qonevo.clean_barcode_scanner.stop_camera();
                camera_dialog.hide();
            }
        });
    },
    
    // Start camera
    start_camera: function(dialog, frm, child_table) {
        navigator.mediaDevices.getUserMedia({ 
            video: { 
                facingMode: 'environment', // Use back camera on mobile
                width: { ideal: 1280 },
                height: { ideal: 720 }
            } 
        })
        .then(function(stream) {
            let video = document.getElementById('camera-video');
            video.srcObject = stream;
            
            $('#start-camera-btn').hide();
            $('#stop-camera-btn').show();
            
            // Start barcode detection
            qonevo.clean_barcode_scanner.start_barcode_detection(video, frm, child_table, dialog);
        })
        .catch(function(err) {
            console.error('Camera error:', err);
            frappe.show_alert({
                message: __('Camera access denied or not available. Please use manual input.'),
                indicator: 'red'
            });
        });
    },
    
    // Stop camera
    stop_camera: function() {
        let video = document.getElementById('camera-video');
        if (video && video.srcObject) {
            let tracks = video.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            video.srcObject = null;
        }
        $('#start-camera-btn').show();
        $('#stop-camera-btn').hide();
        $('#scan-result').hide();
    },
    
    // Start barcode detection (simplified version)
    start_barcode_detection: function(video, frm, child_table, dialog) {
        // For now, we'll use a simple approach
        // In a real implementation, you'd use a library like QuaggaJS or ZXing
        console.log("Barcode detection started - using manual input fallback");
        
        // Show instruction
        frappe.show_alert({
            message: __('Camera started! For now, please type the barcode manually in the input field below.'),
            indicator: 'blue'
        });
        
        // Add manual input field to dialog
        let manual_input_html = `
            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 4px;">
                <label style="font-weight: 500; margin-bottom: 10px; display: block;">
                    Manual Input (while camera is active):
                </label>
                <div style="display: flex; gap: 10px;">
                    <input type="text" 
                           id="manual-barcode-input" 
                           class="form-control" 
                           placeholder="Type: ITEM_CODE|MODEL|SERIAL_NUMBER"
                           style="flex: 1; font-family: monospace;">
                    <button class="btn btn-primary" id="manual-scan-btn">
                        <i class="fa fa-search"></i> Scan
                    </button>
                </div>
            </div>
        `;
        
        dialog.fields_dict.camera_container.$wrapper.append(manual_input_html);
        
        // Add manual input handlers
        $('#manual-barcode-input').on('keypress', function(e) {
            if (e.which === 13) {
                let barcode_value = $(this).val().trim();
                if (barcode_value) {
                    qonevo.clean_barcode_scanner.process_barcode_direct(frm, child_table, barcode_value);
                    qonevo.clean_barcode_scanner.stop_camera();
                    dialog.hide();
                }
            }
        });
        
        $('#manual-scan-btn').on('click', function() {
            let barcode_value = $('#manual-barcode-input').val().trim();
            if (barcode_value) {
                qonevo.clean_barcode_scanner.process_barcode_direct(frm, child_table, barcode_value);
                qonevo.clean_barcode_scanner.stop_camera();
                dialog.hide();
            }
        });
    },
    
    // Direct barcode processing (no dialog)
    process_barcode_direct: function(frm, child_table, barcode_string) {
        console.log("Processing barcode directly:", barcode_string);
        
        // Show loading state
        frappe.show_alert({
            message: __('Processing barcode...'),
            indicator: 'blue'
        });
        
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
                    qonevo.clean_barcode_scanner.add_item_to_table(frm, child_table, r.message, barcode_string);
                    frappe.show_alert({
                        message: `✅ Item ${r.message.item_code} added successfully!`,
                        indicator: 'green'
                    });
                } else {
                    console.log("API failed:", r.message);
                    frappe.show_alert({
                        message: `❌ Barcode not found: ${barcode_string}`,
                        indicator: 'red'
                    });
                }
            },
            error: function(err) {
                console.log("API Error:", err);
                frappe.show_alert({
                    message: `❌ Error scanning barcode: ${err.message || 'Unknown error'}`,
                    indicator: 'red'
                });
            }
        });
    },
    
    // Show scanner dialog (kept for backward compatibility)
    show_scanner_dialog: function(frm, child_table) {
        let dialog = new frappe.ui.Dialog({
            title: __('Barcode Scanner'),
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'instructions',
                    options: `
                        <div style="padding: 15px; background: #f8f9fa; border-radius: 6px; margin: 10px 0; border-left: 4px solid #007bff;">
                            <h4 style="margin: 0 0 10px 0; color: #007bff;">📱 Barcode Scanner Instructions</h4>
                            <ul style="margin: 0; padding-left: 20px;">
                                <li>Scan your barcode using a physical scanner</li>
                                <li>Or type the barcode manually in the field below</li>
                                <li>Format: <code>ITEM_CODE|MODEL|SERIAL_NUMBER</code></li>
                                <li>Example: <code>TEST-ITEM-001|MODEL-123|SERIAL-456</code></li>
                            </ul>
                        </div>
                    `
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'barcode_input',
                    label: __('Scan or Enter Barcode'),
                    reqd: 1,
                    description: __('Enter barcode in format: ITEM_CODE|MODEL|SERIAL_NUMBER')
                },
                {
                    fieldtype: 'Button',
                    fieldname: 'scan_button',
                    label: __('Process Barcode')
                }
            ],
            primary_action_label: __('Add Item'),
            primary_action: function(values) {
                if (values.barcode_input) {
                    qonevo.clean_barcode_scanner.process_barcode(frm, child_table, values.barcode_input, dialog);
                } else {
                    frappe.show_alert({
                        message: __('Please enter a barcode to scan.'),
                        indicator: 'orange'
                    });
                }
            },
            secondary_action_label: __('Close'),
            secondary_action: function() {
                dialog.hide();
            }
        });
        
        // Handle scan button click
        dialog.fields_dict.scan_button.$input.on('click', function() {
            let barcode_value = dialog.get_value('barcode_input');
            if (barcode_value) {
                qonevo.clean_barcode_scanner.process_barcode(frm, child_table, barcode_value, dialog);
            } else {
                frappe.show_alert({
                    message: __('Please enter a barcode to scan.'),
                    indicator: 'orange'
                });
            }
        });
        
        // Handle Enter key in input field
        dialog.fields_dict.barcode_input.$input.on('keypress', function(e) {
            if (e.which === 13) { // Enter key
                e.preventDefault();
                let barcode_value = dialog.get_value('barcode_input');
                if (barcode_value) {
                    qonevo.clean_barcode_scanner.process_barcode(frm, child_table, barcode_value, dialog);
                } else {
                    frappe.show_alert({
                        message: __('Please enter a barcode to scan.'),
                        indicator: 'orange'
                    });
                }
            }
        });
        
        dialog.show();
        
        // Focus on input field
        setTimeout(function() {
            dialog.fields_dict.barcode_input.$input.focus();
        }, 100);
    },
    
    // Process the scanned barcode
    process_barcode: function(frm, child_table, barcode_string, dialog) {
        console.log("Processing barcode:", barcode_string);
        
        // Show loading state
        frappe.show_alert({
            message: __('Processing barcode...'),
            indicator: 'blue'
        });
        
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
                    qonevo.clean_barcode_scanner.add_item_to_table(frm, child_table, r.message, barcode_string);
                    frappe.show_alert({
                        message: `✅ Item ${r.message.item_code} added successfully!`,
                        indicator: 'green'
                    });
                    dialog.hide();
                } else {
                    console.log("API failed:", r.message);
                    frappe.show_alert({
                        message: `❌ Barcode not found: ${barcode_string}`,
                        indicator: 'red'
                    });
                }
            },
            error: function(err) {
                console.log("API Error:", err);
                frappe.show_alert({
                    message: `❌ Error scanning barcode: ${err.message || 'Unknown error'}`,
                    indicator: 'red'
                });
            }
        });
    },
    
    // Add item to the specified table
    add_item_to_table: function(frm, child_table, item_data, barcode_string) {
        console.log("Adding item to table:", child_table, item_data, "Barcode:", barcode_string);
        
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
            frappe.show_alert({
                message: `📈 Quantity increased for ${item_data.item_code}`,
                indicator: 'green'
            });
        } else {
            // Add new item
            let new_row = frm.add_child(child_table);
            frappe.model.set_value(new_row.doctype, new_row.name, 'item_code', item_data.item_code);
            frappe.model.set_value(new_row.doctype, new_row.name, 'qty', 1);
            
            // Add serial number if available
            if (item_data.serial_number) {
                frappe.model.set_value(new_row.doctype, new_row.name, 'serial_no', item_data.serial_number);
                // Also add to custom field
                frappe.model.set_value(new_row.doctype, new_row.name, 'scanned_serial_number', item_data.serial_number);
            }
            
            // Add model number to custom field and description
            if (item_data.model_number && item_data.model_number !== 'NO-MODEL') {
                // Add to custom model_number field
                frappe.model.set_value(new_row.doctype, new_row.name, 'model_number', item_data.model_number);
                // Add to description
                frappe.model.set_value(new_row.doctype, new_row.name, 'description', 
                    `${item_data.item_name} - Model: ${item_data.model_number}`);
            }
            
            // Add scanned barcode to custom field
            frappe.model.set_value(new_row.doctype, new_row.name, 'scanned_barcode', barcode_string);
            
            // Trigger item code change to populate other fields
            frappe.model.trigger('item_code', new_row.doctype, new_row.name);
            console.log("Added new item to table");
        }
        
        frm.refresh_field(child_table);
    }
};

// Add barcode scanner to Delivery Note
frappe.ui.form.on('Delivery Note', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            qonevo.clean_barcode_scanner.override_scan_barcode_field(frm, 'items');
        }
    }
});

// Add barcode scanner to Purchase Receipt
frappe.ui.form.on('Purchase Receipt', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            qonevo.clean_barcode_scanner.override_scan_barcode_field(frm, 'items');
        }
    }
});

// Add barcode scanner to Stock Entry
frappe.ui.form.on('Stock Entry', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            qonevo.clean_barcode_scanner.override_scan_barcode_field(frm, 'items');
        }
    }
});

// Add barcode scanner to Material Request
frappe.ui.form.on('Material Request', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            qonevo.clean_barcode_scanner.override_scan_barcode_field(frm, 'items');
        }
    }
});

// Add barcode scanner to Purchase Order
frappe.ui.form.on('Purchase Order', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            qonevo.clean_barcode_scanner.override_scan_barcode_field(frm, 'items');
        }
    }
});

// Add barcode scanner to Sales Order
frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            qonevo.clean_barcode_scanner.override_scan_barcode_field(frm, 'items');
        }
    }
});

// Add barcode scanner to Stock Reconciliation
frappe.ui.form.on('Stock Reconciliation', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            qonevo.clean_barcode_scanner.override_scan_barcode_field(frm, 'items');
        }
    }
});

// Add barcode scanner to Pick List
frappe.ui.form.on('Pick List', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            qonevo.clean_barcode_scanner.override_scan_barcode_field(frm, 'locations');
        }
    }
});

// Add barcode scanner to Sales Invoice
frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            qonevo.clean_barcode_scanner.override_scan_barcode_field(frm, 'items');
        }
    }
});

// Add barcode scanner to Purchase Invoice
frappe.ui.form.on('Purchase Invoice', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            qonevo.clean_barcode_scanner.override_scan_barcode_field(frm, 'items');
        }
    }
});

// Add barcode scanner to POS Invoice
frappe.ui.form.on('POS Invoice', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            qonevo.clean_barcode_scanner.override_scan_barcode_field(frm, 'items');
        }
    }
});

// Add barcode scanner to Quotation
frappe.ui.form.on('Quotation', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 0) { // Only for draft documents
            qonevo.clean_barcode_scanner.override_scan_barcode_field(frm, 'items');
        }
    }
});

// Add barcode scanner to Point of Sale (special case - it's a page)
frappe.ready(function() {
    // Check if we're on the Point of Sale page
    if (frappe.get_route()[0] === 'point-of-sale') {
        // Wait for the page to load
        setTimeout(function() {
            // Look for POS invoice form
            let pos_form = frappe.get_route()[1];
            if (pos_form && pos_form.includes('pos-invoice')) {
                frappe.ui.form.on('POS Invoice', {
                    refresh: function(frm) {
                        if (frm.doc.docstatus === 0) { // Only for draft documents
                            qonevo.clean_barcode_scanner.override_scan_barcode_field(frm, 'items');
                        }
                    }
                });
            }
        }, 2000);
    }
});
