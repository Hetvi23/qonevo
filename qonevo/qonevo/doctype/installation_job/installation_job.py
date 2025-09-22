# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class InstallationJob(Document):
    def before_save(self):
        """Handle automatic warranty creation when status becomes Completed - Full"""
        self.calculate_summary()
        
        # Check if status changed to Completed - Full and create warranty records
        if self.has_value_changed('status') and self.status == "Completed - Full":
            # Set installation date if not already set
            if not self.installation_date:
                self.installation_date = frappe.utils.today()
            
            # Create warranty records automatically
            self.create_warranty_records_automatically()
    
    def validate(self):
        """Validate Installation Job data"""
        self.validate_installation_items()
        self.validate_photos_and_signature()
        self.calculate_summary()
    
    def validate_installation_items(self):
        """Validate that installation items are properly configured"""
        if not self.installed_items:
            frappe.throw(_("At least one item must be added to the installation job"))
        
        for item in self.installed_items:
            if not item.item:
                frappe.throw(_("Item is required for all installation items"))
            
            if not item.serial_no:
                frappe.throw(_("Serial number is required for item {0}").format(item.item))
    
    def validate_photos_and_signature(self):
        """Validate that photos and signature are provided when job is completed"""
        # Only validate photos and signature when explicitly completing the job
        # Not when status is auto-updated by checkboxes
        if hasattr(self, '_explicitly_completing') and self._explicitly_completing:
            if self.status in ["Completed - Full", "Completed - Partial"]:
                if not self.photos:
                    frappe.throw(_("At least one photo is required before completing the installation"))
                
                if not self.customer_signature:
                    frappe.throw(_("Customer signature is required before completing the installation"))
    
    def calculate_summary(self):
        """Calculate summary statistics"""
        if not self.installed_items:
            self.total_items = 0
            self.installed_count = 0
            self.not_installed_count = 0
            self.completion_percentage = 0
            return
        
        self.total_items = len(self.installed_items)
        self.installed_count = len([item for item in self.installed_items if item.installed == 1])
        self.not_installed_count = self.total_items - self.installed_count
        
        if self.total_items > 0:
            self.completion_percentage = (self.installed_count / self.total_items) * 100
        else:
            self.completion_percentage = 0
    
    def create_warranty_records_automatically(self):
        """Create warranty records automatically when status becomes completed"""
        try:
            # Get Sales Order and Customer details
            sales_order = frappe.get_doc("Sales Order", self.sales_order)
            customer = frappe.get_doc("Customer", self.customer)
            
            warranty_created = 0
            warranty_skipped = 0
            
            for item in self.installed_items:
                if item.installed == 1:  # Only create warranty for installed items
                    # Check if warranty record already exists
                    existing_warranty = frappe.db.exists("Warranty Record", {
                        "serial_no": item.serial_no,
                        "installation_job": self.name
                    })
                    
                    if existing_warranty:
                        warranty_skipped += 1
                        continue
                    
                    # Create new warranty record
                    warranty_doc = frappe.new_doc("Warranty Record")
                    warranty_doc.serial_no = item.serial_no
                    warranty_doc.item = item.item
                    warranty_doc.item_name = item.item_name
                    warranty_doc.customer = self.customer
                    warranty_doc.customer_name = customer.customer_name
                    warranty_doc.sales_order = self.sales_order
                    warranty_doc.delivery_note = self.delivery_note
                    warranty_doc.installation_job = self.name
                    warranty_doc.start_date = self.installation_date or frappe.utils.today()
                    warranty_doc.warranty_period = 3  # Default 3 years
                    warranty_doc.warranty_type = "Standard"
                    warranty_doc.warranty_terms = "Standard warranty terms apply"
                    warranty_doc.status = "Active"
                    
                    # Calculate end date
                    warranty_doc.end_date = frappe.utils.add_years(warranty_doc.start_date, warranty_doc.warranty_period)
                    
                    warranty_doc.insert(ignore_permissions=True)
                    warranty_created += 1
                else:
                    warranty_skipped += 1
            
            if warranty_created > 0:
                frappe.msgprint(
                    _("Created {0} warranty records automatically").format(warranty_created),
                    title=_("Warranty Records Created"),
                    indicator="green"
                )
                
        except Exception as e:
            frappe.log_error(f"Error creating warranty records automatically: {str(e)}")
            # Don't throw error to prevent saving issues
    
    def on_update(self):
        """Handle status changes"""
        if self.has_value_changed("status"):
            self.handle_status_change()
    
    def handle_status_change(self):
        """Handle different status transitions"""
        if self.status == "In Progress":
            self.handle_start_installation()
        elif self.status in ["Completed - Full", "Completed - Partial"]:
            self.handle_complete_installation()
        elif self.status == "Verified":
            self.handle_ops_verification()
        elif self.status == "Closed":
            self.handle_job_closure()
    
    def handle_start_installation(self):
        """Handle when installer starts installation"""
        if not self.installation_date:
            self.installation_date = frappe.utils.today()
        
        frappe.msgprint(
            _("Installation job {0} has been started").format(self.name),
            title=_("Installation Started"),
            indicator="blue"
        )
    
    def handle_complete_installation(self):
        """Handle when installer completes installation"""
        self.validate_photos_and_signature()
        
        # Determine completion type based on installed items
        installed_count = len([item for item in self.installed_items if item.installed == 1])
        if installed_count == self.total_items:
            self.status = "Completed - Full"
        else:
            self.status = "Completed - Partial"
        
        frappe.msgprint(
            _("Installation job {0} completed - {1} of {2} items installed").format(
                self.name, installed_count, self.total_items
            ),
            title=_("Installation Completed"),
            indicator="green"
        )
    
    def handle_ops_verification(self):
        """Handle when operations verifies the job"""
        if not self.warranty_start_action:
            frappe.throw(_("Warranty Start Action is required when verifying the job"))
        
        frappe.msgprint(
            _("Installation job {0} has been verified by Operations").format(self.name),
            title=_("Job Verified"),
            indicator="green"
        )
        
        # Trigger warranty creation
        self.create_warranty_records()
    
    def handle_job_closure(self):
        """Handle when job is closed"""
        frappe.msgprint(
            _("Installation job {0} has been closed").format(self.name),
            title=_("Job Closed"),
            indicator="blue"
        )
    
    def create_warranty_records(self):
        """Create warranty records for installed items"""
        if self.warranty_start_action == "Delay":
            frappe.msgprint(
                _("Warranty creation delayed as per Operations decision"),
                title=_("Warranty Delayed"),
                indicator="orange"
            )
            return
        
        warranty_created = 0
        warranty_skipped = 0
        
        for item in self.installed_items:
            if item.installed == 1:
                # Create warranty record
                warranty_doc = frappe.new_doc("Warranty Record")
                warranty_doc.serial_no = item.serial_no
                warranty_doc.item = item.item
                warranty_doc.customer = self.customer
                warranty_doc.sales_order = self.sales_order
                warranty_doc.delivery_note = self.delivery_note
                warranty_doc.installation_job = self.name
                warranty_doc.start_date = self.installation_date or frappe.utils.today()
                
                # Calculate end date (assuming 3 years warranty)
                warranty_doc.end_date = frappe.utils.add_years(warranty_doc.start_date, 3)
                
                warranty_doc.insert(ignore_permissions=True)
                warranty_created += 1
            else:
                warranty_skipped += 1
        
        frappe.db.commit()
        
        frappe.msgprint(
            _("Created {0} warranty records, skipped {1} uninstalled items").format(
                warranty_created, warranty_skipped
            ),
            title=_("Warranty Records Created"),
            indicator="green"
        )


@frappe.whitelist()
def start_installation(installation_job):
    """Start installation - called by installer"""
    doc = frappe.get_doc("Installation Job", installation_job)
    
    if doc.status != "Scheduled":
        frappe.throw(_("Only scheduled installation jobs can be started"))
    
    doc.status = "In Progress"
    doc.installation_date = frappe.utils.today()
    doc.save()
    
    return {
        "success": True,
        "message": _("Installation job {0} started successfully").format(installation_job)
    }


@frappe.whitelist()
def create_warranty_records(installation_job):
    """Create warranty records for installed items automatically"""
    try:
        doc = frappe.get_doc("Installation Job", installation_job)
        
        if doc.status not in ["Completed - Full", "Completed - Partial"]:
            return {
                "success": False,
                "error": _("Warranty records can only be created for completed installation jobs")
            }
        
        # Get Sales Order and Customer details
        sales_order = frappe.get_doc("Sales Order", doc.sales_order)
        customer = frappe.get_doc("Customer", doc.customer)
        
        warranty_created = 0
        warranty_skipped = 0
        
        for item in doc.installed_items:
            if item.installed == 1:  # Only create warranty for installed items
                # Check if warranty record already exists
                existing_warranty = frappe.db.exists("Warranty Record", {
                    "serial_no": item.serial_no,
                    "installation_job": installation_job
                })
                
                if existing_warranty:
                    warranty_skipped += 1
                    continue
                
                # Create new warranty record
                warranty_doc = frappe.new_doc("Warranty Record")
                warranty_doc.serial_no = item.serial_no
                warranty_doc.item = item.item
                warranty_doc.item_name = item.item_name
                warranty_doc.customer = doc.customer
                warranty_doc.customer_name = customer.customer_name
                warranty_doc.sales_order = doc.sales_order
                warranty_doc.delivery_note = doc.delivery_note
                warranty_doc.installation_job = installation_job
                warranty_doc.start_date = doc.installation_date or frappe.utils.today()
                warranty_doc.warranty_period = 3  # Default 3 years
                warranty_doc.warranty_type = "Standard"
                warranty_doc.warranty_terms = "Standard warranty terms apply"
                warranty_doc.status = "Active"
                
                # Calculate end date
                warranty_doc.end_date = frappe.utils.add_years(warranty_doc.start_date, warranty_doc.warranty_period)
                
                warranty_doc.insert(ignore_permissions=True)
                warranty_created += 1
            else:
                warranty_skipped += 1
        
        frappe.db.commit()
        
        return {
            "success": True,
            "count": warranty_created,
            "message": _("Created {0} warranty records, skipped {1} uninstalled items").format(
                warranty_created, warranty_skipped
            )
        }
        
    except Exception as e:
        frappe.log_error(f"Error creating warranty records: {str(e)}")
        return {
            "success": False,
            "error": _("Error creating warranty records: {0}").format(str(e))
        }


@frappe.whitelist()
def complete_installation(installation_job, installer_notes=None):
    """Complete installation - called by installer"""
    doc = frappe.get_doc("Installation Job", installation_job)
    
    if doc.status not in ["In Progress", "Completed - Full", "Completed - Partial"]:
        frappe.throw(_("Only installation jobs with items being installed can be completed"))
    
    if installer_notes:
        doc.installer_notes = installer_notes
    
    # Set flag to indicate explicit completion (for validation)
    doc._explicitly_completing = True
    
    # Validate completion requirements
    doc.validate_photos_and_signature()
    
    # Set installation date if not already set
    if not doc.installation_date:
        doc.installation_date = frappe.utils.today()
    
    # Status should already be set by the frontend based on installation checkboxes
    # Just ensure it's in a completed state
    installed_count = len([item for item in doc.installed_items if item.installed == 1])
    if installed_count == doc.total_items:
        doc.status = "Completed - Full"
    else:
        doc.status = "Completed - Partial"
    
    doc.save()
    
    # Create warranty records for installed items
    warranty_result = create_warranty_records(installation_job)
    
    return {
        "success": True,
        "message": _("Installation job {0} completed successfully").format(installation_job),
        "warranty_created": warranty_result.get("count", 0) if warranty_result.get("success") else 0
    }


@frappe.whitelist()
def verify_installation(installation_job, ops_notes=None, warranty_action=None):
    """Verify installation - called by operations"""
    doc = frappe.get_doc("Installation Job", installation_job)
    
    if doc.status not in ["Completed - Full", "Completed - Partial"]:
        frappe.throw(_("Only completed installation jobs can be verified"))
    
    if ops_notes:
        doc.ops_verification_notes = ops_notes
    
    if warranty_action:
        doc.warranty_start_action = warranty_action
    
    doc.status = "Verified"
    doc.save()
    
    return {
        "success": True,
        "message": _("Installation job {0} verified successfully").format(installation_job)
    }


@frappe.whitelist()
def close_installation_job(installation_job):
    """Close installation job - called by operations"""
    doc = frappe.get_doc("Installation Job", installation_job)
    
    if doc.status != "Verified":
        frappe.throw(_("Only verified installation jobs can be closed"))
    
    doc.status = "Closed"
    doc.save()
    
    return {
        "success": True,
        "message": _("Installation job {0} closed successfully").format(installation_job)
    }
