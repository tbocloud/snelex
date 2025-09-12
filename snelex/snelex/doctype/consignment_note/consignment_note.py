# Copyright (c) 2025, Snelex and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class ConsignmentNote(Document):
	def validate(self):
		"""Validate the consignment note before saving"""
		self.validate_locations()
		self.calculate_total_pieces()
		self.validate_payment_details()
		self.fetch_supplier_details()
		self.fetch_customer_details()
		self.set_invoiced_to()

	def validate_locations(self):
		"""Validate that consignment from and to are different"""
		if self.consignment_from == self.consignment_to:
			frappe.throw("Consignment From and Consignment To cannot be the same location")

	def calculate_total_pieces(self):
		"""Calculate total number of pieces from all shipment details"""
		total = 0
		if self.number_of_cartons:
			total += self.number_of_cartons
		if self.number_of_bundles:
			total += self.number_of_bundles
		if self.number_of_pieces:
			total += self.number_of_pieces
		if self.number_of_pallets:
			total += self.number_of_pallets
		if self.number_of_bags:
			total += self.number_of_bags

		self.total_no_of_pieces = total

	def validate_payment_details(self):
		"""Validate payment by selection"""
		if not self.payment_by:
			frappe.throw("Payment By is mandatory")

		# Validate based on payment type
		if self.payment_by == "Shipper" and not self.shipper_supplier:
			frappe.throw("Shipper (Supplier) is required when Payment By is Shipper")
		elif self.payment_by == "Receiver" and not self.consignee_customer:
			frappe.throw("Consignee (Customer) is required when Payment By is Receiver")

	def fetch_supplier_details(self):
		"""Fetch supplier details when shipper supplier is selected"""
		if self.shipper_supplier and not self.shipper_display_name:
			supplier = frappe.get_doc("Supplier", self.shipper_supplier)
			self.shipper_display_name = supplier.supplier_name

			# Fetch primary address
			address = frappe.db.get_value("Dynamic Link",
				{"link_doctype": "Supplier", "link_name": self.shipper_supplier, "parenttype": "Address"},
				"parent")

			if address:
				address_doc = frappe.get_doc("Address", address)
				self.shipper_address = address_doc.get_display()

			# Fetch primary contact
			contact = frappe.db.get_value("Dynamic Link",
				{"link_doctype": "Supplier", "link_name": self.shipper_supplier, "parenttype": "Contact"},
				"parent")

			if contact:
				contact_doc = frappe.get_doc("Contact", contact)
				self.shipper_phone = contact_doc.phone
				self.shipper_email = contact_doc.email_id

	def fetch_customer_details(self):
		"""Fetch customer details when consignee customer is selected"""
		if self.consignee_customer and not self.consignee_display_name:
			customer = frappe.get_doc("Customer", self.consignee_customer)
			self.consignee_display_name = customer.customer_name

			# Fetch primary address
			address = frappe.db.get_value("Dynamic Link",
				{"link_doctype": "Customer", "link_name": self.consignee_customer, "parenttype": "Address"},
				"parent")

			if address:
				address_doc = frappe.get_doc("Address", address)
				self.consignee_address = address_doc.get_display()

			# Fetch primary contact
			contact = frappe.db.get_value("Dynamic Link",
				{"link_doctype": "Customer", "link_name": self.consignee_customer, "parenttype": "Contact"},
				"parent")

			if contact:
				contact_doc = frappe.get_doc("Contact", contact)
				self.consignee_phone = contact_doc.phone
				self.consignee_email = contact_doc.email_id

	def set_invoiced_to(self):
		"""Set invoiced to based on payment by selection"""
		if self.payment_by == "Shipper":
			# Convert shipper supplier to customer if exists, otherwise use shipper details
			if self.shipper_supplier:
				# Check if supplier has a linked customer
				customer = frappe.db.get_value("Customer", {"name": self.shipper_supplier}, "name")
				if customer:
					self.invoiced_to = customer
				else:
					# Create customer from supplier if needed or use shipper details
					self.invoiced_to = ""
				self.set_invoiced_to_details_from_shipper()
		elif self.payment_by == "Receiver":
			# Use consignee customer details
			if self.consignee_customer:
				self.invoiced_to = self.consignee_customer
				self.set_invoiced_to_details_from_consignee()
		else:  # 3rd Party
			# Clear invoiced to - will be filled manually
			self.clear_invoiced_to_details()

	def set_invoiced_to_details_from_shipper(self):
		"""Set invoiced to details from shipper information"""
		self.invoiced_to_display_name = self.shipper_display_name
		self.invoiced_to_address = self.shipper_address
		self.invoiced_to_phone = self.shipper_phone
		self.invoiced_to_fax = self.shipper_fax
		self.invoiced_to_email = self.shipper_email
		self.invoiced_to_web = self.shipper_web

	def set_invoiced_to_details_from_consignee(self):
		"""Set invoiced to details from consignee information"""
		self.invoiced_to_display_name = self.consignee_display_name
		self.invoiced_to_address = self.consignee_address
		self.invoiced_to_phone = self.consignee_phone
		self.invoiced_to_fax = self.consignee_fax
		self.invoiced_to_email = self.consignee_email
		self.invoiced_to_web = self.consignee_web

	def clear_invoiced_to_details(self):
		"""Clear invoiced to details for 3rd party payment"""
		self.invoiced_to = ""
		self.invoiced_to_display_name = ""
		self.invoiced_to_address = ""
		self.invoiced_to_phone = ""
		self.invoiced_to_fax = ""
		self.invoiced_to_email = ""
		self.invoiced_to_web = ""

	def on_submit(self):
		"""Actions to perform when consignment note is submitted"""
		self.validate_mandatory_fields_for_submission()
		self.update_status()

	def validate_mandatory_fields_for_submission(self):
		"""Validate mandatory fields required for submission"""
		mandatory_fields = [
			("consignment_date", "Consignment Date"),
			("consignment_from", "Consignment From"),
			("consignment_to", "Consignment To"),
			("payment_by", "Payment By")
		]

		for field, label in mandatory_fields:
			if not self.get(field):
				frappe.throw(f"{label} is mandatory for submission")

		# Validate at least one shipment detail is provided
		if not any([self.number_of_cartons, self.number_of_bundles,
				   self.number_of_pieces, self.number_of_pallets, self.number_of_bags]):
			frappe.throw("At least one shipment detail (Cartons, Bundles, Pieces, Pallets, or Bags) is required")

	def update_status(self):
		"""Update status when submitted"""
		frappe.db.set_value("Consignment Note", self.name, "status", "Submitted")

	def on_cancel(self):
		"""Actions to perform when consignment note is cancelled"""
		frappe.db.set_value("Consignment Note", self.name, "status", "Cancelled")

	def get_location_details(self, location):
		"""Get location details for display"""
		if location:
			location_doc = frappe.get_doc("Location", location)
			return {
				"location_name": location_doc.location_name,
				"address": location_doc.get("address_line_1", ""),
				"city": location_doc.get("city", ""),
				"country": location_doc.get("country", "")
			}
		return {}

@frappe.whitelist()
def get_supplier_details(supplier):
	"""Get supplier details for client-side population"""
	if not supplier:
		return {}

	supplier_doc = frappe.get_doc("Supplier", supplier)
	details = {
		"display_name": supplier_doc.supplier_name,
		"phone": "",
		"email": "",
		"address": ""
	}

	# Get primary address
	address = frappe.db.get_value("Dynamic Link",
		{"link_doctype": "Supplier", "link_name": supplier, "parenttype": "Address"},
		"parent")

	if address:
		address_doc = frappe.get_doc("Address", address)
		details["address"] = address_doc.get_display()

	# Get primary contact
	contact = frappe.db.get_value("Dynamic Link",
		{"link_doctype": "Supplier", "link_name": supplier, "parenttype": "Contact"},
		"parent")

	if contact:
		contact_doc = frappe.get_doc("Contact", contact)
		details["phone"] = contact_doc.phone or ""
		details["email"] = contact_doc.email_id or ""

	return details

@frappe.whitelist()
def get_customer_details(customer):
	"""Get customer details for client-side population"""
	if not customer:
		return {}

	customer_doc = frappe.get_doc("Customer", customer)
	details = {
		"display_name": customer_doc.customer_name,
		"phone": "",
		"email": "",
		"address": ""
	}

	# Get primary address
	address = frappe.db.get_value("Dynamic Link",
		{"link_doctype": "Customer", "link_name": customer, "parenttype": "Address"},
		"parent")

	if address:
		address_doc = frappe.get_doc("Address", address)
		details["address"] = address_doc.get_display()

	# Get primary contact
	contact = frappe.db.get_value("Dynamic Link",
		{"link_doctype": "Customer", "link_name": customer, "parenttype": "Contact"},
		"parent")

	if contact:
		contact_doc = frappe.get_doc("Contact", contact)
		details["phone"] = contact_doc.phone or ""
		details["email"] = contact_doc.email_id or ""

	return details
