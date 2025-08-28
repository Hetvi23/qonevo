# Copyright (c) 2025, Hetvi Patel and contributors
# For license information, please see license.txt

# report: Demo to Order Conversion

import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = [
        {"fieldname": "status", "label": "Demo Status", "fieldtype": "Data", "width": 200},
        {"fieldname": "count", "label": "Count", "fieldtype": "Int", "width": 100}
    ]

    data = frappe.db.sql("""
        SELECT custom_demo_status AS status, COUNT(*) AS count
        FROM `tabLead`
        WHERE custom_demo_status IN ('Completed', 'Converted to Order')
        GROUP BY custom_demo_status
    """, as_dict=True)

    # Prepare chart data
    completed = next((d["count"] for d in data if d["status"] == "Completed"), 0)
    converted = next((d["count"] for d in data if d["status"] == "Converted to Order"), 0)
    ratio = round((converted / completed) * 100, 2) if completed else 0

    chart = {
        "data": {
            "labels": ["Completed", "Converted to Order"],
            "datasets": [
                {
                    "name": "Leads",
                    "values": [completed, converted]
                }
            ]
        },
        "type": "bar",  # could also be 'percentage' or 'donut'
        "colors": ["#FFA500", "#4CAF50"]
    }

    message = f"Conversion Ratio: <b>{ratio}%</b>"

    return columns, data, message, chart
