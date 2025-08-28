# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime, timedelta

def execute(filters=None):
    if not filters:
        filters = {}
    
    # Set default filters
    if not filters.get('start_date'):
        filters['start_date'] = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not filters.get('end_date'):
        filters['end_date'] = datetime.now().strftime('%Y-%m-%d')
    
    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "ticket_id",
            "label": _("Ticket ID"),
            "fieldtype": "Link",
            "options": "HD Ticket",
            "width": 120
        },
        {
            "fieldname": "subject",
            "label": _("Subject"),
            "fieldtype": "Data",
            "width": 200
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Select",
            "width": 100
        },
        {
            "fieldname": "priority",
            "label": _("Priority"),
            "fieldtype": "Link",
            "options": "HD Ticket Priority",
            "width": 100
        },
        {
            "fieldname": "agent_group",
            "label": _("Agent Group"),
            "fieldtype": "Link",
            "options": "HD Team",
            "width": 150
        },
        {
            "fieldname": "customer",
            "label": _("Customer"),
            "fieldtype": "Link",
            "options": "HD Customer",
            "width": 150
        },
        {
            "fieldname": "raised_by",
            "label": _("Raised By"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "start_date",
            "label": _("Start Date"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "end_date",
            "label": _("End Date"),
            "fieldtype": "Date",
            "width": 120
        }
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    query = """
        SELECT 
            t.name as ticket_id,
            t.subject,
            t.status,
            t.priority,
            t.agent_group,
            t.customer,
            t.raised_by,
            t.opening_date as start_date,
            t.resolution_date as end_date,
            t.creation,
            t.resolution_by,
            t.resolution_date,
            t.first_response_time,
            t.avg_response_time,
            t.resolution_time,
            t.user_resolution_time,
            t.feedback_rating
        FROM `tabHD Ticket` t
        WHERE {conditions}
        ORDER BY t.creation DESC
    """.format(conditions=conditions)
    
    data = frappe.db.sql(query, filters, as_dict=1)
    
    # Format the data
    for row in data:
        if row.get('first_response_time'):
            row['first_response_time'] = format_duration(row['first_response_time'])
        if row.get('avg_response_time'):
            row['avg_response_time'] = format_duration(row['avg_response_time'])
        if row.get('resolution_time'):
            row['resolution_time'] = format_duration(row['resolution_time'])
        if row.get('user_resolution_time'):
            row['user_resolution_time'] = format_duration(row['user_resolution_time'])
    
    return data

def get_conditions(filters):
    conditions = ["1=1"]
    
    if filters.get('start_date'):
        conditions.append("DATE(t.creation) >= %(start_date)s")
    
    if filters.get('end_date'):
        conditions.append("DATE(t.creation) <= %(end_date)s")
    
    if filters.get('status'):
        conditions.append("t.status = %(status)s")
    
    if filters.get('priority'):
        conditions.append("t.priority = %(priority)s")
    
    if filters.get('agent_group'):
        conditions.append("t.agent_group = %(agent_group)s")
    
    if filters.get('customer'):
        conditions.append("t.customer = %(customer)s")
    
    return " AND ".join(conditions)

def format_duration(seconds):
    """Convert seconds to human readable duration"""
    if not seconds:
        return ""
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"