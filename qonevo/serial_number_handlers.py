# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from qonevo.barcode_utils import BarcodeUtils


def after_insert(doc, method):
    """Generate barcode when serial number is created"""
    try:
        if doc.item_code and doc.name:
            # Get item details
            item_doc = frappe.get_doc("Item", doc.item_code)
            model_number = item_doc.get("default_manufacturer_part_no") or ""
            
            # Generate barcode for this serial number
            result = BarcodeUtils.generate_item_barcode(
                item_code=doc.item_code,
                model_number=model_number,
                serial_number=doc.name,
                barcode_type="CODE128"
            )
            
            if result.get("success"):
                # Update serial number with barcode info using direct SQL to avoid validation issues
                frappe.db.sql("""
                    UPDATE `tabSerial No` 
                    SET custom_barcode_string = %s, custom_barcode_generated = 1
                    WHERE name = %s
                """, (result.get("barcode_string"), doc.name))
                
                frappe.db.commit()
                
                frappe.logger().info(f"Barcode generated for serial number {doc.name}: {result.get('barcode_string')}")
                
            else:
                frappe.logger().error(f"Failed to generate barcode for serial number {doc.name}: {result.get('error')}")
                
    except Exception as e:
        frappe.logger().error(f"Error generating barcode for serial number {doc.name}: {str(e)}")
        import traceback
        traceback.print_exc()


def after_update(doc, method):
    """Update barcode when serial number is updated"""
    try:
        if doc.item_code and doc.name and doc.has_value_changed("name"):
            # Regenerate barcode if serial number changed
            generate_barcode_for_serial(doc)
            
    except Exception as e:
        frappe.logger().error(f"Error updating barcode for serial number {doc.name}: {str(e)}")


def on_update(doc, method):
    """Generate barcode when serial number is updated (alternative to after_insert)"""
    try:
        if doc.item_code and doc.name:
            # Check if barcode already exists
            existing_barcode = frappe.db.get_value("Serial No", doc.name, "custom_barcode_generated")
            if not existing_barcode:
                generate_barcode_for_serial(doc)
                
    except Exception as e:
        frappe.logger().error(f"Error in on_update for serial number {doc.name}: {str(e)}")


def generate_barcode_for_serial(doc):
    """Generate barcode for a serial number document"""
    try:
        if doc.item_code and doc.name:
            # Get item details
            item_doc = frappe.get_doc("Item", doc.item_code)
            model_number = item_doc.get("default_manufacturer_part_no") or ""
            
            # Generate barcode for this serial number
            result = BarcodeUtils.generate_item_barcode(
                item_code=doc.item_code,
                model_number=model_number,
                serial_number=doc.name,
                barcode_type="CODE128"
            )
            
            if result.get("success"):
                # Update serial number with barcode info using direct SQL to avoid validation issues
                frappe.db.sql("""
                    UPDATE `tabSerial No` 
                    SET custom_barcode_string = %s, custom_barcode_generated = 1
                    WHERE name = %s
                """, (result.get("barcode_string"), doc.name))
                
                frappe.db.commit()
                
                frappe.logger().info(f"Barcode generated for serial number {doc.name}: {result.get('barcode_string')}")
                return True
                
            else:
                frappe.logger().error(f"Failed to generate barcode for serial number {doc.name}: {result.get('error')}")
                return False
                
    except Exception as e:
        frappe.logger().error(f"Error generating barcode for serial number {doc.name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def before_save(doc, method):
    """Validate serial number before saving"""
    try:
        # Check if this is a new serial number
        if doc.is_new():
            # Check if serial number already has a barcode
            existing_barcode = frappe.db.exists("Item Barcode Generator", {
                "serial_number": doc.name,
                "item_code": doc.item_code
            })
            
            if existing_barcode:
                frappe.msgprint(_("Barcode already exists for this serial number"))
                
    except Exception as e:
        frappe.logger().error(f"Error validating serial number {doc.name}: {str(e)}")


@frappe.whitelist()
def regenerate_serial_barcode(serial_number):
    """Regenerate barcode for a specific serial number"""
    try:
        serial_doc = frappe.get_doc("Serial No", serial_number)
        
        # Delete existing barcode generator record
        existing_barcode = frappe.db.exists("Item Barcode Generator", {
            "serial_number": serial_number,
            "item_code": serial_doc.item_code
        })
        
        if existing_barcode:
            frappe.delete_doc("Item Barcode Generator", existing_barcode)
        
        # Generate new barcode
        after_insert(serial_doc, None)
        
        return {"success": True, "message": f"Barcode regenerated for serial number {serial_number}"}
        
    except Exception as e:
        frappe.logger().error(f"Error regenerating barcode for serial number {serial_number}: {str(e)}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def bulk_generate_serial_barcodes(item_code=None):
    """Generate barcodes for all serial numbers of an item or all items"""
    try:
        filters = {}
        if item_code:
            filters["item_code"] = item_code
            
        # Get all serial numbers
        serial_numbers = frappe.get_all("Serial No", 
            filters=filters,
            fields=["name", "item_code"],
            limit=1000  # Limit to prevent timeout
        )
        
        generated_count = 0
        error_count = 0
        
        for serial in serial_numbers:
            try:
                serial_doc = frappe.get_doc("Serial No", serial.name)
                after_insert(serial_doc, None)
                generated_count += 1
            except Exception as e:
                error_count += 1
                frappe.logger().error(f"Error generating barcode for serial {serial.name}: {str(e)}")
        
        return {
            "success": True, 
            "message": f"Generated {generated_count} barcodes, {error_count} errors"
        }
        
    except Exception as e:
        frappe.logger().error(f"Error in bulk barcode generation: {str(e)}")
        return {"success": False, "error": str(e)}
