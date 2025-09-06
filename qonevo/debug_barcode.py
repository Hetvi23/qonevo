#!/usr/bin/env python3

import frappe

def debug_barcode():
    print("=== Debugging Barcode Scanning ===")
    
    # Test the scan_barcode method directly
    from qonevo.barcode_utils import BarcodeUtils
    
    barcode_string = "TEST-ITEM-001|MODEL-123|SERIAL-456"
    print(f"Testing barcode: {barcode_string}")
    
    result = BarcodeUtils.scan_barcode(barcode_string)
    print(f"Scan result: {result}")
    
    # Test the API method
    print(f"\nTesting API method:")
    api_result = frappe.call("qonevo.barcode_utils.scan_item_barcode", barcode_string=barcode_string)
    print(f"API result: {api_result}")
    
    # Check if item exists
    print(f"\nChecking if item exists:")
    item_exists = frappe.db.exists("Item", "TEST-ITEM-001")
    print(f"Item TEST-ITEM-001 exists: {item_exists}")
    
    if item_exists:
        item_doc = frappe.get_doc("Item", "TEST-ITEM-001")
        print(f"Item details: {item_doc.item_name}, {item_doc.default_manufacturer_part_no}")

if __name__ == "__main__":
    debug_barcode()
