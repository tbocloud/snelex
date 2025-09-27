// Copyright (c) 2025, Snelex and contributors
// For license information, please see license.txt

frappe.ui.form.on('Consignment Note', {
	refresh: function(frm) {

		// if (!frm.doc.consignment_date) {
		// 	frm.set_value('consignment_date', frappe.datetime.get_today());
		// }

		// Add custom buttons for submitted documents
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Print Consignment Note'), function() {
				frm.print_doc();
			});

			frm.add_custom_button(__('Email Consignment Note'), function() {
				frappe.route_options = {
					"dt": frm.doc.doctype,
					"dn": frm.doc.name
				};
				frappe.set_route("Form", "Email Queue", "new-email-queue-1");
			});

			// Add Create Job Card button
			frm.add_custom_button(__('Create Job Card'), function() {
				create_job_card_from_consignment_note(frm);
			}, __('Create'));
		}

		// Calculate total pieces on refresh
		calculate_total_pieces(frm);
	},
	consignment_from: function(frm) {
		// Validate that from and to locations are different
		if (frm.doc.consignment_from && frm.doc.consignment_to &&
			frm.doc.consignment_from === frm.doc.consignment_to) {
			frappe.msgprint(__('Consignment From and Consignment To cannot be the same location'));
			frm.set_value('consignment_from', '');
		}
	},

	consignment_to: function(frm) {
		// Validate that from and to locations are different
		if (frm.doc.consignment_from && frm.doc.consignment_to &&
			frm.doc.consignment_from === frm.doc.consignment_to) {
			frappe.msgprint(__('Consignment From and Consignment To cannot be the same location'));
			frm.set_value('consignment_to', '');
		}
	},

	shipper: function(frm) {
	    if (frm.doc.shipper) {
	        set_invoiced_to(frm)
	        frappe.call({
	            method: 'snelex.snelex.doctype.consignment_note.consignment_note.get_shipper_details',
	            args: { shipper: frm.doc.shipper },
	            callback: function(r) {
	                if (r.message) {
	                    frm.set_value('shipper_display_name', r.message.display_name);
	                    frm.set_value('shipper_address', r.message.address);
	                    frm.set_value('shipper_phone', r.message.phone);
	                    frm.set_value('shipper_fax', r.message.fax);
	                    frm.set_value('shipper_email', r.message.email);

	                    // if (frm.doc.payment_by == "Shipper") {
											//
										  //    frm.set_value('invoiced_to_display_name', r.message.display_name);
										  //    frm.set_value('invoiced_to_address', r.message.address);
										  //    frm.set_value('invoiced_to_phone', r.message.phone);
										  //    frm.set_value('invoiced_to_fax', r.message.fax);
										  //    frm.set_value('invoiced_to_email', r.message.email);
											//
	                    // }
	                }
	            }
	        });
	    } else {
	        frm.set_value('shipper_display_name', '');
	        frm.set_value('shipper_address', '');
	        frm.set_value('shipper_phone', '');
	        frm.set_value('shipper_fax', '');
	        frm.set_value('shipper_email', '');
	    }
	},

	consignee_customer: function(frm) {
	    if (frm.doc.consignee_customer) {
	        frappe.call({
	            method: 'snelex.snelex.doctype.consignment_note.consignment_note.get_customer_details',
	            args: { customer: frm.doc.consignee_customer },
	            callback: function(r) {
	                if (r.message) {
	                    frm.set_value('consignee_display_name', r.message.display_name);
	                    frm.set_value('consignee_address', r.message.address);
	                    frm.set_value('consignee_phone', r.message.phone);
	                    frm.set_value('consignee_email', r.message.email);
	                    frm.set_value('consignee_fax', r.message.fax);

											frm.set_value('delivery_contact_person', r.message.display_name);
											frm.set_value('name1', r.message.display_name);
											frm.set_value('delivery_address', r.message.address);
											frm.set_value('delivery_phone', r.message.phone);
											frm.set_value('delivery_email', r.message.email);
											frm.set_value('delivery_fax', r.message.fax);


	                    if (frm.doc.payment_by == "Receiver") {
	                        frm.set_value('invoiced_to', r.message.display_name);
	                        frm.set_value('invoiced_to_display_name', r.message.display_name);
	                        frm.set_value('invoiced_to_address', r.message.address);
	                        frm.set_value('invoiced_to_phone', r.message.phone);
	                        frm.set_value('invoiced_to_fax', r.message.fax);
	                        frm.set_value('invoiced_to_email', r.message.email);
	                    }
	                }
	            }
	        });
	    } else {
	        frm.set_value('consignee_display_name', '');
	        frm.set_value('consignee_address', '');
	        frm.set_value('consignee_phone', '');
	        frm.set_value('consignee_email', '');
	        frm.set_value('consignee_fax', '');
	        frm.set_value('consignee_web', '');
	    }
	},

	invoiced_to: function(frm) {
        if (frm.doc.invoiced_to) {
            frappe.call({
                method: "snelex.snelex.doctype.consignment_note.consignment_note.get_customer_details",
                args: {
                    customer: frm.doc.invoiced_to
                },
                callback: function(r) {
                    if (r.message) {
                        let d = r.message;
                        frm.set_value("invoiced_to_display_name", d.display_name);
                        frm.set_value("invoiced_to_address", d.address);
                        frm.set_value("invoiced_to_phone", d.phone);
                        frm.set_value("invoiced_to_fax", d.fax);
                        frm.set_value("invoiced_to_email", d.email);
                    }
                }
            });
        }
  },
	payment_by: function(frm) {
		if (frm.doc.payment_by === 'Shipper') {
			frm.set_df_property('shipper', 'reqd', 1);
			frm.set_df_property('consignee_customer', 'reqd', 0);
			set_invoiced_to_from_shipper(frm);
		} else if (frm.doc.payment_by === 'Receiver') {
			frm.set_df_property('shipper', 'reqd', 0);
			frm.set_df_property('consignee_customer', 'reqd', 1);
			set_invoiced_to_from_consignee(frm);
		} else {
			frm.set_df_property('shipper', 'reqd', 0);
			frm.set_df_property('consignee_customer', 'reqd', 0);
			// Clear invoiced to for 3rd party
			clear_invoiced_to_details(frm);
		}
	},

	// Calculate total pieces when any shipment detail changes
	number_of_cartons: function(frm) {
		calculate_total_pieces(frm);
	},

	number_of_bundles: function(frm) {
		calculate_total_pieces(frm);
	},

	number_of_pieces: function(frm) {
		calculate_total_pieces(frm);
	},

	number_of_pallets: function(frm) {
		calculate_total_pieces(frm);
	},

	number_of_bags: function(frm) {
		calculate_total_pieces(frm);
	},

	before_submit: function(frm) {
		// Validate mandatory fields before submission
		let mandatory_fields = [
			['consignment_date', 'Consignment Date'],
			['consignment_from', 'Consignment From'],
			['consignment_to', 'Consignment To'],
			['payment_by', 'Payment By']
		];

		let missing_fields = [];
		mandatory_fields.forEach(function(field) {
			if (!frm.doc[field[0]]) {
				missing_fields.push(field[1]);
			}
		});

		if (missing_fields.length > 0) {
			frappe.throw(__('Please fill the following mandatory fields: {0}', [missing_fields.join(', ')]));
		}

		// Validate at least one shipment detail
		if (!frm.doc.number_of_cartons && !frm.doc.number_of_bundles &&
			!frm.doc.number_of_pieces && !frm.doc.number_of_pallets && !frm.doc.number_of_bags) {
			frappe.throw(__('At least one shipment detail (Cartons, Bundles, Pieces, Pallets, or Bags) is required'));
		}

		// Validate payment by specific requirements
		if (frm.doc.payment_by === 'Shipper' && !frm.doc.shipper) {
			frappe.throw(__('Shipper (Supplier) is required when Payment By is Shipper'));
		}
		if (frm.doc.payment_by === 'Receiver' && !frm.doc.consignee_customer) {
			frappe.throw(__('Consignee (Customer) is required when Payment By is Receiver'));
		}
	},
	validate: function(frm) {
		set_invoiced_to(frm);
	}
});

function set_invoiced_to(frm){
	if (frm.doc.payment_by == "Shipper") {
			frm.set_value("invoiced_to", frm.doc.shipper);
			frm.set_value("invoiced_to_display_name", frm.doc.shipper);
	}
}

// Helper function to calculate total pieces
function calculate_total_pieces(frm) {
	let total = 0;

	if (frm.doc.number_of_cartons) {
		total += frm.doc.number_of_cartons;
	}
	if (frm.doc.number_of_bundles) {
		total += frm.doc.number_of_bundles;
	}
	if (frm.doc.number_of_pieces) {
		total += frm.doc.number_of_pieces;
	}
	if (frm.doc.number_of_pallets) {
		total += frm.doc.number_of_pallets;
	}
	if (frm.doc.number_of_bags) {
		total += frm.doc.number_of_bags;
	}

	frm.set_value('total_no_of_pieces', total);
}

// Helper function to set invoiced to from shipper details
function set_invoiced_to_from_shipper(frm) {
	if (frm.doc.shipper) {
		// Check if supplier has a linked customer
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Customer',
				filters: {'supplier': frm.doc.shipper},
				fieldname: 'name'
			},
			callback: function(r) {
				if (r.message && r.message.name) {
					frm.set_value('invoiced_to', r.message.name);
				} else {
					frm.set_value('invoiced_to', '');
				}
				// Set invoiced to details from shipper
				frm.set_value('invoiced_to_display_name', frm.doc.shipper_display_name);
				frm.set_value('invoiced_to_address', frm.doc.shipper_address);
				frm.set_value('invoiced_to_phone', frm.doc.shipper_phone);
				frm.set_value('invoiced_to_fax', frm.doc.shipper_fax);
				frm.set_value('invoiced_to_email', frm.doc.shipper_email);
				frm.set_value('invoiced_to_web', frm.doc.shipper_web);
			}
		});
	} else {
		clear_invoiced_to_details(frm);
	}
}

// Helper function to set invoiced to from consignee details
function set_invoiced_to_from_consignee(frm) {
	if (frm.doc.consignee_customer) {
		frm.set_value('invoiced_to', frm.doc.consignee_customer);
		frm.set_value('invoiced_to_display_name', frm.doc.consignee_display_name);
		frm.set_value('invoiced_to_address', frm.doc.consignee_address);
		frm.set_value('invoiced_to_phone', frm.doc.consignee_phone);
		frm.set_value('invoiced_to_fax', frm.doc.consignee_fax);
		frm.set_value('invoiced_to_email', frm.doc.consignee_email);
		frm.set_value('invoiced_to_web', frm.doc.consignee_web);
	} else {
		clear_invoiced_to_details(frm);
	}
}

// Helper function to clear invoiced to details
function clear_invoiced_to_details(frm) {
	frm.set_value('invoiced_to', '');
	frm.set_value('invoiced_to_display_name', '');
	frm.set_value('invoiced_to_address', '');
	frm.set_value('invoiced_to_phone', '');
	frm.set_value('invoiced_to_fax', '');
	frm.set_value('invoiced_to_email', '');
	frm.set_value('invoiced_to_web', '');
}

// Helper function to create job card from consignment note
function create_job_card_from_consignment_note(frm) {
	frappe.call({
		method: 'snelex.snelex.doctype.job_card.job_card.create_job_card_from_consignment_note',
		args: {
			consignment_note: frm.doc.name
		},
		callback: function(r) {
			if (r.message) {
				frappe.msgprint(__('Job Card {0} created successfully', [r.message]));
				frappe.set_route("Form", "Job Card", r.message);
			}
		}
	});
}

// Custom query for locations to show only active locations
frappe.ui.form.on('Consignment Note', {
	setup: function(frm) {
		// Filter locations to show only active ones
		// frm.set_query('consignment_from', function() {
		// 	return {
		// 		filters: {
		// 			'disabled': 0
		// 		}
		// 	};
		// });

		// frm.set_query('consignment_to', function() {
		// 	return {
		// 		filters: {
		// 			'disabled': 0
		// 		}
		// 	};
		// });

		// Filter suppliers to show only active ones
		// frm.set_query('shipper', function() {
		// 	return {
		// 		filters: {
		// 			'disabled': 0
		// 		}
		// 	};
		// });

		// Filter customers to show only active ones
		// frm.set_query('consignee_customer', function() {
		// 	return {
		// 		filters: {
		// 			'disabled': 0
		// 		}
		// 	};
		// });
	}
});
