#!/usr/bin/env python3
import frappe

def fix_sidebar():
    """Fix sidebar by clearing corrupted workspace data"""
    try:
        # Clear any problematic workspace data
        frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name IS NULL OR label IS NULL")
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent IS NULL OR label IS NULL")
        frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent IS NULL OR label IS NULL")
        
        # Clear user preferences that might be causing issues
        frappe.db.sql("UPDATE `tabUser` SET desk_sidebar = NULL WHERE name = 'Administrator'")
        
        frappe.db.commit()
        print("✅ Sidebar fix applied successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        frappe.db.rollback()

if __name__ == "__main__":
    fix_sidebar() 