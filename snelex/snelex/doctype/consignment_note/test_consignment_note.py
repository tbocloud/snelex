# Copyright (c) 2025, Snelex and Contributors
# See license.txt

import frappe
import unittest
from frappe.utils import today, add_days


class TestConsignmentNote(unittest.TestCase):
	def setUp(self):
		"""Set up test data"""
		self.create_test_location()
		self.create_test_supplier()
		self.create_test_customer()

	def create_test_location(self):
		"""Create test locations if they don't exist"""
		locations = [
			{"location_name": "Test Origin", "location_type": "Warehouse"},
			{"location_name": "Test Destination", "location_type": "Warehouse"}
		]
		
		for location_data in locations:
			if not frappe.db.exists("Location", location_data["location_name"]):
				location = frappe.get_doc({
					"doctype": "Location",
					"location_name": location_data["location_name"],
					"location_type": location_data["location_type"]
				})
				location.insert(ignore_permissions=True)

	def create_test_supplier(self):
		"""Create test supplier if it doesn't exist"""
		if not frappe.db.exists("Supplier", "Test Shipper Supplier"):
			supplier = frappe.get_doc({
				"doctype": "Supplier",
				"supplier_name": "Test Shipper Supplier",
				"supplier_group": "All Supplier Groups"
			})
			supplier.insert(ignore_permissions=True)

	def create_test_customer(self):
		"""Create test customer if it doesn't exist"""
		if not frappe.db.exists("Customer", "Test Consignee Customer"):
			customer = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": "Test Consignee Customer",
				"customer_group": "All Customer Groups",
				"territory": "All Territories"
			})
			customer.insert(ignore_permissions=True)

	def test_consignment_note_creation(self):
		"""Test basic consignment note creation"""
		consignment_note = frappe.get_doc({
			"doctype": "Consignment Note",
			"consignment_date": today(),
			"consignment_from": "Test Origin",
			"consignment_to": "Test Destination",
			"payment_by": "Shipper",
			"shipper_supplier": "Test Shipper Supplier",
			"number_of_cartons": 5,
			"number_of_pieces": 10,
			"description": "Test consignment"
		})
		
		consignment_note.insert()
		self.assertTrue(consignment_note.name)
		self.assertEqual(consignment_note.total_no_of_pieces, 15)

	def test_total_pieces_calculation(self):
		"""Test automatic calculation of total pieces"""
		consignment_note = frappe.get_doc({
			"doctype": "Consignment Note",
			"consignment_date": today(),
			"consignment_from": "Test Origin",
			"consignment_to": "Test Destination",
			"payment_by": "Shipper",
			"number_of_cartons": 2,
			"number_of_bundles": 3,
			"number_of_pieces": 5,
			"number_of_pallets": 1,
			"number_of_bags": 4
		})
		
		consignment_note.insert()
		# Total should be 2 + 3 + 5 + 1 + 4 = 15
		self.assertEqual(consignment_note.total_no_of_pieces, 15)

	def test_same_location_validation(self):
		"""Test validation for same from and to locations"""
		consignment_note = frappe.get_doc({
			"doctype": "Consignment Note",
			"consignment_date": today(),
			"consignment_from": "Test Origin",
			"consignment_to": "Test Origin",  # Same as from
			"payment_by": "Shipper",
			"number_of_cartons": 5
		})
		
		with self.assertRaises(frappe.ValidationError):
			consignment_note.insert()

	def test_payment_by_shipper_validation(self):
		"""Test validation when payment by shipper is selected"""
		consignment_note = frappe.get_doc({
			"doctype": "Consignment Note",
			"consignment_date": today(),
			"consignment_from": "Test Origin",
			"consignment_to": "Test Destination",
			"payment_by": "Shipper",
			# Missing shipper_supplier
			"number_of_cartons": 5
		})
		
		with self.assertRaises(frappe.ValidationError):
			consignment_note.insert()

	def test_payment_by_receiver_validation(self):
		"""Test validation when payment by receiver is selected"""
		consignment_note = frappe.get_doc({
			"doctype": "Consignment Note",
			"consignment_date": today(),
			"consignment_from": "Test Origin",
			"consignment_to": "Test Destination",
			"payment_by": "Receiver",
			# Missing consignee_customer
			"number_of_cartons": 5
		})
		
		with self.assertRaises(frappe.ValidationError):
			consignment_note.insert()

	def test_submission_validation(self):
		"""Test validation during submission"""
		consignment_note = frappe.get_doc({
			"doctype": "Consignment Note",
			"consignment_date": today(),
			"consignment_from": "Test Origin",
			"consignment_to": "Test Destination",
			"payment_by": "Shipper",
			"shipper_supplier": "Test Shipper Supplier",
			"number_of_cartons": 5,
			"description": "Test consignment"
		})
		
		consignment_note.insert()
		consignment_note.submit()
		
		self.assertEqual(consignment_note.docstatus, 1)

	def test_submission_without_shipment_details(self):
		"""Test submission fails without shipment details"""
		consignment_note = frappe.get_doc({
			"doctype": "Consignment Note",
			"consignment_date": today(),
			"consignment_from": "Test Origin",
			"consignment_to": "Test Destination",
			"payment_by": "Shipper",
			"shipper_supplier": "Test Shipper Supplier",
			# No shipment details
			"description": "Test consignment"
		})
		
		consignment_note.insert()
		
		with self.assertRaises(frappe.ValidationError):
			consignment_note.submit()

	def test_supplier_details_fetch(self):
		"""Test automatic fetching of supplier details"""
		consignment_note = frappe.get_doc({
			"doctype": "Consignment Note",
			"consignment_date": today(),
			"consignment_from": "Test Origin",
			"consignment_to": "Test Destination",
			"payment_by": "Shipper",
			"shipper_supplier": "Test Shipper Supplier",
			"number_of_cartons": 5
		})
		
		consignment_note.insert()
		self.assertEqual(consignment_note.shipper_display_name, "Test Shipper Supplier")

	def test_customer_details_fetch(self):
		"""Test automatic fetching of customer details"""
		consignment_note = frappe.get_doc({
			"doctype": "Consignment Note",
			"consignment_date": today(),
			"consignment_from": "Test Origin",
			"consignment_to": "Test Destination",
			"payment_by": "Receiver",
			"consignee_customer": "Test Consignee Customer",
			"number_of_cartons": 5
		})
		
		consignment_note.insert()
		self.assertEqual(consignment_note.consignee_display_name, "Test Consignee Customer")

	def tearDown(self):
		"""Clean up test data"""
		# Delete test consignment notes
		frappe.db.sql("DELETE FROM `tabConsignment Note` WHERE consignment_from = 'Test Origin'")
		frappe.db.commit()