# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

from frappe.model.document import Document
from frappe.utils import today, now
import frappe

class Item(Document):
    def after_insert(self):
        sle_item = {
            "item": self.name,
            "qty": self.opening_qty,
            "rate": self.opening_valuation_rate,
            "target_warehouse": self.opening_warehouse,
        }
        self.create_stock_entry([sle_item], "Receive")

    def create_stock_entry(self: object, stock_entry_items: list, type: str):
        doc = frappe.new_doc("Stock Entry")
        doc.date = today()
        doc.time = now()
        doc.type = type

        for item in stock_entry_items:
            doc.append("stock_entry_items", item)

        doc.insert(ignore_if_duplicate=True)
        doc.submit()
