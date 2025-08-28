# Copyright (c) 2025, Qonevo and contributors
# License: MIT. See LICENSE

import frappe
import json
from frappe import _


def setup_priority_system():
    """Setup priority system for sales orders"""
    
    # Install custom fields
    install_custom_fields()
    
    # Create dashboard
    create_delivery_dashboard()
    
    # Create report
    create_delivery_report()
    
    frappe.msgprint(_("Priority system setup completed successfully!"), indicator="green")


def install_custom_fields():
    """Install custom fields for Sales Order"""
    
    custom_fields = [
        {
            "doctype": "Custom Field",
            "fieldname": "priority",
            "label": "Priority",
            "fieldtype": "Select",
            "options": "Low\nMedium\nHigh\nUrgent",
            "default": "Medium",
            "insert_after": "order_type",
            "parent": "Sales Order",
            "reqd": 1,
            "in_standard_filter": 1,
            "in_list_view": 1,
            "width": "100px"
        },
        {
            "doctype": "Custom Field",
            "fieldname": "priority_status",
            "label": "Priority Status",
            "fieldtype": "Select",
            "options": "Pending\nIn Progress\nCompleted\nOn Hold",
            "default": "Pending",
            "insert_after": "priority",
            "parent": "Sales Order",
            "read_only": 1,
            "in_standard_filter": 1,
            "in_list_view": 1,
            "width": "120px"
        },
        {
            "doctype": "Custom Field",
            "fieldname": "approval_section",
            "label": "Approval Workflow",
            "fieldtype": "Section Break",
            "insert_after": "priority_status",
            "parent": "Sales Order",
            "collapsible": 1,
            "collapsed": 1
        },
        {
            "doctype": "Custom Field",
            "fieldname": "finance_approval_status",
            "label": "Finance Approval",
            "fieldtype": "Select",
            "options": "Pending\nApproved\nRejected",
            "default": "Pending",
            "insert_after": "approval_section",
            "parent": "Sales Order",
            "read_only": 1,
            "in_standard_filter": 1,
            "width": "120px"
        },
        {
            "doctype": "Custom Field",
            "fieldname": "finance_approval_date",
            "label": "Finance Approval Date",
            "fieldtype": "Datetime",
            "insert_after": "finance_approval_status",
            "parent": "Sales Order",
            "read_only": 1,
            "hidden": 1
        },
        {
            "doctype": "Custom Field",
            "fieldname": "finance_approver",
            "label": "Finance Approver",
            "fieldtype": "Link",
            "options": "User",
            "insert_after": "finance_approval_date",
            "parent": "Sales Order",
            "read_only": 1,
            "hidden": 1
        },
        {
            "doctype": "Custom Field",
            "fieldname": "inventory_approval_status",
            "label": "Inventory Approval",
            "fieldtype": "Select",
            "options": "Pending\nApproved\nRejected",
            "default": "Pending",
            "insert_after": "finance_approver",
            "parent": "Sales Order",
            "read_only": 1,
            "in_standard_filter": 1,
            "width": "120px"
        },
        {
            "doctype": "Custom Field",
            "fieldname": "inventory_approval_date",
            "label": "Inventory Approval Date",
            "fieldtype": "Datetime",
            "insert_after": "inventory_approval_status",
            "parent": "Sales Order",
            "read_only": 1,
            "hidden": 1
        },
        {
            "doctype": "Custom Field",
            "fieldname": "inventory_approver",
            "label": "Inventory Approver",
            "fieldtype": "Link",
            "options": "User",
            "insert_after": "inventory_approval_date",
            "parent": "Sales Order",
            "read_only": 1,
            "hidden": 1
        },
        {
            "doctype": "Custom Field",
            "fieldname": "delivery_week",
            "label": "Delivery Week",
            "fieldtype": "Data",
            "insert_after": "delivery_date",
            "parent": "Sales Order",
            "read_only": 1,
            "in_standard_filter": 1,
            "width": "100px"
        }
    ]
    
    for field_data in custom_fields:
        if not frappe.db.exists("Custom Field", {"fieldname": field_data["fieldname"], "parent": field_data["parent"]}):
            try:
                custom_field = frappe.get_doc(field_data)
                custom_field.insert()
                frappe.db.commit()
                print(f"Created custom field: {field_data['fieldname']}")
            except Exception as e:
                print(f"Error creating custom field {field_data['fieldname']}: {str(e)}")
                frappe.db.rollback()


def create_delivery_dashboard():
    """Create delivery tracking dashboard"""
    
    if not frappe.db.exists("Dashboard", "Delivery Tracking Dashboard"):
        dashboard = frappe.get_doc({
            "doctype": "Dashboard",
            "dashboard_name": "Delivery Tracking Dashboard",
            "is_default": 1,
            "is_standard": 1,
            "module": "Qonevo"
        })
        dashboard.insert()
        frappe.db.commit()


def create_delivery_report():
    """Create delivery tracking report"""
    
    if not frappe.db.exists("Report", "Delivery Tracking Report"):
        report = frappe.get_doc({
            "doctype": "Report",
            "report_name": "Delivery Tracking Report",
            "ref_doctype": "Sales Order",
            "report_type": "Script Report",
            "module": "Qonevo",
            "is_standard": 1,
            "report_script": """
import frappe
from frappe import _
from frappe.utils import getdate, add_days, get_week_start, get_week_end

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"fieldname": "sales_order", "label": _("Sales Order"), "fieldtype": "Link", "options": "Sales Order", "width": 120},
        {"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link", "options": "Customer", "width": 150},
        {"fieldname": "customer_name", "label": _("Customer Name"), "fieldtype": "Data", "width": 150},
        {"fieldname": "priority", "label": _("Priority"), "fieldtype": "Data", "width": 80},
        {"fieldname": "delivery_date", "label": _("Delivery Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "total_qty", "label": _("Total Qty"), "fieldtype": "Float", "width": 80},
        {"fieldname": "grand_total", "label": _("Total Amount"), "fieldtype": "Currency", "width": 120},
        {"fieldname": "finance_approval_status", "label": _("Finance Approval"), "fieldtype": "Data", "width": 100},
        {"fieldname": "inventory_approval_status", "label": _("Inventory Approval"), "fieldtype": "Data", "width": 100},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100}
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    data = frappe.db.sql(\"\"\"
        SELECT 
            so.name as sales_order,
            so.customer,
            so.customer_name,
            so.priority,
            so.delivery_date,
            so.total_qty,
            so.grand_total,
            so.finance_approval_status,
            so.inventory_approval_status,
            so.status
        FROM `tabSales Order` so
        WHERE so.docstatus = 1
        AND so.status NOT IN ('Cancelled', 'Closed')
        {conditions}
        ORDER BY so.priority DESC, so.delivery_date ASC
    \"\"\".format(conditions=conditions), filters, as_dict=1)
    
    return data

def get_conditions(filters):
    conditions = ""
    
    if filters.get("priority"):
        conditions += " AND so.priority = %(priority)s"
    
    if filters.get("finance_approval_status"):
        conditions += " AND so.finance_approval_status = %(finance_approval_status)s"
    
    if filters.get("inventory_approval_status"):
        conditions += " AND so.inventory_approval_status = %(inventory_approval_status)s"
    
    if filters.get("delivery_date_from"):
        conditions += " AND so.delivery_date >= %(delivery_date_from)s"
    
    if filters.get("delivery_date_to"):
        conditions += " AND so.delivery_date <= %(delivery_date_to)s"
    
    if filters.get("customer"):
        conditions += " AND so.customer = %(customer)s"
    
    return conditions
"""
        })
        report.insert()
        frappe.db.commit()


@frappe.whitelist()
def install():
    """Install the priority system"""
    setup_priority_system() 