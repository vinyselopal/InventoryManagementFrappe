// Copyright (c) 2024, Viny Selopal and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Ledger"] = {
	"filters": [
		{
			"fieldname":"Item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"reqd": 1
		},
		{
			"fieldname":"Warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"reqd": 1
		},
	]
};
