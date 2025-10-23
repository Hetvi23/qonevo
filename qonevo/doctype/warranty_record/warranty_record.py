# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class WarrantyRecord(Document):
    def validate(self):
        """Validate Warranty Record data"""
        self.validate_dates()
        self.calculate_end_date()
        self.check_warranty_status()
    
    def validate_dates(self):
        """Validate start and end dates"""
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                frappe.throw(_("End date must be after start date"))
    
    def calculate_end_date(self):
        """Calculate end date based on start date and warranty period"""
        if self.start_date and self.warranty_period:
            self.end_date = frappe.utils.add_years(self.start_date, self.warranty_period)
    
    def check_warranty_status(self):
        """Check and update warranty status based on dates"""
        if self.end_date:
            today = frappe.utils.today()
            if self.end_date < today:
                self.status = "Expired"
            elif self.status == "Expired" and self.end_date >= today:
                self.status = "Active"
    
    def on_update(self):
        """Handle status changes"""
        if self.has_value_changed("status"):
            self.handle_status_change()
    
    def handle_status_change(self):
        """Handle warranty status changes"""
        if self.status == "Expired":
            frappe.msgprint(
                _("Warranty {0} has expired").format(self.name),
                title=_("Warranty Expired"),
                indicator="orange"
            )
        elif self.status == "Cancelled":
            frappe.msgprint(
                _("Warranty {0} has been cancelled").format(self.name),
                title=_("Warranty Cancelled"),
                indicator="red"
            )


@frappe.whitelist()
def get_warranty_status(serial_no):
    """Get warranty status for a serial number"""
    warranty = frappe.get_value("Warranty Record", 
                               {"serial_no": serial_no, "status": "Active"}, 
                               ["name", "start_date", "end_date", "status"])
    
    if warranty:
        return {
            "has_warranty": True,
            "warranty_name": warranty[0],
            "start_date": warranty[1],
            "end_date": warranty[2],
            "status": warranty[3]
        }
    else:
        return {
            "has_warranty": False
        }


@frappe.whitelist()
def extend_warranty(warranty_record, additional_years):
    """Extend warranty period"""
    doc = frappe.get_doc("Warranty Record", warranty_record)
    
    if doc.status != "Active":
        frappe.throw(_("Only active warranties can be extended"))
    
    doc.warranty_period += int(additional_years)
    doc.calculate_end_date()
    doc.save()
    
    return {
        "success": True,
        "message": _("Warranty {0} extended by {1} years").format(warranty_record, additional_years)
    }







