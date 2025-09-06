# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
import json
import base64
from frappe import _
from frappe.utils import cint, flt
import barcode
from barcode.writer import ImageWriter
from io import BytesIO


class BarcodeUtils:
    """Utility class for barcode generation and scanning"""
    
    @staticmethod
    def generate_item_barcode(item_code, model_number=None, serial_number=None, barcode_type="CODE128"):
        """
        Generate barcode for item with item code, model number, and serial number
        
        Args:
            item_code (str): Item code
            model_number (str): Model number (manufacturer part number)
            serial_number (str): Serial number of the item
            barcode_type (str): Type of barcode to generate (default: CODE128)
        
        Returns:
            dict: Contains barcode data, image, and metadata
        """
        try:
            # Get item details
            item_doc = frappe.get_doc("Item", item_code)
            model_number = model_number or item_doc.get("default_manufacturer_part_no") or ""
            
            # Create structured barcode data
            barcode_data = {
                "item_code": item_code,
                "model_number": model_number,
                "serial_number": serial_number,
                "item_name": item_doc.item_name,
                "barcode_type": barcode_type
            }
            
            # Create barcode string (item_code|model_number|serial_number)
            if serial_number:
                barcode_string = f"{item_code}|{model_number}|{serial_number}" if model_number else f"{item_code}||{serial_number}"
            else:
                barcode_string = f"{item_code}|{model_number}" if model_number else item_code
            
            # Generate barcode image
            barcode_image = BarcodeUtils._generate_barcode_image(barcode_string, barcode_type)
            
            return {
                "success": True,
                "barcode_data": barcode_data,
                "barcode_string": barcode_string,
                "barcode_image": barcode_image,
                "item_code": item_code,
                "model_number": model_number,
                "serial_number": serial_number
            }
            
        except Exception as e:
            frappe.log_error(f"Error generating barcode for item {item_code}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def _generate_barcode_image(barcode_string, barcode_type="CODE128"):
        """Generate barcode image as base64 string"""
        try:
            # Create barcode
            barcode_class = barcode.get_barcode_class(barcode_type)
            barcode_instance = barcode_class(barcode_string, writer=ImageWriter())
            
            # Generate image
            buffer = BytesIO()
            barcode_instance.write(buffer, options={
                'module_width': 0.2,
                'module_height': 15.0,
                'quiet_zone': 6.5,
                'font_size': 10,
                'text_distance': 5.0,
                'background': 'white',
                'foreground': 'black',
            })
            
            # Convert to base64
            buffer.seek(0)
            image_data = buffer.getvalue()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            return f"data:image/png;base64,{base64_image}"
            
        except Exception as e:
            frappe.log_error(f"Error generating barcode image: {str(e)}")
            return None
    
    @staticmethod
    def scan_barcode(barcode_string):
        """
        Scan barcode and extract item information
        
        Args:
            barcode_string (str): Scanned barcode string
        
        Returns:
            dict: Item information extracted from barcode
        """
        try:
            # Parse barcode string (format: item_code|model_number|serial_number)
            if "|" in barcode_string:
                parts = barcode_string.split("|")
                item_code = parts[0]
                model_number = parts[1] if len(parts) > 1 and parts[1] else ""
                serial_number = parts[2] if len(parts) > 2 and parts[2] else ""
            else:
                item_code = barcode_string
                model_number = ""
                serial_number = ""
            
            # Validate item exists
            if not frappe.db.exists("Item", item_code):
                return {
                    "success": False,
                    "error": f"Item {item_code} not found"
                }
            
            # Get item details
            item_doc = frappe.get_doc("Item", item_code)
            
            # Verify model number if provided
            if model_number and item_doc.get("default_manufacturer_part_no") != model_number:
                frappe.logger().warning(f"Model number mismatch for item {item_code}: barcode={model_number}, item={item_doc.get('default_manufacturer_part_no')}")
            
            return {
                "success": True,
                "item_code": item_code,
                "model_number": model_number,
                "serial_number": serial_number,
                "item_name": item_doc.item_name,
                "item_group": item_doc.item_group,
                "stock_uom": item_doc.stock_uom,
                "description": item_doc.description,
                "brand": item_doc.brand,
                "standard_rate": item_doc.standard_rate,
                "is_stock_item": item_doc.is_stock_item,
                "has_serial_no": item_doc.has_serial_no,
                "has_batch_no": item_doc.has_batch_no
            }
            
        except Exception as e:
            frappe.log_error(f"Error scanning barcode {barcode_string}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_item_by_barcode(barcode_string):
        """
        Get item details by scanning barcode - compatible with existing ERPNext barcode system
        
        Args:
            barcode_string (str): Scanned barcode string
        
        Returns:
            dict: Item details in ERPNext format
        """
        try:
            # First try our custom barcode format
            result = BarcodeUtils.scan_barcode(barcode_string)
            if result.get("success"):
                return {
                    "item_code": result["item_code"],
                    "item_name": result["item_name"],
                    "barcode": barcode_string,
                    "uom": result["stock_uom"],
                    "serial_number": result.get("serial_number", ""),
                    "model_number": result.get("model_number", "")
                }
            
            # Fallback to existing ERPNext barcode system
            from erpnext.stock.utils import scan_barcode
            return scan_barcode(barcode_string)
            
        except Exception as e:
            frappe.log_error(f"Error getting item by barcode {barcode_string}: {str(e)}")
            return {}
    
    @staticmethod
    def generate_bulk_barcodes(item_codes, barcode_type="CODE128"):
        """
        Generate barcodes for multiple items
        
        Args:
            item_codes (list): List of item codes
            barcode_type (str): Type of barcode to generate
        
        Returns:
            dict: Results for each item
        """
        results = {}
        
        for item_code in item_codes:
            results[item_code] = BarcodeUtils.generate_item_barcode(item_code, barcode_type=barcode_type)
        
        return results
    
    @staticmethod
    def validate_barcode_format(barcode_string):
        """
        Validate barcode string format
        
        Args:
            barcode_string (str): Barcode string to validate
        
        Returns:
            bool: True if valid format
        """
        try:
            if not barcode_string or not isinstance(barcode_string, str):
                return False
            
            # Check if it's our custom format (item_code|model_number)
            if "|" in barcode_string:
                parts = barcode_string.split("|")
                if len(parts) == 2 and parts[0] and parts[1]:
                    return True
            
            # Check if it's a simple item code
            if frappe.db.exists("Item", barcode_string):
                return True
            
            return False
            
        except Exception:
            return False


@frappe.whitelist()
def generate_item_barcode(item_code, model_number=None, serial_number=None, barcode_type="CODE128"):
    """API endpoint for generating item barcode"""
    return BarcodeUtils.generate_item_barcode(item_code, model_number, serial_number, barcode_type)


@frappe.whitelist()
def scan_item_barcode(barcode_string):
    """API endpoint for scanning item barcode"""
    try:
        result = BarcodeUtils.scan_barcode(barcode_string)
        return result
    except Exception as e:
        frappe.log_error(f"Error in scan_item_barcode API: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def get_item_by_barcode(barcode_string):
    """API endpoint for getting item by barcode (ERPNext compatible)"""
    return BarcodeUtils.get_item_by_barcode(barcode_string)


@frappe.whitelist()
def generate_bulk_barcodes(item_codes, barcode_type="CODE128"):
    """API endpoint for generating multiple barcodes"""
    if isinstance(item_codes, str):
        item_codes = json.loads(item_codes)
    return BarcodeUtils.generate_bulk_barcodes(item_codes, barcode_type)
