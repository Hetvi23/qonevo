# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def check_and_fix_serial_barcode_fields():
    """Check if custom fields exist and create them if they don't"""
    
    print("Checking and fixing Serial No custom fields...")
    print("=" * 50)
    
    # Check if custom fields exist
    barcode_string_field = frappe.db.exists("Custom Field", {
        "dt": "Serial No",
        "fieldname": "custom_barcode_string"
    })
    
    barcode_generated_field = frappe.db.exists("Custom Field", {
        "dt": "Serial No", 
        "fieldname": "custom_barcode_generated"
    })
    
    print(f"Barcode String field exists: {bool(barcode_string_field)}")
    print(f"Barcode Generated field exists: {bool(barcode_generated_field)}")
    
    if not barcode_string_field or not barcode_generated_field:
        print("Creating missing custom fields...")
        
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
            ]
        }
        
        create_custom_fields(custom_fields, update=True)
        frappe.db.commit()
        print("✓ Custom fields created successfully!")
    else:
        print("✓ All custom fields already exist!")
    
    # Test the fields
    print("\nTesting custom fields...")
    try:
        # Get a sample serial number
        serials = frappe.get_all("Serial No", limit=1)
        if serials:
            serial_name = serials[0].name
            barcode_string = frappe.db.get_value("Serial No", serial_name, "custom_barcode_string")
            barcode_generated = frappe.db.get_value("Serial No", serial_name, "custom_barcode_generated")
            
            print(f"Sample serial: {serial_name}")
            print(f"Barcode String: {barcode_string or 'None'}")
            print(f"Barcode Generated: {barcode_generated or 'None'}")
        else:
            print("No serial numbers found to test")
            
    except Exception as e:
        print(f"Error testing fields: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✓ Custom fields check completed!")


def test_serial_barcode_generation():
    """Test generating barcodes for serial numbers"""
    
    print("\nTesting serial barcode generation...")
    print("=" * 40)
    
    try:
        # Get a serial number
        serials = frappe.get_all("Serial No", 
            filters={"item_code": ["!=", ""]},
            fields=["name", "item_code"],
            limit=1
        )
        
        if not serials:
            print("No serial numbers found. Please create a serial number first.")
            return
        
        serial = serials[0]
        print(f"Testing with serial: {serial.name} for item: {serial.item_code}")
        
        # Get item details
        item_doc = frappe.get_doc("Item", serial.item_code)
        model_number = item_doc.get("default_manufacturer_part_no") or ""
        
        print(f"Item: {item_doc.item_name}")
        print(f"Model: {model_number}")
        
        # Generate barcode
        from qonevo.barcode_utils import BarcodeUtils
        
        result = BarcodeUtils.generate_item_barcode(
            item_code=serial.item_code,
            model_number=model_number,
            serial_number=serial.name,
            barcode_type="CODE128"
        )
        
        if result.get("success"):
            print(f"✓ Barcode generated: {result.get('barcode_string')}")
            
            # Update serial number
            frappe.db.sql("""
                UPDATE `tabSerial No` 
                SET custom_barcode_string = %s, custom_barcode_generated = 1
                WHERE name = %s
            """, (result.get("barcode_string"), serial.name))
            
            frappe.db.commit()
            
            # Verify update
            updated_barcode = frappe.db.get_value("Serial No", serial.name, "custom_barcode_string")
            if updated_barcode:
                print(f"✓ Barcode stored in serial number: {updated_barcode}")
            else:
                print("✗ Barcode not stored in serial number")
                
        else:
            print(f"✗ Failed to generate barcode: {result.get('error')}")
            
    except Exception as e:
        print(f"✗ Error in test: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_and_fix_serial_barcode_fields()
    test_serial_barcode_generation()
