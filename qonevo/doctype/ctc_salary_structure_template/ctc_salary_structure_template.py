# Copyright (c) 2024, Qonevo and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CTCSalaryStructureTemplate(Document):
	def validate(self):
		self.validate_ctc_range()
		self.validate_currency()
		self.validate_earnings_and_deductions()

	def validate_ctc_range(self):
		if self.ctc_range_from and self.ctc_range_to:
			if self.ctc_range_from >= self.ctc_range_to:
				frappe.throw(_("CTC Range From must be less than CTC Range To"))

	def validate_currency(self):
		if not self.currency:
			frappe.throw(_("Currency is required"))

	def validate_earnings_and_deductions(self):
		if not self.earnings and not self.deductions:
			frappe.throw(_("At least one earning or deduction component is required"))

	@frappe.whitelist()
	def create_salary_structure(self, employee_name=None):
		"""Create a salary structure based on this template"""
		if not self.earnings and not self.deductions:
			frappe.throw(_("No salary components defined in template"))

		# Create salary structure
		salary_structure = frappe.new_doc("Salary Structure")
		salary_structure.company = self.company
		salary_structure.currency = self.currency
		salary_structure.is_active = "Yes"
		
		# Generate name based on template and CTC range
		salary_structure.name = f"{self.template_name} - {self.ctc_range_from}-{self.ctc_range_to}"

		# Add earnings
		for earning in self.earnings:
			salary_structure.append("earnings", {
				"salary_component": earning.salary_component,
				"amount": earning.amount,
				"amount_based_on_formula": earning.amount_based_on_formula,
				"formula": earning.formula,
				"condition": earning.condition
			})

		# Add deductions
		for deduction in self.deductions:
			salary_structure.append("deductions", {
				"salary_component": deduction.salary_component,
				"amount": deduction.amount,
				"amount_based_on_formula": deduction.amount_based_on_formula,
				"formula": deduction.formula,
				"condition": deduction.condition
			})

		salary_structure.insert()
		salary_structure.submit()

		# Update template with created salary structure
		self.salary_structure_template = salary_structure.name
		self.save()

		return salary_structure.name


@frappe.whitelist()
def get_matching_template(ctc, company, currency):
	"""Find matching CTC template for given CTC amount"""
	filters = {
		"company": company,
		"currency": currency,
		"is_active": "Yes",
		"ctc_range_from": ["<=", ctc],
		"ctc_range_to": [">=", ctc]
	}
	
	templates = frappe.get_all(
		"CTC Salary Structure Template",
		filters=filters,
		fields=["name", "template_name", "salary_structure_template"],
		order_by="ctc_range_from desc"
	)
	
	return templates[0] if templates else None


@frappe.whitelist()
def create_salary_structure_from_ctc(ctc, company, currency, employee_name=None):
	"""Create or find salary structure based on CTC"""
	# First, try to find matching template
	template = get_matching_template(ctc, company, currency)
	
	if template and template.salary_structure_template:
		# Return existing salary structure
		return template.salary_structure_template
	elif template:
		# Create salary structure from template
		template_doc = frappe.get_doc("CTC Salary Structure Template", template.name)
		return template_doc.create_salary_structure(employee_name)
	else:
		# No matching template found
		frappe.throw(_("No matching CTC template found for CTC {0} in company {1}").format(ctc, company))






