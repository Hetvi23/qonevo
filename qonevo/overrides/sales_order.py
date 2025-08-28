import frappe
from frappe import _
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

class QonevoSalesOrder(SalesOrder):
    def validate(self):
        super().validate()
        self.validate_priority_workflow()

    def validate_priority_workflow(self):
        """Validate priority workflow based on status"""
        if self.priority == "High" and self.status in ["Draft", "On Hold"]:
            # High priority orders should be processed quickly
            if self.delivery_date:
                from frappe.utils import add_days, getdate
                if getdate(self.delivery_date) < add_days(getdate(), 7):
                    frappe.msgprint(_("High priority order with delivery date less than 7 days. Please expedite processing."), indicator="orange")

    def on_submit(self):
        super().on_submit()
        self.update_priority_status()

    def update_priority_status(self):
        """Update priority status when order is submitted"""
        if self.priority:
            frappe.db.set_value("Sales Order", self.name, "priority_status", "In Progress")

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
