app_name = "scm_addon"
app_title = "SCM-ERPNEXT"
app_publisher = "VAPTECH"
app_description = "scm custom app for erpnext"
app_email = "vaptech.kenya@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "scm_addon",
		"logo": "/assets/scm_addon/logo.png",
		"title": "SCM-ERPNEXT",
		"route": "/app/scm"
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
    "/assets/scm_addon/css/scm_addon.css",
    "/assets/scm_addon/css/customer_visit_map.css",
    "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
]
app_include_js = [
    "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
    "/assets/scm_addon/js/customer_visit_map.js"
]

# include js, css files in header of web template
# web_include_css = "/assets/scm_addon/css/scm_addon.css"
# web_include_js = "/assets/scm_addon/js/scm_addon.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "scm_addon/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}


# include js in doctype views
doctype_js = {
	"Customer Visit": "public/js/customer_visit.js"
}

doctype_list_js = {
	"Customer Visit": "public/js/customer_visit_list.js",
	"Sales By Rep": "public/js/sales_by_rep_list.js"
}# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "scm_addon/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "scm_addon.utils.jinja_methods",
# 	"filters": "scm_addon.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "scm_addon.install.before_install"
after_install = "scm_addon.install.after_install"
after_migrate = "scm_addon.install.after_migrate"
fixtures = [
    {"dt": "Dashboard Chart", "filters": [["module", "=", "SCM"]]},
    {"dt": "Workspace", "filters": [["module", "=", "SCM"]]},
    {"dt": "Module Onboarding", "filters": [["module", "=", "SCM"]]},
    {"dt": "Onboarding Step", "filters": [["name", "in", [
        "Create Route Plan", "Create Activity Type",
        "Assign Territories", "Manage Sales Rep Routes"
    ]]]},
]

# Uninstallation
# ------------

# before_uninstall = "scm_addon.uninstall.before_uninstall"
# after_uninstall = "scm_addon.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "scm_addon.utils.before_app_install"
# after_app_install = "scm_addon.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "scm_addon.utils.before_app_uninstall"
# after_app_uninstall = "scm_addon.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "scm_addon.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Customer Visit": {
        "on_submit": "scm_addon.scm.doctype.customer_visit.customer_visit.update_sales_by_rep",
        "on_cancel": "scm_addon.scm.doctype.customer_visit.customer_visit.update_sales_by_rep"
    },
    "Sales Order": {
        "before_validate": "scm_addon.scm.doctype.customer_visit.customer_visit.set_sales_order_defaults"
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"all": [
		"scm_addon.scm.doctype.customer_visit.customer_visit.refresh_all_sales_by_rep"
	],
	"daily": [
		"scm_addon.scm.doctype.customer_visit.customer_visit.refresh_all_sales_by_rep"
	],
}

# Testing
# -------

# before_tests = "scm_addon.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "scm_addon.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "scm_addon.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["scm_addon.utils.before_request"]
# after_request = ["scm_addon.utils.after_request"]

# Job Events
# ----------
# before_job = ["scm_addon.utils.before_job"]
# after_job = ["scm_addon.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"scm_addon.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

