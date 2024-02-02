# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from ..stock_entry.stock_entry import create_sle

class Item(Document):
	def on_save(self):
		if self.opening_warehouse and self.opening_qty:
			create_sle(self.opening_warehouse, self.opening_qty, self, self.valuation_rate)
