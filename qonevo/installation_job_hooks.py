# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def delivery_note_on_submit(doc, method):
    """
    Create Installation Job when Delivery Note is submitted and Sales Order has Installation Required = Yes.
    """
    print(f"🔧 INSTALLATION JOB HOOK: delivery_note_on_submit triggered for {doc.name}")
    
    try:
        # Check if this Delivery Note has items with serial numbers
        has_serial_items = False
        serial_items = []
        
        for item in doc.items:
            if item.serial_no or item.serial_and_batch_bundle:
                has_serial_items = True
                serial_items.append(item)
                print(f"📦 INSTALLATION JOB HOOK: Found serial item {item.item_code} with serial {item.serial_no}")
        
        if not has_serial_items:
            print(f"⏭️ INSTALLATION JOB HOOK: No serial items found in Delivery Note {doc.name}, skipping")
            return
        
        # Get Sales Order from the first item
        sales_order_name = None
        for item in doc.items:
            if item.against_sales_order:
                sales_order_name = item.against_sales_order
                break
        
        if not sales_order_name:
            print(f"⚠️ INSTALLATION JOB HOOK: No Sales Order found in Delivery Note {doc.name}, skipping")
            return
        
        # Get Sales Order details
        sales_order = frappe.get_doc("Sales Order", sales_order_name)
        
        print(f"📋 INSTALLATION JOB HOOK: Creating Installation Job for Sales Order {sales_order_name}")
        
        # Create Installation Job
        installation_job = frappe.new_doc("Installation Job")
        installation_job.sales_order = sales_order_name
        installation_job.delivery_note = doc.name
        installation_job.customer = sales_order.customer
        installation_job.status = "Scheduled"
        
        # Add installation items from Delivery Note items
        for item in doc.items:
            if item.serial_no or item.serial_and_batch_bundle:
                print(f"➕ INSTALLATION JOB HOOK: Adding installation item {item.item_code}")
                
                # Extract serial numbers from the item
                serial_numbers = get_item_serial_numbers(item)
                
                # Create installation item for each serial number
                for serial_no in serial_numbers:
                    installation_item = installation_job.append("installed_items")
                    installation_item.item = item.item_code
                    installation_item.qty = 1  # Each serial number represents 1 item
                    installation_item.serial_no = serial_no
                    installation_item.installed = 0  # Default to not installed
                    installation_item.installation_status = "Pending"
        
        # Save the Installation Job
        installation_job.insert(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"✅ INSTALLATION JOB HOOK: Successfully created Installation Job {installation_job.name}")
        print(f"🎉 INSTALLATION JOB HOOK: Installation Job created with {len(installation_job.installed_items)} items")
        
        # Show success message to user
        frappe.msgprint(
            _("Installation Job {0} created successfully with {1} items").format(
                installation_job.name, len(installation_job.installed_items)
            ),
            title=_("Installation Job Created"),
            indicator="green"
        )
        
    except Exception as e:
        print(f"❌ INSTALLATION JOB HOOK: Error creating Installation Job: {str(e)}")
        frappe.logger().error(f"Error creating Installation Job for Delivery Note {doc.name}: {str(e)}")
        
        # Show error message to user
        frappe.msgprint(
            _("Error creating Installation Job: {0}").format(str(e)),
            title=_("Installation Job Error"),
            indicator="red"
        )


def delivery_note_on_cancel(doc, method):
    """
    Cancel Installation Job when Delivery Note is cancelled.
    """
    print(f"🔧 INSTALLATION JOB HOOK: delivery_note_on_cancel triggered for {doc.name}")
    
    try:
        # Find Installation Jobs linked to this Delivery Note
        installation_jobs = frappe.get_all("Installation Job",
                                         filters={"delivery_note": doc.name},
                                         fields=["name", "status"])
        
        if not installation_jobs:
            print(f"ℹ️ INSTALLATION JOB HOOK: No Installation Jobs found for Delivery Note {doc.name}")
            return
        
        print(f"📋 INSTALLATION JOB HOOK: Found {len(installation_jobs)} Installation Jobs to cancel")
        
        for job in installation_jobs:
            if job.status != "Cancelled":
                print(f"🗑️ INSTALLATION JOB HOOK: Cancelling Installation Job {job.name}")
                
                # Update status to Cancelled
                frappe.db.set_value("Installation Job", job.name, "status", "Cancelled")
                frappe.db.commit()
                
                print(f"✅ INSTALLATION JOB HOOK: Successfully cancelled Installation Job {job.name}")
            else:
                print(f"ℹ️ INSTALLATION JOB HOOK: Installation Job {job.name} already cancelled")
        
        print(f"🎉 INSTALLATION JOB HOOK: Successfully processed {len(installation_jobs)} Installation Jobs")
        
    except Exception as e:
        print(f"❌ INSTALLATION JOB HOOK: Error cancelling Installation Jobs: {str(e)}")
        frappe.logger().error(f"Error cancelling Installation Jobs for Delivery Note {doc.name}: {str(e)}")


def get_item_serial_numbers(item):
    """
    Extract serial numbers from a Delivery Note item.
    """
    serial_numbers = []
    
    # Check if using new serial and batch bundle
    if item.serial_and_batch_bundle:
        try:
            bundle_doc = frappe.get_doc("Serial and Batch Bundle", item.serial_and_batch_bundle)
            for entry in bundle_doc.entries:
                if entry.serial_no:
                    serial_numbers.append(entry.serial_no)
        except Exception as e:
            frappe.logger().error(f"Error reading serial bundle: {str(e)}")
    
    # Check old serial_no field
    elif item.serial_no:
        # Split by newlines and commas, clean up
        serials = item.serial_no.replace('\n', ',').split(',')
        for serial in serials:
            serial = serial.strip()
            if serial:
                serial_numbers.append(serial)
    
    return serial_numbers

