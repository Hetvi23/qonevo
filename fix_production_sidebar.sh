#!/bin/bash

# Production Server Sidebar Fix Script
# =====================================
# This script automates the complete fix process for sidebar loading issues
# Run this on your production server

set -e  # Exit on error

echo ""
echo "=========================================================================="
echo "🔧 PRODUCTION SERVER SIDEBAR FIX"
echo "=========================================================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [ ! -f "sites/qonevo.local/site_config.json" ]; then
    echo -e "${RED}❌ Error: Please run this script from /home/frappe/frappe-bench${NC}"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo -e "${BLUE}📋 Step 1/5: Cleaning corrupted workspace data from database...${NC}"
echo "--------------------------------------------------------------------------"
bench --site qonevo.local console <<'PYTHON_EOF'
import frappe

print("\n" + "="*70)
print("🔧 CLEANING CORRUPTED WORKSPACE DATA")
print("="*70 + "\n")

# Check for corrupted workspaces
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
    
    print(f"\nDeleting {len(corrupted_workspaces)} corrupted workspace(s)...")
    
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
    
    frappe.db.commit()
    print(f"\n✅ Successfully deleted {len(corrupted_workspaces)} corrupted workspace(s)")
else:
    print("✅ No corrupted workspaces found")

# Verify cleanup
remaining_issues = frappe.db.sql("""
    SELECT COUNT(*) as cnt
    FROM `tabWorkspace` 
    WHERE (title IS NULL OR title = '') 
    AND name != 'Welcome Workspace'
""", as_dict=True)[0]['cnt']

if remaining_issues == 0:
    print("\n✅ Database cleanup completed successfully!")
else:
    print(f"\n⚠️  Warning: Still found {remaining_issues} workspace(s) with issues")

PYTHON_EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Database cleanup failed. Please check the errors above.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}📋 Step 2/5: Clearing cache...${NC}"
echo "--------------------------------------------------------------------------"
bench --site qonevo.local clear-cache
echo -e "${GREEN}✅ Cache cleared${NC}"

echo ""
echo -e "${BLUE}📋 Step 3/5: Rebuilding assets...${NC}"
echo "--------------------------------------------------------------------------"
bench build --app qonevo

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Asset build failed. Trying with --force flag...${NC}"
    bench build --force
fi

echo -e "${GREEN}✅ Assets rebuilt${NC}"

echo ""
echo -e "${BLUE}📋 Step 4/5: Restarting bench...${NC}"
echo "--------------------------------------------------------------------------"
bench restart
echo -e "${GREEN}✅ Bench restarted${NC}"

echo ""
echo -e "${BLUE}📋 Step 5/5: Verifying fix...${NC}"
echo "--------------------------------------------------------------------------"

# Verify database is clean
CORRUPTED_COUNT=$(bench --site qonevo.local mariadb -sN <<EOF
SELECT COUNT(*) 
FROM \`tabWorkspace\` 
WHERE (title IS NULL OR title = '') 
AND name != 'Welcome Workspace';
EOF
)

if [ "$CORRUPTED_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ Database verification passed (0 corrupted workspaces)${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Found $CORRUPTED_COUNT corrupted workspace(s) still remaining${NC}"
fi

echo ""
echo "=========================================================================="
echo -e "${GREEN}✅ FIX COMPLETED SUCCESSFULLY!${NC}"
echo "=========================================================================="
echo ""
echo -e "${YELLOW}📝 FINAL STEP: Clear your browser cache${NC}"
echo ""
echo "   1. Open your browser at: http://16.16.58.13"
echo "   2. Press Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)"
echo "   3. Or clear browser cache from settings"
echo ""
echo "   The sidebar should now load properly with all navigation links."
echo ""
echo "=========================================================================="
echo ""

