# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count
from pypika.terms import Case
from pypika import Field
from pypika import functions as fn

class StockEntry(Document):

	def create_sle(self, warehouse,qty, item):
		new_sle_doc = frappe.new_doc('Stock Ledger Entry')
		new_sle_doc.item = item
		new_sle_doc.warehouse = warehouse
		new_sle_doc.qty_change = qty

		stock_ledger_entries = frappe.qb.from_("Stock Ledger Entry").where(item == item.item)
		print(stock_ledger_entries)
		stock_ledger_old_valuation_rates_sum = stock_ledger_entries.select(fn.Sum(Field("valuation_rate") * Field("qty_change")))
		stock_ledger_ttl_qtys = stock_ledger_entries.select(fn.Sum(stock_ledger_entries.qty_change))
		new_sle_doc.valuation_rate = (stock_ledger_old_valuation_rates_sum + (item.rate * item.qty)) / (stock_ledger_ttl_qtys + item.qty)
		
		new_sle_doc.insert()

	def on_submit(self):
		for item in self.items:
			if self.type == "Receive":
				self.create_sle(item.target_warehouse, item.qty, item)

			elif self.type == "Consume":
				self.create_sle(item.source_warehouse, -item.qty, item)

			else:
				self.create_sle(item.target_warehouse, item.qty, item)
				self.create_sle(item.source_warehouse, -item.qty, item)

	def create_reverse_sle(self, warehouse, qty, item):
		new_sle_doc = frappe.new_doc('Stock Ledger Entry')
		new_sle_doc.item = item
		new_sle_doc.warehouse = item.warehouse
		new_sle_doc.qty_change = qty

		stock_ledger_entries = frappe.qb.from_("Stock Ledger Entry").where(item == item.item)
		stock_ledger_old_valuation_rates_sum = stock_ledger_entries.select(fn.Sum(Field("valuation_rate") * Field("qty_change")))
		stock_ledger_ttl_qtys = stock_ledger_entries.select(fn.Sum(stock_ledger_entries.qty_change))

		new_sle_doc.valuation_rate = (stock_ledger_old_valuation_rates_sum + (item.rate * item.qty)) / (stock_ledger_ttl_qtys + item.qty)
		
		new_sle_doc.insert()

	def on_cancel(self):
		for item in self.items:
			if self.type == "Receive":
				create_reverse_sle(item.target_warehouse, - item.qty, item)

			elif self.type == "Consume":
				create_reverse_sle(item.source_warehouse, item.qty, item)

			else:
				create_reverse_sle(item.target_warehouse, - item.qty, item)
				create_reverse_sle(item.source_warehouse, item.qty, item)
	
