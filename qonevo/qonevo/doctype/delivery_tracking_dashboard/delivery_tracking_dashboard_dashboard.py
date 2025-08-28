from frappe import _


def get_data():
    return {
        "fieldname": "delivery_tracking_dashboard",
        "non_standard_fieldnames": {
            "Sales Order": "delivery_tracking_dashboard",
            "Delivery Note": "delivery_tracking_dashboard",
        },
        "transactions": [
            {
                "label": _("Sales Orders"),
                "items": ["Sales Order"],
            },
            {
                "label": _("Delivery"),
                "items": ["Delivery Note"],
            },
        ],
    } 