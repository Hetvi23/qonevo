frappe.ui.form.on('Lead', {
    refresh(frm) {
        console.log("Lead Custom Script Loaded");
        if (!frm.is_new()) {
            setTimeout(() => {
                frm.page.remove_inner_button("Create");
                if (frm.page.wrapper.find('[data-label="Create"]').length > 0) {
                    frm.page.wrapper.find('[data-label="Create"]').hide();
                }

                console.log("Attempted to hide Create button via Timeout");
            }, 500);

            frm.add_custom_button(__('Create Opportunity'), function () {
                frappe.call({
                    method: 'qonevo.api.create_opportunities_for_lead',
                    args: {
                        lead_name: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __('Creating Opportunities...'),
                    callback: function (r) {
                        if (r.message) {
                            let opportunities = r.message;
                            let html = '<ul>';
                            opportunities.forEach(opp => {
                                html += `<li><a href="${opp.url}" target="_blank">${opp.name}</a></li>`;
                            });
                            html += '</ul>';

                            frappe.msgprint({
                                title: __('Opportunities Created'),
                                message: html,
                                indicator: 'green',
                                wide: true
                            });
                        }
                    }
                });
            });
        }
    }
});
