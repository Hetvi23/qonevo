#!/usr/bin/env python3
"""
Test script to check data returned by Purchase Receipt Manager backend methods
"""

import frappe
import json

def test_get_pos_without_pr():
    """Test the get_pos_without_pr method"""
    print("=" * 60)
    print("TESTING: get_pos_without_pr()")
    print("=" * 60)
    
    try:
        # Call the method
        result = frappe.call('qonevo.qonevo.doctype.requirement_gathering.requirement_gathering.get_pos_without_pr')
        
        print(f"Method returned: {type(result)}")
        print(f"Result: {json.dumps(result, indent=2, default=str)}")
        
        if result:
            print(f"\nFound {len(result)} Purchase Orders without PRs")
            for i, po in enumerate(result, 1):
                print(f"\n{i}. PO: {po.get('name', 'N/A')}")
                print(f"   Supplier: {po.get('supplier', 'N/A')}")
                print(f"   Date: {po.get('transaction_date', 'N/A')}")
                print(f"   Amount: {po.get('grand_total', 'N/A')}")
        else:
            print("\nNo Purchase Orders found without PRs")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def test_get_po_items():
    """Test the get_po_items method with a sample PO"""
    print("\n" + "=" * 60)
    print("TESTING: get_po_items()")
    print("=" * 60)
    
    try:
        # First, get a list of POs to test with
        pos = frappe.get_list(
            "Purchase Order",
            filters={"docstatus": 1},
            fields=["name"],
            limit=1
        )
        
        if not pos:
            print("No submitted Purchase Orders found to test with")
            return
        
        test_po = pos[0].name
        print(f"Testing with PO: {test_po}")
        
        # Call the method
        result = frappe.call(
            'qonevo.qonevo.doctype.requirement_gathering.requirement_gathering.get_po_items',
            args={'po_name': test_po}
        )
        
        print(f"Method returned: {type(result)}")
        print(f"Result: {json.dumps(result, indent=2, default=str)}")
        
        if result:
            print(f"\nFound {len(result)} items in PO {test_po}")
            for i, item in enumerate(result, 1):
                print(f"\n{i}. Item: {item.get('item_code', 'N/A')}")
                print(f"   Name: {item.get('item_name', 'N/A')}")
                print(f"   Qty: {item.get('qty', 'N/A')}")
                print(f"   Rate: {item.get('rate', 'N/A')}")
        else:
            print(f"\nNo items found in PO {test_po}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def test_purchase_order_data():
    """Test raw Purchase Order data to understand the structure"""
    print("\n" + "=" * 60)
    print("TESTING: Raw Purchase Order Data")
    print("=" * 60)
    
    try:
        # Get all submitted POs
        pos = frappe.get_list(
            "Purchase Order",
            filters={"docstatus": 1},
            fields=["name", "supplier", "transaction_date", "grand_total", "company", "status"],
            limit=5
        )
        
        print(f"Found {len(pos)} submitted Purchase Orders:")
        for i, po in enumerate(pos, 1):
            print(f"\n{i}. PO: {po.name}")
            print(f"   Supplier: {po.supplier}")
            print(f"   Date: {po.transaction_date}")
            print(f"   Amount: {po.grand_total}")
            print(f"   Status: {po.status}")
            print(f"   Company: {po.company}")
            
            # Check if this PO has any Purchase Receipts
            prs = frappe.get_list(
                "Purchase Receipt",
                filters={
                    "purchase_order": po.name,
                    "docstatus": ["!=", 2]  # Not cancelled
                },
                fields=["name", "docstatus"]
            )
            
            if prs:
                print(f"   Has PRs: YES ({len(prs)} PRs)")
                for pr in prs:
                    print(f"     - {pr.name} (status: {pr.docstatus})")
            else:
                print(f"   Has PRs: NO")
                
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def test_supplier_data():
    """Test supplier data to ensure we can get supplier names"""
    print("\n" + "=" * 60)
    print("TESTING: Supplier Data")
    print("=" * 60)
    
    try:
        # Get a few suppliers
        suppliers = frappe.get_list(
            "Supplier",
            fields=["name", "supplier_name", "supplier_type"],
            limit=5
        )
        
        print(f"Found {len(suppliers)} suppliers:")
        for i, supplier in enumerate(suppliers, 1):
            print(f"\n{i}. Supplier: {supplier.name}")
            print(f"   Name: {supplier.supplier_name}")
            print(f"   Type: {supplier.supplier_type}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Purchase Receipt Manager - Data Testing")
    print("=" * 60)
    
    # Run all tests
    test_purchase_order_data()
    test_supplier_data()
    test_get_pos_without_pr()
    test_get_po_items()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60) 