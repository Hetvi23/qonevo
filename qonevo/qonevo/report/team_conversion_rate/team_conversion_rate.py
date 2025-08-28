# Copyright (c) 2025, Hetvi Patel and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    from frappe import session, db

    total_leads = db.count("Lead")
    converted_leads = db.count("Lead", {
        "custom_linked_sales_order": ["is", "set"]
    })

    rate = (converted_leads / total_leads) * 100 if total_leads else 0

    columns = [
        {"label": "Total Leads", "fieldname": "total", "fieldtype": "Int"},
        {"label": "Converted Leads", "fieldname": "converted", "fieldtype": "Int"},
        {"label": "Conversion Rate (%)", "fieldname": "rate", "fieldtype": "Percent"},
    ]

    data = [{
        "total": total_leads,
        "converted": converted_leads,
        "rate": round(rate, 2)
    }]

    return columns, data
