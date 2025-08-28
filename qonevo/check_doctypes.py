#!/usr/bin/env python3
import frappe

def check_doctypes():
    print("Checking Qonevo doctypes...")
    
    # Check if qonevo app is installed
    try:
        doctypes = frappe.get_all('DocType', filters={'module': 'Qonevo'}, fields=['name', 'module', 'istable'])
        print(f"Found {len(doctypes)} doctypes in Qonevo module:")
        for dt in doctypes:
            print(f"  - {dt.name} (istable: {dt.istable})")
    except Exception as e:
        print(f"Error getting doctypes: {e}")
    
    # Check specifically for Requirement Generation/Gathering
    try:
        if frappe.db.exists('DocType', 'Requirement Generation'):
            print("✅ Requirement Generation doctype exists")
        else:
            print("❌ Requirement Generation doctype does not exist")
            
        if frappe.db.exists('DocType', 'Requirement Gathering'):
            print("✅ Requirement Gathering doctype exists")
        else:
            print("❌ Requirement Gathering doctype does not exist")
    except Exception as e:
        print(f"Error checking Requirement doctypes: {e}")
    
    # Check for Requirement Items
    try:
        if frappe.db.exists('DocType', 'Requirement Items'):
            print("✅ Requirement Items doctype exists")
        else:
            print("❌ Requirement Items doctype does not exist")
    except Exception as e:
        print(f"Error checking Requirement Items: {e}")

if __name__ == "__main__":
    check_doctypes() 