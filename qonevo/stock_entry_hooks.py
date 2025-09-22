# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def add_manufacturing_serial(sales_order, serial_no, item_code, manufacturing_date):
    """
    Add a manufacturing serial to the sales order's custom_manufactured_serials table.
    """
    print(f"➕ MANUFACTURING SERIAL: Adding serial {serial_no} for item {item_code} to Sales Order {sales_order.name}")
    
    try:
        # Check if the serial already exists
        print(f"🔍 MANUFACTURING SERIAL: Checking if serial {serial_no} already exists")
        existing_serial = frappe.db.exists("Manufacturing Serials", {
            "parent": sales_order.name,
            "parenttype": "Sales Order",
            "parentfield": "custom_manufactured_serials",
            "serial_no": serial_no,
            "item_code": item_code
        })
        
        if existing_serial:
            print(f"⚠️ MANUFACTURING SERIAL: Serial {serial_no} already exists in Sales Order {sales_order.name}, skipping")
            return
        
        # Create new manufacturing serial entry
        print(f"📝 MANUFACTURING SERIAL: Creating new manufacturing serial entry")
        manufacturing_serial = frappe.new_doc("Manufacturing Serials")
        manufacturing_serial.parent = sales_order.name
        manufacturing_serial.parenttype = "Sales Order"
        manufacturing_serial.parentfield = "custom_manufactured_serials"
        manufacturing_serial.serial_no = serial_no
        manufacturing_serial.item_code = item_code
        manufacturing_serial.manufacturing_date = manufacturing_date
        
        manufacturing_serial.insert(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"✅ MANUFACTURING SERIAL: Successfully added serial {serial_no} to Sales Order {sales_order.name}")
        
    except Exception as e:
        print(f"❌ MANUFACTURING SERIAL: Error adding serial {serial_no}: {str(e)}")
        frappe.logger().error(f"Error adding manufacturing serial {serial_no}: {str(e)}")


def serial_bundle_after_insert(doc, method):
    """
    Called when a Serial and Batch Bundle is created.
    This will trigger our manufacturing serials logic when serial numbers are created.
    """
    print(f"🔧 SERIAL BUNDLE HOOK: serial_bundle_after_insert triggered for {doc.name}")
    
    try:
        # Check if this bundle is related to a Stock Entry
        if not doc.voucher_type == "Stock Entry":
            print(f"⏭️ SERIAL BUNDLE HOOK: Bundle {doc.name} is not for Stock Entry, skipping")
            return
        
        stock_entry_name = doc.voucher_no
        print(f"📋 SERIAL BUNDLE HOOK: Processing Serial Bundle {doc.name} for Stock Entry {stock_entry_name}")
        
        # Get the Stock Entry
        if not frappe.db.exists("Stock Entry", stock_entry_name):
            print(f"❌ SERIAL BUNDLE HOOK: Stock Entry {stock_entry_name} not found")
            return
        
        stock_entry_doc = frappe.get_doc("Stock Entry", stock_entry_name)
        
        # Check if Stock Entry has work order
        if not stock_entry_doc.work_order:
            print(f"⏭️ SERIAL BUNDLE HOOK: Stock Entry {stock_entry_name} has no work order, skipping")
            return
        
        # Check if Stock Entry type is Manufacture (only process manufacturing serials)
        if stock_entry_doc.purpose != "Manufacture":
            print(f"⏭️ SERIAL BUNDLE HOOK: Stock Entry {stock_entry_name} purpose is {stock_entry_doc.purpose}, not Manufacture - skipping")
            return
        
        print(f"🏭 SERIAL BUNDLE HOOK: Stock Entry {stock_entry_name} has Work Order {stock_entry_doc.work_order} and purpose is Manufacture")
        
        # Get Work Order and Sales Order
        work_order = frappe.get_doc("Work Order", stock_entry_doc.work_order)
        if not work_order.sales_order:
            print(f"⏭️ SERIAL BUNDLE HOOK: Work Order {work_order.name} has no sales order, skipping")
            return
        
        sales_order = frappe.get_doc("Sales Order", work_order.sales_order)
        print(f"📦 SERIAL BUNDLE HOOK: Processing Sales Order {sales_order.name}")
        
        # Process the serial bundle entries (only production bundles with positive qty)
        if doc.entries:
            # Check if this is a production bundle (positive qty or qty is None but has serials)
            is_production = False
            if doc.total_qty is not None and doc.total_qty > 0:
                is_production = True
                print(f"📦 SERIAL BUNDLE HOOK: Bundle has {len(doc.entries)} entries with positive qty {doc.total_qty} (production)")
            elif doc.total_qty is None:
                # If qty is None, check if any entry has positive qty
                for entry in doc.entries:
                    if entry.qty and entry.qty > 0:
                        is_production = True
                        print(f"📦 SERIAL BUNDLE HOOK: Bundle has {len(doc.entries)} entries with None total_qty but positive entry qty (production)")
                        break
            
            if is_production:
                serials_found = False
                for entry in doc.entries:
                    if entry.serial_no:
                        serials_found = True
                        print(f"➕ SERIAL BUNDLE HOOK: Processing production serial {entry.serial_no}")
                        
                        # Use the item_code from the bundle
                        item_code = doc.item_code
                        print(f"📦 SERIAL BUNDLE HOOK: Serial {entry.serial_no} belongs to item {item_code}")
                        
                        # Add manufacturing serial
                        add_manufacturing_serial(sales_order, entry.serial_no, item_code, stock_entry_doc.posting_date)
                
                if not serials_found:
                    print(f"⏭️ SERIAL BUNDLE HOOK: No serial numbers found in production bundle entries")
            else:
                qty_info = doc.total_qty if doc.total_qty is not None else "None"
                print(f"⏭️ SERIAL BUNDLE HOOK: Skipping bundle with qty {qty_info} (not production)")
        else:
            print(f"⏭️ SERIAL BUNDLE HOOK: No entries in bundle, skipping")
        
        # Update custom_serials_added checkbox
        current_value = frappe.db.get_value("Sales Order", sales_order.name, "custom_serials_added")
        if current_value != 1:
            frappe.db.set_value("Sales Order", sales_order.name, "custom_serials_added", 1)
            frappe.db.commit()
            print(f"✅ SERIAL BUNDLE HOOK: Updated custom_serials_added to 1 for Sales Order {sales_order.name}")
        else:
            print(f"ℹ️ SERIAL BUNDLE HOOK: custom_serials_added already set to 1 for Sales Order {sales_order.name}")
        
        print(f"🎉 SERIAL BUNDLE HOOK: Successfully processed Serial Bundle {doc.name}")
        
    except Exception as e:
        print(f"❌ SERIAL BUNDLE HOOK: Error in serial_bundle_after_insert: {str(e)}")
        frappe.logger().error(f"Error in serial_bundle_after_insert: {str(e)}")