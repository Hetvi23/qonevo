# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def setup_manufacturing_serials():
    """Setup manufacturing serials custom field in Sales Order"""
    
    print("Setting up Manufacturing Serials system...")
    
    # Custom fields for Sales Order
    custom_fields = {
        "Sales Order": [
            {
                "fieldname": "custom_manufactured_serials",
                "label": "Manufactured Serials",
                "fieldtype": "Table",
                "options": "Manufacturing Serials",
                "insert_after": "packed_items",
                "read_only": 1,
                "description": "Serial numbers manufactured through work orders"
            },
            {
                "fieldname": "custom_serials_added",
                "label": "Serials Added",
                "fieldtype": "Check",
                "insert_after": "custom_manufactured_serials",
                "read_only": 1,
                "description": "Whether manufacturing serials have been added to this sales order"
            }
        ]
    }
    
    try:
        create_custom_fields(custom_fields, update=True)
        frappe.db.commit()
        print("✓ Manufacturing Serials custom fields created successfully!")
        
        # Test the fields
        print("\nTesting custom fields...")
        try:
            # Get a sample sales order
            sales_orders = frappe.get_all("Sales Order", limit=1)
            if sales_orders:
                so_name = sales_orders[0].name
                manufactured_serials = frappe.db.get_value("Sales Order", so_name, "custom_manufactured_serials")
                serials_added = frappe.db.get_value("Sales Order", so_name, "custom_serials_added")
                
                print(f"Sample Sales Order: {so_name}")
                print(f"Manufactured Serials: {manufactured_serials or 'None'}")
                print(f"Serials Added: {serials_added or 'None'}")
            else:
                print("No sales orders found to test")
                
        except Exception as e:
            print(f"Error testing fields: {str(e)}")
        
        print("\n" + "=" * 50)
        print("✓ Manufacturing Serials setup completed!")
        
    except Exception as e:
        print(f"Error setting up Manufacturing Serials: {str(e)}")
        frappe.logger().error(f"Error in setup_manufacturing_serials: {str(e)}")


if __name__ == "__main__":
    setup_manufacturing_serials()

