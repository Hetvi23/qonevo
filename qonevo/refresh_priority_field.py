# Copyright (c) 2025, Qonevo and contributors
# License: MIT. See LICENSE

import frappe
from frappe import _

@frappe.whitelist()
def refresh_priority_field():
    """Force refresh the priority field to ensure it's visible"""
    
    try:
        # Get the priority custom field
        if frappe.db.exists("Custom Field", {"fieldname": "priority", "dt": "Sales Order"}):
            custom_field = frappe.get_doc("Custom Field", {"fieldname": "priority", "dt": "Sales Order"})
            
            # Ensure the field is properly configured
            custom_field.hidden = 0
            custom_field.read_only = 0
            custom_field.in_list_view = 1
            custom_field.in_standard_filter = 1
            custom_field.reqd = 1
            custom_field.insert_after = "order_type"
            custom_field.save()
            
            print(f"Priority field refreshed: {custom_field.name}")
            print(f"Field properties: hidden={custom_field.hidden}, read_only={custom_field.read_only}")
            
            # Clear cache
            frappe.clear_cache()
            
            frappe.msgprint(_("Priority field refreshed successfully! Please refresh your browser."), indicator="green")
            
        else:
            frappe.msgprint(_("Priority field not found!"), indicator="red")
            
    except Exception as e:
        frappe.msgprint(f"Error refreshing priority field: {str(e)}", indicator="red")

@frappe.whitelist()
def check_form_fields():
    """Check what fields are available in the Sales Order form"""
    
    try:
        # Get Sales Order meta
        meta = frappe.get_meta("Sales Order")
        
        print("Sales Order form fields:")
        for field in meta.fields:
            if field.fieldname in ["priority", "priority_status", "delivery_week"]:
                print(f"- {field.fieldname}: {field.label} ({field.fieldtype}) - Hidden: {field.hidden}")
        
        # Check custom fields specifically
        custom_fields = frappe.get_all(
            "Custom Field",
            filters={"dt": "Sales Order"},
            fields=["fieldname", "label", "hidden", "read_only", "insert_after"]
        )
        
        print("\nCustom fields for Sales Order:")
        for field in custom_fields:
            print(f"- {field.fieldname}: {field.label} - Hidden: {field.hidden}, Read Only: {field.read_only}, Insert After: {field.insert_after}")
            
        return True
        
    except Exception as e:
        print(f"Error checking form fields: {str(e)}")
        return False 