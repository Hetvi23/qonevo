// Copyright (c) 2024, Qonevo and contributors
// For license information, please see license.txt

frappe.query_reports["Engineer Ticket Report"] = {
    "filters": [
        {
            "fieldname": "start_date",
            "label": __("Start Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -30),
            "reqd": 1
        },
        {
            "fieldname": "end_date",
            "label": __("End Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "Open\nReplied\nResolved\nClosed\nEngineer Alligned\nSpare Requested"
        },
        {
            "fieldname": "priority",
            "label": __("Priority"),
            "fieldtype": "Link",
            "options": "HD Ticket Priority"
        },
        {
            "fieldname": "agent_group",
            "label": __("Agent Group"),
            "fieldtype": "Link",
            "options": "HD Team"
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "HD Customer"
        }
    ]
}; 