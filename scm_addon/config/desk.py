from frappe import _

def get_data():
	return [
		{
			"label": _("SCM"),
			"icon": "octicon octicon-organization",
			"items": [
				{
					"type": "doctype",
					"name": "Route Plan",
					"label": _("Route Plan"),
					"description": _("Manage route plans"),
				},
				{
					"type": "doctype",
					"name": "Territory",
					"label": _("Territory"),
					"description": _("Manage territories"),
				},
				{
					"type": "doctype",
					"name": "Sales Person",
					"label": _("Sales Person"),
					"description": _("Manage sales persons"),
				},
			]
		}
	]