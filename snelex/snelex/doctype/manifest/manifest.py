# Copyright (c) 2025, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Manifest(Document):
	pass
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


