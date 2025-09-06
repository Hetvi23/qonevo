# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def get_context(context):
    context.title = _("Barcode Manager")
    context.no_cache = 1
    
    # Get recent barcode generators
    context.recent_barcodes = frappe.get_all(
        "Item Barcode Generator",
        fields=["name", "item_code", "item_name", "model_number", "barcode_type", "creation"],
        order_by="creation desc",
        limit=10
    )
    
    # Get items without barcodes
    context.items_without_barcodes = frappe.db.sql("""
        SELECT i.name, i.item_name, i.default_manufacturer_part_no
        FROM `tabItem` i
        LEFT JOIN `tabItem Barcode Generator` ibg ON i.name = ibg.item_code
        WHERE i.is_stock_item = 1 AND ibg.name IS NULL
        LIMIT 10
    """, as_dict=True)
    
    # Get barcode statistics
    context.stats = {
        "total_items": frappe.db.count("Item", {"is_stock_item": 1}),
        "items_with_barcodes": frappe.db.count("Item Barcode Generator"),
        "barcode_types": frappe.db.sql("""
            SELECT barcode_type, COUNT(*) as count
            FROM `tabItem Barcode Generator`
            GROUP BY barcode_type
        """, as_dict=True)
    }
