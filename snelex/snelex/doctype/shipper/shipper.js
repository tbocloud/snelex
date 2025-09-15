// Copyright (c) 2025, sammish and contributors
// For license information, please see license.txt

frappe.ui.form.on("Shipper", {
  setup: function (frm) {
    frm.set_query("address", function (doc) {
      return {
        filters: {
          link_doctype: "Shipper",
          link_name: doc.name,
        },
      };
    });
  },
  address: function (frm) {
    if (frm.doc.address) {
      frappe.call({
        method: "frappe.contacts.doctype.address.address.get_address_display",
        args: {
          address_dict: frm.doc.address,
        },
        callback: function (r) {
          frm.set_value("primary_address", r.message);
        },
      });
    }
    if (!frm.doc.address) {
      frm.set_value("primary_address", "");
    }
  },
});
