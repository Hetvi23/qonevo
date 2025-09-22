# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def delivery_note_on_load(doc, method):
    """
    Hook to populate serial numbers from Sales Order's custom_manufactured_serials
    when creating a Delivery Note from Sales Order.
    """
    print(f"🔧 DELIVERY NOTE HOOK: delivery_note_on_load triggered for {doc.name}")
    
    # Check if any item has a sales order reference
    has_sales_order = False
    sales_orders_found = []
    
    for item in doc.items:
        if item.against_sales_order:
            has_sales_order = True
            sales_orders_found.append(item.against_sales_order)
            print(f"📦 DELIVERY NOTE HOOK: Item {item.item_code} linked to Sales Order {item.against_sales_order}")
    
    if not has_sales_order:
        print(f"⚠️ DELIVERY NOTE HOOK: No items with sales order references found in {doc.name}")
        return
    
    print(f"📋 DELIVERY NOTE HOOK: Found {len(sales_orders_found)} items with sales order references: {sales_orders_found}")
    
    try:
        print(f"🔍 DELIVERY NOTE HOOK: Processing {len(doc.items)} items in Delivery Note {doc.name}")
        
        # Process each item in the Delivery Note
        for i, item in enumerate(doc.items):
            print(f"📦 DELIVERY NOTE HOOK: Processing item {i+1}: {item.item_code}")
            
            if not item.against_sales_order:
                print(f"⏭️ DELIVERY NOTE HOOK: Item {item.item_code} has no sales order reference, skipping")
                continue
                
            print(f"📋 DELIVERY NOTE HOOK: Getting Sales Order {item.against_sales_order}")
            # Get the Sales Order for this item
            sales_order = frappe.get_doc("Sales Order", item.against_sales_order)
            print(f"📋 DELIVERY NOTE HOOK: Sales Order {sales_order.name} found, Customer: {sales_order.customer}")
            
            # Check if Sales Order has manufacturing serials
            if not hasattr(sales_order, 'custom_manufactured_serials') or not sales_order.custom_manufactured_serials:
                print(f"⚠️ DELIVERY NOTE HOOK: Sales Order {sales_order.name} has no manufacturing serials, skipping")
                continue
            
            print(f"✅ DELIVERY NOTE HOOK: Sales Order {sales_order.name} has {len(sales_order.custom_manufactured_serials)} manufacturing serials")
            
            # Create a mapping of item_code to serial numbers for this Sales Order
            print(f"🗺️ DELIVERY NOTE HOOK: Creating item-serial mapping for Sales Order {sales_order.name}")
            item_serials_map = {}
            for manufacturing_serial in sales_order.custom_manufactured_serials:
                item_code = manufacturing_serial.item_code
                serial_no = manufacturing_serial.serial_no
                
                print(f"🗺️ DELIVERY NOTE HOOK: Mapping serial {serial_no} to item {item_code}")
                
                if item_code not in item_serials_map:
                    item_serials_map[item_code] = []
                item_serials_map[item_code].append(serial_no)
            
            item_code = item.item_code
            print(f"🔍 DELIVERY NOTE HOOK: Looking for manufacturing serials for item {item_code}")
            
            # Check if this item has manufacturing serials
            if item_code in item_serials_map:
                available_serials = item_serials_map[item_code]
                required_qty = item.qty
                
                print(f"✅ DELIVERY NOTE HOOK: Found {len(available_serials)} manufacturing serials for item {item_code}: {available_serials}")
                print(f"📊 DELIVERY NOTE HOOK: Required quantity: {required_qty}, Available serials: {len(available_serials)}")
                
                # Handle multiple quantity
                if required_qty <= len(available_serials):
                    # Take the required number of serials
                    selected_serials = available_serials[:int(required_qty)]
                    print(f"✅ DELIVERY NOTE HOOK: Sufficient serials available, selecting {len(selected_serials)}: {selected_serials}")
                    
                    # Set the serial numbers for this item
                    if item.serial_and_batch_bundle:
                        # Update existing bundle
                        print(f"📦 DELIVERY NOTE HOOK: Updating serial bundle for item {item_code}")
                        update_serial_bundle(item, selected_serials)
                    else:
                        # Create new bundle or use serial_no field
                        print(f"📝 DELIVERY NOTE HOOK: Setting serial numbers for item {item_code}")
                        set_item_serials(item, selected_serials)
                    
                    frappe.logger().info(f"Set {len(selected_serials)} serials for item {item_code} in Delivery Note {doc.name}")
                    print(f"🎉 DELIVERY NOTE HOOK: Successfully set {len(selected_serials)} serials for item {item_code}")
                else:
                    # Not enough serials available
                    print(f"⚠️ DELIVERY NOTE HOOK: Insufficient serials - need {required_qty}, have {len(available_serials)}")
                    frappe.msgprint(
                        _("Warning: Only {0} serial numbers available for item {1}, but {2} required").format(
                            len(available_serials), item_code, required_qty
                        ),
                        title=_("Serial Number Warning"),
                        indicator="orange"
                    )
                    
                    # Use all available serials
                    if available_serials:
                        print(f"📝 DELIVERY NOTE HOOK: Using all available serials: {available_serials}")
                        if item.serial_and_batch_bundle:
                            update_serial_bundle(item, available_serials)
                        else:
                            set_item_serials(item, available_serials)
            else:
                print(f"⚠️ DELIVERY NOTE HOOK: No manufacturing serials found for item {item_code}")
        
    except Exception as e:
        print(f"❌ DELIVERY NOTE HOOK: Error in delivery_note_on_load: {str(e)}")
        frappe.logger().error(f"Error in delivery_note_on_load: {str(e)}")
        frappe.msgprint(
            _("Warning: Could not populate manufacturing serials: {0}").format(str(e)),
            title=_("Serial Number Warning"),
            indicator="orange"
        )


def update_serial_bundle(item, serial_numbers):
    """
    Update the Serial and Batch Bundle with the provided serial numbers.
    """
    try:
        if not item.serial_and_batch_bundle:
            return
        
        bundle_doc = frappe.get_doc("Serial and Batch Bundle", item.serial_and_batch_bundle)
        
        # Clear existing entries
        bundle_doc.entries = []
        
        # Add new entries for each serial number
        for serial_no in serial_numbers:
            bundle_doc.append("entries", {
                "serial_no": serial_no,
                "batch_no": "",
                "qty": 1,
                "incoming_rate": item.rate or 0
            })
        
        # Update total qty
        bundle_doc.total_qty = len(serial_numbers)
        
        bundle_doc.save()
        frappe.db.commit()
        
    except Exception as e:
        frappe.logger().error(f"Error updating serial bundle: {str(e)}")


def set_item_serials(item, serial_numbers):
    """
    Set serial numbers for an item using the serial_no field.
    """
    try:
        # Join serial numbers with newlines
        serial_no_string = '\n'.join(serial_numbers)
        item.serial_no = serial_no_string
        
    except Exception as e:
        frappe.logger().error(f"Error setting item serials: {str(e)}")


def delivery_note_validate(doc, method):
    """
    Validate that serial numbers are properly set for items with manufacturing serials.
    """
    # Check if any item has a sales order reference
    has_sales_order = False
    for item in doc.items:
        if item.against_sales_order:
            has_sales_order = True
            break
    
    if not has_sales_order:
        return
    
    try:
        # Validate each item
        for item in doc.items:
            if not item.against_sales_order:
                continue
                
            # Get the Sales Order for this item
            sales_order = frappe.get_doc("Sales Order", item.against_sales_order)
            
            # Check if Sales Order has manufacturing serials
            if not hasattr(sales_order, 'custom_manufactured_serials') or not sales_order.custom_manufactured_serials:
                continue
            
            # Create a mapping of item_code to available serial numbers
            item_serials_map = {}
            for manufacturing_serial in sales_order.custom_manufactured_serials:
                item_code = manufacturing_serial.item_code
                serial_no = manufacturing_serial.serial_no
                
                if item_code not in item_serials_map:
                    item_serials_map[item_code] = []
                item_serials_map[item_code].append(serial_no)
            
            item_code = item.item_code
            
            if item_code in item_serials_map:
                # This item should have manufacturing serials
                available_serials = item_serials_map[item_code]
                required_qty = item.qty
                
                # Get serial numbers from the item
                item_serials = get_item_serial_numbers(item)
                
                if not item_serials:
                    frappe.msgprint(
                        _("Item {0} has manufacturing serials available but none are set in the Delivery Note").format(item_code),
                        title=_("Serial Number Validation"),
                        indicator="orange"
                    )
                elif len(item_serials) < required_qty:
                    frappe.msgprint(
                        _("Item {0} requires {1} serial numbers but only {2} are set").format(
                            item_code, required_qty, len(item_serials)
                        ),
                        title=_("Serial Number Validation"),
                        indicator="orange"
                    )
        
    except Exception as e:
        frappe.logger().error(f"Error in delivery_note_validate: {str(e)}")


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


@frappe.whitelist()
def populate_manufacturing_serials(delivery_note, items):
    """
    Server method to populate manufacturing serials for Delivery Note items.
    Called from JavaScript.
    """
    print(f"🔧 DELIVERY NOTE SERVER: populate_manufacturing_serials called for {delivery_note}")
    print(f"📦 DELIVERY NOTE SERVER: Processing {len(items)} items")
    
    try:
        result_items = []
        
        for i, item_data in enumerate(items):
            print(f"📦 DELIVERY NOTE SERVER: Processing item {i+1}: {item_data.get('item_code', 'Unknown')}")
            
            if not item_data.get('against_sales_order'):
                print(f"⏭️ DELIVERY NOTE SERVER: Item {i+1} has no sales order reference, skipping")
                result_items.append({
                    'serial_no': item_data.get('serial_no', ''),
                    'serial_and_batch_bundle': item_data.get('serial_and_batch_bundle', '')
                })
                continue
            
            # Get the Sales Order
            sales_order_name = item_data['against_sales_order']
            print(f"📋 DELIVERY NOTE SERVER: Getting Sales Order {sales_order_name}")
            sales_order = frappe.get_doc("Sales Order", sales_order_name)
            print(f"📋 DELIVERY NOTE SERVER: Sales Order {sales_order.name} found, Customer: {sales_order.customer}")
            
            # Check if Sales Order has manufacturing serials
            if not hasattr(sales_order, 'custom_manufactured_serials') or not sales_order.custom_manufactured_serials:
                print(f"⚠️ DELIVERY NOTE SERVER: Sales Order {sales_order.name} has no manufacturing serials")
                result_items.append({
                    'serial_no': item_data.get('serial_no', ''),
                    'serial_and_batch_bundle': item_data.get('serial_and_batch_bundle', '')
                })
                continue
            
            print(f"✅ DELIVERY NOTE SERVER: Sales Order {sales_order.name} has {len(sales_order.custom_manufactured_serials)} manufacturing serials")
            
            # Create a mapping of item_code to serial numbers
            print(f"🗺️ DELIVERY NOTE SERVER: Creating item-serial mapping for Sales Order {sales_order.name}")
            item_serials_map = {}
            for manufacturing_serial in sales_order.custom_manufactured_serials:
                item_code = manufacturing_serial.item_code
                serial_no = manufacturing_serial.serial_no
                
                print(f"🗺️ DELIVERY NOTE SERVER: Mapping serial {serial_no} to item {item_code}")
                
                if item_code not in item_serials_map:
                    item_serials_map[item_code] = []
                item_serials_map[item_code].append(serial_no)
            
            item_code = item_data['item_code']
            print(f"🔍 DELIVERY NOTE SERVER: Looking for manufacturing serials for item {item_code}")
            
            # Check if this item has manufacturing serials
            if item_code in item_serials_map:
                available_serials = item_serials_map[item_code]
                required_qty = item_data.get('qty', 1)
                
                print(f"✅ DELIVERY NOTE SERVER: Found {len(available_serials)} manufacturing serials for item {item_code}: {available_serials}")
                print(f"📊 DELIVERY NOTE SERVER: Required quantity: {required_qty}, Available serials: {len(available_serials)}")
                
                # Handle multiple quantity
                if required_qty <= len(available_serials):
                    # Take the required number of serials
                    selected_serials = available_serials[:int(required_qty)]
                    print(f"✅ DELIVERY NOTE SERVER: Sufficient serials available, selecting {len(selected_serials)}: {selected_serials}")
                    
                    # Set the serial numbers for this item
                    serial_no_string = '\n'.join(selected_serials)
                    
                    result_items.append({
                        'serial_no': serial_no_string,
                        'serial_and_batch_bundle': item_data.get('serial_and_batch_bundle', '')
                    })
                else:
                    # Not enough serials available - use all available
                    print(f"⚠️ DELIVERY NOTE SERVER: Insufficient serials - need {required_qty}, have {len(available_serials)}")
                    if available_serials:
                        serial_no_string = '\n'.join(available_serials)
                        print(f"📝 DELIVERY NOTE SERVER: Using all available serials: {available_serials}")
                        result_items.append({
                            'serial_no': serial_no_string,
                            'serial_and_batch_bundle': item_data.get('serial_and_batch_bundle', '')
                        })
                    else:
                        print(f"⚠️ DELIVERY NOTE SERVER: No serials available for item {item_code}")
                        result_items.append({
                            'serial_no': item_data.get('serial_no', ''),
                            'serial_and_batch_bundle': item_data.get('serial_and_batch_bundle', '')
                        })
            else:
                print(f"⚠️ DELIVERY NOTE SERVER: No manufacturing serials found for item {item_code}")
                result_items.append({
                    'serial_no': item_data.get('serial_no', ''),
                    'serial_and_batch_bundle': item_data.get('serial_and_batch_bundle', '')
                })
        
        print(f"🎉 DELIVERY NOTE SERVER: Successfully processed {len(items)} items, returning {len(result_items)} results")
        return {
            'success': True,
            'items': result_items
        }
        
    except Exception as e:
        print(f"❌ DELIVERY NOTE SERVER: Error in populate_manufacturing_serials: {str(e)}")
        frappe.logger().error(f"Error in populate_manufacturing_serials: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
