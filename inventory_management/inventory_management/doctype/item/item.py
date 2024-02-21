# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from ..stock_entry.stock_entry import create_sle
from ..stock_entry.test_stock_entry import create_test_stock_entry

class Item(Document):
	def after_insert(self):
		sle_item = {
			"item": self.name,
			"qty": self.opening_qty,
			"rate": self.opening_valuation_rate,
			"target_warehouse": self.opening_warehouse,
			"name": self.name,
    	}
		create_test_stock_entry([sle_item], "Receive")