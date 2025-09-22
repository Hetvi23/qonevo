# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class InstallationJobItem(Document):
    def validate(self):
        """Validate Installation Job Item data"""
        if self.installed == 1:
            self.installation_status = "Installed"
            self.not_installed_reason = None
        elif self.installed == 0:
            self.installation_status = "Not Installed"
            if not self.not_installed_reason:
                frappe.throw(_("Reason is required when item is not installed"))
        else:
            self.installation_status = "Pending"
