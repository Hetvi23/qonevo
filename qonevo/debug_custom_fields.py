# Copyright (c) 2025, Qonevo and contributors
# License: MIT. See LICENSE

import frappe
from frappe import _

@frappe.whitelist()
def debug_custom_fields():
    """Debug Custom Field structure"""
    try:
        # Get Custom Field meta
        meta = frappe.get_meta("Custom Field")
        print("Custom Field fields:")
        for field in meta.fields:
            print(f"- {field.fieldname}: {field.fieldtype}")
        
        # Check existing custom fields for Sales Order
        custom_fields = frappe.get_all(
            "Custom Field", 
            fields=["name", "fieldname", "label", "fieldtype", "dt"]
        )
        
        print("\nAll Custom Fields:")
        for field in custom_fields:
            print(f"- {field.name}: {field.fieldname} ({field.dt})")
        
        # Check Sales Order specific fields
        sales_order_fields = [f for f in custom_fields if f.dt == "Sales Order"]
        print(f"\nSales Order Custom Fields ({len(sales_order_fields)}):")
        for field in sales_order_fields:
            print(f"- {field.fieldname}: {field.label}")
        
        return {
            "meta_fields": [f.fieldname for f in meta.fields],
            "all_custom_fields": custom_fields,
            "sales_order_fields": sales_order_fields
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)} 