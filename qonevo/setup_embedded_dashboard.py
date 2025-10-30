#!/usr/bin/env python3
"""
Setup script for Embedded Delivery Dashboard
This script creates the workspace and page for the embedded dashboard
"""

import frappe
import json
import os

def setup_embedded_dashboard():
    """Setup the embedded delivery dashboard"""
    print("Setting up Embedded Delivery Dashboard...")
    
    # Create the Page
    create_delivery_dashboard_page()
    
    # Create the Workspace
    create_delivery_dashboard_workspace()
    
    print("✅ Embedded Delivery Dashboard setup completed!")
    print("📊 You can now access the dashboard from the Selling module workspace")

def create_delivery_dashboard_page():
    """Create the delivery dashboard page"""
    try:
        # Check if page already exists
        if frappe.db.exists("Page", "delivery-dashboard-page"):
            print("📄 Page 'delivery-dashboard-page' already exists")
            return
        
        # Create the page
        page = frappe.get_doc({
            "doctype": "Page",
            "name": "delivery-dashboard-page",
            "title": "Delivery Dashboard",
            "route": "delivery-dashboard-page",
            "template": "delivery_dashboard_page.html",
            "published": 1,
            "for_user": "Administrator"
        })
        
        page.insert()
        print("✅ Created Page: delivery-dashboard-page")
        
    except Exception as e:
        print(f"❌ Error creating page: {str(e)}")

def create_delivery_dashboard_workspace():
    """Create the delivery dashboard workspace"""
    try:
        # Check if workspace already exists
        if frappe.db.exists("Workspace", "delivery-dashboard"):
            print("📊 Workspace 'delivery-dashboard' already exists")
            return
        
        # Create the workspace
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "name": "delivery-dashboard",
            "label": "Delivery Dashboard",
            "title": "Delivery Dashboard",
            "extends": "Selling",
            "extends_another_page": 0,
            "for_user": "Administrator",
            "icon": "chart-line",
            "is_default": 0,
            "is_standard": 0,
            "module": "Qonevo",
            "page_name": "delivery-dashboard",
            "pin_to_bottom": 0,
            "pin_to_top": 0,
            "shortcuts": [],
            "shortcuts_label": "",
            "links": [
                {
                    "hidden": 0,
                    "icon": "chart-line",
                    "label": "Delivery Overview",
                    "link_to": "delivery-dashboard-page",
                    "link_type": "Page",
                    "onboard": 0,
                    "type": "Link"
                }
            ]
        })
        
        workspace.insert()
        print("✅ Created Workspace: delivery-dashboard")
        
    except Exception as e:
        print(f"❌ Error creating workspace: {str(e)}")

def update_selling_workspace():
    """Update the Selling workspace to include the delivery dashboard link"""
    try:
        # Get the Selling workspace
        selling_workspace = frappe.get_doc("Workspace", "Selling")
        
        # Check if delivery dashboard link already exists
        existing_links = [link.label for link in selling_workspace.links]
        if "Delivery Dashboard" in existing_links:
            print("📊 Delivery Dashboard link already exists in Selling workspace")
            return
        
        # Add the delivery dashboard link
        selling_workspace.append("links", {
            "hidden": 0,
            "icon": "chart-line",
            "label": "Delivery Dashboard",
            "link_to": "delivery-dashboard-page",
            "link_type": "Page",
            "onboard": 0,
            "type": "Link"
        })
        
        selling_workspace.save()
        print("✅ Added Delivery Dashboard link to Selling workspace")
        
    except Exception as e:
        print(f"❌ Error updating Selling workspace: {str(e)}")

if __name__ == "__main__":
    # This will be called when the script is executed
    setup_embedded_dashboard()
    update_selling_workspace() 