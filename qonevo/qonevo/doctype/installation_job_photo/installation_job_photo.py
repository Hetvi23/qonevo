# Copyright (c) 2025, Qonevo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class InstallationJobPhoto(Document):
    def validate(self):
        """Validate Installation Job Photo data"""
        if not self.taken_date:
            self.taken_date = frappe.utils.today()
