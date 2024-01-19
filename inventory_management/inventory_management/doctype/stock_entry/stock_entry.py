# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StockEntry(Document):
	def on_submit(self):
		for item in self.items:
			if self.type == "Receive":
				print("receive")
				new_doc = frappe.new_doc('Stock Ledger Entry')
				new_doc.item = item
				new_doc.warehouse = item.target_warehouse
				new_doc.qty_change = item.qty
				old_entry = frappe.get_doc(doctype = "Stock Ledger Entry", item = item.item)
				old_valuation = old_entry.valuation_rate or 0
				old_qty = old_entry.qty_change or 0
				new_doc.valuation_rate = (old_valuation * old_qty) + (item.rate * item.qty) / (old_qty + item.qty)
				new_doc.insert()

			elif self.type == "Consume":
				print("consume")
				new_doc = frappe.new_doc('Stock Ledger Entry')
				new_doc.item = item
				new_doc.warehouse = item.source_warehouse
				new_doc.qty_change = - item.qty
				old_entry = frappe.get_doc(doctype = "Stock Ledger Entry", item = item.item)
				old_valuation = old_entry.valuation_rate or 0
				old_qty = old_entry.qty_change or 0
				new_doc.valuation_rate = (old_valuation * old_qty) + (item.rate * item.qty) / (old_qty + item.qty)
				new_doc.insert()
			else:
				print("transfer")
				new_doc = frappe.new_doc('Stock Ledger Entry')
				new_doc.item = item
				new_doc.warehouse = item.target_warehouse
				new_doc.qty_change = item.qty
				old_entry = frappe.get_doc(doctype="Stock Ledger Entry", item= item.item)
				old_valuation = old_entry.valuation_rate or 0
				old_qty = old_entry.qty_change or 0
				new_doc.valuation_rate = (old_valuation * old_qty) + (item.rate * item.qty) / (old_qty + item.qty)
				new_doc.insert()
				new_doc = frappe.new_doc('Stock Ledger Entry')
				new_doc.item = item
				new_doc.warehouse = item.source_warehouse
				new_doc.qty_change = - item.qty
				old_entry = frappe.get_doc(doctype = "Stock Ledger Entry", item = item.item)
				old_valuation = old_entry.valuation_rate or 0
				old_qty = old_entry.qty_change or 0
				new_doc.valuation_rate = (old_valuation * old_qty) + (item.rate * item.qty) / (old_qty + item.qty)
				new_doc.insert()

	def on_cancel(self):
		for item in self.items:
			if self.type == "Receive":
				print("receive")
				new_doc = frappe.new_doc('Stock Ledger Entry')
				old_doc = frappe.get_doc(doctype = "Stock Ledger Entry", item = item.item)
				new_doc.item = item
				new_doc.warehouse = item.target_warehouse
				new_doc.qty_change = - item.qty
				old_valuation = old_doc.valuation_rate or 0
				old_qty = old_doc.qty_change or 0
				new_doc.valuation_rate = (old_valuation * old_qty) + (item.rate * - item.qty) / (old_qty - item.qty)
				new_doc.insert()

			elif self.type == "Consume":
				print("consume")
				new_doc = frappe.new_doc('Stock Ledger Entry')
				old_doc = frappe.get_doc(doctype = "Stock Ledger Entry", item = item.item)
				new_doc.item = item
				new_doc.warehouse = item.source_warehouse
				new_doc.qty_change = item.qty
				old_valuation = old_entry.valuation_rate or 0
				old_qty = old_entry.qty_change or 0
				new_doc.valuation_rate = (old_valuation * old_qty) + (item.rate * item.qty) / (old_qty + item.qty)
				new_doc.insert()
			else:
				print("transfer")
				new_doc = frappe.new_doc('Stock Ledger Entry')
				old_entry = frappe.get_doc(doctype="Stock Ledger Entry", item= item.item)
				new_doc.item = item
				new_doc.warehouse = item.target_warehouse
				new_doc.qty_change = - item.qty
				old_valuation = old_entry.valuation_rate or 0
				old_qty = old_entry.qty_change or 0
				new_doc.valuation_rate = (old_valuation * old_qty) + (item.rate * - item.qty) / (old_qty - item.qty)
				new_doc.insert()
				new_doc = frappe.new_doc('Stock Ledger Entry')
				new_doc.item = item
				new_doc.warehouse = item.source_warehouse
				new_doc.qty_change = item.qty
				old_entry = frappe.get_doc(doctype = "Stock Ledger Entry", item = item.item)
				old_valuation = old_entry.valuation_rate or 0
				old_qty = old_entry.qty_change or 0
				new_doc.valuation_rate = (old_valuation * old_qty) + (item.rate * item.qty) / (old_qty + item.qty)
				new_doc.insert()
	pass
