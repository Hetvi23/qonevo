# Copyright (c) 2025, Qonevo and contributors
# License: MIT. See LICENSE

import frappe
from frappe import _

@frappe.whitelist()
def remove_approval_fields():
    """Remove approval-related custom fields since workflow is being used"""
    
    try:
        # Fields to remove
        fields_to_remove = [
            "finance_approval_status",
            "inventory_approval_status"
        ]
        
        for fieldname in fields_to_remove:
            if frappe.db.exists("Custom Field", {"fieldname": fieldname, "dt": "Sales Order"}):
                custom_field = frappe.get_doc("Custom Field", {"fieldname": fieldname, "dt": "Sales Order"})
                custom_field.delete()
                print(f"Removed custom field: {fieldname}")
        
        frappe.db.commit()
        frappe.msgprint(_("Approval fields removed successfully!"), indicator="green")
        
    except Exception as e:
        frappe.msgprint(f"Error removing approval fields: {str(e)}", indicator="red")
        frappe.db.rollback()

@frappe.whitelist()
def check_priority_field():
    """Check if priority field is visible and working"""
    
    try:
        # Check if priority field exists
        if frappe.db.exists("Custom Field", {"fieldname": "priority", "dt": "Sales Order"}):
            custom_field = frappe.get_doc("Custom Field", {"fieldname": "priority", "dt": "Sales Order"})
            print(f"Priority field exists: {custom_field.name}")
            print(f"Field properties: hidden={custom_field.hidden}, read_only={custom_field.read_only}")
            
            # Check if it's in the form
            sales_order_meta = frappe.get_meta("Sales Order")
            priority_field = sales_order_meta.get_field("priority")
            if priority_field:
                print(f"Priority field found in form: {priority_field.fieldname}")
                print(f"Field type: {priority_field.fieldtype}")
                print(f"Options: {priority_field.options}")
            else:
                print("Priority field not found in Sales Order form")
                
        else:
            print("Priority custom field does not exist")
            
        return True
        
    except Exception as e:
        print(f"Error checking priority field: {str(e)}")
        return False 