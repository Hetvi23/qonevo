# Copyright (c) 2025, Hetvi Patel and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = [
        {"label": "Salesperson", "fieldname": "salesperson", "fieldtype": "Link", "options": "User", "width": 200},
        {"label": "Demos Completed", "fieldname": "completed", "fieldtype": "Int", "width": 150},
        {"label": "Orders Converted", "fieldname": "converted", "fieldtype": "Int", "width": 150},
        {"label": "Conversion Rate (%)", "fieldname": "conversion_rate", "fieldtype": "Percent", "width": 150},
    ]

    data = []

    # Get all users who are assigned as Lead Owners
    salespersons = frappe.db.sql("""
        SELECT DISTINCT lead_owner 
        FROM `tabLead`
        WHERE lead_owner IS NOT NULL
    """, as_dict=True)

    for sp in salespersons:
        owner = sp.lead_owner
        completed = frappe.db.count("Lead", {
            "lead_owner": owner,
            "custom_demo_status": "Completed"
        })
        converted = frappe.db.count("Lead", {
            "lead_owner": owner,
            "custom_demo_status": "Converted to Order"
        })
        rate = round((converted / completed) * 100, 2) if completed else 0

        data.append({
            "salesperson": owner,
            "completed": completed,
            "converted": converted,
            "conversion_rate": rate
        })

    chart = {
        "data": {
            "labels": [row["salesperson"] for row in data],
            "datasets": [
                {
                    "name": "Conversion Rate (%)",
                    "values": [row["conversion_rate"] for row in data]
                }
            ]
        },
        "type": "bar",
        "colors": ["#4CAF50"]
    }

    return columns, data, None, chart
