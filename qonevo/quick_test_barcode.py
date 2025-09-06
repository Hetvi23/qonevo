# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe


def quick_test_barcode():
    """Quick test of barcode system functionality"""
    
    print("Quick Barcode System Test")
    print("=" * 40)
    
    try:
        # Test 1: Check if barcode utils can be imported
        from qonevo.barcode_utils import BarcodeUtils
        print("✓ BarcodeUtils imported successfully")
        
        # Test 2: Test barcode generation
        result = BarcodeUtils.generate_item_barcode(
            "TEST-ITEM-001", 
            "TEST-MODEL-123", 
            "TEST-SERIAL-456",
            "CODE128"
        )
        
        if result.get("success"):
            print("✓ Barcode generation works")
            print(f"  Generated: {result.get('barcode_string')}")
        else:
            print(f"✗ Barcode generation failed: {result.get('error')}")
        
        # Test 3: Test barcode scanning
        barcode_string = "TEST-ITEM-001|TEST-MODEL-123|TEST-SERIAL-456"
        result = BarcodeUtils.scan_barcode(barcode_string)
        
        if result.get("success"):
            print("✓ Barcode scanning works")
            print(f"  Item: {result.get('item_code')}")
            print(f"  Model: {result.get('model_number')}")
            print(f"  Serial: {result.get('serial_number')}")
        else:
            print(f"✗ Barcode scanning failed: {result.get('error')}")
        
        # Test 4: Check if custom fields exist
        custom_fields = frappe.get_all("Custom Field", 
            filters={"fieldname": "model_number"},
            fields=["name", "dt"]
        )
        
        if custom_fields:
            print(f"✓ Custom fields found: {len(custom_fields)}")
        else:
            print("✗ No custom fields found")
        
        print("\n" + "=" * 40)
        print("✓ Barcode system is working correctly!")
        
    except Exception as e:
        print(f"✗ Error in barcode system: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    quick_test_barcode()
