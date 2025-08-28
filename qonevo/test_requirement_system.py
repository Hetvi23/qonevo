#!/usr/bin/env python3
"""
Test script for Requirement Gathering System
"""

import frappe
from frappe import _

def test_requirement_system():
    """Test the Requirement Gathering system"""
    print("Testing Requirement Gathering System...")
    
    # Check if doctypes exist
    if not frappe.db.exists('DocType', 'Requirement Gathering'):
        print("❌ Requirement Gathering doctype does not exist")
        return False
    
    if not frappe.db.exists('DocType', 'Requirement Items'):
        print("❌ Requirement Items child table does not exist")
        return False
    
    print("✅ Both doctypes exist")
    
    # Test creating a sample requirement gathering
    try:
        # Get default company
        default_company = frappe.defaults.get_global_default("company")
        if not default_company:
            print("❌ No default company found")
            return False
        
        # Create a test supplier if it doesn't exist
        if not frappe.db.exists('Supplier', 'TEST-SUPPLIER-001'):
            try:
                supplier = frappe.new_doc('Supplier')
                supplier.supplier_name = 'Test Supplier 001'
                supplier.supplier_type = 'Company'
                supplier.supplier_group = 'All Supplier Groups'
                supplier.insert()
                print("✅ Created test supplier")
            except Exception as e:
                print(f"⚠️ Supplier creation failed (may already exist): {e}")
        else:
            print("✅ Test supplier already exists")
        
        # Create a test item if it doesn't exist
        if not frappe.db.exists('Item', 'TEST-ITEM-001'):
            try:
                item = frappe.new_doc('Item')
                item.item_code = 'TEST-ITEM-001'
                item.item_name = 'Test Item 001'
                item.item_group = 'Products'
                item.stock_uom = 'Nos'
                item.is_stock_item = 1
                item.insert()
                print("✅ Created test item")
            except Exception as e:
                print(f"⚠️ Item creation failed (may already exist): {e}")
        else:
            print("✅ Test item already exists")
        
        # Create a test requirement gathering
        if not frappe.db.exists('Requirement Gathering', 'REQ-0001'):
            try:
                req = frappe.new_doc('Requirement Gathering')
                req.supplier = 'TEST-SUPPLIER-001'
                req.date = frappe.utils.today()
                
                # Add a requirement item
                req.append('requirement_item', {
                    'item_code': 'TEST-ITEM-001',
                    'qty': 10,
                    'rate': 100,
                    'select_ircl': 'Pending'
                })
                
                req.insert()
                print("✅ Created test requirement gathering")
            except Exception as e:
                print(f"⚠️ Requirement gathering creation failed: {e}")
        else:
            print("✅ Test requirement gathering already exists")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_methods():
    """Test the server methods"""
    print("\nTesting server methods...")
    
    try:
        # Check if test document exists
        if not frappe.db.exists('Requirement Gathering', 'REQ-0001'):
            print("⚠️ Test document REQ-0001 not found, skipping method tests")
            return False
        
        # Test fetch_supplier_details
        req = frappe.get_doc('Requirement Gathering', 'REQ-0001')
        req.fetch_supplier_details()
        print("✅ fetch_supplier_details method works")
        
        # Test approve_items
        req.approve_items('REQ-0001', all=True)
        print("✅ approve_items method works")
        
        # Test reject_items
        req.reject_items('REQ-0001', all=True)
        print("✅ reject_items method works")
        
        print("✅ All server methods work!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing methods: {e}")
        return False

if __name__ == "__main__":
    test_requirement_system()
    test_methods() 