# Copyright (c) 2025, Hetvi Patel and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    from frappe import db
    from frappe.utils import nowdate

    count = db.count("Lead", {"custom_demo_scheduled_on": nowdate()})

    columns = [{"label": "Demos Today", "fieldname": "count", "fieldtype": "Int"}]
    data = [{"count": count}]

    return columns, data

