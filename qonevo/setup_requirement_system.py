#!/usr/bin/env python3
import frappe
from frappe import _

def setup_requirement_system():
    """Setup the complete requirement gathering system"""
    print("Setting up Requirement Gathering System...")
    
    # Create custom fields for Supplier
    create_supplier_custom_fields()
    
    # Create sample supplier
    create_sample_supplier()
    
    # Create sample items
    create_sample_items()
    
    # Create sample requirement
    create_sample_requirement()
    
    print("Requirement Gathering System setup completed!")

def create_supplier_custom_fields():
    """Create custom fields for Supplier doctype"""
    print("Creating custom fields for Supplier...")
    
    custom_fields = [
        {
            "fieldname": "supplier_address",
            "fieldtype": "Small Text",
            "label": "Supplier Address",
            "dt": "Supplier"
        },
        {
            "fieldname": "contact_person",
            "fieldtype": "Data",
            "label": "Contact Person",
            "dt": "Supplier"
        },
        {
            "fieldname": "gstin",
            "fieldtype": "Data",
            "label": "GSTIN",
            "dt": "Supplier"
        },
        {
            "fieldname": "payment_terms",
            "fieldtype": "Data",
            "label": "Payment Terms",
            "dt": "Supplier"
        },
        {
            "fieldname": "supply_terms",
            "fieldtype": "Data",
            "label": "Supply Terms",
            "dt": "Supplier"
        },
        {
            "fieldname": "transport_details",
            "fieldtype": "Data",
            "label": "Transport Details",
            "dt": "Supplier"
        }
    ]
    
    for field in custom_fields:
        create_custom_field(field)

def create_custom_field(field_data):
    """Create a custom field"""
    try:
        # Check if custom field already exists
        existing = frappe.db.exists("Custom Field", {
            "dt": field_data["dt"],
            "fieldname": field_data["fieldname"]
        })
        
        if existing:
            print(f"Custom field {field_data['fieldname']} already exists for {field_data['dt']}")
            return
        
        # Create custom field
        custom_field = frappe.new_doc("Custom Field")
        custom_field.dt = field_data["dt"]
        custom_field.fieldname = field_data["fieldname"]
        custom_field.fieldtype = field_data["fieldtype"]
        custom_field.label = field_data["label"]
        custom_field.insert()
        
        print(f"Created custom field: {field_data['fieldname']} for {field_data['dt']}")
        
    except Exception as e:
        print(f"Error creating custom field {field_data['fieldname']}: {str(e)}")

def create_sample_supplier():
    """Create a sample supplier"""
    print("Creating sample supplier...")
    
    try:
        # Check if supplier already exists
        if frappe.db.exists("Supplier", "Sample Supplier"):
            print("Sample Supplier already exists")
            return
        
        supplier = frappe.new_doc("Supplier")
        supplier.supplier_name = "Sample Supplier"
        supplier.supplier_type = "Company"
        supplier.country = "India"
        supplier.supplier_address = "123 Sample Street, Sample City, Sample State - 123456"
        supplier.contact_person = "John Doe"
        supplier.gstin = "22AAAAA0000A1Z5"
        supplier.payment_terms = "Net 30 days"
        supplier.supply_terms = "FOB Destination"
        supplier.transport_details = "Road transport, delivery within 7 days"
        supplier.insert()
        
        print("Sample Supplier created successfully")
        
    except Exception as e:
        print(f"Error creating sample supplier: {str(e)}")

def create_sample_items():
    """Create sample items"""
    print("Creating sample items...")
    
    items = [
        {
            "item_code": "ITEM-001",
            "item_name": "Sample Item 1",
            "item_group": "Products",
            "stock_uom": "Nos",
            "standard_rate": 100.0
        },
        {
            "item_code": "ITEM-002", 
            "item_name": "Sample Item 2",
            "item_group": "Products",
            "stock_uom": "Nos",
            "standard_rate": 200.0
        },
        {
            "item_code": "ITEM-003",
            "item_name": "Sample Item 3", 
            "item_group": "Products",
            "stock_uom": "Nos",
            "standard_rate": 150.0
        }
    ]
    
    for item_data in items:
        try:
            # Check if item already exists
            if frappe.db.exists("Item", item_data["item_code"]):
                print(f"Item {item_data['item_code']} already exists")
                continue
            
            item = frappe.new_doc("Item")
            item.item_code = item_data["item_code"]
            item.item_name = item_data["item_name"]
            item.item_group = item_data["item_group"]
            item.stock_uom = item_data["stock_uom"]
            item.standard_rate = item_data["standard_rate"]
            item.is_stock_item = 1
            item.insert()
            
            print(f"Created item: {item_data['item_code']}")
            
        except Exception as e:
            print(f"Error creating item {item_data['item_code']}: {str(e)}")

def create_sample_requirement():
    """Create a sample requirement generation"""
    print("Creating sample requirement generation...")
    
    try:
        # Check if requirement already exists
        if frappe.db.exists("Requirement Generation", "REQ-0001"):
            print("Sample requirement already exists")
            return
        
        # Get sample supplier
        supplier = frappe.get_value("Supplier", {"supplier_name": "Sample Supplier"}, "name")
        if not supplier:
            print("Sample supplier not found, creating requirement without supplier")
            supplier = None
        
        # Get sample items
        items = frappe.get_all("Item", filters={"item_code": ["in", ["ITEM-001", "ITEM-002", "ITEM-003"]]}, fields=["name", "item_code", "item_name", "standard_rate"])
        
        if not items:
            print("No sample items found")
            return
        
        requirement = frappe.new_doc("Requirement Generation")
        requirement.date = frappe.utils.today()
        requirement.supplier = supplier
        
        # Add items
        for item in items[:2]:  # Add first 2 items
            requirement.append("requirement_item", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": 10,
                "rate": item.standard_rate,
                "amount": 10 * item.standard_rate,
                "select_ircl": "Pending"
            })
        
        requirement.insert()
        
        print(f"Created sample requirement: {requirement.name}")
        
    except Exception as e:
        print(f"Error creating sample requirement: {str(e)}")

if __name__ == "__main__":
    setup_requirement_system() 