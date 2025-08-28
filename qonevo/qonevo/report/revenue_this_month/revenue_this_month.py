# Copyright (c) 2025, Hetvi Patel and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    from frappe import db
    from frappe.utils import nowdate, get_first_day

    month_start = get_first_day(nowdate())

    revenue = db.sql("""
        SELECT SUM(grand_total) 
        FROM `tabSales Order` 
        WHERE transaction_date >= %s AND docstatus = 1
    """, (month_start))[0][0] or 0

    columns = [{"label": "Revenue This Month", "fieldname": "revenue", "fieldtype": "Currency"}]
    data = [{"revenue": revenue}]

    return columns, data

