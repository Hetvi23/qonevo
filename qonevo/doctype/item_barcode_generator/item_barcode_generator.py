# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from qonevo.barcode_utils import BarcodeUtils


class ItemBarcodeGenerator(Document):
    def validate(self):
        """Validate and generate barcode data"""
        if not self.item_code:
            frappe.throw("Item Code is required")
        
        # Get item details
        item_doc = frappe.get_doc("Item", self.item_code)
        
        # Set model number from item if not provided
        if not self.model_number:
            self.model_number = item_doc.get("default_manufacturer_part_no") or ""
        
        # Set title
        if not self.title:
            if self.serial_number:
                self.title = f"{self.item_code} - {self.serial_number}"
            else:
                self.title = f"{self.item_code} - {self.model_number}" if self.model_number else self.item_code
        
        # Generate barcode
        self._generate_barcode()
        
        # Populate item details
        self._populate_item_details(item_doc)
    
    def _generate_barcode(self):
        """Generate barcode string and image"""
        try:
            result = BarcodeUtils.generate_item_barcode(
                self.item_code, 
                self.model_number, 
                self.serial_number,
                self.barcode_type
            )
            
            if result.get("success"):
                self.barcode_string = result.get("barcode_string")
                self.barcode_image = f'<img src="{result.get("barcode_image")}" style="max-width: 300px; height: auto;" />'
            else:
                frappe.throw(f"Error generating barcode: {result.get('error')}")
                
        except Exception as e:
            frappe.throw(f"Error generating barcode: {str(e)}")
    
    def _populate_item_details(self, item_doc):
        """Populate item details from item document"""
        self.item_name = item_doc.item_name
        self.item_group = item_doc.item_group
        self.stock_uom = item_doc.stock_uom
        self.description = item_doc.description
        self.brand = item_doc.brand
        self.standard_rate = item_doc.standard_rate
    
    def on_update(self):
        """Called after document is updated"""
        # Update item's barcode if this is the primary barcode
        self._update_item_barcode()
    
    def _update_item_barcode(self):
        """Update item's barcode in Item Barcode child table"""
        try:
            item_doc = frappe.get_doc("Item", self.item_code)
            
            # Check if barcode already exists
            existing_barcode = None
            for barcode in item_doc.barcodes:
                if barcode.barcode == self.barcode_string:
                    existing_barcode = barcode
                    break
            
            # Add new barcode if it doesn't exist
            if not existing_barcode:
                item_doc.append("barcodes", {
                    "barcode": self.barcode_string,
                    "barcode_type": self.barcode_type,
                    "uom": self.stock_uom
                })
                item_doc.save()
                frappe.msgprint(f"Barcode added to item {self.item_code}")
            
        except Exception as e:
            frappe.log_error(f"Error updating item barcode: {str(e)}")
    
    @frappe.whitelist()
    def regenerate_barcode(self):
        """Regenerate barcode with current settings"""
        self._generate_barcode()
        self.save()
        frappe.msgprint("Barcode regenerated successfully")
    
    @frappe.whitelist()
    def print_barcode(self):
        """Print barcode"""
        return {
            "barcode_string": self.barcode_string,
            "barcode_image": self.barcode_image,
            "item_code": self.item_code,
            "item_name": self.item_name,
            "model_number": self.model_number
        }
