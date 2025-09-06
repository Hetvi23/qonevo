# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from qonevo.barcode_utils import BarcodeUtils
from qonevo.serial_number_handlers import after_insert, regenerate_serial_barcode, bulk_generate_serial_barcodes


def test_serial_barcode_system():
    """Test the serial number barcode system functionality"""
    
    print("Testing Serial Number Barcode System...")
    print("=" * 50)
    
    # Test 1: Generate barcode with serial number
    print("\n1. Testing barcode generation with serial number...")
    try:
        # Get a sample item that has serial numbers enabled
        items = frappe.get_all("Item", 
            filters={"is_stock_item": 1, "has_serial_no": 1}, 
            fields=["name", "item_name", "default_manufacturer_part_no"],
            limit=1
        )
        
        if items:
            item = items[0]
            test_serial = f"TEST-SERIAL-{frappe.utils.now()}"
            
            result = BarcodeUtils.generate_item_barcode(
                item.name, 
                item.default_manufacturer_part_no or "TEST-MODEL-123",
                test_serial,
                "CODE128"
            )
            
            if result.get("success"):
                print(f"✓ Barcode generated for {item.name} with serial {test_serial}")
                print(f"  Barcode String: {result.get('barcode_string')}")
                print(f"  Model Number: {result.get('model_number')}")
                print(f"  Serial Number: {result.get('serial_number')}")
            else:
                print(f"✗ Barcode generation failed: {result.get('error')}")
        else:
            print("✗ No items with serial numbers found for testing")
            
    except Exception as e:
        print(f"✗ Error in barcode generation test: {str(e)}")
    
    # Test 2: Scan barcode with serial number
    print("\n2. Testing barcode scanning with serial number...")
    try:
        if items:
            item = items[0]
            test_serial = f"TEST-SERIAL-{frappe.utils.now()}"
            barcode_string = f"{item.name}|{item.default_manufacturer_part_no or 'TEST-MODEL-123'}|{test_serial}"
            
            result = BarcodeUtils.scan_barcode(barcode_string)
            
            if result.get("success"):
                print(f"✓ Barcode scanned successfully")
                print(f"  Item Code: {result.get('item_code')}")
                print(f"  Model Number: {result.get('model_number')}")
                print(f"  Serial Number: {result.get('serial_number')}")
                print(f"  Item Name: {result.get('item_name')}")
            else:
                print(f"✗ Barcode scanning failed: {result.get('error')}")
        else:
            print("✗ No items found for testing")
            
    except Exception as e:
        print(f"✗ Error in barcode scanning test: {str(e)}")
    
    # Test 3: Test serial number handler
    print("\n3. Testing serial number handler...")
    try:
        if items:
            item = items[0]
            test_serial = f"TEST-SERIAL-HANDLER-{frappe.utils.now()}"
            
            # Create a mock serial number document
            class MockSerialDoc:
                def __init__(self, item_code, name):
                    self.item_code = item_code
                    self.name = name
                    self.is_new = lambda: True
                
                def db_set(self, field, value):
                    print(f"  Would set {field} = {value}")
            
            mock_serial = MockSerialDoc(item.name, test_serial)
            after_insert(mock_serial, None)
            print(f"✓ Serial number handler executed for {test_serial}")
            
        else:
            print("✗ No items found for testing")
            
    except Exception as e:
        print(f"✗ Error in serial number handler test: {str(e)}")
    
    # Test 4: Test barcode format validation
    print("\n4. Testing barcode format validation...")
    try:
        valid_barcodes = [
            "ITEM-001|MODEL-123|SERIAL-456",
            "ITEM-002||SERIAL-789",  # No model number
            "ITEM-003|MODEL-456",    # No serial number
            "SIMPLE-ITEM"            # Simple item code
        ]
        
        invalid_barcodes = [
            "",
            None,
            "|",
            "|MODEL-ONLY",
            "||SERIAL-ONLY"
        ]
        
        for barcode in valid_barcodes:
            is_valid = BarcodeUtils.validate_barcode_format(barcode)
            print(f"  {barcode}: {'✓ Valid' if is_valid else '✗ Invalid'}")
        
        for barcode in invalid_barcodes:
            is_valid = BarcodeUtils.validate_barcode_format(barcode)
            print(f"  {barcode}: {'✓ Valid' if is_valid else '✗ Invalid'}")
            
    except Exception as e:
        print(f"✗ Error in barcode validation test: {str(e)}")
    
    # Test 5: Test ERPNext compatibility with serial numbers
    print("\n5. Testing ERPNext compatibility with serial numbers...")
    try:
        if items:
            item = items[0]
            test_serial = f"TEST-SERIAL-COMPAT-{frappe.utils.now()}"
            barcode_string = f"{item.name}|{item.default_manufacturer_part_no or 'TEST-MODEL-123'}|{test_serial}"
            
            result = BarcodeUtils.get_item_by_barcode(barcode_string)
            
            if result and result.get("item_code"):
                print(f"✓ ERPNext compatible barcode scanning works with serial numbers")
                print(f"  Item Code: {result.get('item_code')}")
                print(f"  Item Name: {result.get('item_name')}")
                print(f"  Serial Number: {result.get('serial_number')}")
                print(f"  Model Number: {result.get('model_number')}")
            else:
                print(f"✗ ERPNext compatible barcode scanning failed")
        else:
            print("✗ No items found for testing")
            
    except Exception as e:
        print(f"✗ Error in ERPNext compatibility test: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Serial Number Barcode System testing completed!")
    print("\nNext steps:")
    print("1. Create a serial number for an item")
    print("2. Check if barcode is automatically generated")
    print("3. Test scanning the barcode in logistics modules")
    print("4. Verify serial number is populated in item tables")


if __name__ == "__main__":
    test_serial_barcode_system()
