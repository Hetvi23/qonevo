#!/usr/bin/env python3
import frappe

def fix_workspace_issue():
    """Fix workspace issues that are causing sidebar problems"""
    
    # Clear any corrupted workspace data
    try:
        # Delete any problematic workspace entries
        frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name LIKE '%qonevo%'")
        frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent LIKE '%qonevo%'")
        frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent LIKE '%qonevo%'")
        frappe.db.sql("DELETE FROM `tabWorkspace Chart` WHERE parent LIKE '%qonevo%'")
        frappe.db.sql("DELETE FROM `tabWorkspace Number Card` WHERE parent LIKE '%qonevo%'")
        frappe.db.sql("DELETE FROM `tabWorkspace Custom Block` WHERE parent LIKE '%qonevo%'")
        
        # Clear user workspace preferences
        frappe.db.sql("UPDATE `tabUser` SET desk_sidebar = NULL WHERE name = 'Administrator'")
        
        frappe.db.commit()
        print("✅ Workspace data cleared successfully")
        
    except Exception as e:
        print(f"❌ Error clearing workspace data: {e}")
        frappe.db.rollback()

if __name__ == "__main__":
    fix_workspace_issue() 