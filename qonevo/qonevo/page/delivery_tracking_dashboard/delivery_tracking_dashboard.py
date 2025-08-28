# Copyright (c) 2025, Qonevo and contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.utils import getdate, add_days, get_week_start, get_week_end


def get_context(context):
    context.title = _("Delivery Tracking Dashboard")
    context.no_cache = 1
    
    # Get delivery data for the current week
    context.delivery_data = get_delivery_data()
    context.priority_data = get_priority_data()
    context.approval_data = get_approval_data()
    
    return context


def get_delivery_data():
    """Get delivery data for current week"""
    today = getdate()
    week_start = get_week_start(today)
    week_end = get_week_end(today)
    
    # Get sales orders with delivery dates in current week
    sales_orders = frappe.get_all(
        "Sales Order",
        filters={
            "delivery_date": ["between", [week_start, week_end]],
            "docstatus": 1,
            "status": ["not in", ["Cancelled", "Closed"]]
        },
        fields=["name", "customer", "customer_name", "delivery_date", "priority", 
                "total_qty", "grand_total", "finance_approval_status", "inventory_approval_status"]
    )
    
    # Group by delivery date
    delivery_by_date = {}
    for so in sales_orders:
        delivery_date = str(so.delivery_date)
        if delivery_date not in delivery_by_date:
            delivery_by_date[delivery_date] = []
        delivery_by_date[delivery_date].append(so)
    
    return {
        "week_start": week_start,
        "week_end": week_end,
        "sales_orders": sales_orders,
        "delivery_by_date": delivery_by_date,
        "total_orders": len(sales_orders),
        "total_qty": sum(so.total_qty for so in sales_orders),
        "total_amount": sum(so.grand_total for so in sales_orders)
    }


def get_priority_data():
    """Get priority distribution data"""
    priority_counts = frappe.get_all(
        "Sales Order",
        filters={
            "docstatus": 1,
            "status": ["not in", ["Cancelled", "Closed"]]
        },
        fields=["priority", "count(name) as count"],
        group_by="priority"
    )
    
    return priority_counts


def get_approval_data():
    """Get approval status data"""
    approval_counts = frappe.get_all(
        "Sales Order",
        filters={
            "docstatus": 1,
            "status": ["not in", ["Cancelled", "Closed"]]
        },
        fields=[
            "finance_approval_status", 
            "inventory_approval_status", 
            "count(name) as count"
        ],
        group_by="finance_approval_status, inventory_approval_status"
    )
    
    return approval_counts 