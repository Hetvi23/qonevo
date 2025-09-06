#!/usr/bin/env python3
# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

"""
Installation script for the Barcode System
Run this script to set up the barcode system in your Frappe/ERPNext installation
"""

import frappe
import sys
import os

def install_barcode_system():
    """Install the barcode system"""
    
    print("Installing Barcode System...")
    print("=" * 50)
    
    try:
        # Initialize Frappe
        frappe.init(site='your-site.com')  # Replace with your site name
        frappe.connect()
        
        # Import and run setup
        from qonevo.setup_barcode_system import setup_barcode_system, create_sample_barcodes
        
        print("1. Setting up custom fields and configurations...")
        setup_barcode_system()
        
        print("2. Creating sample barcodes...")
        create_sample_barcodes()
        
        print("3. Testing barcode system...")
        from qonevo.test_barcode_system import test_barcode_system
        test_barcode_system()
        
        print("\n" + "=" * 50)
        print("✓ Barcode System installed successfully!")
        print("\nNext steps:")
        print("1. Go to Barcode Management workspace")
        print("2. Generate barcodes for your items")
        print("3. Test barcode scanning in logistics modules")
        print("4. Check the README_BARCODE_SYSTEM.md for detailed usage")
        
    except Exception as e:
        print(f"✗ Installation failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure you're in the correct Frappe bench directory")
        print("2. Check if the site name is correct")
        print("3. Ensure all dependencies are installed")
        print("4. Check Frappe error logs for more details")
        sys.exit(1)

if __name__ == "__main__":
    # Check if we're in a Frappe bench
    if not os.path.exists('sites'):
        print("Error: This script must be run from a Frappe bench directory")
        print("Please navigate to your bench directory and run:")
        print("python apps/qonevo/qonevo/install_barcode_system.py")
        sys.exit(1)
    
    # Get site name from command line argument or prompt
    if len(sys.argv) > 1:
        site_name = sys.argv[1]
    else:
        site_name = input("Enter your site name: ").strip()
    
    if not site_name:
        print("Error: Site name is required")
        sys.exit(1)
    
    # Update the site name in the script
    with open(__file__, 'r') as f:
        content = f.read()
    
    content = content.replace("site='your-site.com'", f"site='{site_name}'")
    
    with open(__file__, 'w') as f:
        f.write(content)
    
    install_barcode_system()
