# Copyright (c) 2025, Hetvi Patel and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class RequirementItems(Document):
    def validate(self):
        self.calculate_amount()

@frappe.whitelist()
def fetch_item_details(docname):
    """Fetch item details when item_code is selected"""
    doc = frappe.get_doc("Requirement Items", docname)
    if doc.item_code:
        item = frappe.get_doc("Item", doc.item_code)
        doc.item_name = item.item_name
        
        # Try to get default buying rate from Item Price
        try:
            item_price = frappe.get_value(
                "Item Price",
                {
                    "item_code": doc.item_code,
                    "price_list": "Standard Buying",
                    "valid_from": ["<=", frappe.utils.today()],
                    "valid_upto": [">=", frappe.utils.today()]
                },
                "price_list_rate"
            )
            if item_price:
                doc.rate = item_price
            else:
                # If no item price found, try to get standard rate
                doc.rate = item.standard_rate or 0
        except:
            # If no item price found, try to get standard rate
            try:
                doc.rate = item.standard_rate or 0
            except:
                doc.rate = 0
        
        # Calculate amount
        calculate_amount(docname)
        doc.save()
        return {"status": "success"}

@frappe.whitelist()
def calculate_amount(docname):
    """Calculate amount based on qty and rate"""
    doc = frappe.get_doc("Requirement Items", docname)
    if doc.qty and doc.rate:
        doc.amount = doc.qty * doc.rate
    else:
        doc.amount = 0
    doc.save()
    return {"status": "success"}


