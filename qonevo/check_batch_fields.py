#!/usr/bin/env python3

import frappe

def check_batch_fields():
    print("=== Checking All Custom Fields ===")
    
    # Check custom fields for Batch
    batch_fields = frappe.db.sql("""
        SELECT fieldname, label, fieldtype, description 
        FROM `tabCustom Field` 
        WHERE dt = 'Batch' 
        ORDER BY fieldname
    """, as_dict=True)
    
    if batch_fields:
        print(f"\nFound {len(batch_fields)} custom fields in Batch DocType:")
        for field in batch_fields:
            print(f"  - {field.fieldname}: {field.label} ({field.fieldtype})")
            if field.description:
                print(f"    Description: {field.description}")
    else:
        print("\nNo custom fields found in Batch DocType")
    
    # Check custom fields for Serial No
    serial_fields = frappe.db.sql("""
        SELECT fieldname, label, fieldtype, description 
        FROM `tabCustom Field` 
        WHERE dt = 'Serial No' 
        ORDER BY fieldname
    """, as_dict=True)
    
    # Check custom fields for Delivery Note Item
    delivery_note_item_fields = frappe.db.sql("""
        SELECT fieldname, label, fieldtype, description 
        FROM `tabCustom Field` 
        WHERE dt = 'Delivery Note Item' 
        ORDER BY fieldname
    """, as_dict=True)
    
    if serial_fields:
        print(f"\nFound {len(serial_fields)} custom fields in Serial No DocType:")
        for field in serial_fields:
            print(f"  - {field.fieldname}: {field.label} ({field.fieldtype})")
            if field.description:
                print(f"    Description: {field.description}")
    else:
        print("\nNo custom fields found in Serial No DocType")
    
    if delivery_note_item_fields:
        print(f"\nFound {len(delivery_note_item_fields)} custom fields in Delivery Note Item DocType:")
        for field in delivery_note_item_fields:
            print(f"  - {field.fieldname}: {field.label} ({field.fieldtype})")
            if field.description:
                print(f"    Description: {field.description}")
    else:
        print("\nNo custom fields found in Delivery Note Item DocType")
    
    # Check for any fields with different naming patterns
    print(f"\n=== Checking for alternative naming patterns ===")
    
    # Look for fields that might be barcode-related with different names
    alternative_fields = frappe.db.sql("""
        SELECT fieldname, label, fieldtype, dt
        FROM `tabCustom Field` 
        WHERE (
            fieldname LIKE '%qr%' OR fieldname LIKE '%QR%' OR
            fieldname LIKE '%code%' OR fieldname LIKE '%Code%' OR
            fieldname LIKE '%string%' OR fieldname LIKE '%String%' OR
            fieldname LIKE '%generated%' OR fieldname LIKE '%Generated%' OR
            label LIKE '%QR%' OR label LIKE '%qr%' OR
            label LIKE '%Code%' OR label LIKE '%code%' OR
            label LIKE '%String%' OR label LIKE '%string%' OR
            label LIKE '%Generated%' OR label LIKE '%generated%'
        )
        ORDER BY dt, fieldname
    """, as_dict=True)
    
    if alternative_fields:
        print(f"Found {len(alternative_fields)} fields with alternative naming patterns:")
        for field in alternative_fields:
            print(f"  - {field.dt}.{field.fieldname}: {field.label} ({field.fieldtype})")
    else:
        print("No alternative naming patterns found")
    
    # Also check if there are any barcode-related fields
    barcode_fields = frappe.db.sql("""
        SELECT fieldname, label, fieldtype, dt
        FROM `tabCustom Field` 
        WHERE (fieldname LIKE '%barcode%' OR label LIKE '%barcode%' OR label LIKE '%Barcode%')
        ORDER BY dt, fieldname
    """, as_dict=True)
    
    if barcode_fields:
        print(f"\nFound {len(barcode_fields)} barcode-related custom fields:")
        for field in barcode_fields:
            print(f"  - {field.dt}.{field.fieldname}: {field.label} ({field.fieldtype})")
    else:
        print("\nNo barcode-related custom fields found")
