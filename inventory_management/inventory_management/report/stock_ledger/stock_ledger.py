# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data

def get_columns(filters):
	columns = [
		{
			"fieldname":"item",
			"label": _("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"reqd": 1
		},
		{
			"fieldname":"warehouse",
			"label": _("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"reqd": 1
		},
		{
			"fieldname":"qty_change",
			"label": _("Qty Change"),
			"fieldtype": "Int",
			"reqd": 1
		},
		{
			"fieldname":"valuation_rate",
			"label": _("Valuation Rate"),
			"fieldtype": "Currency",
			"reqd": 1
		},

	]
	return columns

def get_data(filters):
	Sle = frappe.qb.DocType("Stock Ledger Entry")
	query = frappe.qb.from_(Sle).select("*")


	for condition in ["Warehouse", "Item"]:
		if filters.get(condition):
			query = query.where((Sle[condition] == filters.get(condition)))

	sles = query.run(as_dict=True, debug=True)
	return sles

