# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def setup_installation_job_system():
    """
    Setup the complete Installation Job system with all DocTypes, workflows, and custom fields.
    """
    print("🔧 Setting up Installation Job System...")
    
    try:
        # Create DocTypes
        create_doctypes()
        
        # Custom fields not required - installation is automatic for all Sales Orders
        
        # Create workflows
        create_workflows()
        
        # Create reports
        create_reports()
        
        # Create roles if they don't exist
        create_roles()
        
        # Commit all changes
        frappe.db.commit()
        
        print("✅ Installation Job System setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error setting up Installation Job System: {str(e)}")
        frappe.logger().error(f"Error setting up Installation Job System: {str(e)}")
        raise


def create_doctypes():
    """Create all required DocTypes"""
    print("📝 Creating DocTypes...")
    
    doctypes = [
        "Installation Job",
        "Installation Job Item", 
        "Installation Job Photo",
        "Warranty Record"
    ]
    
    for doctype in doctypes:
        if not frappe.db.exists("DocType", doctype):
            print(f"   Creating {doctype}...")
            # DocType creation will be handled by the JSON files
        else:
            print(f"   {doctype} already exists")


def create_custom_fields():
    """Custom fields not required - installation is automatic for all Sales Orders"""
    print("ℹ️ No custom fields required - installation is automatic for all Sales Orders")


def create_workflows():
    """Create workflows"""
    print("🔄 Creating workflows...")
    
    if not frappe.db.exists("Workflow", "Installation Job Workflow"):
        print("   Creating Installation Job Workflow...")
        # Workflow creation will be handled by fixtures


def create_reports():
    """Create reports"""
    print("📊 Creating reports...")
    
    if not frappe.db.exists("Report", "Installation Job Report"):
        print("   Creating Installation Job Report...")
        # Report creation will be handled by fixtures


def create_roles():
    """Create required roles"""
    print("👥 Creating roles...")
    
    roles = [
        {
            "role_name": "Installer",
            "desk_access": 1,
            "restrict_to_domain": None,
            "disabled": 0
        },
        {
            "role_name": "Operations Manager", 
            "desk_access": 1,
            "restrict_to_domain": None,
            "disabled": 0
        }
    ]
    
    for role_data in roles:
        if not frappe.db.exists("Role", role_data["role_name"]):
            print(f"   Creating role: {role_data['role_name']}")
            role = frappe.new_doc("Role")
            role.role_name = role_data["role_name"]
            role.desk_access = role_data["desk_access"]
            role.restrict_to_domain = role_data["restrict_to_domain"]
            role.disabled = role_data["disabled"]
            role.insert(ignore_permissions=True)
        else:
            print(f"   Role {role_data['role_name']} already exists")


@frappe.whitelist()
def test_installation_job_creation():
    """Test function to create a sample Installation Job"""
    print("🧪 Testing Installation Job creation...")
    
    try:
        # Create a test Installation Job
        installation_job = frappe.new_doc("Installation Job")
        installation_job.sales_order = "SO-00001"  # Replace with actual SO
        installation_job.delivery_note = "DN-00001"  # Replace with actual DN
        installation_job.customer = "Customer 1"  # Replace with actual customer
        installation_job.status = "Scheduled"
        
        # Add test items
        test_item = installation_job.append("installed_items")
        test_item.item = "Test Item"
        test_item.qty = 1
        test_item.serial_no = "TEST-001"
        test_item.installed = 0
        test_item.installation_status = "Pending"
        
        installation_job.insert(ignore_permissions=True)
        frappe.db.commit()
        
        print(f"✅ Test Installation Job created: {installation_job.name}")
        return {
            "success": True,
            "message": f"Test Installation Job {installation_job.name} created successfully"
        }
        
    except Exception as e:
        print(f"❌ Error creating test Installation Job: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@frappe.whitelist()
def get_installation_job_summary():
    """Get summary of Installation Jobs"""
    try:
        summary = frappe.db.sql("""
            SELECT 
                status,
                COUNT(*) as count
            FROM `tabInstallation Job`
            WHERE docstatus != 2
            GROUP BY status
            ORDER BY status
        """, as_dict=True)
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    setup_installation_job_system()
