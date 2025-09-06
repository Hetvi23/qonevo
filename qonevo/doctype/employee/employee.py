# Copyright (c) 2024, Qonevo and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from qonevo.qonevo.doctype.ctc_salary_structure_template.ctc_salary_structure_template import (
	create_salary_structure_from_ctc,
	get_matching_template
)


def validate_ctc_salary_structure(doc, method):
	"""Validate and handle CTC-based salary structure assignment"""
	if not doc.ctc or not doc.company or not doc.salary_currency:
		return

	# Check if CTC has changed
	if doc.has_value_changed("ctc") and doc.ctc > 0:
		handle_ctc_based_salary_structure(doc)


def handle_ctc_based_salary_structure(doc):
	"""Handle CTC-based salary structure creation/assignment"""
	try:
		# Check if auto assign is enabled
		if not getattr(doc, 'auto_assign_salary_structure', True):
			return
			
		# Try to find or create salary structure based on CTC
		salary_structure_name = create_salary_structure_from_ctc(
			doc.ctc, 
			doc.company, 
			doc.salary_currency, 
			doc.name
		)
		
		if salary_structure_name:
			# Check if employee already has an active salary structure assignment
			existing_assignment = frappe.db.get_value(
				"Salary Structure Assignment",
				{
					"employee": doc.name,
					"docstatus": 1,
					"to_date": ["is", "not set"]
				},
				"name"
			)
			
			if existing_assignment:
				# End the existing assignment
				frappe.db.set_value(
					"Salary Structure Assignment",
					existing_assignment,
					"to_date",
					frappe.utils.today()
				)
			
			# Create new salary structure assignment
			create_salary_structure_assignment(doc, salary_structure_name)
			
			frappe.msgprint(
				_("Salary structure '{0}' has been assigned to employee {1} based on CTC {2}").format(
					salary_structure_name, doc.employee_name, doc.ctc
				)
			)
			
	except Exception as e:
		frappe.log_error(
			f"Error in CTC-based salary structure assignment for employee {doc.name}: {str(e)}",
			"CTC Salary Structure Error"
		)
		frappe.msgprint(
			_("Could not automatically assign salary structure based on CTC. Please assign manually."),
			indicator="orange"
		)


def create_salary_structure_assignment(doc, salary_structure_name):
	"""Create salary structure assignment for the employee"""
	from hrms.payroll.doctype.salary_structure.salary_structure import create_salary_structure_assignment
	
	# Get default payroll payable account
	payroll_payable_account = frappe.db.get_value(
		"Company", 
		doc.company, 
		"default_payroll_payable_account"
	)
	
	if not payroll_payable_account:
		frappe.throw(_('Please set "Default Payroll Payable Account" in Company Defaults'))
	
	# Create assignment
	assignment_name = create_salary_structure_assignment(
		employee=doc.name,
		salary_structure=salary_structure_name,
		company=doc.company,
		currency=doc.salary_currency,
		from_date=frappe.utils.today(),
		payroll_payable_account=payroll_payable_account
	)
	
	return assignment_name


@frappe.whitelist()
def get_suggested_salary_structure(employee_name):
	"""Get suggested salary structure based on current CTC"""
	doc = frappe.get_doc("Employee", employee_name)
	
	if not doc.ctc or not doc.company or not doc.salary_currency:
		return None
	
	template = get_matching_template(
		doc.ctc, 
		doc.company, 
		doc.salary_currency
	)
	
	return template
