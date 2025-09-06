# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def setup_barcode_system():
    """Setup barcode system with custom fields and configurations"""
    
    # Custom fields for logistics modules
    custom_fields = {
        "Serial No": [
            {
                "fieldname": "custom_barcode_string",
                "label": "Barcode String",
                "fieldtype": "Data",
                "insert_after": "item_code",
                "read_only": 1,
                "description": "Generated barcode string for this serial number"
            },
            {
                "fieldname": "custom_barcode_generated",
                "label": "Barcode Generated",
                "fieldtype": "Check",
                "insert_after": "custom_barcode_string",
                "read_only": 1,
                "description": "Whether barcode has been generated for this serial number"
            }
        ],
        "Delivery Note Item": [
            {
                "fieldname": "model_number",
                "label": "Model Number",
                "fieldtype": "Data",
                "insert_after": "item_name",
                "read_only": 1,
                "description": "Manufacturer part number from barcode scan"
            },
            {
                "fieldname": "scanned_serial_number",
                "label": "Scanned Serial Number",
                "fieldtype": "Data",
                "insert_after": "model_number",
                "read_only": 1,
                "description": "Serial number from barcode scan"
            },
            {
                "fieldname": "scanned_barcode",
                "label": "Scanned Barcode",
                "fieldtype": "Data",
                "insert_after": "barcode",
                "read_only": 1,
                "description": "Original barcode string from scan"
            }
        ],
        "Purchase Receipt Item": [
            {
                "fieldname": "model_number",
                "label": "Model Number",
                "fieldtype": "Data",
                "insert_after": "item_name",
                "read_only": 1,
                "description": "Manufacturer part number from barcode scan"
            },
            {
                "fieldname": "scanned_serial_number",
                "label": "Scanned Serial Number",
                "fieldtype": "Data",
                "insert_after": "model_number",
                "read_only": 1,
                "description": "Serial number from barcode scan"
            },
            {
                "fieldname": "scanned_barcode",
                "label": "Scanned Barcode",
                "fieldtype": "Data",
                "insert_after": "barcode",
                "read_only": 1,
                "description": "Original barcode string from scan"
            }
        ],
        "Stock Entry Detail": [
            {
                "fieldname": "model_number",
                "label": "Model Number",
                "fieldtype": "Data",
                "insert_after": "item_name",
                "read_only": 1,
                "description": "Manufacturer part number from barcode scan"
            },
            {
                "fieldname": "scanned_serial_number",
                "label": "Scanned Serial Number",
                "fieldtype": "Data",
                "insert_after": "model_number",
                "read_only": 1,
                "description": "Serial number from barcode scan"
            },
            {
                "fieldname": "scanned_barcode",
                "label": "Scanned Barcode",
                "fieldtype": "Data",
                "insert_after": "barcode",
                "read_only": 1,
                "description": "Original barcode string from scan"
            }
        ],
        "Material Request Item": [
            {
                "fieldname": "model_number",
                "label": "Model Number",
                "fieldtype": "Data",
                "insert_after": "item_name",
                "read_only": 1,
                "description": "Manufacturer part number from barcode scan"
            },
            {
                "fieldname": "scanned_serial_number",
                "label": "Scanned Serial Number",
                "fieldtype": "Data",
                "insert_after": "model_number",
                "read_only": 1,
                "description": "Serial number from barcode scan"
            },
            {
                "fieldname": "scanned_barcode",
                "label": "Scanned Barcode",
                "fieldtype": "Data",
                "insert_after": "barcode",
                "read_only": 1,
                "description": "Original barcode string from scan"
            }
        ],
        "Purchase Order Item": [
            {
                "fieldname": "model_number",
                "label": "Model Number",
                "fieldtype": "Data",
                "insert_after": "item_name",
                "read_only": 1,
                "description": "Manufacturer part number from barcode scan"
            },
            {
                "fieldname": "scanned_serial_number",
                "label": "Scanned Serial Number",
                "fieldtype": "Data",
                "insert_after": "model_number",
                "read_only": 1,
                "description": "Serial number from barcode scan"
            },
            {
                "fieldname": "scanned_barcode",
                "label": "Scanned Barcode",
                "fieldtype": "Data",
                "insert_after": "barcode",
                "read_only": 1,
                "description": "Original barcode string from scan"
            }
        ],
        "Sales Order Item": [
            {
                "fieldname": "model_number",
                "label": "Model Number",
                "fieldtype": "Data",
                "insert_after": "item_name",
                "read_only": 1,
                "description": "Manufacturer part number from barcode scan"
            },
            {
                "fieldname": "scanned_serial_number",
                "label": "Scanned Serial Number",
                "fieldtype": "Data",
                "insert_after": "model_number",
                "read_only": 1,
                "description": "Serial number from barcode scan"
            },
            {
                "fieldname": "scanned_barcode",
                "label": "Scanned Barcode",
                "fieldtype": "Data",
                "insert_after": "barcode",
                "read_only": 1,
                "description": "Original barcode string from scan"
            }
        ]
    }
    
    # Create custom fields
    create_custom_fields(custom_fields, update=True)
    
    # Create property setters to show barcode fields
    property_setters = [
        {
            "doctype": "Delivery Note Item",
            "doctype_or_field": "DocField",
            "field_name": "barcode",
            "property": "hidden",
            "value": 0
        },
        {
            "doctype": "Purchase Receipt Item",
            "doctype_or_field": "DocField", 
            "field_name": "barcode",
            "property": "hidden",
            "value": 0
        },
        {
            "doctype": "Stock Entry Detail",
            "doctype_or_field": "DocField",
            "field_name": "barcode", 
            "property": "hidden",
            "value": 0
        },
        {
            "doctype": "Material Request Item",
            "doctype_or_field": "DocField",
            "field_name": "barcode",
            "property": "hidden", 
            "value": 0
        },
        {
            "doctype": "Purchase Order Item",
            "doctype_or_field": "DocField",
            "field_name": "barcode",
            "property": "hidden",
            "value": 0
        },
        {
            "doctype": "Sales Order Item",
            "doctype_or_field": "DocField",
            "field_name": "barcode",
            "property": "hidden",
            "value": 0
        }
    ]
    
    for prop in property_setters:
        if not frappe.db.exists("Property Setter", {
            "doc_type": prop["doctype"],
            "field_name": prop["field_name"],
            "property": prop["property"]
        }):
            frappe.get_doc({
                "doctype": "Property Setter",
                "doc_type": prop["doctype"],
                "doctype_or_field": prop["doctype_or_field"],
                "field_name": prop["field_name"],
                "property": prop["property"],
                "value": prop["value"],
                "property_type": "Check"
            }).insert(ignore_permissions=True)
    
    frappe.db.commit()
    print("Barcode system setup completed successfully!")


def create_sample_barcodes():
    """Create sample barcodes for testing"""
    try:
        # Get some sample items
        items = frappe.get_all("Item", 
            filters={"is_stock_item": 1}, 
            fields=["name", "item_name", "default_manufacturer_part_no"],
            limit=5
        )
        
        for item in items:
            # Create barcode generator record
            barcode_doc = frappe.get_doc({
                "doctype": "Item Barcode Generator",
                "item_code": item.name,
                "model_number": item.default_manufacturer_part_no or f"MODEL-{item.name}",
                "barcode_type": "CODE128"
            })
            barcode_doc.insert(ignore_permissions=True)
            
        frappe.db.commit()
        print(f"Created sample barcodes for {len(items)} items")
        
    except Exception as e:
        print(f"Error creating sample barcodes: {str(e)}")


if __name__ == "__main__":
    setup_barcode_system()
    create_sample_barcodes()
