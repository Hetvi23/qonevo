# Copyright (c) 2025, Qonevo and contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.utils import getdate, add_days, get_week_start, get_week_end

def get_context(context):
    """Get context for the delivery dashboard page"""
    
    context.update({
        "delivery_data": get_delivery_data(),
        "priority_data": get_priority_data(),
        "total_orders": get_total_orders(),
        "total_qty": get_total_qty(),
        "total_amount": get_total_amount(),
        "priority_levels": 4,  # Low, Medium, High, Urgent
        "this_week_count": get_this_week_count(),
        "next_week_count": get_next_week_count()
    })

def get_delivery_data():
    """Get sales orders with priority for delivery tracking"""
    
    try:
        # Get current week start and end
        today = getdate()
        week_start = get_week_start(today)
        week_end = get_week_end(today)
        next_week_start = add_days(week_end, 1)
        next_week_end = add_days(next_week_start, 6)
        
        # Fetch sales orders with priority
        orders = frappe.get_all(
            "Sales Order",
            filters={
                "docstatus": 1,  # Submitted orders
                "delivery_date": ["between", [week_start, next_week_end]]
            },
            fields=["name", "customer", "priority", "priority_status", "delivery_date", "grand_total"],
            order_by="delivery_date"
        )
        
        # Process orders to add colors and formatting
        for order in orders:
            # Priority colors
            priority_colors = {
                "Urgent": "danger",
                "High": "warning", 
                "Medium": "info",
                "Low": "secondary"
            }
            order.priority_color = priority_colors.get(order.priority, "secondary")
            
            # Status colors
            status_colors = {
                "Pending": "warning",
                "In Progress": "info",
                "Completed": "success",
                "On Hold": "danger"
            }
            order.status_color = status_colors.get(order.priority_status, "secondary")
            
            # Format delivery date
            if order.delivery_date:
                order.delivery_date = order.delivery_date.strftime("%Y-%m-%d")
        
        return orders
        
    except Exception as e:
        frappe.log_error(f"Error getting delivery data: {str(e)}")
        return []

def get_priority_data():
    """Get priority distribution data"""
    
    try:
        # Get counts by priority
        priority_counts = frappe.get_all(
            "Sales Order",
            filters={"docstatus": 1},
            fields=["priority", "count(name) as count"],
            group_by="priority"
        )
        
        # Define priority colors and order
        priority_config = [
            {"name": "Urgent", "color": "danger"},
            {"name": "High", "color": "warning"},
            {"name": "Medium", "color": "info"},
            {"name": "Low", "color": "secondary"}
        ]
        
        # Create priority data with counts
        priority_data = []
        for config in priority_config:
            count = 0
            for item in priority_counts:
                if item.priority == config["name"]:
                    count = item.count
                    break
            
            priority_data.append({
                "name": config["name"],
                "color": config["color"],
                "count": count
            })
        
        return priority_data
        
    except Exception as e:
        frappe.log_error(f"Error getting priority data: {str(e)}")
        return []

def get_total_orders():
    """Get total number of submitted sales orders"""
    
    try:
        return frappe.db.count("Sales Order", filters={"docstatus": 1})
    except:
        return 0

def get_total_qty():
    """Get total quantity from all submitted sales orders"""
    
    try:
        result = frappe.db.sql("""
            SELECT SUM(qty) 
            FROM `tabSales Order Item` soi
            JOIN `tabSales Order` so ON soi.parent = so.name
            WHERE so.docstatus = 1
        """, as_dict=True)
        
        return result[0].get('SUM(qty)', 0) if result else 0
    except:
        return 0

def get_total_amount():
    """Get total amount from all submitted sales orders"""
    
    try:
        result = frappe.db.sql("""
            SELECT SUM(grand_total) 
            FROM `tabSales Order` 
            WHERE docstatus = 1
        """, as_dict=True)
        
        return result[0].get('SUM(grand_total)', 0) if result else 0
    except:
        return 0

def get_this_week_count():
    """Get count of orders for current week"""
    
    try:
        today = getdate()
        week_start = get_week_start(today)
        week_end = get_week_end(today)
        
        return frappe.db.count(
            "Sales Order",
            filters={
                "docstatus": 1,
                "delivery_date": ["between", [week_start, week_end]]
            }
        )
    except:
        return 0

def get_next_week_count():
    """Get count of orders for next week"""
    
    try:
        today = getdate()
        week_end = get_week_end(today)
        next_week_start = add_days(week_end, 1)
        next_week_end = add_days(next_week_start, 6)
        
        return frappe.db.count(
            "Sales Order",
            filters={
                "docstatus": 1,
                "delivery_date": ["between", [next_week_start, next_week_end]]
            }
        )
    except:
        return 0 