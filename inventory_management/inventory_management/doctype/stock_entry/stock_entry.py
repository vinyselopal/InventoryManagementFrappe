# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum
from pypika.terms import Case
from pypika import Field
from pypika import functions as fn


class StockEntry(Document):
    def create_sle(self, warehouse, qty, stock_ledger_item):
        new_sle_doc = frappe.new_doc("Stock Ledger Entry")
        new_sle_doc.item = stock_ledger_item
        new_sle_doc.warehouse = warehouse
        new_sle_doc.qty_change = qty

        stock_ledger_entries = frappe.qb.from_("Stock Ledger Entry")
        item = stock_ledger_item.item

        item_field = frappe.qb.Field("item")
        qty_change_field = frappe.qb.Field("qty_change")
        valuation_rate_field = frappe.qb.Field("valuation_rate")

        item_stock_ledger_entries = stock_ledger_entries.select("*").where(
            item_field == item
        )

        ttl_valuation_rate = Sum(valuation_rate_field * qty_change_field).as_(
            "val_rate_sum"
        )
        response = item_stock_ledger_entries.select(ttl_valuation_rate).run(
            as_dict=True
        )
        stock_ledger_old_valuation_rates_sum = response[0].val_rate_sum or 0

        ttl_qty = Sum(item_stock_ledger_entries.qty_change).as_("qtysum")
        response = item_stock_ledger_entries.select(ttl_qty).run(as_dict=True)
        print("response", response)
        stock_ledger_ttl_qtys = response[0].qtysum or 0

        valuation_rate = (
            stock_ledger_old_valuation_rates_sum
            + (stock_ledger_item.rate * stock_ledger_item.qty)
        ) / (stock_ledger_ttl_qtys + stock_ledger_item.qty)
        new_sle_doc.valuation_rate = valuation_rate
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

    def on_cancel(self):
        for item in self.items:
            if self.type == "Receive":
                self.create_sle(item.target_warehouse, -item.qty, item)

            elif self.type == "Consume":
                self.create_sle(item.source_warehouse, item.qty, item)

            else:
                self.create_sle(item.target_warehouse, -item.qty, item)
                self.create_sle(item.source_warehouse, item.qty, item)
