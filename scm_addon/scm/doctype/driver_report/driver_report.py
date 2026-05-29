# Copyright (c) 2026, VAPTECH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta


class DriverReport(Document):
	"""Driver Report DocType for tracking driver performance metrics"""

	def before_save(self):
		"""Calculate driver metrics before saving"""
		self.update_driver_metrics()

	def update_driver_metrics(self):
		"""Update trips, deliveries, and distance metrics for the driver using raw SQL."""
		if not self.driver:
			return

		# Get the driver's full name (via fetch_from in JSON, but set explicitly for safety)
		driver_full = frappe.db.get_value("Driver", self.driver, "full_name")
		self.driver_name = driver_full or self.driver

		# Get the most recent vehicle used by this driver
		last_vehicle = frappe.db.get_value(
			"Delivery Trip",
			filters={"driver": self.driver, "docstatus": ["!=", 2]},
			fieldname="vehicle",
			order_by="creation desc"
		)
		self.vehicle = last_vehicle

		# ---- Trips ----
		trip_data = frappe.db.sql("""
			SELECT
				COUNT(*)                                  AS total_trips,
				SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed_trips
			FROM `tabDelivery Trip`
			WHERE driver = %s
			  AND docstatus != 2
		""", self.driver, as_dict=True)

		total_trips      = trip_data[0].total_trips or 0
		completed_trips  = trip_data[0].completed_trips or 0

		# ---- Deliveries & distance from Delivery Stop (child of Delivery Trip) ----
		stop_data = frappe.db.sql("""
			SELECT
				COUNT(DISTINCT ds.delivery_note)                                AS total_deliveries,
				COUNT(DISTINCT CASE WHEN dn.docstatus = 1 THEN dn.name END)    AS completed_deliveries,
				COALESCE(SUM(ds.distance), 0)                                    AS total_distance
			FROM `tabDelivery Stop` ds
			INNER JOIN `tabDelivery Trip` dt ON dt.name = ds.parent AND ds.parenttype = 'Delivery Trip'
			LEFT JOIN `tabDelivery Note` dn ON dn.name = ds.delivery_note
			WHERE dt.driver = %s
			  AND dt.docstatus != 2
			  AND ds.delivery_note IS NOT NULL
			  AND ds.delivery_note != ''
		""", self.driver, as_dict=True)

		delivery_count           = stop_data[0].total_deliveries or 0
		completed_delivery_count = stop_data[0].completed_deliveries or 0
		total_distance           = stop_data[0].total_distance or 0

		# Update fields
		self.trips                = total_trips
		self.completed_trips       = completed_trips
		self.deliveries            = delivery_count
		self.completed_deliveries  = completed_delivery_count
		self.distance_covered      = round(total_distance, 2)


@frappe.whitelist()
def get_driver_metrics(driver):
	"""Get metrics for a specific driver"""
	if not driver:
		return None

	doc = frappe.new_doc("Driver Report")
	doc.driver = driver
	doc.update_driver_metrics()

	return {
		"driver": doc.driver,
		"trips": doc.trips,
		"completed_trips": doc.completed_trips,
		"deliveries": doc.deliveries,
		"completed_deliveries": doc.completed_deliveries,
		"distance_covered": doc.distance_covered
	}


@frappe.whitelist()
def refresh_all_driver_reports():
	"""Generate/refresh driver reports for all active drivers"""
	# Get all active Driver records from the system
	drivers = frappe.get_list(
		"Driver",
		filters={
			"status": "Active",
		},
		fields=["name", "full_name"]
	)

	# If no drivers with Active status, get all drivers
	if not drivers:
		drivers = frappe.get_list(
			"Driver",
			fields=["name", "full_name"]
		)

	created_count = 0
	updated_count = 0

	for driver in drivers:
		driver_name = driver.get("name")

		# Check if driver report already exists
		existing = frappe.db.exists("Driver Report", {"driver": driver_name})

		if existing:
			# Update existing report
			doc = frappe.get_doc("Driver Report", existing)
		else:
			# Create new report
			doc = frappe.new_doc("Driver Report")
			doc.driver = driver_name
			created_count += 1

		# Always calculate and update metrics
		doc.update_driver_metrics()
		doc.save()
		updated_count += 1

	return {
		"message": f"Driver reports updated. Created: {created_count}, Updated: {updated_count}",
		"created": created_count,
		"updated": updated_count
	}


def update_driver_report(driver):
	"""Update or create driver report for a specific driver - called on Delivery Trip changes"""
	if not driver:
		return

	# Check if driver report exists
	existing = frappe.db.exists("Driver Report", {"driver": driver})

	if existing:
		# Update existing report
		doc = frappe.get_doc("Driver Report", existing)
	else:
		# Create new report if it doesn't exist
		doc = frappe.new_doc("Driver Report")
		doc.driver = driver

	# Calculate and update metrics
	doc.update_driver_metrics()
	doc.save(ignore_permissions=True)


def update_driver_report_on_trip_change(doc, method):
	"""Hook function called when Delivery Trip is created, updated, or submitted"""
	if doc.driver:
		update_driver_report(doc.driver)


def ensure_all_drivers_initialized():
	"""Ensure all Driver records have Driver Report records.
	Called during installation/migration to bootstrap the system."""

	# Get all Driver records from the system
	all_drivers = frappe.get_list(
		"Driver",
		fields=["name"],
		pluck="name"
	)

	for driver in all_drivers:
		try:
			# Check if report already exists
			existing = frappe.db.get_value(
				"Driver Report",
				{"driver": driver},
				"name"
			)

			if not existing:
				# Create record for this driver (metrics will be calculated by update_driver_metrics)
				doc = frappe.new_doc("Driver Report")
				doc.driver = driver
				doc.trips = 0
				doc.completed_trips = 0
				doc.deliveries = 0
				doc.completed_deliveries = 0
				doc.distance_covered = 0.0
				doc.insert(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(f"Error initializing Driver Report for {driver}: {str(e)}")
