# Copyright (c) 2024, Viny Selopal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.query_builder.functions import Sum


class StockEntry(Document):
    def validate(self):
        self.validate_balance_qty()
        self.validate_mandatory_warehouses()

    def validate_balance_qty(self):
        pass

    def validate_mandatory_warehouses(self):
        pass

    def on_submit(self):
        for item in self.items:
            if self.type == "Receive":
                create_sle(item.target_warehouse, item.qty, item)

            elif self.type == "Consume":
                create_sle(item.source_warehouse, -item.qty, item)

            else:
                create_sle(item.target_warehouse, item.qty, item)
                create_sle(item.source_warehouse, -item.qty, item)

    def on_cancel(self):
        for item in self.items:
            if self.type == "Receive":
                create_sle(item.target_warehouse, -item.qty, item)

            elif self.type == "Consume":
                create_sle(item.source_warehouse, item.qty, item)

            else:
                create_sle(item.target_warehouse, -item.qty, item)
                create_sle(item.source_warehouse, item.qty, item)


def create_sle(warehouse: str, qty: float, item: dict) -> None:
    sle = frappe.new_doc("Stock Ledger Entry")
    sle.item = item.item
    sle.warehouse = warehouse
    sle.qty_change = qty
    sle.valuation_rate = get_valuation_rate(item)
    sle.insert()


def get_valuation_rate(item: dict) -> float:
    StockLedgerEntry = frappe.qb.DocType("Stock Ledger Entry")

    result = (
        frappe.qb.from_(StockLedgerEntry)
        .select(
            Sum(StockLedgerEntry.valuation_rate * StockLedgerEntry.qty_change).as_("valuation_rate_sum"),
            Sum(StockLedgerEntry.qty_change).as_("qty_change"),
        )
        .where(
            (StockLedgerEntry.item == item)
            & (StockLedgerEntry.docstatus == 1)
        )
    ).run(as_dict=True)

    return (
       (result[0].valuation_rate_sum + (item.rate * item.qty)) / (result[0].qty_change + item.qty)
    ) if result else 0