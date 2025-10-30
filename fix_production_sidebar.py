#!/usr/bin/env python3
"""
Production Server Sidebar Fix Script
=====================================
This script fixes the sidebar loading issues caused by corrupted workspace data.

Run this script on your production server:
    cd /home/frappe/frappe-bench
    bench --site qonevo.local execute qonevo.fix_production_sidebar.fix_sidebar_issues
"""

import frappe

def fix_sidebar_issues():
    """Fix sidebar loading issues by cleaning corrupted workspace data"""
    
    print("\n" + "="*70)
    print("🔧 PRODUCTION SERVER SIDEBAR FIX")
    print("="*70 + "\n")
    
    # Step 1: Check for corrupted workspaces
    print("📋 STEP 1: Checking for corrupted workspaces...")
    print("-" * 70)
    
    corrupted_workspaces = frappe.db.sql("""
        SELECT name, label, title, module, public
        FROM `tabWorkspace` 
        WHERE (title IS NULL OR title = '') 
        AND name != 'Welcome Workspace'
    """, as_dict=True)
    
    if corrupted_workspaces:
        print(f"⚠️  Found {len(corrupted_workspaces)} corrupted workspace(s):")
        for ws in corrupted_workspaces:
            print(f"   • {ws.name} (label: '{ws.label}', title: '{ws.title}')")
    else:
        print("✅ No corrupted workspaces found")
    
    # Step 2: Delete corrupted workspaces
    if corrupted_workspaces:
        print(f"\n📋 STEP 2: Deleting {len(corrupted_workspaces)} corrupted workspace(s)...")
        print("-" * 70)
        
        for ws in corrupted_workspaces:
            try:
                # Delete related child tables first
                frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s", ws.name)
                frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent = %s", ws.name)
                frappe.db.sql("DELETE FROM `tabWorkspace Chart` WHERE parent = %s", ws.name)
                frappe.db.sql("DELETE FROM `tabWorkspace Number Card` WHERE parent = %s", ws.name)
                frappe.db.sql("DELETE FROM `tabWorkspace Custom Block` WHERE parent = %s", ws.name)
                frappe.db.sql("DELETE FROM `tabWorkspace Quick List` WHERE parent = %s", ws.name)
                
                # Delete the workspace
                frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = %s", ws.name)
                
                print(f"   ✅ Deleted: {ws.name}")
            except Exception as e:
                print(f"   ❌ Error deleting {ws.name}: {e}")
                frappe.db.rollback()
                return False
        
        frappe.db.commit()
        print(f"✅ Successfully deleted {len(corrupted_workspaces)} corrupted workspace(s)")
    else:
        print("\n📋 STEP 2: No workspaces to delete")
        print("-" * 70)
    
    # Step 3: Check for workspace links with NULL values
    print("\n📋 STEP 3: Checking workspace links...")
    print("-" * 70)
    
    null_links_count = frappe.db.sql("""
        SELECT COUNT(*) as cnt
        FROM `tabWorkspace Link`
        WHERE link_to IS NULL OR link_to = ''
    """, as_dict=True)[0]['cnt']
    
    if null_links_count > 0:
        print(f"⚠️  Found {null_links_count} workspace link(s) with NULL link_to")
        print("   These are typically section headers and are okay")
    else:
        print("✅ No problematic workspace links found")
    
    # Step 4: Verify cleanup
    print("\n📋 STEP 4: Verifying cleanup...")
    print("-" * 70)
    
    remaining_issues = frappe.db.sql("""
        SELECT COUNT(*) as cnt
        FROM `tabWorkspace` 
        WHERE (title IS NULL OR title = '') 
        AND name != 'Welcome Workspace'
    """, as_dict=True)[0]['cnt']
    
    if remaining_issues == 0:
        print("✅ All corrupted workspaces have been cleaned up")
    else:
        print(f"⚠️  Still found {remaining_issues} workspace(s) with issues")
        return False
    
    # Final summary
    print("\n" + "="*70)
    print("✅ DATABASE CLEANUP COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\n📝 NEXT STEPS:")
    print("   1. Clear cache: bench --site qonevo.local clear-cache")
    print("   2. Rebuild assets: bench build --app qonevo")
    print("   3. Restart bench: bench restart")
    print("   4. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)")
    print("\n")
    
    return True

if __name__ == "__main__":
    fix_sidebar_issues()

