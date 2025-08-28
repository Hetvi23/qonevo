# Copyright (c) 2025, Hetvi Patel and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    from frappe import db
    from frappe.utils import nowdate, get_first_day

    month_start = get_first_day(nowdate())

    lost = db.count("Opportunity", {
        "status": "Lost",
        "transaction_date": [">=", month_start]
    })

    columns = [{"label": "Lost Opportunities", "fieldname": "lost", "fieldtype": "Int"}]
    data = [{"lost": lost}]

    return columns, data

