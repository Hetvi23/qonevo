#!/usr/bin/env python3
import frappe

def check_doctype():
    try:
        # Check if doctype exists
        if frappe.db.exists('DocType', 'Requirement Generation'):
            print("✅ Requirement Generation doctype exists")
            
            # Get the doctype
            doctype = frappe.get_doc('DocType', 'Requirement Generation')
            print(f"📋 Doctype fields:")
            
            for field in doctype.fields:
                print(f"  - {field.fieldname}: {field.fieldtype} ({field.label})")
                
        else:
            print("❌ Requirement Generation doctype does not exist")
            
        # Check if child table exists
        if frappe.db.exists('DocType', 'Requirement Generation Item'):
            print("✅ Requirement Generation Item child table exists")
        else:
            print("❌ Requirement Generation Item child table does not exist")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_doctype() 