# Copyright (c) 2025, Qonevo and contributors
# License: MIT. See LICENSE

import frappe
from frappe import _
from frappe.model.document import Document


class DeliveryTrackingDashboard(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.desk.doctype.dashboard_chart_link.dashboard_chart_link import DashboardChartLink
        from frappe.desk.doctype.number_card_link.number_card_link import NumberCardLink
        from frappe.types import DF

        cards: DF.Table[NumberCardLink]
        chart_options: DF.Code | None
        charts: DF.Table[DashboardChartLink]
        dashboard_name: DF.Data
        is_default: DF.Check
        is_standard: DF.Check
        module: DF.Link | None

    # end: auto-generated types

    def on_update(self):
        if self.is_default:
            # make all other dashboards non-default
            frappe.db.sql(
                "update `tabDelivery Tracking Dashboard` set is_default = 0 where name != %s",
                self.name,
            ) 