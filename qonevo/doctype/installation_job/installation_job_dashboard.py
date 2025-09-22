# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def get_data():
    """Get dashboard data for Installation Job"""
    return {
        "fieldname": "installation_job",
        "transactions": [
            {
                "label": _("Related"),
                "items": ["Warranty Record"]
            }
        ],
        "non_standard_fieldnames": {
            "Warranty Record": "installation_job"
        }
    }
