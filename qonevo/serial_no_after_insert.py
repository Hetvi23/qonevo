import frappe
from qonevo.barcode_utils import BarcodeUtils

def after_insert(doc, method):
    """Generate barcode when a new serial number is created"""
    try:
        # Get item details
        item = frappe.get_doc("Item", doc.item_code)
        model_number = item.get("default_manufacturer_part_no") or "NO-MODEL"
        
        # Generate barcode
        result = BarcodeUtils.generate_item_barcode(
            item_code=doc.item_code,
            model_number=model_number,
            serial_number=doc.name,
            barcode_type="CODE128"
        )
        
        if result.get("success"):
            # Update the serial number with barcode info
            frappe.db.sql("""
                UPDATE `tabSerial No` 
                SET custom_barcode_string = %s, custom_barcode_generated = 1
                WHERE name = %s
            """, (result.get("barcode_string"), doc.name))
            
            frappe.db.commit()
            frappe.msgprint(f"Barcode generated for serial number {doc.name}")
        else:
            frappe.log_error(f"Failed to generate barcode for serial {doc.name}: {result.get('error')}")
            
    except Exception as e:
        frappe.log_error(f"Error in serial_no_after_insert: {str(e)}")
