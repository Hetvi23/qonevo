// Copyright (c) 2025, Qonevo and contributors
// For license information, please see license.txt

console.log('🚀 QONEVO Delivery Note JavaScript loaded!');

frappe.ui.form.on('Delivery Note', {
    refresh: function(frm) {
        console.log('🔧 DELIVERY NOTE JS: refresh triggered for', frm.doc.name || 'new document');

        // Add a button to manually populate serials
        if (frm.doc.docstatus === 0) { // Only for draft documents
            console.log('🔘 DELIVERY NOTE JS: Adding Populate Manufacturing Serials button...');
            frm.add_custom_button(__('Populate Manufacturing Serials'), function() {
                console.log('🔘 DELIVERY NOTE JS: Manual populate button clicked');
                populate_manufacturing_serials_simple(frm);
            }, __('Actions'));

            // Also add a button in the main toolbar for visibility
            frm.add_custom_button(__('🚀 Populate Serials'), function() {
                console.log('🔘 DELIVERY NOTE JS: Main toolbar populate button clicked');
                populate_manufacturing_serials_simple(frm);
            });

            console.log('✅ DELIVERY NOTE JS: Buttons added successfully');
        } else {
            console.log('⚠️ DELIVERY NOTE JS: Document is submitted/cancelled, not adding buttons');
        }

        // Try to populate serials automatically on refresh
        setTimeout(function() {
            console.log('🔄 DELIVERY NOTE JS: Auto-populating serials on refresh...');
            populate_manufacturing_serials_simple(frm);
        }, 1000);
    },
    
    onload: function(frm) {
        console.log('🔧 DELIVERY NOTE JS: onload triggered for', frm.doc.name || 'new document');

        // Try to populate serials automatically on load
        setTimeout(function() {
            console.log('🔄 DELIVERY NOTE JS: Auto-populating serials on load...');
            populate_manufacturing_serials_simple(frm);
        }, 2000);
    }
});

// Direct approach that checks for form availability
$(document).ready(function() {
    console.log('📄 DELIVERY NOTE JS: Document ready, checking for Delivery Note form...');

    // Wait for ERPNext to fully load
    setTimeout(function() {
        try {
            // Check if we're on a Delivery Note form
            if (typeof frappe !== 'undefined' && frappe.get_route && frappe.get_route()[0] === 'delivery-note') {
                console.log('✅ DELIVERY NOTE JS: Delivery Note form detected, setting up serial population...');

                // Try to get the form multiple times with increasing delays
                let attempts = 0;
                const maxAttempts = 10;

                const checkForm = function() {
                    attempts++;
                    console.log(`🔍 DELIVERY NOTE JS: Attempt ${attempts} to find form...`);

                    try {
                        // Use cur_frm instead of frappe.get_form()
                        if (cur_frm && cur_frm.doc && cur_frm.doc.items && cur_frm.doc.items.length > 0) {
                            console.log('✅ DELIVERY NOTE JS: Form found and ready, populating serials...');
                            populate_manufacturing_serials_simple(cur_frm);
                            return;
                        }
                    } catch (e) {
                        console.log('⚠️ DELIVERY NOTE JS: Form not ready yet:', e.message);
                    }

                    if (attempts < maxAttempts) {
                        setTimeout(checkForm, 500); // Try again in 500ms
                    } else {
                        console.log('❌ DELIVERY NOTE JS: Max attempts reached, form not found');
                    }
                };

                // Start checking for the form
                checkForm();
            } else {
                console.log('ℹ️ DELIVERY NOTE JS: Not on Delivery Note form');
            }
        } catch (e) {
            console.error('❌ DELIVERY NOTE JS: Error in document ready:', e);
        }
    }, 3000); // Increased delay to 3 seconds
});

function populate_manufacturing_serials_simple(frm) {
    try {
        console.log('🔧 DELIVERY NOTE JS: Starting simple serial population...');

        // Check if form is ready
        if (!frm || !frm.doc || !frm.doc.items || frm.doc.items.length === 0) {
            console.log('⚠️ DELIVERY NOTE JS: Form not ready or no items found');
            return;
        }

        console.log(`📦 DELIVERY NOTE JS: Form ready with ${frm.doc.items.length} items`);

        // Check for sales order references
        let has_sales_order = false;
        let sales_orders_found = [];
        frm.doc.items.forEach((item, index) => {
            if (item.against_sales_order) {
                has_sales_order = true;
                sales_orders_found.push(item.against_sales_order);
                console.log(`📦 DELIVERY NOTE JS: Item ${index + 1} (${item.item_code}) linked to Sales Order ${item.against_sales_order}`);
            }
        });

        if (!has_sales_order) {
            console.log('⚠️ DELIVERY NOTE JS: No items with sales order references found');
            return;
        }

        console.log(`✅ DELIVERY NOTE JS: Found items with sales order references: ${sales_orders_found.join(', ')}`);
        console.log('📞 DELIVERY NOTE JS: Calling server method...');
        
        // Call server method
        frappe.call({
            method: 'qonevo.delivery_note_hooks.populate_manufacturing_serials',
            args: {
                delivery_note: frm.doc.name || 'new',
                items: frm.doc.items
            },
            callback: function(r) {
                console.log('📞 DELIVERY NOTE JS: Server response received:', r);

                if (r.message && r.message.success && r.message.items) {
                    console.log('✅ DELIVERY NOTE JS: Server method successful, updating form fields...');

                    // Update each item
                    r.message.items.forEach((item_data, index) => {
                        if (frm.doc.items[index] && item_data.serial_no) {
                            // Direct field update
                            frm.doc.items[index].serial_no = item_data.serial_no;
                            console.log(`✅ DELIVERY NOTE JS: Set serial for item ${index + 1}: ${item_data.serial_no}`);
                        } else if (frm.doc.items[index]) {
                            console.log(`⚠️ DELIVERY NOTE JS: No serial data for item ${index + 1}`);
                        }
                    });

                    // Refresh the form
                    frm.refresh_fields();
                    console.log('🔄 DELIVERY NOTE JS: Form fields refreshed');

                    // Show success message
                    frappe.show_alert({
                        message: 'Manufacturing serials populated successfully!',
                        indicator: 'green'
                    });

                    console.log('🎉 DELIVERY NOTE JS: Serial population completed successfully');
                } else {
                    console.log('❌ DELIVERY NOTE JS: Server method failed or no serials returned');
                    if (r.message && r.message.error) {
                        console.log('❌ DELIVERY NOTE JS: Server error:', r.message.error);
                        frappe.show_alert({
                            message: 'Error: ' + r.message.error,
                            indicator: 'red'
                        });
                    }
                }
            },
            error: function(err) {
                console.error('❌ DELIVERY NOTE JS: Server call error:', err);
                frappe.show_alert({
                    message: 'Error calling server method',
                    indicator: 'red'
                });
            }
        });
        
    } catch (error) {
        console.error('❌ DELIVERY NOTE JS: Error in populate_manufacturing_serials_simple:', error);
    }
}

// Keep the original function for backward compatibility
function populate_manufacturing_serials(frm) {
    return populate_manufacturing_serials_simple(frm);
}
