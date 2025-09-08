import frappe
from frappe import _
from datetime import datetime, timedelta
import calendar

def get_context(context):
    """Get context for the embedded delivery dashboard"""
    context.update({
        "delivery_data": get_delivery_data(),
        "priority_data": get_priority_data(),
        "total_orders": get_total_orders(),
        "total_qty": get_total_qty(),
        "total_amount": get_total_amount(),
        "priority_levels": 4,
        "this_week_count": get_this_week_count(),
        "next_week_count": get_next_week_count()
    })

@frappe.whitelist()
def get_dashboard_data():
    """API method to get dashboard data for AJAX updates"""
    return {
        "delivery_data": get_delivery_data(),
        "priority_data": get_priority_data(),
        "total_orders": get_total_orders(),
        "total_qty": get_total_qty(),
        "total_amount": get_total_amount(),
        "this_week_count": get_this_week_count(),
        "next_week_count": get_next_week_count()
    }

def get_delivery_data():
    """Get delivery data for the current and next week"""
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    next_week_start = end_of_week + timedelta(days=1)
    next_week_end = next_week_start + timedelta(days=6)
    
    # Get sales orders with delivery dates in current and next week
    orders = frappe.get_all(
        "Sales Order",
        filters={
            "docstatus": 1,  # Submitted orders
            "delivery_date": ["between", [start_of_week, next_week_end]]
        },
        fields=["name", "customer", "custom_priority", "delivery_date", "delivery_week", "grand_total"],
        order_by="delivery_date"
    )
    
    delivery_data = []
    for order in orders:
        # Get total quantity for this order
        total_qty = frappe.db.sql("""
            SELECT SUM(qty) as total_qty 
            FROM `tabSales Order Item` 
            WHERE parent = %s
        """, order.name, as_dict=True)
        
        qty = total_qty[0].total_qty if total_qty and total_qty[0].total_qty else 0
        
        # Determine priority color
        priority_colors = {
            "Urgent": "urgent",
            "High": "high", 
            "Medium": "medium",
            "Low": "low"
        }
        
        # Determine status color
        status_colors = {
            "Pending": "pending",
            "Completed": "completed"
        }
        
        delivery_data.append({
            "name": order.name,
            "customer": order.customer,
            "priority": order.custom_priority or "Medium",
            "priority_color": priority_colors.get(order.custom_priority, "medium"),
            "delivery_date": order.delivery_date.strftime("%d-%m-%Y") if order.delivery_date else "",
            "priority_status": "Pending",  # Default status since field doesn't exist
            "status_color": "pending",  # Default color
            "total_qty": qty,
            "grand_total": order.grand_total or 0
        })
    
    return delivery_data

def get_priority_data():
    """Get priority distribution data"""
    priorities = ["Urgent", "High", "Medium", "Low"]
    priority_data = []
    
    for priority in priorities:
        count = frappe.db.count("Sales Order", {
            "docstatus": 1,
            "custom_priority": priority
        })
        
        colors = {
            "Urgent": "urgent",
            "High": "high",
            "Medium": "medium", 
            "Low": "low"
        }
        
        priority_data.append({
            "name": priority,
            "count": count,
            "color": colors.get(priority, "medium")
        })
    
    return priority_data

def get_total_orders():
    """Get total number of submitted sales orders"""
    return frappe.db.count("Sales Order", {"docstatus": 1})

def get_total_qty():
    """Get total quantity from all submitted sales orders"""
    result = frappe.db.sql("""
        SELECT SUM(soi.qty) as total_qty
        FROM `tabSales Order Item` soi
        JOIN `tabSales Order` so ON soi.parent = so.name
        WHERE so.docstatus = 1
    """, as_dict=True)
    
    return result[0].total_qty if result and result[0].total_qty else 0

def get_total_amount():
    """Get total amount from all submitted sales orders"""
    result = frappe.db.sql("""
        SELECT SUM(grand_total) as total_amount
        FROM `tabSales Order`
        WHERE docstatus = 1
    """, as_dict=True)
    
    return result[0].total_amount if result and result[0].total_amount else 0

def get_this_week_count():
    """Get count of orders for this week"""
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    return frappe.db.count("Sales Order", {
        "docstatus": 1,
        "delivery_date": ["between", [start_of_week, end_of_week]]
    })

def get_next_week_count():
    """Get count of orders for next week"""
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    next_week_start = end_of_week + timedelta(days=1)
    next_week_end = next_week_start + timedelta(days=6)
    
    return frappe.db.count("Sales Order", {
        "docstatus": 1,
        "delivery_date": ["between", [next_week_start, next_week_end]]
    }) 