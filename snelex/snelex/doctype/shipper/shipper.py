# Copyright (c) 2025, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Shipper(Document):
    def validate(self):
        self.create_customer()

    def create_customer(self):
        if not frappe.db.exists("Customer", {"customer_name": self.name}):
            customer_doc = frappe.new_doc("Customer")
            customer_doc.customer_name = self.name
            customer_doc.customer_type = "Individual"

            address_name = frappe.db.get_value(
                "Dynamic Link",
                {"link_doctype": "Shipper", "link_name": self.name, "parenttype": "Address"},
                "parent"
            )
            if address_name:
                mobile_no = frappe.db.get_value("Address", address_name, "phone")
                if mobile_no:
                    customer_doc.mobile_no = mobile_no

            customer_doc.insert(ignore_permissions=True)
