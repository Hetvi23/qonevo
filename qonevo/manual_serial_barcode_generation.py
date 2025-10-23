# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from qonevo.barcode_utils import BarcodeUtils


def generate_barcodes_for_existing_serials():
    """Generate barcodes for existing serial numbers"""
    
    print("Generating barcodes for existing serial numbers...")
    print("=" * 50)
    
    try:
        # Get all serial numbers that don't have barcodes yet
        serials = frappe.db.sql("""
            SELECT name, item_code 
            FROM `tabSerial No` 
            WHERE (custom_barcode_generated IS NULL OR custom_barcode_generated = 0)
            AND item_code IS NOT NULL
            LIMIT 10
        """, as_dict=True)
        
        if not serials:
            print("No serial numbers found that need barcodes")
            return
        
        print(f"Found {len(serials)} serial numbers to process")
        
        success_count = 0
        error_count = 0
        
        for serial in serials:
            try:
                print(f"Processing serial: {serial.name} for item: {serial.item_code}")
                
                # Get item details
                item_doc = frappe.get_doc("Item", serial.item_code)
                model_number = item_doc.get("default_manufacturer_part_no") or ""
                
                # Generate barcode
                result = BarcodeUtils.generate_item_barcode(
                    item_code=serial.item_code,
                    model_number=model_number,
                    serial_number=serial.name,
                    barcode_type="CODE128"
                )
                
                if result.get("success"):
                    # Update serial number with barcode info
                    frappe.db.sql("""
                        UPDATE `tabSerial No` 
                        SET custom_barcode_string = %s, custom_barcode_generated = 1
                        WHERE name = %s
                    """, (result.get("barcode_string"), serial.name))
                    
                    print(f"  ✓ Generated barcode: {result.get('barcode_string')}")
                    success_count += 1
                    
                else:
                    print(f"  ✗ Failed to generate barcode: {result.get('error')}")
                    error_count += 1
                    
            except Exception as e:
                print(f"  ✗ Error processing {serial.name}: {str(e)}")
                error_count += 1
        
        frappe.db.commit()
        
        print("\n" + "=" * 50)
        print(f"✓ Successfully generated {success_count} barcodes")
        print(f"✗ {error_count} errors")
        
    except Exception as e:
        print(f"Error in bulk generation: {str(e)}")
        import traceback
        traceback.print_exc()


def test_serial_barcode_flow():
    """Test the complete serial barcode flow"""
    
    print("Testing Serial Barcode Flow...")
    print("=" * 40)
    
    try:
        # Test 1: Create a test serial number
        print("1. Creating test serial number...")
        
        # Get an item that has serial numbers enabled
        items = frappe.get_all("Item", 
            filters={"is_stock_item": 1, "has_serial_no": 1}, 
            fields=["name", "item_name", "default_manufacturer_part_no"],
            limit=1
        )
        
        if not items:
            print("No items with serial numbers found. Creating a test item...")
            # Create a test item
            item_doc = frappe.get_doc({
                "doctype": "Item",
                "item_code": "TEST-SERIAL-ITEM-001",
                "item_name": "Test Serial Item",
                "item_group": "All Item Groups",
                "stock_uom": "Nos",
                "is_stock_item": 1,
                "has_serial_no": 1,
                "default_manufacturer_part_no": "TEST-MODEL-001"
            })
            item_doc.insert(ignore_permissions=True)
            items = [{"name": "TEST-SERIAL-ITEM-001", "item_name": "Test Serial Item", "default_manufacturer_part_no": "TEST-MODEL-001"}]
        
        item = items[0]
        test_serial = f"TEST-SN-{frappe.utils.now().replace(':', '').replace(' ', '').replace('-', '')}"
        
        # Create serial number
        serial_doc = frappe.get_doc({
            "doctype": "Serial No",
            "item_code": item["name"],
            "serial_no": test_serial
        })
        serial_doc.insert(ignore_permissions=True)
        
        print(f"  ✓ Created serial number: {test_serial}")
        
        # Test 2: Generate barcode for this serial
        print("2. Generating barcode for serial number...")
        
        result = BarcodeUtils.generate_item_barcode(
            item_code=item["name"],
            model_number=item.get("default_manufacturer_part_no", ""),
            serial_number=test_serial,
            barcode_type="CODE128"
        )
        
        if result.get("success"):
            print(f"  ✓ Generated barcode: {result.get('barcode_string')}")
            
            # Test 3: Update serial number with barcode
            print("3. Updating serial number with barcode...")
            
            frappe.db.sql("""
                UPDATE `tabSerial No` 
                SET custom_barcode_string = %s, custom_barcode_generated = 1
                WHERE name = %s
            """, (result.get("barcode_string"), test_serial))
            
            frappe.db.commit()
            
            # Test 4: Verify barcode is stored
            print("4. Verifying barcode is stored...")
            
            stored_barcode = frappe.db.get_value("Serial No", test_serial, "custom_barcode_string")
            if stored_barcode:
                print(f"  ✓ Barcode stored in serial number: {stored_barcode}")
            else:
                print("  ✗ Barcode not stored in serial number")
            
            # Test 5: Test scanning the barcode
            print("5. Testing barcode scanning...")
            
            scan_result = BarcodeUtils.scan_barcode(result.get("barcode_string"))
            if scan_result.get("success"):
                print(f"  ✓ Barcode scanned successfully")
                print(f"    Item: {scan_result.get('item_code')}")
                print(f"    Model: {scan_result.get('model_number')}")
                print(f"    Serial: {scan_result.get('serial_number')}")
            else:
                print(f"  ✗ Barcode scanning failed: {scan_result.get('error')}")
        
        else:
            print(f"  ✗ Failed to generate barcode: {result.get('error')}")
        
        print("\n" + "=" * 40)
        print("✓ Serial barcode flow test completed!")
        
    except Exception as e:
        print(f"✗ Error in test: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the test first
    test_serial_barcode_flow()
    
    # Then generate barcodes for existing serials
    generate_barcodes_for_existing_serials()
