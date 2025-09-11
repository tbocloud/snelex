// Copyright (c) 2025, Snelex and contributors
// For license information, please see license.txt

frappe.ui.form.on('Job Card', {
	refresh: function(frm) {
		// Set default job date to today if not set
		if (!frm.doc.job_date) {
			frm.set_value('job_date', frappe.datetime.get_today());
		}
		
		// Set default status if not set
		if (!frm.doc.job_status) {
			frm.set_value('job_status', 'Open');
		}
		
		if (!frm.doc.advance_status) {
			frm.set_value('advance_status', 'Open');
		}
		
		// Add custom buttons for submitted documents
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Print Job Card'), function() {
				frm.print_doc();
			});
			
			frm.add_custom_button(__('View Consignment Note'), function() {
				if (frm.doc.consignment_note) {
					frappe.set_route("Form", "Consignment Note", frm.doc.consignment_note);
				}
			});
		}
		
		// Add button to create job card from consignment note (for new documents)
		if (frm.is_new()) {
			frm.add_custom_button(__('From Consignment Note'), function() {
				show_consignment_note_dialog(frm);
			}, __('Get Items From'));
		}
	},

	consignment_note: function(frm) {
		if (frm.doc.consignment_note) {
			// Fetch consignment note details
			frappe.call({
				method: 'snelex.snelex.doctype.job_card.job_card.get_consignment_note_details',
				args: {
					consignment_note: frm.doc.consignment_note
				},
				callback: function(r) {
					if (r.message) {
						// Populate fields from consignment note
						frm.set_value('consignment_from', r.message.consignment_from);
						frm.set_value('consignment_to', r.message.consignment_to);
						frm.set_value('payment_by', r.message.payment_by);
						frm.set_value('tracking_no', r.message.tracking_no);
						
						// Shipper information
						frm.set_value('shipper_name', r.message.shipper_name);
						frm.set_value('shipper_contact', r.message.shipper_name);
						frm.set_value('shipper_phone', r.message.shipper_phone);
						frm.set_value('shipper_email', r.message.shipper_email);
						
						// Consignee information
						frm.set_value('consignee_name', r.message.consignee_name);
						frm.set_value('consignee_contact', r.message.consignee_name);
						frm.set_value('consignee_phone', r.message.consignee_phone);
						frm.set_value('consignee_email', r.message.consignee_email);
						
						// Shipment summary
						frm.set_value('total_pieces', r.message.total_pieces);
						frm.set_value('total_weight', r.message.total_weight);
						frm.set_value('number_of_cartons', r.message.number_of_cartons);
						frm.set_value('number_of_bundles', r.message.number_of_bundles);
						
						// Job description from consignment note description
						if (r.message.job_description) {
							frm.set_value('job_description', r.message.job_description);
						}
					}
				}
			});
		} else {
			// Clear all fields when consignment note is cleared
			clear_consignment_fields(frm);
		}
	},

	job_status: function(frm) {
		// Auto-set actual delivery date when status is completed
		if (frm.doc.job_status === 'Completed' && !frm.doc.actual_delivery_date) {
			frm.set_value('actual_delivery_date', frappe.datetime.get_today());
		}
	},

	before_submit: function(frm) {
		// Validate mandatory fields before submission
		let mandatory_fields = [
			['job_date', 'Job Date'],
			['consignment_note', 'Consignment Note'],
			['job_status', 'Job Status']
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

		// Validate consignment note is submitted
		if (frm.doc.consignment_note) {
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Consignment Note',
					filters: {'name': frm.doc.consignment_note},
					fieldname: 'docstatus'
				},
				async: false,
				callback: function(r) {
					if (r.message && r.message.docstatus != 1) {
						frappe.throw(__('Job Card can only be created from submitted Consignment Notes'));
					}
				}
			});
		}
	}
});

// Helper function to show consignment note selection dialog
function show_consignment_note_dialog(frm) {
	let dialog = new frappe.ui.Dialog({
		title: __('Select Consignment Note'),
		fields: [
			{
				fieldtype: 'Link',
				fieldname: 'consignment_note',
				label: __('Consignment Note'),
				options: 'Consignment Note',
				reqd: 1,
				get_query: function() {
					return {
						filters: {
							'docstatus': 1  // Only submitted consignment notes
						}
					};
				}
			}
		],
		primary_action: function() {
			let values = dialog.get_values();
			if (values.consignment_note) {
				// Check if job card already exists for this consignment note
				frappe.call({
					method: 'frappe.client.get_value',
					args: {
						doctype: 'Job Card',
						filters: {'consignment_note': values.consignment_note},
						fieldname: 'name'
					},
					callback: function(r) {
						if (r.message && r.message.name) {
							frappe.msgprint(__('Job Card {0} already exists for this Consignment Note', [r.message.name]));
						} else {
							frm.set_value('consignment_note', values.consignment_note);
							dialog.hide();
						}
					}
				});
			}
		},
		primary_action_label: __('Select')
	});
	
	dialog.show();
}

// Helper function to clear consignment-related fields
function clear_consignment_fields(frm) {
	let fields_to_clear = [
		'consignment_from', 'consignment_to', 'payment_by', 'tracking_no',
		'shipper_name', 'shipper_contact', 'shipper_phone', 'shipper_email',
		'consignee_name', 'consignee_contact', 'consignee_phone', 'consignee_email',
		'total_pieces', 'total_weight', 'number_of_cartons', 'number_of_bundles'
	];
	
	fields_to_clear.forEach(function(field) {
		frm.set_value(field, '');
	});
}

// Custom query for consignment note to show only submitted ones
frappe.ui.form.on('Job Card', {
	setup: function(frm) {
		// Filter consignment notes to show only submitted ones
		frm.set_query('consignment_note', function() {
			return {
				filters: {
					'docstatus': 1
				}
			};
		});
	}
});