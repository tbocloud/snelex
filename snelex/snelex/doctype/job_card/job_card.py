# Copyright (c) 2025, Snelex and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class JobCard(Document):
	def validate(self):
		"""Validate the job card before saving"""
		self.validate_consignment_note()
		self.fetch_consignment_details()
		self.set_default_values()

	def validate_consignment_note(self):
		"""Validate that consignment note exists and is submitted"""
		if self.consignment_note:
			cn_doc = frappe.get_doc("Consignment Note", self.consignment_note)
			if cn_doc.docstatus != 1:
				frappe.throw("Job Card can only be created from submitted Consignment Notes")

	def fetch_consignment_details(self):
		"""Fetch details from the linked consignment note"""
		if self.consignment_note:
			cn_doc = frappe.get_doc("Consignment Note", self.consignment_note)
			
			# Basic details
			self.consignment_from = cn_doc.consignment_from
			self.consignment_to = cn_doc.consignment_to
			self.payment_by = cn_doc.payment_by
			self.tracking_no = cn_doc.tracking_no
			
			# Shipper information
			self.shipper_name = cn_doc.shipper_display_name
			self.shipper_contact = cn_doc.shipper_display_name
			self.shipper_phone = cn_doc.shipper_phone
			self.shipper_email = cn_doc.shipper_email
			
			# Consignee information
			self.consignee_name = cn_doc.consignee_display_name
			self.consignee_contact = cn_doc.consignee_display_name
			self.consignee_phone = cn_doc.consignee_phone
			self.consignee_email = cn_doc.consignee_email
			
			# Shipment summary
			self.total_pieces = cn_doc.total_no_of_pieces
			self.total_weight = cn_doc.total_weight_lbs
			self.number_of_cartons = cn_doc.number_of_cartons
			self.number_of_bundles = cn_doc.number_of_bundles
			
			# Copy description as job description
			if cn_doc.description:
				self.job_description = cn_doc.description

	def set_default_values(self):
		"""Set default values for new job cards"""
		if not self.job_date:
			self.job_date = today()
		
		if not self.job_status:
			self.job_status = "Open"
		
		if not self.advance_status:
			self.advance_status = "Open"

	def on_submit(self):
		"""Actions to perform when job card is submitted"""
		self.validate_mandatory_fields_for_submission()
		self.update_status()

	def validate_mandatory_fields_for_submission(self):
		"""Validate mandatory fields required for submission"""
		mandatory_fields = [
			("job_date", "Job Date"),
			("consignment_note", "Consignment Note"),
			("job_status", "Job Status")
		]
		
		for field, label in mandatory_fields:
			if not self.get(field):
				frappe.throw(f"{label} is mandatory for submission")

	def update_status(self):
		"""Update status when submitted"""
		if self.job_status == "Open":
			self.job_status = "In Progress"

	def on_cancel(self):
		"""Actions to perform when job card is cancelled"""
		self.job_status = "Cancelled"

	def before_save(self):
		"""Actions before saving the document"""
		# Update actual delivery date when status is completed
		if self.job_status == "Completed" and not self.actual_delivery_date:
			self.actual_delivery_date = today()


@frappe.whitelist()
def create_job_card_from_consignment_note(consignment_note):
	"""Create a new job card from a consignment note"""
	if not consignment_note:
		frappe.throw("Consignment Note is required")
	
	# Check if consignment note is submitted
	cn_doc = frappe.get_doc("Consignment Note", consignment_note)
	if cn_doc.docstatus != 1:
		frappe.throw("Job Card can only be created from submitted Consignment Notes")
	
	# Check if job card already exists for this consignment note
	existing_job_card = frappe.db.get_value("Job Card", {"consignment_note": consignment_note}, "name")
	if existing_job_card:
		frappe.throw(f"Job Card {existing_job_card} already exists for this Consignment Note")
	
	# Create new job card
	job_card = frappe.get_doc({
		"doctype": "Job Card",
		"consignment_note": consignment_note,
		"job_date": today(),
		"job_status": "Open",
		"advance_status": "Open"
	})
	
	job_card.insert()
	frappe.db.commit()
	
	return job_card.name

@frappe.whitelist()
def get_consignment_note_details(consignment_note):
	"""Get consignment note details for job card creation"""
	if not consignment_note:
		return {}
	
	cn_doc = frappe.get_doc("Consignment Note", consignment_note)
	
	return {
		"consignment_from": cn_doc.consignment_from,
		"consignment_to": cn_doc.consignment_to,
		"payment_by": cn_doc.payment_by,
		"tracking_no": cn_doc.tracking_no,
		"shipper_name": cn_doc.shipper_display_name,
		"shipper_phone": cn_doc.shipper_phone,
		"shipper_email": cn_doc.shipper_email,
		"consignee_name": cn_doc.consignee_display_name,
		"consignee_phone": cn_doc.consignee_phone,
		"consignee_email": cn_doc.consignee_email,
		"total_pieces": cn_doc.total_no_of_pieces,
		"total_weight": cn_doc.total_weight_lbs,
		"number_of_cartons": cn_doc.number_of_cartons,
		"number_of_bundles": cn_doc.number_of_bundles,
		"job_description": cn_doc.description
	}