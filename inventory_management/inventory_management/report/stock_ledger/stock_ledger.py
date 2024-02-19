# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
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
		}
	]
	sle = frappe.qb.DocType("Stock Ledger Entry")
	data = frappe.qb.from_(sle).select("*").run(as_dict=True)
	print("data", data)
	
	return columns, data


