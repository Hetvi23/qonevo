# Production Server Sidebar Fix Guide

## Problem
The sidebar is not loading on the production server and showing errors:
- `Uncaught TypeError: Cannot read properties of null (reading 'toLowerCase')` in router.js
- `Uncaught TypeError: frappe.ready is not a function` in clean_barcode_scanner.js

## Root Cause
- Corrupted workspace data with NULL titles in the database
- JavaScript code using `frappe.ready()` which doesn't work in desk environment

## Solution Overview
1. Pull latest code (already done)
2. Clean corrupted workspace data from database
3. Clear cache
4. Rebuild assets
5. Restart bench

---

## Step-by-Step Instructions

### OPTION 1: Automated Script (RECOMMENDED)

#### Step 1: Run the Fix Script
```bash
cd /home/frappe/frappe-bench
bench --site qonevo.local execute qonevo.fix_production_sidebar.fix_sidebar_issues
```

This script will:
- ✅ Check for corrupted workspaces
- ✅ Delete corrupted workspace data
- ✅ Verify cleanup was successful

#### Step 2: Clear Cache
```bash
cd /home/frappe/frappe-bench
bench --site qonevo.local clear-cache
```

#### Step 3: Rebuild Assets
```bash
cd /home/frappe/frappe-bench
bench build --app qonevo
```

This rebuilds the JavaScript files with the fixes.

#### Step 4: Restart Bench
```bash
cd /home/frappe/frappe-bench
bench restart
```

#### Step 5: Clear Browser Cache
1. Open your browser at http://16.16.58.13
2. Press `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
3. Or clear browser cache completely from browser settings

---

### OPTION 2: Manual Database Cleanup

If you prefer to do it manually or the script doesn't work:

#### Step 1: Connect to Database Console
```bash
cd /home/frappe/frappe-bench
bench --site qonevo.local console
```

#### Step 2: Run Cleanup Commands

Paste this into the console:

```python
import frappe

# Check for corrupted workspaces
corrupted = frappe.db.sql("""
    SELECT name, label, title, module
    FROM `tabWorkspace` 
    WHERE (title IS NULL OR title = '') 
    AND name != 'Welcome Workspace'
""", as_dict=True)

print(f"Found {len(corrupted)} corrupted workspaces")
for ws in corrupted:
    print(f"  - {ws.name}")

# Delete corrupted workspaces
for ws in corrupted:
    # Delete child records first
    frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s", ws.name)
    frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent = %s", ws.name)
    frappe.db.sql("DELETE FROM `tabWorkspace Chart` WHERE parent = %s", ws.name)
    frappe.db.sql("DELETE FROM `tabWorkspace Number Card` WHERE parent = %s", ws.name)
    frappe.db.sql("DELETE FROM `tabWorkspace Custom Block` WHERE parent = %s", ws.name)
    frappe.db.sql("DELETE FROM `tabWorkspace Quick List` WHERE parent = %s", ws.name)
    
    # Delete workspace
    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = %s", ws.name)
    print(f"✅ Deleted {ws.name}")

# Commit changes
frappe.db.commit()
print("✅ Database cleanup completed!")
```

#### Step 3: Exit Console
Type `exit` and press Enter

#### Step 4: Clear Cache
```bash
bench --site qonevo.local clear-cache
```

#### Step 5: Rebuild Assets
```bash
bench build --app qonevo
```

#### Step 6: Restart Bench
```bash
bench restart
```

#### Step 7: Clear Browser Cache
Hard refresh your browser at http://16.16.58.13 (Ctrl+Shift+R)

---

## Verification Steps

After completing the fix, verify everything is working:

### 1. Check Database
```bash
cd /home/frappe/frappe-bench
bench --site qonevo.local mariadb
```

Then run:
```sql
SELECT COUNT(*) as corrupted_count
FROM `tabWorkspace` 
WHERE (title IS NULL OR title = '') 
AND name != 'Welcome Workspace';
```

Should show `0` corrupted workspaces.

Type `exit` to leave mariadb.

### 2. Check Browser Console
1. Open http://16.16.58.13 in browser
2. Press F12 to open Developer Tools
3. Go to Console tab
4. Refresh page (Ctrl+Shift+R)
5. Check for errors:
   - ❌ Should NOT see: `frappe.ready is not a function`
   - ❌ Should NOT see: `Cannot read properties of null`
   - ✅ Sidebar should load with all navigation links

### 3. Test Sidebar Navigation
1. Click on different modules in the sidebar (Home, Accounting, Stock, etc.)
2. All should load without errors
3. Gray placeholder boxes should be gone

---

## Troubleshooting

### Issue: Script not found
**Error:** `ModuleNotFoundError: No module named 'qonevo.fix_production_sidebar'`

**Solution:**
```bash
cd /home/frappe/frappe-bench/apps/qonevo
git pull
bench restart
# Then try running the script again
```

### Issue: Sidebar still showing gray boxes
**Solution:**
1. Clear browser cache completely (not just hard refresh)
2. Try opening in incognito/private window
3. Try different browser
4. Check browser console for remaining JavaScript errors

### Issue: Permission denied errors
**Solution:**
Run commands with proper user:
```bash
sudo su - frappe
cd /home/frappe/frappe-bench
# Then run the commands
```

### Issue: Redis connection warnings
**Error:** `Cannot connect to redis_cache`

**Solution:** This is just a warning, safe to ignore. The fix will still work.

### Issue: Assets not rebuilding
**Solution:**
```bash
cd /home/frappe/frappe-bench
bench build --force
bench restart
```

---

## Files Modified (Already in Git)

The following files have been fixed and are in the latest code:

1. **qonevo/public/js/clean_barcode_scanner.js**
   - Fixed: Removed `frappe.ready()` usage
   - Changed to proper `frappe.ui.form.on()` pattern

2. **qonevo/setup_embedded_dashboard.py**
   - Fixed: Added missing `title` field to workspace creation
   - Fixed: Added `link_to` field to workspace links
   - Changed link type from "Card Break" to "Link"

---

## Quick Command Reference

```bash
# All-in-one fix (after pulling code)
cd /home/frappe/frappe-bench
bench --site qonevo.local execute qonevo.fix_production_sidebar.fix_sidebar_issues
bench --site qonevo.local clear-cache
bench build --app qonevo
bench restart

# Then hard refresh browser (Ctrl+Shift+R)
```

---

## Support

If you still face issues after following this guide:

1. Check the browser console (F12) for specific error messages
2. Check bench logs: `bench --site qonevo.local logs`
3. Take a screenshot of the error and share it

---

**Last Updated:** 2025-10-30  
**Fix Version:** Commit 75453e1



