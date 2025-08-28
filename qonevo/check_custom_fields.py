# Copyright (c) 2025, Qonevo and contributors
# License: MIT. See LICENSE

import frappe
from frappe import _

@frappe.whitelist()
def check_custom_fields():
    """Check existing custom fields for Sales Order"""
    try:
        # Check existing custom fields
        custom_fields = frappe.get_all(
            "Custom Field", 
            filters={"parent": "Sales Order"}, 
            fields=["fieldname", "label", "fieldtype", "options"]
        )
        
        print("Existing custom fields for Sales Order:")
        for field in custom_fields:
            print(f"- {field.fieldname}: {field.label} ({field.fieldtype})")
        
        # Check if our fields exist
        required_fields = ["priority", "priority_status", "finance_approval_status", "inventory_approval_status", "delivery_week"]
        missing_fields = []
        
        for field_name in required_fields:
            if not frappe.db.exists("Custom Field", {"fieldname": field_name, "parent": "Sales Order"}):
                missing_fields.append(field_name)
        
        print(f"\nMissing fields: {missing_fields}")
        
        return {
            "existing_fields": custom_fields,
            "missing_fields": missing_fields
        }
        
    except Exception as e:
        print(f"Error checking custom fields: {str(e)}")
        return {"error": str(e)}

@frappe.whitelist()
def create_single_custom_field():
    """Create a single custom field to test"""
    try:
        # Create priority field
        if not frappe.db.exists("Custom Field", {"fieldname": "priority", "parent": "Sales Order"}):
            field_data = {
                "doctype": "Custom Field",
                "fieldname": "priority",
                "label": "Priority",
                "fieldtype": "Select",
                "options": "Low\nMedium\nHigh\nUrgent",
                "default": "Medium",
                "insert_after": "order_type",
                "parent": "Sales Order",
                "reqd": 1,
                "in_standard_filter": 1,
                "in_list_view": 1,
                "width": "100px"
            }
            
            custom_field = frappe.get_doc(field_data)
            custom_field.insert()
            frappe.db.commit()
            print("Successfully created priority field")
            return True
        else:
            print("Priority field already exists")
            return True
            
    except Exception as e:
        print(f"Error creating custom field: {str(e)}")
        frappe.db.rollback()
        return False 