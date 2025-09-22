# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    """Execute Installation Job Report"""
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data


def get_columns():
    """Get report columns"""
    return [
        {
            "fieldname": "name",
            "label": _("Installation Job"),
            "fieldtype": "Link",
            "options": "Installation Job",
            "width": 150
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "customer",
            "label": _("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150
        },
        {
            "fieldname": "sales_order",
            "label": _("Sales Order"),
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 120
        },
        {
            "fieldname": "delivery_note",
            "label": _("Delivery Note"),
            "fieldtype": "Link",
            "options": "Delivery Note",
            "width": 120
        },
        {
            "fieldname": "assigned_installer",
            "label": _("Assigned Installer"),
            "fieldtype": "Link",
            "options": "User",
            "width": 150
        },
        {
            "fieldname": "installation_date",
            "label": _("Installation Date"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "total_items",
            "label": _("Total Items"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "installed_count",
            "label": _("Installed"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "completion_percentage",
            "label": _("Completion %"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "creation",
            "label": _("Created"),
            "fieldtype": "Datetime",
            "width": 150
        }
    ]


def get_data(filters):
    """Get report data"""
    conditions = get_conditions(filters)
    
    query = """
        SELECT 
            ij.name,
            ij.status,
            ij.customer,
            ij.sales_order,
            ij.delivery_note,
            ij.assigned_installer,
            ij.installation_date,
            ij.total_items,
            ij.installed_count,
            ij.completion_percentage,
            ij.creation
        FROM `tabInstallation Job` ij
        WHERE ij.docstatus != 2
        {conditions}
        ORDER BY ij.creation DESC
    """.format(conditions=conditions)
    
    return frappe.db.sql(query, as_dict=True)


def get_conditions(filters):
    """Get filter conditions"""
    conditions = []
    
    if filters.get("status"):
        conditions.append("ij.status = '{0}'".format(filters.get("status")))
    
    if filters.get("customer"):
        conditions.append("ij.customer = '{0}'".format(filters.get("customer")))
    
    if filters.get("assigned_installer"):
        conditions.append("ij.assigned_installer = '{0}'".format(filters.get("assigned_installer")))
    
    if filters.get("from_date"):
        conditions.append("ij.installation_date >= '{0}'".format(filters.get("from_date")))
    
    if filters.get("to_date"):
        conditions.append("ij.installation_date <= '{0}'".format(filters.get("to_date")))
    
    return " AND " + " AND ".join(conditions) if conditions else ""
