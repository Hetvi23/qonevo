// Copyright (c) 2025, Qonevo and contributors
// For license information, please see license.txt

console.log('🚀 Installation Job JavaScript loaded successfully!');

frappe.ui.form.on('Installation Job', {
    refresh: function(frm) {
        // Add custom buttons based on status
        if (frm.doc.status === 'In Progress') {
            frm.add_custom_button(__('Complete Installation'), function() {
                complete_installation(frm);
            }, __('Actions'));
        }
        
        if (frm.doc.status === 'Completed - Full' || frm.doc.status === 'Completed - Partial') {
            frm.add_custom_button(__('Verify Installation'), function() {
                verify_installation(frm);
            }, __('Actions'));
        }
        
        if (frm.doc.status === 'Verified') {
            frm.add_custom_button(__('Close Job'), function() {
                close_job(frm);
            }, __('Actions'));
        }
        
        // Add photo upload button
        if (frm.doc.status === 'In Progress') {
            frm.add_custom_button(__('Add Photo'), function() {
                add_photo(frm);
            }, __('Actions'));
        }
        
        // Add signature button
        if (frm.doc.status === 'In Progress') {
            frm.add_custom_button(__('Capture Signature'), function() {
                capture_signature(frm);
            }, __('Actions'));
        }
        
        // Add debug button to manually trigger status update
        frm.add_custom_button(__('Debug Status Update'), function() {
            console.log('🔧 Manual status update triggered');
            update_installation_status(frm);
        }, __('Debug'));
    },
    
    installed_items: {
        installed: function(frm, cdt, cdn) {
            let row = locals[cdt][cdn];
            console.log('🔧 Checkbox changed for item:', row.serial_no, 'installed:', row.installed);
            
            if (row.installed) {
                row.installation_status = 'Installed';
                row.not_installed_reason = '';
                console.log('✅ Item marked as installed');
            } else {
                row.installation_status = 'Not Installed';
                if (!row.not_installed_reason) {
                    row.not_installed_reason = 'Client Delay';
                }
                console.log('❌ Item marked as not installed');
            }
            frm.refresh_field('installed_items');
            
            // Auto-update status based on installation progress
            console.log('🔄 Calling update_installation_status...');
            update_installation_status(frm);
        },
        
        not_installed_reason: function(frm, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.not_installed_reason && !row.installed) {
                row.installation_status = 'Not Installed';
            }
            frm.refresh_field('installed_items');
            
            // Auto-update status based on installation progress
            update_installation_status(frm);
        }
    }
});

function update_installation_status(frm) {
    // Count installed and total items
    let total_items = frm.doc.installed_items.length;
    let installed_count = 0;
    let has_any_installation = false;
    
    console.log('🔍 Update Installation Status - Total items:', total_items);
    
    frm.doc.installed_items.forEach(function(item, index) {
        console.log(`   Item ${index + 1}: installed = ${item.installed}, serial = ${item.serial_no}`);
        if (item.installed) {
            installed_count++;
            has_any_installation = true;
        }
    });
    
    console.log('📊 Counts:', {
        total_items: total_items,
        installed_count: installed_count,
        has_any_installation: has_any_installation,
        current_status: frm.doc.status
    });
    
    // Auto-update status based on installation progress
    if (total_items === 0) {
        // No items - keep as Scheduled
        if (frm.doc.status !== 'Scheduled') {
            frm.set_value('status', 'Scheduled');
        }
    } else if (!has_any_installation) {
        // No items installed yet - keep as Scheduled
        if (frm.doc.status !== 'Scheduled') {
            frm.set_value('status', 'Scheduled');
        }
    } else if (installed_count === total_items) {
        // All items installed - mark as Completed - Full
        console.log('✅ All items installed - setting status to Completed - Full');
        if (frm.doc.status !== 'Completed - Full') {
            console.log('🔄 Changing status from', frm.doc.status, 'to Completed - Full');
            frm.set_value('status', 'Completed - Full');
            // Set installation date when completed
            if (!frm.doc.installation_date) {
                frm.set_value('installation_date', frappe.datetime.get_today());
            }
            // Save the form to trigger backend processing
            frm.save().then(function() {
                console.log('💾 Form saved, creating warranty records...');
                // Create warranty records automatically after save
                create_warranty_records(frm);
            });
        } else {
            console.log('ℹ️ Status already Completed - Full');
        }
    } else if (installed_count > 0) {
        // Some items installed - mark as Completed - Partial
        console.log('⚠️ Some items installed - setting status to Completed - Partial');
        if (frm.doc.status !== 'Completed - Partial') {
            console.log('🔄 Changing status from', frm.doc.status, 'to Completed - Partial');
            frm.set_value('status', 'Completed - Partial');
            // Set installation date when partially completed
            if (!frm.doc.installation_date) {
                frm.set_value('installation_date', frappe.datetime.get_today());
            }
            // Save the form to trigger backend processing
            frm.save().then(function() {
                console.log('💾 Form saved, creating warranty records...');
                // Create warranty records automatically for installed items after save
                create_warranty_records(frm);
            });
        } else {
            console.log('ℹ️ Status already Completed - Partial');
        }
    } else {
        // No items installed - mark as In Progress
        console.log('🚀 No items installed yet - setting status to In Progress');
        if (frm.doc.status !== 'In Progress') {
            console.log('🔄 Changing status from', frm.doc.status, 'to In Progress');
            frm.set_value('status', 'In Progress');
            // Save the form
            frm.save();
        } else {
            console.log('ℹ️ Status already In Progress');
        }
    }
    
    // Update summary fields
    frm.set_value('total_items', total_items);
    frm.set_value('installed_count', installed_count);
    frm.set_value('not_installed_count', total_items - installed_count);
    
    if (total_items > 0) {
        frm.set_value('completion_percentage', (installed_count / total_items) * 100);
    } else {
        frm.set_value('completion_percentage', 0);
    }
}

function complete_installation(frm) {
    // Validate that photos and signature are present
    if (!frm.doc.photos || frm.doc.photos.length === 0) {
        frappe.msgprint(__('At least one photo is required before completing the installation'), __('Validation Error'));
        return;
    }
    
    if (!frm.doc.customer_signature) {
        frappe.msgprint(__('Customer signature is required before completing the installation'), __('Validation Error'));
        return;
    }
    
    // Show notes dialog
    let d = new frappe.ui.Dialog({
        title: __('Complete Installation'),
        fields: [
            {
                fieldtype: 'Small Text',
                fieldname: 'installer_notes',
                label: __('Installer Notes'),
                default: frm.doc.installer_notes || ''
            }
        ],
        primary_action_label: __('Complete'),
        primary_action: function(values) {
            frappe.call({
                method: 'qonevo.qonevo.doctype.installation_job.installation_job.complete_installation',
                args: {
                    installation_job: frm.doc.name,
                    installer_notes: values.installer_notes
                },
                callback: function(r) {
                    if (r.message.success) {
                        frappe.msgprint(r.message.message, __('Success'));
                        d.hide();
                        frm.reload_doc();
                    }
                }
            });
        }
    });
    
    d.show();
}

function verify_installation(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Verify Installation'),
        fields: [
            {
                fieldtype: 'Small Text',
                fieldname: 'ops_notes',
                label: __('Ops Verification Notes'),
                default: frm.doc.ops_verification_notes || ''
            },
            {
                fieldtype: 'Select',
                fieldname: 'warranty_action',
                label: __('Warranty Start Action'),
                options: 'Start Now\nPartial Start\nDelay',
                default: frm.doc.warranty_start_action || 'Start Now',
                reqd: 1
            }
        ],
        primary_action_label: __('Verify'),
        primary_action: function(values) {
            frappe.call({
                method: 'qonevo.qonevo.doctype.installation_job.installation_job.verify_installation',
                args: {
                    installation_job: frm.doc.name,
                    ops_notes: values.ops_notes,
                    warranty_action: values.warranty_action
                },
                callback: function(r) {
                    if (r.message.success) {
                        frappe.msgprint(r.message.message, __('Success'));
                        d.hide();
                        frm.reload_doc();
                    }
                }
            });
        }
    });
    
    d.show();
}

function close_job(frm) {
    frappe.confirm(
        __('Are you sure you want to close this installation job?'),
        function() {
            frappe.call({
                method: 'qonevo.qonevo.doctype.installation_job.installation_job.close_installation_job',
                args: {
                    installation_job: frm.doc.name
                },
                callback: function(r) {
                    if (r.message.success) {
                        frappe.msgprint(r.message.message, __('Success'));
                        frm.reload_doc();
                    }
                }
            });
        }
    );
}

function add_photo(frm) {
    let d = new frappe.ui.Dialog({
        title: __('Add Photo'),
        fields: [
            {
                fieldtype: 'Data',
                fieldname: 'photo_name',
                label: __('Photo Name'),
                reqd: 1
            },
            {
                fieldtype: 'Select',
                fieldname: 'photo_type',
                label: __('Photo Type'),
                options: 'Installation\nSetup\nSite\nProblem\nOther',
                default: 'Installation'
            },
            {
                fieldtype: 'Attach',
                fieldname: 'photo_file',
                label: __('Photo File'),
                reqd: 1
            },
            {
                fieldtype: 'Small Text',
                fieldname: 'description',
                label: __('Description')
            }
        ],
        primary_action_label: __('Add Photo'),
        primary_action: function(values) {
            let photo_row = frm.add_child('photos');
            photo_row.photo_name = values.photo_name;
            photo_row.photo_type = values.photo_type;
            photo_row.photo_file = values.photo_file;
            photo_row.description = values.description;
            photo_row.taken_date = frappe.datetime.get_today();
            
            frm.refresh_field('photos');
            frm.save();
            d.hide();
        }
    });
    
    d.show();
}

function capture_signature(frm) {
    // This would integrate with a signature capture library
    // For now, we'll use a simple file upload
    frappe.msgprint(__('Please upload the customer signature file using the Customer Signature field'), __('Info'));
}

function create_warranty_records(frm) {
    // Create warranty records for installed items
    frappe.call({
        method: 'qonevo.qonevo.doctype.installation_job.installation_job.create_warranty_records',
        args: {
            installation_job: frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.msgprint(
                    __('Created {0} warranty records automatically').format(r.message.count),
                    __('Warranty Records Created'),
                    'green'
                );
            } else if (r.message && r.message.error) {
                frappe.msgprint(r.message.error, __('Error'), 'red');
            }
        }
    });
}
