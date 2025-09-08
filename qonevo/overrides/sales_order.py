import frappe
from frappe import _
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

class QonevoSalesOrder(SalesOrder):
    def validate(self):
        super().validate()


def after_submit(doc, method):
    if doc.quotation:
        quotation = frappe.get_doc("Quotation", doc.quotation)
        if quotation.opportunity:
            opportunity = frappe.get_doc("Opportunity", quotation.opportunity)
            if opportunity.party_type == "Lead" and opportunity.party_name:
                lead = frappe.get_doc("Lead", opportunity.party_name)
                lead.custom_linked_sales_order = doc.name
                lead.save()
                frappe.db.commit()

    # Set initial priority status
    if not doc.priority_status:
        doc.priority_status = "Pending"
    doc.save()
