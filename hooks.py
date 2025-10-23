# Copyright (c) 2024, Qonevo and Contributors
# License: GNU General Public License v3. See license.txt

from . import __version__ as app_version

app_name = "qonevo"
app_title = "Qonevo"
app_publisher = "Qonevo"
app_description = "Custom HR and Payroll enhancements"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "admin@qonevo.com"
app_license = "GNU General Public License v3"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/qonevo/css/qonevo.css"
app_include_js = [
    "/assets/qonevo/js/clean_barcode_scanner.js"
]


fixtures = [
    "Custom Field",
	"Property Setter"
]

# include js, css files in header of web template
# web_include_css = "/assets/qonevo/css/qonevo.css"
# web_include_js = "/assets/qonevo/js/qonevo.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "qonevo/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Delivery Note" : "qonevo/public/js/delivery_note.js",
    "Purchase Receipt" : "qonevo/doctype/purchase_receipt/purchase_receipt.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "qonevo.utils.jinja_methods",
#	"filters": "qonevo.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "qonevo.install.before_install"
after_install = "qonevo.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "qonevo.uninstall.before_uninstall"
# after_uninstall = "qonevo.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "qonevo.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"Employee": "qonevo.qonevo.doctype.employee.employee.Employee"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Employee": {
		"validate": "qonevo.qonevo.doctype.employee.employee.validate_ctc_salary_structure"
	},
	"Serial No": {
		"after_insert": "qonevo.serial_no_after_insert.after_insert",
		"on_update": "qonevo.serial_number_handlers.on_update",
		"after_update": "qonevo.serial_number_handlers.after_update",
		"before_save": "qonevo.serial_number_handlers.before_save"
	},
	"Serial and Batch Bundle": {
		"after_insert": "qonevo.stock_entry_hooks.serial_bundle_after_insert"
	},
	"Stock Entry": {
		"on_cancel": "qonevo.stock_entry_hooks.stock_entry_on_cancel"
	},
	"Delivery Note": {
		"before_save": "qonevo.delivery_note_hooks.delivery_note_on_load",
		"validate": "qonevo.delivery_note_hooks.delivery_note_validate",
		"on_submit": "qonevo.installation_job_hooks.delivery_note_on_submit",
		"on_cancel": "qonevo.installation_job_hooks.delivery_note_on_cancel"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"qonevo.tasks.all"
#	],
#	"daily": [
#		"qonevo.tasks.daily"
#	],
#	"hourly": [
#		"qonevo.tasks.hourly"
#	],
#	"weekly": [
#		"qonevo.tasks.weekly"
#	]
#	"monthly": [
#		"qonevo.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "qonevo.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "qonevo.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "qonevo.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"qonevo.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []





