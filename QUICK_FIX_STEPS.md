# 🚀 Quick Fix - Production Sidebar Issues

## Problem
- Sidebar not loading (showing gray boxes)
- JavaScript errors in console

## 🎯 QUICKEST FIX (Copy and Paste These Commands)

### On Your Production Server, run these commands:

```bash
# Step 1: Go to bench directory
cd /home/frappe/frappe-bench

# Step 2: Pull latest code (if not already done)
cd apps/qonevo
git pull
cd ../..

# Step 3: Run the automated fix script
bash apps/qonevo/fix_production_sidebar.sh
```

That's it! The script will automatically:
- ✅ Clean corrupted database entries
- ✅ Clear cache  
- ✅ Rebuild assets
- ✅ Restart bench
- ✅ Verify the fix

### Final Step (In Your Browser):
1. Open http://16.16.58.13
2. Press **Ctrl+Shift+R** (Windows/Linux) or **Cmd+Shift+R** (Mac) to hard refresh

---

## Alternative: Manual Steps

If the automated script doesn't work, follow these manual steps:

### Step 1: Clean Database
```bash
cd /home/frappe/frappe-bench
bench --site qonevo.local console
```

Then paste this code:
```python
import frappe

corrupted = frappe.db.sql("""
    SELECT name FROM `tabWorkspace` 
    WHERE (title IS NULL OR title = '') 
    AND name != 'Welcome Workspace'
""", as_dict=True)

for ws in corrupted:
    frappe.db.sql("DELETE FROM `tabWorkspace Link` WHERE parent = %s", ws.name)
    frappe.db.sql("DELETE FROM `tabWorkspace Shortcut` WHERE parent = %s", ws.name)
    frappe.db.sql("DELETE FROM `tabWorkspace Chart` WHERE parent = %s", ws.name)
    frappe.db.sql("DELETE FROM `tabWorkspace Number Card` WHERE parent = %s", ws.name)
    frappe.db.sql("DELETE FROM `tabWorkspace Custom Block` WHERE parent = %s", ws.name)
    frappe.db.sql("DELETE FROM `tabWorkspace Quick List` WHERE parent = %s", ws.name)
    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name = %s", ws.name)
    print(f"✅ Deleted {ws.name}")

frappe.db.commit()
print("✅ Done!")
```

Type `exit` to leave the console.

### Step 2: Clear Cache
```bash
bench --site qonevo.local clear-cache
```

### Step 3: Rebuild Assets  
```bash
bench build --app qonevo
```

### Step 4: Restart
```bash
bench restart
```

### Step 5: Browser Hard Refresh
- Press **Ctrl+Shift+R** or **Cmd+Shift+R**

---

## ✅ How to Verify It's Fixed

1. Open http://16.16.58.13 in browser
2. Press F12 → Go to Console tab
3. You should NOT see these errors:
   - ❌ `frappe.ready is not a function`
   - ❌ `Cannot read properties of null`
4. Sidebar should show all navigation links (no gray boxes)

---

## 📚 More Details

For detailed explanation and troubleshooting, see:
- **PRODUCTION_SIDEBAR_FIX_GUIDE.md** - Complete detailed guide
- **fix_production_sidebar.py** - Python cleanup script
- **fix_production_sidebar.sh** - Bash automation script

---

## 🆘 Still Having Issues?

1. Check browser console (F12) for error messages
2. Try opening in incognito/private window
3. Try completely clearing browser cache (not just hard refresh)
4. Check logs: `bench --site qonevo.local logs`

---

**Fix Applied:** ✅  
**Last Updated:** 2025-10-30  
**Commit:** 75453e1

