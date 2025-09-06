#!/usr/bin/env python3

import frappe

def test_barcode_system():
    print("=== Testing Barcode System ===")
    
    # Create a test item if it doesn't exist
    item_code = "TEST-ITEM-001"
    if not frappe.db.exists("Item", item_code):
        print(f"Creating test item: {item_code}")
        test_item = frappe.get_doc({
            "doctype": "Item",
            "item_code": item_code,
            "item_name": "Test Item 001",
            "item_group": "All Item Groups",
            "default_manufacturer_part_no": "MODEL-123",
            "has_serial_no": 1,
            "is_stock_item": 1,
            "is_sales_item": 1,
            "is_purchase_item": 1,
            "stock_uom": "Nos"
        })
        test_item.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"✅ Created test item: {item_code}")
    else:
        print(f"✅ Test item already exists: {item_code}")
    
    # Test barcode generation
    print(f"\n=== Testing Barcode Generation ===")
    from qonevo.barcode_utils import BarcodeUtils
    
    result = BarcodeUtils.generate_item_barcode(
        item_code="TEST-ITEM-001",
        model_number="MODEL-123",
        serial_number="SERIAL-456",
        barcode_type="CODE128"
    )
    
    if result.get("success"):
        barcode_string = result.get("barcode_string")
        print(f"✅ Generated barcode: {barcode_string}")
        
        # Test barcode scanning
        print(f"\n=== Testing Barcode Scanning ===")
        scan_result = BarcodeUtils.scan_barcode(barcode_string)
        print(f"Scan result: {scan_result}")
        
        if scan_result.get("success"):
            print(f"✅ Barcode scanning successful!")
            print(f"   Item Code: {scan_result.get('item_code')}")
            print(f"   Item Name: {scan_result.get('item_name')}")
            print(f"   Model Number: {scan_result.get('model_number')}")
            print(f"   Serial Number: {scan_result.get('serial_number')}")
        else:
            print(f"❌ Barcode scanning failed: {scan_result.get('error')}")
        
        # Test item lookup (ERPNext compatible)
        print(f"\n=== Testing Item Lookup ===")
        lookup_result = BarcodeUtils.get_item_by_barcode(barcode_string)
        print(f"Lookup result: {lookup_result}")
        
        if lookup_result:
            print(f"✅ Item lookup successful!")
            print(f"   Item Code: {lookup_result.get('item_code')}")
            print(f"   Item Name: {lookup_result.get('item_name')}")
            print(f"   Barcode: {lookup_result.get('barcode')}")
            print(f"   UOM: {lookup_result.get('uom')}")
        else:
            print(f"❌ Item lookup failed")
        
    else:
        print(f"❌ Barcode generation failed: {result.get('error')}")

if __name__ == "__main__":
    test_barcode_system()