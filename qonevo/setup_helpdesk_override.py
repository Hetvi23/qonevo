# Copyright (c) 2024, Qonevo and contributors
# For license information, please see license.txt

import frappe
import json
import os
from frappe import _

def setup_helpdesk_override():
    """Set up helpdesk overrides for qonevo"""
    try:
        # Create Engineer Ticket Report
        create_engineer_report()
        
        # Update HD Ticket DocType with custom statuses
        update_hd_ticket_statuses()
        
        frappe.msgprint("✅ Qonevo Helpdesk overrides set up successfully!")
        
    except Exception as e:
        frappe.log_error(f"Error setting up helpdesk override: {str(e)}")
        frappe.msgprint(f"❌ Error: {str(e)}")

def create_engineer_report():
    """Create the Engineer Ticket Report"""
    try:
        # Check if report already exists
        if not frappe.db.exists("Report", "Engineer Ticket Report"):
            # Create report
            report = frappe.new_doc("Report")
            report.report_name = "Engineer Ticket Report"
            report.ref_doctype = "HD Ticket"
            report.report_type = "Script Report"
            report.module = "Qonevo"
            report.is_standard = "No"
            report.insert()
            
            # Create report file
            create_report_file()
            
            frappe.msgprint("✅ Engineer Ticket Report created successfully!")
        else:
            frappe.msgprint("ℹ️ Engineer Ticket Report already exists")
            
    except Exception as e:
        frappe.log_error(f"Error creating engineer report: {str(e)}")
        frappe.msgprint(f"❌ Error creating report: {str(e)}")

def create_report_file():
    """Create the report Python file"""
    import os
    
    report_dir = "apps/qonevo/qonevo/overrides/helpdesk/report"
    os.makedirs(report_dir, exist_ok=True)
    
    # Create the Python file
    report_content = '''import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": _("Ticket ID"), "fieldname": "ticket_id", "fieldtype": "Link", "options": "HD Ticket", "width": 120},
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "HD Customer", "width": 150},
        {"label": _("Start Date"), "fieldname": "start_date", "fieldtype": "Date", "width": 100},
        {"label": _("End Date"), "fieldname": "end_date", "fieldtype": "Date", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": _("Priority"), "fieldname": "priority", "fieldtype": "Data", "width": 100}
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    query = """
        SELECT 
            t.opening_date as date,
            t.name as ticket_id,
            t.customer,
            t.opening_date as start_date,
            t.resolution_date as end_date,
            t.status,
            t.priority
        FROM `tabHD Ticket` t
        WHERE {conditions}
        ORDER BY t.opening_date DESC
    """.format(conditions=conditions)
    
    return frappe.db.sql(query, filters, as_dict=1)

def get_conditions(filters):
    conditions = ["1=1"]
    
    if filters.get("start_date"):
        conditions.append("t.opening_date >= %(start_date)s")
    
    if filters.get("end_date"):
        conditions.append("t.opening_date <= %(end_date)s")
    
    if filters.get("status"):
        conditions.append("t.status = %(status)s")
    
    if filters.get("priority"):
        conditions.append("t.priority = %(priority)s")
    
    if filters.get("agent_group"):
        conditions.append("t.agent_group = %(agent_group)s")
    
    if filters.get("customer"):
        conditions.append("t.customer = %(customer)s")
    
    # Engineer-specific filtering
    if frappe.has_permission("HD Ticket", "read", user=frappe.session.user):
        if "Engineer" in [role.role for role in frappe.get_roles(frappe.session.user)]:
            conditions.append("t.agent = %(user)s")
            filters["user"] = frappe.session.user
    
    return " AND ".join(conditions)
'''
    
    with open(f"{report_dir}/engineer_ticket_report.py", "w") as f:
        f.write(report_content)

def update_hd_ticket_statuses():
    """Update HD Ticket DocType with custom statuses"""
    try:
        # Get the HD Ticket DocType
        hd_ticket = frappe.get_doc("DocType", "HD Ticket")
        
        # Find the status field
        status_field = None
        for field in hd_ticket.fields:
            if field.fieldname == "status":
                status_field = field
                break
        
        if status_field:
            # Update the options to include custom statuses
            current_options = status_field.options or ""
            options_list = [opt.strip() for opt in current_options.split('\n') if opt.strip()]
            
            # Add our custom statuses if they don't exist
            custom_statuses = [
                "Engineer Alligned",
                "Spare Requested", 
                "Hold",
                "Reopen"
            ]
            
            for status in custom_statuses:
                if status not in options_list:
                    options_list.append(status)
            
            # Update the field options
            status_field.options = '\n'.join(options_list)
            hd_ticket.save()
            
            frappe.msgprint("✅ HD Ticket statuses updated successfully!")
        else:
            frappe.msgprint("❌ Status field not found in HD Ticket DocType")
            
    except Exception as e:
        frappe.log_error(f"Error updating HD Ticket statuses: {str(e)}")
        frappe.msgprint(f"❌ Error updating statuses: {str(e)}")

def remove_helpdesk_override():
    """Remove helpdesk overrides"""
    try:
        # Remove the report
        if frappe.db.exists("Report", "Engineer Ticket Report"):
            frappe.delete_doc("Report", "Engineer Ticket Report")
            frappe.msgprint("✅ Engineer Ticket Report removed")
        
        # Revert HD Ticket statuses to original
        revert_hd_ticket_statuses()
        
        frappe.msgprint("✅ Helpdesk overrides removed successfully!")
        
    except Exception as e:
        frappe.log_error(f"Error removing helpdesk override: {str(e)}")
        frappe.msgprint(f"❌ Error: {str(e)}")

def revert_hd_ticket_statuses():
    """Revert HD Ticket statuses to original"""
    try:
        hd_ticket = frappe.get_doc("DocType", "HD Ticket")
        
        # Find the status field
        status_field = None
        for field in hd_ticket.fields:
            if field.fieldname == "status":
                status_field = field
                break
        
        if status_field:
            # Revert to original statuses
            original_statuses = [
                "Open",
                "Replied", 
                "Resolved",
                "Closed"
            ]
            
            status_field.options = '\n'.join(original_statuses)
            hd_ticket.save()
            
            frappe.msgprint("✅ HD Ticket statuses reverted to original")
        else:
            frappe.msgprint("❌ Status field not found in HD Ticket DocType")
            
    except Exception as e:
        frappe.log_error(f"Error reverting HD Ticket statuses: {str(e)}")
        frappe.msgprint(f"❌ Error reverting statuses: {str(e)}")

if __name__ == "__main__":
    setup_helpdesk_override() 