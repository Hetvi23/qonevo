# Copyright (c) 2024, Qonevo and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.model.mapper import get_mapped_doc
from erpnext.crm.doctype.lead.lead import _set_missing_values


@frappe.whitelist()
def make_opportunity(source_name, target_doc=None):
	"""Override standard make_opportunity to include organisation_name mapping"""
	def set_missing_values(source, target):
		_set_missing_values(source, target)
		# Map organisation_name from Lead's company_name
		if source.company_name:
			target.organisation_name = source.company_name

	target_doc = get_mapped_doc(
		"Lead",
		source_name,
		{
			"Lead": {
				"doctype": "Opportunity",
				"field_map": {
					"campaign_name": "campaign",
					"doctype": "opportunity_from",
					"name": "party_name",
					"lead_name": "contact_display",
					"company_name": "customer_name",
					"email_id": "contact_email",
					"mobile_no": "contact_mobile",
					"lead_owner": "opportunity_owner",
					"notes": "notes",
				},
			}
		},
		target_doc,
		set_missing_values,
	)

	return target_doc
