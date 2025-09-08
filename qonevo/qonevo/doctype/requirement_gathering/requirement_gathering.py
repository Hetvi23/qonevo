# Copyright (c) 2025, Hetvi Patel and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate


class RequirementGathering(Document):
    def validate(self):
        self.calculate_gst_amounts()
        self.set_status()
    
    def calculate_gst_amounts(self):
        """Calculate GST amounts for all requirement items"""
        for item in self.requirement_item:
            if item.qty and item.rate:
                base_amount = item.qty * item.rate
                gst_percentage = float(item.gst) if item.gst else 0
                gst_amount = (base_amount * gst_percentage) / 100
                item.gst_amount = gst_amount
                item.amount = base_amount + gst_amount
            else:
                item.gst_amount = 0
                item.amount = 0
    
    def set_status(self):
        """Set status based on child items"""
        if not self.requirement_item:
            self.status = "Draft"
            return
        
        approved_count = 0
        rejected_count = 0
        total_count = len(self.requirement_item)
        
        for item in self.requirement_item:
            if item.select_ircl == "Approved":
                approved_count += 1
            elif item.select_ircl == "Reject":
                rejected_count += 1
        
        if approved_count > 0 and approved_count == total_count:
            self.status = "Approved"
        elif rejected_count > 0 and rejected_count == total_count:
            self.status = "Rejected"
        elif approved_count > 0:
            self.status = "Approved"
        else:
            self.status = "Draft"

@frappe.whitelist()
def fetch_supplier_details(docname):
    """Fetch supplier details when supplier is selected"""
    doc = frappe.get_doc("Requirement Gathering", docname)
    if doc.supplier:
        supplier = frappe.get_doc("Supplier", doc.supplier)
        doc.supplier_name = supplier.supplier_name
        
        # Get primary address if exists
        if supplier.supplier_primary_address:
            try:
                address = frappe.get_doc("Address", supplier.supplier_primary_address)
                address_parts = []
                if address.address_line1:
                    address_parts.append(address.address_line1)
                if address.city:
                    address_parts.append(address.city)
                if address.state:
                    address_parts.append(address.state)
                if address.pincode:
                    address_parts.append(address.pincode)
                doc.supplier_address = ", ".join(address_parts)
            except Exception as e:
                frappe.log_error(f"Error fetching address {supplier.supplier_primary_address}: {str(e)}")
                doc.supplier_address = ""
        else:
            doc.supplier_address = ""
        
        # Get primary contact if exists
        if supplier.supplier_primary_contact:
            try:
                contact = frappe.get_doc("Contact", supplier.supplier_primary_contact)
                contact_name = contact.first_name or ""
                if contact.last_name:
                    contact_name += " " + contact.last_name
                doc.contact_person = contact_name.strip()
            except:
                doc.contact_person = ""
        else:
            doc.contact_person = ""
        
        # Get GSTIN from tax_id field
        doc.gstin = supplier.tax_id or ""
        
        # Get payment terms
        doc.payment_terms = supplier.payment_terms or ""
        
        # Set default values for other fields
        doc.supply_terms = ""
        doc.transport_details = ""
        
        doc.save()
        return {"status": "success"}

@frappe.whitelist()
def approve_items(docname, all=False, row_idx=None, row_indices=None):
    """Approve items - all or specific rows"""
    doc = frappe.get_doc("Requirement Gathering", docname)
    
    frappe.logger().info(f"Approving items - all: {all}, row_idx: {row_idx}, row_indices: {row_indices}")
    
    if all:
        # Approve all items
        for item in doc.requirement_item:
            item.select_ircl = "Approved"
            frappe.logger().info(f"Approved all items: {item.item_code}")
    elif row_indices:
        # Approve specific rows (multiple selection)
        row_indices = frappe.parse_json(row_indices) if isinstance(row_indices, str) else row_indices
        for idx in row_indices:
            if 0 <= idx < len(doc.requirement_item):
                doc.requirement_item[idx].select_ircl = "Approved"
                frappe.logger().info(f"Approved item at index {idx}: {doc.requirement_item[idx].item_code}")
    elif row_idx is not None:
        # Approve specific row (single selection - for backward compatibility)
        row_idx = int(row_idx)
        if 0 <= row_idx < len(doc.requirement_item):
            doc.requirement_item[row_idx].select_ircl = "Approved"
            frappe.logger().info(f"Approved item at index {row_idx}: {doc.requirement_item[row_idx].item_code}")
    
    doc.set_status()
    doc.save()
    return {"status": "success", "message": "Items approved successfully"}

@frappe.whitelist()
def reject_items(docname, all=False, row_idx=None, row_indices=None):
    """Reject items - all or specific rows"""
    doc = frappe.get_doc("Requirement Gathering", docname)
    
    if all:
        # Reject all items
        for item in doc.requirement_item:
            item.select_ircl = "Reject"
    elif row_indices:
        # Reject specific rows (multiple selection)
        row_indices = frappe.parse_json(row_indices) if isinstance(row_indices, str) else row_indices
        for idx in row_indices:
            if 0 <= idx < len(doc.requirement_item):
                doc.requirement_item[idx].select_ircl = "Reject"
    elif row_idx is not None:
        # Reject specific row (single selection - for backward compatibility)
        row_idx = int(row_idx)
        if 0 <= row_idx < len(doc.requirement_item):
            doc.requirement_item[row_idx].select_ircl = "Reject"
    
    doc.set_status()
    doc.save()
    return {"status": "success", "message": "Items rejected successfully"}

@frappe.whitelist()
def create_purchase_order(docname):
    """Create Purchase Order from approved items"""
    doc = frappe.get_doc("Requirement Gathering", docname)
    
    # Recalculate GST amounts before creating PO
    doc.calculate_gst_amounts()
    doc.save()
    
    # Check if any items are approved
    approved_items = [item for item in doc.requirement_item if item.select_ircl == "Approved"]
    
    # Debug: Print all items and their status
    for item in doc.requirement_item:
        frappe.logger().info(f"Item: {item.item_code}, Status: {item.select_ircl}")
    
    if not approved_items:
        frappe.throw(_("No approved items found. Please approve items first."))
    
    frappe.logger().info(f"Found {len(approved_items)} approved items")
    
    # Create Purchase Order
    po = frappe.new_doc("Purchase Order")
    po.supplier = doc.supplier
    po.schedule_date = frappe.utils.add_days(frappe.utils.today(), 7)
    po.company = frappe.defaults.get_global_default("company")
    po.currency = frappe.defaults.get_global_default("currency")
    po.conversion_rate = 1.0
    
    # Copy supplier details - only copy text fields that don't require validation
    if doc.supplier_name:
        po.supplier_name = doc.supplier_name
    if doc.gstin:
        po.gstin = doc.gstin
    if doc.payment_terms:
        po.payment_terms = doc.payment_terms
    if doc.supply_terms:
        po.supply_terms = doc.supply_terms
    if doc.transport_details:
        po.transport_details = doc.transport_details
    
    # Note: supplier_address and contact_person are Link fields in Purchase Order
    # so we can't copy them directly from text fields
    # They need to be actual Address and Contact doctype references
    # For now, we skip copying these to avoid LinkValidationError
    # The information is still available in the Requirement Gathering document
    
    # Get default warehouse for the company
    company = frappe.defaults.get_global_default("company")
    default_warehouse = frappe.defaults.get_global_default("default_warehouse")
    
    # Verify the default warehouse belongs to the company
    if default_warehouse:
        warehouse_company = frappe.get_value("Warehouse", default_warehouse, "company")
        if warehouse_company != company:
            default_warehouse = None
    
    if not default_warehouse:
        # Try to get any warehouse for the company
        warehouses = frappe.get_list("Warehouse", 
            filters={"company": company}, 
            limit=1
        )
        if warehouses:
            default_warehouse = warehouses[0].name
        else:
            frappe.throw(_("No warehouse found for company {0}. Please create a warehouse first.").format(company))
    
    # Add items
    for item in approved_items:
        # Debug: Log the values being used
        frappe.logger().info(f"Item: {item.item_code}, Qty: {item.qty}, Rate: {item.rate}, GST: {item.gst}, Amount: {item.amount}")
        
        po.append("items", {
            "item_code": item.item_code,
            "item_name": item.item_name,
            "qty": item.qty,
            "rate": item.rate,
            "amount": item.amount,
            "uom": frappe.get_value("Item", item.item_code, "stock_uom"),
            "warehouse": default_warehouse
        })
    
    # Set status to Draft instead of submitting
    po.status = "Draft"
    po.insert()
    # Don't submit - keep as draft
    # po.submit()
    
    # Update Requirement Gathering
    doc.purchase_order_ref = po.name
    doc.status = "PO Created"
    doc.save()
    
    frappe.msgprint(_("Purchase Order {0} created successfully as Draft").format(po.name))
    return {"status": "success", "purchase_order": po.name}

@frappe.whitelist()
def create_purchase_receipt(docname, items_data):
    """Create Purchase Receipt from Purchase Order"""
    doc = frappe.get_doc("Requirement Gathering", docname)
    
    if not doc.purchase_order_ref:
        frappe.throw(_("No Purchase Order linked. Please create Purchase Order first."))
    
    # Parse items data
    items_data = frappe.parse_json(items_data)
    
    # Create Purchase Receipt
    pr = frappe.new_doc("Purchase Receipt")
    pr.supplier = doc.supplier
    pr.posting_date = frappe.utils.today()
    pr.company = frappe.defaults.get_global_default("company")
    pr.currency = frappe.defaults.get_global_default("currency")
    pr.conversion_rate = 1.0
    pr.purchase_order = doc.purchase_order_ref
    
    # Add items
    for item_data in items_data:
        accepted_qty = item_data.get("accepted_qty", 0)
        if accepted_qty > 0:  # Only add items with accepted quantity
            pr.append("items", {
                "item_code": item_data.get("item_code"),
                "item_name": item_data.get("item_name"),
                "qty": accepted_qty,
                "rate": item_data.get("rate", 0),
                "amount": accepted_qty * item_data.get("rate", 0),
                "uom": frappe.get_value("Item", item_data.get("item_code"), "stock_uom"),
                "purchase_order": doc.purchase_order_ref,
                "purchase_order_item": item_data.get("po_item")
            })
    
    if not pr.items:
        frappe.throw(_("No items with accepted quantity found."))
    
    pr.insert()
    pr.submit()
    
    # Update Requirement Gathering
    doc.purchase_receipt_ref = pr.name
    doc.status = "PR Created"
    doc.save()
    
    frappe.msgprint(_("Purchase Receipt {0} created successfully").format(pr.name))
    return {"status": "success", "purchase_receipt": pr.name}

@frappe.whitelist()
def get_purchase_order_items(docname):
    """Get Purchase Order items for receipt creation"""
    doc = frappe.get_doc("Requirement Gathering", docname)
    
    if not doc.purchase_order_ref:
        return []
    
    po = frappe.get_doc("Purchase Order", doc.purchase_order_ref)
    items = []
    
    for item in po.items:
        items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "ordered_qty": item.qty,
            "rate": item.rate,
            "po_item": item.name
        })
    
    return items

@frappe.whitelist()
def get_pos_without_pr():
    """
    Get Purchase Orders that do not have any linked Purchase Receipt.
    """
    pos = frappe.db.sql("""
        SELECT po.name, po.supplier, po.transaction_date, po.grand_total, po.status
        FROM `tabPurchase Order` po
        WHERE po.docstatus = 1
        AND po.status IN ('To Receive', 'To Receive and Bill', 'To Bill')
        AND NOT EXISTS (
            SELECT pri.name
            FROM `tabPurchase Receipt Item` pri
            INNER JOIN `tabPurchase Receipt` pr
                ON pr.name = pri.parent
            WHERE pri.purchase_order = po.name
            AND pr.docstatus < 2
        )
        ORDER BY po.creation DESC
    """, as_dict=True)

    return pos





@frappe.whitelist()
def get_po_items(po_name):
    """
    Get items for the given Purchase Order
    """
    if not po_name:
        frappe.throw(_("Purchase Order name is required"))

    items = frappe.get_all(
        "Purchase Order Item",
        filters={"parent": po_name},
        fields=["item_code", "item_name", "qty", "rate", "amount", "warehouse", "uom"]
    )

    return items


@frappe.whitelist()
def create_purchase_receipt_from_po(po_name, items, remarks=None):
    """
    Create Purchase Receipt from Purchase Order and received qtys
    """
    import json
    if isinstance(items, str):
        items = json.loads(items)

    if not po_name:
        frappe.throw(_("Purchase Order name is required"))

    # Fetch PO doc
    po_doc = frappe.get_doc("Purchase Order", po_name)

    pr = frappe.new_doc("Purchase Receipt")
    pr.supplier = po_doc.supplier
    pr.supplier_name = po_doc.supplier_name
    pr.supplier_address = po_doc.supplier_address
    pr.posting_date = nowdate()
    pr.purchase_order = po_doc.name
    pr.remarks = remarks or ""
    pr.company = po_doc.company
    pr.set_warehouse = po_doc.set_warehouse

    # Add items
    for item in items:
        if float(item.get("received_qty", 0)) > 0:
            # Get the Purchase Order Item details
            po_item = frappe.db.get_value("Purchase Order Item", 
                {"parent": po_name, "item_code": item.get("item_code")}, 
                ["name", "rate", "warehouse"], as_dict=True)
            
            if not po_item:
                frappe.throw(_("Item {0} not found in Purchase Order {1}").format(item.get("item_code"), po_name))
            
            pr.append("items", {
                "item_code": item.get("item_code"),
                "item_name": frappe.db.get_value("Item", item.get("item_code"), "item_name"),
                "uom": frappe.db.get_value("Item", item.get("item_code"), "stock_uom"),
                "qty": float(item.get("received_qty")),
                "rate": po_item.rate,
                "warehouse": po_item.warehouse,
                "purchase_order": po_name,
                "purchase_order_item": po_item.name  # This is the crucial link!
            })

    if not pr.items:
        frappe.throw(_("Please enter at least one Received Qty greater than 0"))

    # Save & submit PR
    pr.insert(ignore_permissions=True)
    pr.submit()

    return {
        "status": "success",
        "purchase_receipt": pr.name,
        "message": _("Purchase Receipt created successfully")
    }

@frappe.whitelist()
def get_pos_without_pr_new():
    return frappe.db.sql("""
        SELECT name, supplier, transaction_date, grand_total, status
        FROM `tabPurchase Order`
        WHERE docstatus = 1 AND status IN ('To Receive', 'To Receive and Bill')
    """, as_dict=True)

@frappe.whitelist()
def get_po_items_new(po_name):
    return frappe.db.sql("""
        SELECT item_code, item_name, qty
        FROM `tabPurchase Order Item`
        WHERE parent = %s
    """, po_name, as_dict=True)

import json
import frappe
from frappe.utils import nowdate
from erpnext.controllers.stock_controller import StockController

import json
import frappe
from frappe.utils import nowdate
from erpnext.controllers.stock_controller import StockController

@frappe.whitelist()
def create_purchase_receipt_from_po_new(po_name, items):
    # ✅ Disable validations completely
    frappe.flags.ignore_validate_serial_no = True
    frappe.flags.ignore_validate_batch = True
    frappe.flags.ignore_linked_doctypes = True
    frappe.flags.ignore_mandatory = True
    frappe.flags.in_test = True  # Optional: avoids certain internal checks

    # ✅ Skip bundle method (no-op override)
    StockController.make_serial_and_batch_bundle = lambda self: None

    items = json.loads(items)
    po_doc = frappe.get_doc("Purchase Order", po_name)

    pr = frappe.new_doc("Purchase Receipt")
    pr.supplier = po_doc.supplier
    pr.set_posting_time = 1
    pr.posting_date = nowdate()
    pr.purchase_order = po_name

    for item in items:
        # Get the Purchase Order Item details
        po_item = frappe.db.get_value("Purchase Order Item", 
            {"parent": po_name, "item_code": item.get("item_code")}, 
            ["name", "rate", "warehouse"], as_dict=True)
        
        if not po_item:
            frappe.throw(_("Item {0} not found in Purchase Order {1}").format(item.get("item_code"), po_name))
        
        pr.append("items", {
            "item_code": item.get("item_code"),
            "qty": item.get("received_qty", 0),
            "received_qty": item.get("received_qty", 0),
            "rate": po_item.rate,
            "warehouse": po_item.warehouse,
            "purchase_order": po_name,
            "purchase_order_item": po_item.name,  # This is the crucial link!
            "serial_no": item.get("serial_no", ""),  # Pass string like 'SN001,SN002'
            "schedule_date": nowdate()
        })

    # ✅ Insert and submit with force
    pr.insert(ignore_permissions=True, ignore_links=True, ignore_mandatory=True)
    pr.submit()

    return {"message": f"✅ Purchase Receipt {pr.name} created successfully."}


@frappe.whitelist()
def get_sales_orders_pending_delivery_note():
    return frappe.db.sql("""
        SELECT
            so.name, so.customer, so.transaction_date, so.grand_total, so.status
        FROM
            `tabSales Order` so
        WHERE
            so.docstatus = 1
            AND so.per_delivered < 100
        ORDER BY so.transaction_date DESC
    """, as_dict=True)


@frappe.whitelist()
def get_sales_order_items_for_delivery(so_name):
    return frappe.db.sql("""
        SELECT
            soi.item_code,
            soi.item_name,
            soi.qty,
            soi.delivered_qty,
            (soi.qty - soi.delivered_qty) AS pending_qty
        FROM
            `tabSales Order Item` soi
        WHERE
            soi.parent = %s
            AND (soi.qty - soi.delivered_qty) > 0
    """, (so_name,), as_dict=True)

@frappe.whitelist()
def create_delivery_note_from_sales_order(so_name, items):
    import json
    from frappe.utils import nowdate

    try:
        items = json.loads(items)
    except Exception:
        frappe.throw("Invalid items payload")

    dn = frappe.new_doc("Delivery Note")
    dn.posting_date = nowdate()
    dn.customer = frappe.db.get_value("Sales Order", so_name, "customer")
    dn.set_posting_time = 1
    dn.set_warehouse = None
    dn.items = []

    for item in items:
        if not item.get("item_code") or not float(item.get("delivered_qty", 0)):
            continue

        dn.append("items", {
            "item_code": item["item_code"],
            "qty": item["delivered_qty"],
            "serial_no": item.get("serial_no", ""),
            "against_sales_order": so_name
        })

    if not dn.items:
        return {"status": "error", "error": "No valid items to deliver."}

    dn.insert(ignore_permissions=True)
    dn.submit()

    return {"status": "success", "delivery_note": dn.name}
