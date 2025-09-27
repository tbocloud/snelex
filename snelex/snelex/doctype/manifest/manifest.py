# Copyright (c) 2025, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.naming import make_autoname
from frappe.model.document import Document

class Manifest(Document):
    def validate(self):
        self.generate_manifest_number()
        self.generate_job_card_number()
        
    def generate_manifest_number(self):
        """Generate Manifest Number Automatically"""
        if not self.manifest_number:
            if self.location:
                location = frappe.get_doc("Location", self.location)
                prefix = location.custom_location_code or "MNF"
                self.manifest_number = make_autoname(f"{prefix}-.#####")

    def generate_job_card_number(self):
        """Generate Job Card Number Automatically"""
        if not self.job_card_number:
            if self.location:
                location = frappe.get_doc("Location", self.location)
                prefix = location.custom_location_code or "JCN"
                self.job_card_number = make_autoname(f"#####.-{prefix}")

@frappe.whitelist()
def get_consignment_details(manifest_date,location):
	# "arguments are from manifest doctype"
	if manifest_date and location:
		consignment=frappe.get_all("Consignment Note",
		filters={
			"consignment_date":manifest_date,
			"consignment_to":location

		},
		fields=["name","consignment_date","consignee_customer","shipper","remarks"]
		)
		if consignment:
			return consignment
