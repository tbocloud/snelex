def get_data():
	return {
		"fieldname": "shipper",
		"non_standard_fieldnames": {"Customer": "customer_name"},
		"transactions": [
			{"items": ["Customer"]},
		],
	}
