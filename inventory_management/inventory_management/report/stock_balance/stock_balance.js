// Copyright (c) 2024, Viny Selopal and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Ledger"] = {
	"filters": [
		{
			"fieldname":"Item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
		},
		{
			"fieldname":"Warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
		},
		{
			"fieldname":"To Date",
			"label": __("To Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname":"From Date",
			"label": __("From Date"),
			"fieldtype": "Date",
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "qty_change" && data && data.qty_change < 0) {
			value = "<span style='color:red'>" + value + "</span>";
		}
		else if (column.fieldname == "qty_change" && data && data.qty_change > 0) {
			value = "<span style='color:green'>" + value + "</span>";
		}

		return value;
	},
};
