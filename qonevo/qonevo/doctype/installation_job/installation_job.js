// Copyright (c) 2025, Qonevo and contributors
// For license information, please see license.txt

console.log('🚀 Installation Job JavaScript loaded successfully!');

frappe.ui.form.on('Installation Job', {
    refresh: function(frm) {
        // Add custom buttons based on status - only show Start Installation for Scheduled jobs
        if (frm.doc.status === 'Scheduled') {
            frm.add_custom_button(__('Start Installation'), function() {
                start_installation(frm);
            }, __('Actions'));
        }
    },
    
    installed_items: {
        installed: function(frm, cdt, cdn) {
            let row = locals[cdt][cdn];
            
            if (row.installed) {
                row.installation_status = 'Installed';
                row.not_installed_reason = '';
            } else {
                row.installation_status = 'Not Installed';
                if (!row.not_installed_reason) {
                    row.not_installed_reason = 'Client Delay';
                }
            }
            frm.refresh_field('installed_items');
            
            // Auto-update installation job status based on installed items
            setTimeout(function() {
                update_installation_status(frm);
            }, 100);
        },
        
        not_installed_reason: function(frm, cdt, cdn) {
            let row = locals[cdt][cdn];
            if (row.not_installed_reason && !row.installed) {
                row.installation_status = 'Not Installed';
            }
            frm.refresh_field('installed_items');
            
            // Auto-update installation job status based on installed items
            setTimeout(function() {
                update_installation_status(frm);
            }, 100);
        }
    }
});


function start_installation(frm) {
    frappe.call({
        method: 'qonevo.qonevo.doctype.installation_job.installation_job.start_installation',
        args: {
            installation_job: frm.doc.name
        },
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.msgprint(r.message.message, __('Success'), 'green');
                frm.reload_doc();
            } else {
                frappe.msgprint(r.message || __('Error starting installation'), __('Error'), 'red');
            }
        }
    });
}

function update_installation_status(frm) {
    console.log('🔄 Updating installation status...');
    
    if (!frm.doc.installed_items || frm.doc.installed_items.length === 0) {
        console.log('❌ No installed items found');
        return;
    }
    
    let total_items = frm.doc.installed_items.length;
    let installed_count = frm.doc.installed_items.filter(item => item.installed === 1).length;
    let not_installed_count = total_items - installed_count;
    
    console.log(`📊 Total: ${total_items}, Installed: ${installed_count}, Not Installed: ${not_installed_count}`);
    
    // Update counts
    frm.set_value('total_items', total_items);
    frm.set_value('installed_count', installed_count);
    frm.set_value('not_installed_count', not_installed_count);
    frm.set_value('completion_percentage', total_items > 0 ? (installed_count / total_items) * 100 : 0);
    
    // Auto-update job status based on installation progress
    if (frm.doc.status === 'In Progress') {
        let new_status = null;
        let message = '';
        
        if (installed_count === total_items && total_items > 0) {
            // All items installed
            new_status = 'Completed - Full';
            message = __('All items have been installed. Installation marked as Completed - Full.');
        } else if (installed_count > 0) {
            // Some items installed
            new_status = 'Completed - Partial';
            message = __('Some items have been installed. Installation marked as Completed - Partial.');
        }
        
        if (new_status && new_status !== frm.doc.status) {
            console.log(`✅ Updating status from ${frm.doc.status} to ${new_status}`);
            frm.set_value('status', new_status);
            frappe.msgprint(message);
        } else {
            console.log('ℹ️ Status remains:', frm.doc.status);
        }
    }
    
    // Save the document to persist changes
    frm.save();
}
