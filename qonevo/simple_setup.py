# Copyright (c) 2025, Qonevo and contributors
# License: MIT. See LICENSE

import frappe
from frappe import _


@frappe.whitelist()
def setup_priority_system():
    """Setup priority system for sales orders"""

    try:
        # Create custom fields one by one
        create_custom_field("priority", "Priority", "Select", "Low\nMedium\nHigh\nUrgent", "Medium", "order_type", "Sales Order", reqd=1, in_standard_filter=1, in_list_view=1, width="100px")
        create_custom_field("priority_status", "Priority Status", "Select", "Pending\nIn Progress\nCompleted\nOn Hold", "Pending", "priority", "Sales Order", read_only=1, in_standard_filter=1, in_list_view=1, width="120px")
        create_custom_field("finance_approval_status", "Finance Approval", "Select", "Pending\nApproved\nRejected", "Pending", "priority_status", "Sales Order", read_only=1, in_standard_filter=1, width="120px")
        create_custom_field("inventory_approval_status", "Inventory Approval", "Select", "Pending\nApproved\nRejected", "Pending", "finance_approval_status", "Sales Order", read_only=1, in_standard_filter=1, width="120px")
        create_custom_field("delivery_week", "Delivery Week", "Data", "", "", "delivery_date", "Sales Order", read_only=1, in_standard_filter=1, width="100px")

        frappe.msgprint(_("Priority system setup completed successfully!"), indicator="green")

    except Exception as e:
        frappe.msgprint(f"Error setting up priority system: {str(e)}", indicator="red")


def create_custom_field(fieldname, label, fieldtype, options, default, insert_after, dt, **kwargs):
    """Create a custom field"""

    if frappe.db.exists("Custom Field", {"fieldname": fieldname, "dt": dt}):
        print(f"Custom field {fieldname} already exists")
        return

    field_data = {
        "doctype": "Custom Field",
        "fieldname": fieldname,
        "label": label,
        "fieldtype": fieldtype,
        "insert_after": insert_after,
        "dt": dt
    }

    if options:
        field_data["options"] = options
    if default:
        field_data["default"] = default

    # Add additional kwargs
    for key, value in kwargs.items():
        field_data[key] = value

    try:
        custom_field = frappe.get_doc(field_data)
        custom_field.insert()
        frappe.db.commit()
        print(f"Created custom field: {fieldname}")
    except Exception as e:
        print(f"Error creating custom field {fieldname}: {str(e)}")
        frappe.db.rollback()


@frappe.whitelist()
def create_sample_data():
    """Create sample sales orders with priority"""

    # Get existing customers
    existing_customers = frappe.get_all("Customer", fields=["name"], limit=3)
    if not existing_customers:
        frappe.msgprint(_("No customers found. Please create customers first."), indicator="red")
        return

    # Get existing items
    existing_items = frappe.get_all("Item", fields=["name"], limit=3)
    if not existing_items:
        frappe.msgprint(_("No items found. Please create items first."), indicator="red")
        return

    # Create sample sales orders
    priorities = ["Low", "Medium", "High", "Urgent"]
    customers = [c.name for c in existing_customers]
    items = [i.name for i in existing_items]

    for i in range(5):
        priority = priorities[i % len(priorities)]
        customer = customers[i % len(customers)]
        item = items[i % len(items)]

        sales_order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": customer,
            "transaction_date": frappe.utils.today(),
            "delivery_date": frappe.utils.add_days(frappe.utils.today(), 7 + i),
            "priority": priority,
            "priority_status": "Pending",
            "finance_approval_status": "Pending",
            "inventory_approval_status": "Pending",
            "items": [{
                "item_code": item,
                "qty": 10 + i,
                "rate": 100 + (i * 10)
            }]
        })

        sales_order.insert()
        sales_order.submit()

    frappe.msgprint(_("Sample data created successfully!"), indicator="green") 