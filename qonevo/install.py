# Copyright (c) 2024, Qonevo and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.desk.doctype.client_script.client_script import get_client_script


def after_install():
	"""Run after app installation"""
	install_custom_fields()
	install_client_scripts()
	setup_barcode_system()


def install_custom_fields():
	"""Install custom fields for Employee doctype"""
	custom_fields = {
		"Employee": [
			{
				"fieldname": "ctc_salary_structure_section",
				"fieldtype": "Section Break",
				"label": "CTC-Based Salary Structure",
				"insert_after": "salary_currency",
			},
			{
				"fieldname": "suggested_salary_structure",
				"fieldtype": "Data",
				"label": "Suggested Salary Structure",
				"insert_after": "ctc_salary_structure_section",
				"read_only": 1,
			},
			{
				"fieldname": "auto_assign_salary_structure",
				"fieldtype": "Check",
				"label": "Auto Assign Salary Structure",
				"insert_after": "suggested_salary_structure",
				"default": "1",
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()


def install_client_scripts():
	"""Install client scripts for Employee doctype"""
	client_script = {
		"apply_to": "Employee",
		"client_script": """frappe.ui.form.on('Employee', {
	refresh: function(frm) {
		// Add custom button to get suggested salary structure
		if (frm.doc.ctc && frm.doc.company && frm.doc.salary_currency) {
			frm.add_custom_button(__('Get Suggested Salary Structure'), function() {
				frm.call('get_suggested_salary_structure').then(r => {
					if (r.message) {
						frm.set_value('suggested_salary_structure', r.message.template_name);
						frappe.msgprint(__('Suggested Salary Structure: {0}', [r.message.template_name]));
					} else {
						frappe.msgprint(__('No matching salary structure template found for this CTC.'));
					}
				});
			}, __('CTC Actions'));
		}
	},

	ctc: function(frm) {
		// Clear suggested salary structure when CTC changes
		if (frm.doc.ctc) {
			frm.set_value('suggested_salary_structure', '');
		}
	},

	company: function(frm) {
		// Clear suggested salary structure when company changes
		if (frm.doc.company) {
			frm.set_value('suggested_salary_structure', '');
		}
	},

	salary_currency: function(frm) {
		// Clear suggested salary structure when currency changes
		if (frm.doc.salary_currency) {
			frm.set_value('suggested_salary_structure', '');
		}
	},

	auto_assign_salary_structure: function(frm) {
		// Show/hide message based on auto assign setting
		if (frm.doc.auto_assign_salary_structure) {
			frappe.msgprint(__('Salary structure will be automatically assigned when CTC is saved.'));
		}
	}
});""",
		"enabled": 1,
		"name": "Employee CTC Salary Structure"
	}
	
	# Check if client script already exists
	if not frappe.db.exists("Client Script", "Employee CTC Salary Structure"):
		doc = frappe.new_doc("Client Script")
		doc.update(client_script)
		doc.insert(ignore_permissions=True)
		frappe.db.commit()


def setup_barcode_system():
	"""Setup barcode system after installation"""
	try:
		from qonevo.setup_barcode_system import setup_barcode_system as setup_barcode
		setup_barcode()
		print("Barcode system setup completed successfully!")
	except Exception as e:
		print(f"Error setting up barcode system: {str(e)}")
		frappe.log_error(f"Barcode system setup error: {str(e)}")



